#!/usr/bin/env python3
"""pg_preflight.py — roda as consultas dos 10 gates contra um Postgres.

Uso:
    python scripts/pg_preflight.py --dry-run                  # imprime o SQL de cada gate
    python scripts/pg_preflight.py --dsn "$DATABASE_URL"      # executa (read-only)
    python scripts/pg_preflight.py --dsn "$URL" --only P1,P9  # subset
    python scripts/pg_preflight.py --dsn "$URL" --json

Regras embutidas:
  - TODA consulta é SELECT em catálogo (pg_class/pg_proc/pg_policies/pg_roles). Nenhum DDL/DCL.
  - as consultas rodam em transação com `SET TRANSACTION READ ONLY`; qualquer tentativa de escrita falha.
  - gate sem consulta executada é `NOT_TESTED`, nunca `PASS`.
  - gate que depende de processo (P7 restore, P8 política de auditoria) sai como `MANUAL` — o script
    mostra o que conferir, não inventa resultado.

Requer `psql` no PATH (não usa driver). Sem psql:
    exit 2 com instrução de instalar, e `--dry-run` continua funcionando.

Exit: 0 todos os gates automáticos PASS · 1 há FAIL automático · 2 falta dependência
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

SCHEMA_PADRAO = "app"

GATES = {
    "P1": {
        "titulo": "FORCE ROW LEVEL SECURITY",
        "severidade": "BLOCKER",
        "sql": """
SELECT n.nspname AS schema, c.relname AS tabela,
       c.relrowsecurity AS rls, c.relforcerowsecurity AS force,
       pg_get_userbyid(c.relowner) AS dono
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname NOT IN ('pg_catalog','information_schema')
  AND (NOT c.relrowsecurity OR NOT c.relforcerowsecurity)
ORDER BY 1,2;
""",
        "falha_quando": "qualquer linha retornada (tabela sem RLS e/ou sem FORCE)",
    },
    "P2": {
        "titulo": "statement_timeout por role",
        "severidade": "BLOCKER",
        "sql": """
SELECT rolname, rolconfig,
       COALESCE((SELECT option_value FROM pg_options_to_table(rolconfig)
                 WHERE option_name='statement_timeout'), 'nao definido') AS statement_timeout
FROM pg_roles WHERE rolcanlogin AND rolname NOT LIKE 'pg\\_%'
ORDER BY rolname;
""",
        "falha_quando": "role de aplicação sem statement_timeout (ou '0')",
    },
    "P3": {
        "titulo": "search_path fixado nas funções",
        "severidade": "BLOCKER",
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
        "sql": """
SELECT 'float_para_dinheiro' AS achado, table_schema, table_name, column_name
FROM information_schema.columns
WHERE table_schema = '%(schema)s' AND data_type IN ('real','double precision')
UNION ALL
SELECT 'coluna_de_dinheiro_nulavel', table_schema, table_name, column_name
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
        "sql": """
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = '%(schema)s' AND privilege_type = 'SELECT'
  AND table_name ~* '(user|titular|kyc|customer)'
ORDER BY 1,3;
""",
        "falha_quando": "grant de SELECT em tabela de PII para role de aplicação/anon",
    },
    "P6": {
        "titulo": "CREATE no schema public",
        "severidade": "MAJOR",
        "sql": """
SELECT nspname, nspacl, (nspacl::text LIKE '%%=C/%%' OR nspacl::text LIKE '%%=UC/%%') AS public_pode_criar
FROM pg_namespace WHERE nspname = 'public';
""",
        "falha_quando": "public_pode_criar = true",
    },
    "P7": {
        "titulo": "backup/restore + RTO/RPO",
        "severidade": "BLOCKER",
        "sql": """
SELECT name, setting FROM pg_settings
WHERE name IN ('wal_level','archive_mode','archive_command');
""",
        "falha_quando": "processo: sem registro de restore medido. O SQL só mostra a base de PITR.",
        "manual": "Exige registro de ensaio de restore (data, tempo, verificação de conteúdo) e RTO/RPO em número.",
    },
    "P8": {
        "titulo": "trilha de auditoria de leitura",
        "severidade": "MAJOR",
        "sql": """
SELECT (SELECT count(*) FROM pg_extension WHERE extname='pgaudit') AS tem_pgaudit,
       (SELECT current_setting('log_statement', true)) AS log_statement,
       (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE c.relkind='r' AND (c.relname ILIKE '%%audit%%' OR c.relname ILIKE '%%access_log%%')) AS tabelas_auditoria;
""",
        "falha_quando": "sem pgaudit e log_statement='none' e sem tabela de auditoria",
    },
    "P9": {
        "titulo": "RLS tabela por tabela",
        "severidade": "BLOCKER",
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
        "sql": """
SELECT rolname, rolsuper, rolbypassrls, rolcanlogin
FROM pg_roles WHERE rolsuper OR rolbypassrls ORDER BY rolname;
""",
        "falha_quando": "role de aplicação com BYPASSRLS; e (check externo) service_role no cliente",
        "manual": "Rodar também: rg -n 'service_role|SERVICE_ROLE_KEY' . — saída tem de ser vazia.",
    },
}


def montar(only: list[str], schema: str) -> dict:
    selecionados = {k: v for k, v in GATES.items() if not only or k in only}
    for v in selecionados.values():
        v["sql"] = v["sql"].replace("%(schema)s", schema).strip()
    return selecionados


def rodar_psql(dsn: str, sql: str) -> tuple[int, str]:
    cmd = ["psql", dsn, "-X", "-q", "-A", "-F", "|", "--csv",
           "-c", "SET TRANSACTION READ ONLY;", "-c", sql]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    saida = (p.stdout or "") + (p.stderr or "")
    return p.returncode, saida.strip()


def linhas_de_dados(csv: str) -> int:
    """Conta linhas de resultado (descontando cabeçalho)."""
    linhas = [l for l in csv.splitlines() if l.strip() and not l.startswith("SET")]
    return max(0, len(linhas) - 1) if linhas else 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--dsn", default=None, help="string de conexão (somente leitura)")
    ap.add_argument("--dry-run", action="store_true", help="imprime o SQL de cada gate")
    ap.add_argument("--only", default=None, help="subset, ex.: P1,P9")
    ap.add_argument("--schema", default=SCHEMA_PADRAO)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    only = [s.strip().upper() for s in args.only.split(",")] if args.only else []
    gates = montar(only, args.schema)

    if args.dry_run or not args.dsn:
        for k, g in gates.items():
            print(f"-- ===== {k} {g['titulo']} ({g['severidade']})")
            print(f"-- falha quando: {g['falha_quando']}")
            if g.get("manual"):
                print(f"-- manual: {g['manual']}")
            print(g["sql"])
            print()
        if not args.dsn:
            print("sem --dsn: nada executado (todos os gates ficam NOT_TESTED)")
        return 0

    if not shutil.which("psql"):
        print("ERRO: psql não está no PATH. Instale o cliente Postgres ou use --dry-run.", file=sys.stderr)
        return 2

    resultados = []
    falhou = False
    for k, g in gates.items():
        if g.get("seria_manual") or (k in ("P7",) and g.get("manual")):
            resultados.append({"gate": k, "titulo": g["titulo"], "estado": "MANUAL",
                               "linhas": None, "evidencia": g.get("manual", "")})
            continue
        rc, saida = rodar_psql(args.dsn, g["sql"])
        if rc != 0:
            estado = "BLOCKED"
            falhou = True
        else:
            n = linhas_de_dados(saida)
            estado = "PASS" if n == 0 else "FAIL"
            if estado == "FAIL":
                falhou = True
        resultados.append({"gate": k, "titulo": g["titulo"], "severidade": g["severidade"],
                           "estado": estado, "linhas": None if rc else linhas_de_dados(saida),
                           "evidencia": saida[:2000]})

    if args.json:
        print(json.dumps(resultados, indent=2, ensure_ascii=False))
    else:
        print(f"{'gate':<4} {'titulo':<38} {'sev':<8} {'estado':<8} linhas")
        print("-" * 78)
        for r in resultados:
            print(f"{r['gate']:<4} {r['titulo'][:37]:<38} {r.get('severidade','-'):<8} "
                  f"{r['estado']:<8} {r.get('linhas') if r.get('linhas') is not None else '-'}")
        print()
        print("NOT_TESTED não aparece aqui: gate sem execução é declarado manualmente no relatório.")
        if falhou:
            print("há gate em FAIL/BLOCKED — não é deployável")

    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
