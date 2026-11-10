#!/usr/bin/env python3
"""pg_preflight.py — roda as consultas dos 10 gates contra um Postgres/Supabase.

Uso:
    python scripts/pg_preflight.py --dry-run                       # imprime o SQL de cada gate
    python scripts/pg_preflight.py --dsn "host=... user=... dbname=..."
    python scripts/pg_preflight.py --docker pgchk                  # via container (sem psql local)
    python scripts/pg_preflight.py --docker pgchk --dbname betcheck --user postgres
    python scripts/pg_preflight.py --dsn "$URL" --only P1,P9 --json

Garantias:
  - toda consulta é SELECT de catálogo, executada em transação READ ONLY;
  - cada gate tem uma REGRA DE VEREDITO própria (`veredito`): lista de infratores, contagem escalar ou
    processo manual. "0 linhas = PASS" para todos era o defeito da v1.0.0: P2/P6/P8/P10 devolvem linha
    mesmo em banco sadio, e passavam a FAIL falso;
  - gate de processo (P7 restore, P8 política, P10 externo) sai como `MANUAL` — o script não inventa veredito;
  - gate sem execução é `NOT_TESTED`, nunca `PASS`.

Exit: 0 todos PASS/MANUAL · 1 há FAIL · 2 falta dependência (psql ou container)
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys

SCHEMA_PADRAO = "app"

# ------------------------------------------------------------------ gates
# veredito: "rows"     -> infratores listados; 0 linhas = PASS
#           "contagem" -> consulta escalar; resultado 0 = PASS
#           "manual"   -> processo; nunca vira PASS automático
GATES: dict[str, dict] = {
    "P1": {
        "titulo": "FORCE ROW LEVEL SECURITY",
        "severidade": "BLOCKER",
        "veredito": "rows",
        "sql": """
SELECT n.nspname AS schema, c.relname AS tabela,
       c.relrowsecurity AS rls, c.relforcerowsecurity AS force,
       pg_get_userbyid(c.relowner) AS dono
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname NOT IN ('pg_catalog','information_schema')
  AND (NOT c.relrowsecurity OR NOT c.relforcerowsecurity)
ORDER BY 1,2;
""",
        "falha_quando": "qualquer linha (tabela sem RLS e/ou sem FORCE)",
    },
    "P2": {
        "titulo": "statement_timeout por role",
        "severidade": "BLOCKER",
        "escopo": "cluster",
        "veredito": "contagem",
        "sql": """
SELECT rolname, rolconfig FROM pg_roles
WHERE rolcanlogin AND NOT rolsuper AND rolname NOT LIKE 'pg\\_%' ORDER BY 1;
""",
        "veredito_sql": """
SELECT count(*) FROM pg_roles r
WHERE r.rolcanlogin AND NOT r.rolsuper AND r.rolname NOT LIKE 'pg\\_%'
  AND COALESCE((SELECT option_value FROM pg_options_to_table(r.rolconfig)
                WHERE option_name = 'statement_timeout'), '0') IN ('0','');
""",
        "falha_quando": "role de login sem statement_timeout (default 0 = sem limite)",
    },
    "P3": {
        "titulo": "search_path fixado nas funções",
        "severidade": "BLOCKER",
        "veredito": "rows",
        "sql": """
SELECT n.nspname AS schema, p.proname AS funcao, p.prosecdef AS security_definer,
       array_to_string(p.proconfig, ', ') AS config
FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname NOT IN ('pg_catalog','information_schema')
  AND (p.proconfig IS NULL
       OR NOT EXISTS (SELECT 1 FROM unnest(p.proconfig) c WHERE c LIKE 'search_path=%'))
ORDER BY p.prosecdef DESC, 1,2;
""",
        "falha_quando": "qualquer função de negócio sem search_path (prioridade: SECURITY DEFINER)",
    },
    "P4": {
        "titulo": "constraints de integridade",
        "severidade": "BLOCKER",
        "veredito": "rows",
        "sql": """
SELECT 'float_em_dinheiro' AS achado, table_schema, table_name, column_name
FROM information_schema.columns
WHERE table_schema = '%(schema)s' AND data_type IN ('real','double precision')
UNION ALL
SELECT 'coluna_monetaria_nulavel', table_schema, table_name, column_name
FROM information_schema.columns
WHERE table_schema = '%(schema)s' AND is_nullable = 'YES'
  AND column_name ~* '(balance|saldo|amount|valor|total)'
ORDER BY 1,3,4;
""",
        "falha_quando": "qualquer linha (float em dinheiro ou coluna monetária nulável)",
    },
    "P5": {
        "titulo": "PII exposta por tabela",
        "severidade": "BLOCKER",
        "veredito": "rows",
        "sql": """
SELECT g.grantee, g.table_schema, g.table_name, g.privilege_type
FROM information_schema.role_table_grants g
JOIN pg_class c ON c.relname = g.table_name
JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = g.table_schema
WHERE g.table_schema = '%(schema)s' AND g.privilege_type = 'SELECT'
  AND c.relkind = 'r'                       -- só tabela base; view com máscara é o alvo correto
  AND g.table_name ~* '(user|titular|kyc|customer)'
  AND g.grantee <> current_user
ORDER BY 1,3;
""",
        "falha_quando": "grant de SELECT em tabela de PII para role de aplicação/anon",
    },
    "P6": {
        "titulo": "CREATE no schema public",
        "severidade": "MAJOR",
        "veredito": "contagem",
        "sql": """
SELECT nspname, nspacl FROM pg_namespace WHERE nspname = 'public';
""",
        "veredito_sql": """
SELECT count(*) FROM pg_namespace n
WHERE n.nspname = 'public'
  AND (
        EXISTS (SELECT 1 FROM aclexplode(n.nspacl) a
                WHERE a.grantee = 0 AND a.privilege_type = 'CREATE')
        OR (n.nspacl IS NULL AND current_setting('server_version_num')::int < 150000)
      );
""",
        "falha_quando": "CREATE para PUBLIC no schema public (ACL nula só é suspeita em PG < 15, quando o default era permissivo)",
    },
    "P7": {
        "titulo": "backup/restore + RTO/RPO",
        "severidade": "BLOCKER",
        "escopo": "cluster",
        "veredito": "manual",
        "sql": """
SELECT name, setting FROM pg_settings
WHERE name IN ('wal_level','archive_mode','archive_command');
""",
        "falha_quando": "processo: sem registro de restore medido. O SQL só mostra a base de PITR.",
        "instrucao": "Exige registro de ensaio de restore (data, tempo medido, verificação de conteúdo) e "
                     "RTO/RPO em número.",
    },
    "P8": {
        "titulo": "trilha de auditoria de leitura",
        "severidade": "MAJOR",
        "veredito": "contagem",
        "sql": """
SELECT (SELECT count(*) FROM pg_extension WHERE extname='pgaudit') AS pgaudit,
       current_setting('log_statement', true) AS log_statement,
       (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE c.relkind='r' AND (c.relname ILIKE '%%audit%%' OR c.relname ILIKE '%%access_log%%')) AS tabelas_auditoria;
""",
        "veredito_sql": """
SELECT CASE WHEN (SELECT count(*) FROM pg_extension WHERE extname='pgaudit') > 0
              OR COALESCE(current_setting('log_statement', true), 'none') <> 'none'
              OR (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                  WHERE c.relkind='r' AND (c.relname ILIKE '%%audit%%'
                                           OR c.relname ILIKE '%%access_log%%')) > 0
            THEN 0 ELSE 1 END;
""",
        "falha_quando": "sem pgaudit, log_statement='none' e sem tabela de auditoria",
    },
    "P9": {
        "titulo": "RLS tabela por tabela",
        "severidade": "BLOCKER",
        "veredito": "rows",
        "sql": """
SELECT n.nspname, c.relname AS tabela_sem_policy
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname = '%(schema)s'
  AND NOT EXISTS (SELECT 1 FROM pg_policies p
                  WHERE p.schemaname = n.nspname AND p.tablename = c.relname)
ORDER BY 2;
""",
        "falha_quando": "qualquer tabela do schema de negócio sem policy",
    },
    "P10": {
        "titulo": "segregação de credencial",
        "severidade": "BLOCKER",
        "escopo": "cluster",
        "veredito": "contagem",
        "sql": """
SELECT rolname, rolsuper, rolbypassrls, rolcanlogin
FROM pg_roles WHERE rolbypassrls AND NOT rolsuper ORDER BY rolname;
""",
        "veredito_sql": """
SELECT count(*) FROM pg_roles
WHERE rolcanlogin AND rolbypassrls AND NOT rolsuper AND rolname NOT LIKE 'pg\\_%';
""",
        "falha_quando": "role de login NÃO-superuser com BYPASSRLS (superuser é esperado); e (externo) service_role no cliente",
        "instrucao": "Rodar também: rg -n 'service_role|SERVICE_ROLE_KEY' . — saída tem de ser vazia.",
    },
}


def preparar(only: list[str], schema: str) -> dict:
    sel = {k: dict(v) for k, v in GATES.items() if not only or k in only}
    for v in sel.values():
        v["sql"] = v["sql"].replace("%(schema)s", schema).strip()
        if "veredito_sql" in v:
            v["veredito_sql"] = v["veredito_sql"].replace("%(schema)s", schema).strip()
    return sel


def comando_psql(args) -> list[str] | None:
    if args.docker:
        if not shutil.which("docker"):
            return None
        return ["docker", "exec", "-i", args.docker, "psql",
                "-U", args.user or "postgres", "-d", args.dbname or "postgres"]
    if not shutil.which("psql"):
        return None
    return ["psql", args.dsn]


RE_RUIDO = re.compile(r"^(WARNING|NOTICE|HINT|DETAIL|LINE \d+|psql:|SET$|BEGIN$|ROLLBACK$)")


def rodar(base: list[str], sql: str) -> tuple[int, str]:
    """Executa o SELECT dentro de BEGIN READ ONLY ... ROLLBACK.

    A v1.0.0 usava `-c "SET TRANSACTION READ ONLY;"` sozinho, que o psql executa FORA de bloco de
    transação — o Postgres emite WARNING e o read-only não vale. Aqui o bloco é explícito.
    """
    script = f"BEGIN READ ONLY;\n{sql}\nROLLBACK;"
    cmd = base + ["-X", "-q", "-A", "-F", "|", "--csv", "-v", "ON_ERROR_STOP=1", "-c", script]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        return p.returncode, (p.stderr or p.stdout or "").strip()[:800]
    linhas = [l for l in (p.stdout or "").splitlines() if l.strip() and not RE_RUIDO.match(l.strip())]
    return 0, "\n".join(linhas)


def escalar(csv: str) -> int | None:
    """Primeiro valor numérico da saída (consulta escalar)."""
    for linha in csv.splitlines():
        for campo in linha.replace(",", "|").split("|"):
            c = campo.strip().strip('"')
            if c.isdigit():
                return int(c)
    return None


def linhas_dados(csv: str) -> int:
    ls = [l for l in csv.splitlines() if l.strip()]
    return max(0, len(ls) - 1) if ls else 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--dsn", default=None, help="string de conexão (read-only)")
    ap.add_argument("--docker", default=None, help="container com psql (alternativa ao psql local)")
    ap.add_argument("--dbname", default=None)
    ap.add_argument("--user", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None, help="subset, ex.: P1,P9")
    ap.add_argument("--schema", default=SCHEMA_PADRAO)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    only = [s.strip().upper() for s in args.only.split(",")] if args.only else []
    gates = preparar(only, args.schema)

    if args.dry_run or (not args.dsn and not args.docker):
        for k, g in gates.items():
            print(f"-- ===== {k} {g['titulo']} ({g['severidade']}) · veredito: {g['veredito']}")
            print(f"-- falha quando: {g['falha_quando']}")
            if g.get("instrucao"):
                print(f"-- manual: {g['instrucao']}")
            print(g["sql"])
            if "veredito_sql" in g:
                print(f"-- contagem de falhas (0 = PASS):\n{g['veredito_sql']}")
            print()
        if not args.dry_run:
            print("sem alvo: nada executado (todos os gates ficam NOT_TESTED)")
        return 0

    base = comando_psql(args)
    if base is None:
        onde = "--docker sem 'docker' no PATH" if args.docker else "psql não está no PATH"
        print(f"ERRO: {onde}. Use --docker <container> ou --dry-run.", file=sys.stderr)
        return 2

    resultados, falhou = [], False
    for k, g in gates.items():
        if g["veredito"] == "manual":
            rc, ev = rodar(base, g["sql"]) if g.get("sql") else (0, "")
            resultados.append({"gate": k, "titulo": g["titulo"], "severidade": g["severidade"],
                               "estado": "MANUAL", "escopo": g.get("escopo", "banco"), "infratores": None,
                               "evidencia": ev[:800], "instrucao": g.get("instrucao", "")})
            continue

        rc, ev = rodar(base, g["sql"])
        if rc != 0:
            resultados.append({"gate": k, "titulo": g["titulo"], "severidade": g["severidade"],
                               "estado": "BLOCKED", "escopo": g.get("escopo", "banco"),
                               "infratores": None, "evidencia": ev[:800]})
            falhou = True
            continue

        n_falhas = None
        if g["veredito"] == "contagem":
            rc2, ev2 = rodar(base, g["veredito_sql"])
            n_falhas = escalar(ev2) if rc2 == 0 else None
            if n_falhas is None:
                estado = "BLOCKED"
                falhou = True
            else:
                estado = "PASS" if n_falhas == 0 else "FAIL"
                falhou = falhou or estado == "FAIL"
        else:
            n = linhas_dados(ev)
            estado = "PASS" if n == 0 else "FAIL"
            falhou = falhou or estado == "FAIL"

        resultados.append({"gate": k, "titulo": g["titulo"], "severidade": g["severidade"],
                           "estado": estado, "escopo": g.get("escopo", "banco"),
                           "infratores": n_falhas if n_falhas is not None else linhas_dados(ev),
                           "evidencia": ev[:800]})

    if args.json:
        print(json.dumps(resultados, indent=2, ensure_ascii=False))
    else:
        print(f"{'gate':<4} {'titulo':<34} {'sev':<8} {'escopo':<8} {'estado':<8} {'infratores':>10}")
        print("-" * 82)
        for r in resultados:
            marca = r["estado"] if r["estado"] != "FAIL" else "FAIL"
            print(f"{r['gate']:<4} {r['titulo'][:33]:<34} {r['severidade']:<8} "
                  f"{r.get('escopo', 'banco'):<8} {marca:<8} "
                  f"{(r['infratores'] if r['infratores'] is not None else '-'):>10}")
        bloqueantes = [r for r in resultados if r["estado"] == "FAIL" and r["severidade"] == "BLOCKER"]
        manuais = [r for r in resultados if r["estado"] == "MANUAL"]
        print()
        if bloqueantes:
            print(f"BLOCKER em FAIL: {', '.join(r['gate'] for r in bloqueantes)} — não é deployável")
        elif falhou:
            print("há gate em FAIL (MAJOR) — deployável com plano, não com silêncio")
        else:
            print("nenhum gate automático em FAIL")
        if manuais:
            print(f"MANUAL (não automatizável, declarado): {', '.join(r['gate'] for r in manuais)}")

    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
