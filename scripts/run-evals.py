#!/usr/bin/env python3
"""run-evals.py — runner e auditor de evals do arsenal.

Comandos:
  --list                     lista cenários (todas as skills ou --skill)
  --check                    auditoria determinística de coerência dos evals
  --schema                   valida cada evals.json contra evals.schema.json
  --prompts                  gera prompts prontos em evals-prompts/ para execução manual
  --record                    equivalente a: python scripts/record-eval.py (repassa os argumentos)
  --report                   estado consolidado (declarados × executados por skill)

O que ele NÃO faz: executar o comportamento da skill. Isso exige sessão de agente real; o harness
valida, prepara o prompt, e guarda o veredito de quem executou.

Exit:
  --check/--schema : 0 = ok · 1 = problema
  --report         : 0 = todos executados · 1 = há cenário sem resultado
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def apontar_raiz(argv: list[str]) -> list[str]:
    """Consome `--raiz <pasta>` e reposiciona RAIZ e tudo que deriva dela.

    Sem isso, apontar o verificador para uma fixture é impossível: ele sempre enxerga o repo
    de onde o arquivo foi copiado. Um ataque a estes scripts caiu nessa armadilha -- rodar com
    `cwd=fixture` não muda nada, porque a raiz vem de `__file__`, e o resultado é verde sem
    medir absolutamente nada.

    Reatribuir só o global não basta: SKILLS/RESULTADOS/PROMPTS/SCHEMA são calculados no
    import, a partir da RAIZ original. Foram incluídos aqui de propósito; qualquer outro
    derivado novo precisa entrar nesta lista, senão passa a apontar para dois lugares.
    """
    global RAIZ, SKILLS, RESULTADOS, PROMPTS, SCHEMA
    restante = list(argv)
    nova = None
    for i, a in enumerate(restante):
        if a == "--raiz" and i + 1 < len(restante):
            nova = Path(restante[i + 1]).resolve()
            del restante[i:i + 2]
            break
        if a.startswith("--raiz="):
            nova = Path(a.split("=", 1)[1]).resolve()
            del restante[i]
            break
    if nova is not None:
        RAIZ = nova
        SKILLS = RAIZ / "skills"
        RESULTADOS = RAIZ / "evals-results"
        PROMPTS = RAIZ / "evals-prompts"
        SCHEMA = RAIZ / "evals.schema.json"
        if not SKILLS.is_dir():
            print(f"ERRO: {SKILLS} não existe -- nada para avaliar", file=sys.stderr)
            raise SystemExit(2)
    return restante
SKILLS = RAIZ / "skills"
RESULTADOS = RAIZ / "evals-results"
PROMPTS = RAIZ / "evals-prompts"
SCHEMA = RAIZ / "evals.schema.json"

# Fonte única em scripts/_tracks.py (era uma cópia manual que esqueceu a 10ª skill).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tracks import para_apelido as _para_apelido  # noqa: E402

CURTO = _para_apelido()

STOP = set("""a o as os um uma de da do das dos e ou que em no na nos nas para por com sem ao aos
se ser é são estar está como quando onde qual quais seu sua seus suas este esta isso isto
não mais menos muito pouco todo toda todos todas ele ela eles elas você vocês nós
the a an of to in on and or is are be with without not no do does this that it its
must should shall can could will would may might""".split())


def carregar(skill: Path) -> dict:
    f = skill / "evals" / "evals.json"
    if not f.is_file():
        return {"cases": [], "erro": "evals/evals.json ausente"}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"cases": [], "erro": f"JSON inválido: {exc}"}


def corpus(skill: Path) -> str:
    partes = []
    for nome in ("SKILL.md", "README.md"):
        p = skill / nome
        if p.is_file():
            partes.append(p.read_text(encoding="utf-8", errors="replace"))
    for sub in ("references", "templates"):
        d = skill / sub
        if d.is_dir():
            for p in d.rglob("*.md"):
                partes.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(partes).lower()


def termos(texto: str) -> set[str]:
    achados = re.findall(r"[a-záàâãéêíóôõúç0-9][a-záàâãéêíóôõúç0-9\-]{3,}", texto.lower())
    return {t for t in achados if t not in STOP and len(t) >= 5}


def validar_schema() -> tuple[int, list[str]]:
    if not SCHEMA.is_file():
        return 1, ["evals.schema.json ausente na raiz"]
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return 1, [f"evals.schema.json inválido: {exc}"]

    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None

    if jsonschema is None:
        # Declarar a limitação, não escondê-la. Sem a lib cai no checador manual abaixo, que
        # cobre campos obrigatórios e o padrão de `id` -- mas não vê enum, minLength,
        # additionalProperties nem tipo. Sair com "skills validadas: OK" nesse regime fazia um
        # ambiente sem jsonschema parecer ter passado uma validação completa (o CI passou a
        # instalar a dependência exatamente por causa disso; o código continuou mentindo).
        print("AVISO: jsonschema ausente -- validação PARCIAL (só campos obrigatórios e "
              "padrão de id). Instale com: python -m pip install jsonschema", file=sys.stderr)

    obrig = schema.get("properties", {}).get("cases", {}).get("items", {}).get("required", [])
    padrao = re.compile(r"^[a-z][a-z0-9-]+$")
    erros: list[str] = []
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        dados = carregar(skill)
        if dados.get("erro"):
            erros.append(f"{skill.name}: {dados['erro']}")
            continue
        if jsonschema is not None:
            try:
                jsonschema.validate(dados, schema)
                continue
            except jsonschema.ValidationError as exc:  # type: ignore[attr-defined]
                erros.append(f"{skill.name}: {exc.message} (em {list(exc.absolute_path)})")
                continue
        # fallback sem a lib: checagem manual do essencial
        for c in dados.get("cases", []):
            for ch in obrig:
                if not c.get(ch):
                    erros.append(f"{skill.name}/{c.get('id', '?')}: falta '{ch}'")
            if not padrao.match(str(c.get("id", ""))):
                erros.append(f"{skill.name}/{c.get('id', '?')}: id fora do padrão")
    return (1 if erros else 0), erros


def cmd_check(skill_filtro: str | None) -> int:
    total_casos = total_erros = total_avisos = 0
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        if skill_filtro and skill_filtro not in skill.name:
            continue
        dados = carregar(skill)
        casos = dados.get("cases", [])
        texto = corpus(skill)
        problemas, avisos = [], []
        if not casos:
            problemas.append("nenhum caso")
        ids = [c.get("id") for c in casos]
        if len(ids) != len(set(ids)):
            problemas.append("id duplicado")
        for c in casos:
            cid = c.get("id", "?")
            for campo in ("id", "title", "input", "expected", "fails_if"):
                if not c.get(campo):
                    problemas.append(f"{cid}: campo '{campo}' vazio")
            exp, fal = str(c.get("expected", "")), str(c.get("fails_if", ""))
            if exp and fal and exp.strip().lower() == fal.strip().lower():
                problemas.append(f"{cid}: expected == fails_if")
            termos_exp = termos(exp)
            achados = {t for t in termos_exp if t in texto}
            cobertura = len(achados) / len(termos_exp) if termos_exp else 1.0
            if termos_exp and cobertura < 0.34:
                problemas.append(f"{cid}: cobertura {len(achados)}/{len(termos_exp)} — regra pode não existir")
            elif termos_exp and cobertura < 0.6:
                avisos.append(f"{cid}: cobertura baixa ({len(achados)}/{len(termos_exp)})")
        total_casos += len(casos)
        total_erros += len(problemas)
        total_avisos += len(avisos)
        marca = "OK" if not problemas else "PROBLEMA"
        print(f"{skill.name:<40} {len(casos):>3} casos  {marca}")
        for p in problemas:
            print(f"    ERRO  {p}")
        for a in avisos:
            print(f"    aviso {a}")
    print()
    print(f"casos analisados: {total_casos} | erros: {total_erros} | avisos: {total_avisos}")
    return 0 if total_erros == 0 else 1


def cmd_list(skill_filtro: str | None, batch: int | None) -> int:
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        if skill_filtro and skill_filtro not in skill.name:
            continue
        casos = carregar(skill).get("cases", [])
        print(f"\n## {skill.name} ({len(casos)} casos)")
        for c in (casos[:batch] if batch else casos):
            print(f"  - {c.get('id')}: {str(c.get('input', ''))[:78]}")
    return 0


def cmd_prompts(skill_filtro: str | None, batch: int | None) -> int:
    PROMPTS.mkdir(exist_ok=True)
    gerados = 0
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        if skill_filtro and skill_filtro not in skill.name:
            continue
        casos = carregar(skill).get("cases", [])
        if not casos:
            continue
        destino = PROMPTS / skill.name
        destino.mkdir(parents=True, exist_ok=True)
        for c in (casos[:batch] if batch else casos):
            texto = (
                f"# Eval `{c['id']}` — {skill.name}\n\n"
                f"## Instrução\n\nCarregue a skill `{skill.name}` e responda ao cenário abaixo **como a skill "
                f"responderia**. Não consulte `expected` nem `fails_if` antes de responder.\n\n"
                f"## Cenário (input)\n\n{c['input']}\n\n"
                f"## Como julgar depois\n\n"
                f"- esperado: {c['expected']}\n"
                f"- reprova se: {c['fails_if']}\n\n"
                f"## Registro\n\n```bash\npython scripts/record-eval.py --skill {skill.name} "
                f"--eval-id {c['id']} --verdict <PASS|PARTIAL|FAIL|BLOCKED> "
                f"--response-file <arquivo> --evidence \"<trecho literal>\"\n```\n"
            )
            (destino / f"{c['id']}.md").write_text(texto, encoding="utf-8", newline="\n")
            gerados += 1
    print(f"prompts gerados: {gerados} em {PROMPTS.relative_to(RAIZ)}/")
    return 0


def cmd_report() -> int:
    print(f"{'skill':<42}{'declarados':>11}{'executados':>12}{'PASS':>6}{'PARTIAL':>9}{'FAIL':>6}{'BLOCKED':>9}")
    print("-" * 95)
    faltando = 0
    total = total_exec = 0
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        casos = carregar(skill).get("cases", [])
        total += len(casos)
        curto = CURTO.get(skill.name, skill.name.replace("dz23-", ""))
        pasta = RESULTADOS / curto
        vereditos: list[str] = []
        cobertos: set[str] = set()
        if pasta.is_dir():
            for md in pasta.glob("*.md"):
                texto = md.read_text(encoding="utf-8", errors="replace")
                m = re.search(r"\*\*Veredito:\*\*\s*\*{0,2}(PASS|PARTIAL|FAIL|NOT_TESTED|BLOCKED|NOT_RECOVERED)",
                              texto)
                if not m:
                    continue
                vereditos.append(m.group(1))
                mi = re.match(r"\d{4}-\d{2}-\d{2}-(.+)$", md.stem)
                if mi:
                    cobertos.add(mi.group(1))
        # Cobertura se mede por CENARIO DISTINTO, nao por arquivo. Contar arquivos fazia reexecutar
        # um caso ja registrado somar +1 de cobertura: com dois registros de
        # migration-without-rollback (09/11 autoavaliacao e 18/11 execucao real em Postgres), o
        # relatorio dizia 48 registrados / 96 pendentes enquanto o check correto dizia 47 / 97 -- os
        # dois "verdes" porque liam premissas diferentes. Reexecucao e historico legitimo; credito
        # extra e que nao e. O ultimo veredito por cenario e o que vale na contagem de estado.
        exec_ = len(cobertos & {str(c.get("id")) for c in casos if isinstance(c, dict)})
        total_exec += exec_
        sem = len(casos) - exec_
        faltando += max(0, sem)
        por_veredito: dict[str, str] = {}
        if pasta.is_dir():
            for md in sorted(pasta.glob("*.md")):          # ordem cronologica: o mais novo vence
                mi = re.match(r"\d{4}-\d{2}-\d{2}-(.+)$", md.stem)
                if not mi:
                    continue
                mv = re.search(r"\*\*Veredito:\*\*\s*\*{0,2}(PASS|PARTIAL|FAIL|NOT_TESTED|BLOCKED|NOT_RECOVERED)",
                               md.read_text(encoding="utf-8", errors="replace"))
                if mv:
                    por_veredito[mi.group(1)] = mv.group(1)
        conta = lambda v: sum(1 for x in por_veredito.values() if x == v)  # noqa: E731
        print(f"{skill.name:<42}{len(casos):>11}{exec_:>12}{conta('PASS'):>6}{conta('PARTIAL'):>9}"
              f"{conta('FAIL'):>6}{conta('BLOCKED'):>9}")
    print()
    pct = (total_exec / total * 100) if total else 0
    print(f"TOTAL: {total} declarados · {total_exec} registrados ({pct:.1f}%) · {faltando} sem resultado")
    return 0 if faltando == 0 else 1



def cmd_audit() -> int:
    """Estado da auditoria externa dos registros selecionados."""
    arq = RESULTADOS / "_audit-notes" / "AUDIT-STATUS.json"
    if not arq.is_file():
        print("sem AUDIT-STATUS.json — nenhum laudo conferido")
        return 0
    dados = json.loads(arq.read_text(encoding="utf-8"))
    conta: dict[str, int] = {}
    for l in dados.get("laudos", []):
        print(f"laudo: {l['arquivo']}\n   status: {l['status']} | veredito: {l['veredito']}")
        for m in l.get("motivos", []):
            print(f"   motivo: {m}")
    print()
    print(f"{'#':>3} {'eval':<34} {'status':<16} {'laudo':<28}")
    print("-" * 86)
    for e in dados["evals"]:
        conta[e["audit_status"]] = conta.get(e["audit_status"], 0) + 1
        print(f"{e['num']:>3} {e['eval_id']:<34} {e['audit_status']:<16} {e.get('laudo', '-'):<28}")
    print()
    for k in ("LITERAL", "PARÁFRASE", "NOT_AUDITED", "AUDITED_LITERAL"):
        print(f"{k:<14} {conta.get(k, 0)}")
    pend = conta.get("NOT_AUDITED", 0)
    if pend:
        print(f"\n{pend} eval(s) aguardam re-auditoria: audit-package/REAUDIT-PROMPT.md")
    return 0



def cmd_verify_quotes(laudo: str | None, como_json: bool) -> int:
    """Verifica se as citações dos laudos existem nas respostas.

    Sem --laudo: verifica os laudos marcados VALIDO em AUDIT-STATUS.json.
    Com --laudo: verifica o arquivo informado (serve de controle negativo).
    """
    import importlib.util

    caminho_mod = RAIZ / "scripts" / "check-audit-quotes.py"
    spec = importlib.util.spec_from_file_location("check_audit_quotes", caminho_mod)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    alvos: list[str] = []
    if laudo:
        alvos = [laudo]
    else:
        arq = RESULTADOS / "_audit-notes" / "AUDIT-STATUS.json"
        if not arq.is_file():
            # Antes isto devolvia 0 ("nada a verificar"), entao apagar o arquivo de
            # estado desligava silenciosamente a checagem de citacao fabricada.
            # Ausencia de estado e falha, nao aprovacao.
            print(f"FALHA: {arq.relative_to(RAIZ)} ausente — nao ha o que verificar, "
                  f"e isso nao e uma aprovacao")
            return 1
        try:
            dados = json.loads(arq.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"FALHA: {arq.relative_to(RAIZ)} ilegivel: {exc}")
            return 1
        alvos = [l["arquivo"] for l in dados.get("laudos", []) if l.get("status") == "VALIDO"]

    if not alvos:
        print("FALHA: nenhum laudo com status VALIDO registrado em AUDIT-STATUS.json")
        return 1

    saida = []
    falhou = False
    for alvo in alvos:
        try:
            res = mod.verificar_laudo(alvo)
        except FileNotFoundError:
            print(f"ERRO: laudo ausente: {alvo}")
            falhou = True
            continue
        saida.append(res)
        if not res["citacoes"]:
            print(f"{alvo}: AVISO — nenhuma citação longa encontrada")
            falhou = True
        elif not res["ok"]:
            falhou = True

    if como_json:
        print(json.dumps(saida, indent=2, ensure_ascii=False))
    else:
        for res in saida:
            r = res["resumo"]
            marca = "OK" if res["ok"] else "FALHA"
            print(f"{res['laudo']:<42} {marca:<6} verbatim={r['VERBATIM']:>3} "
                  f"adaptado={r['ADAPTADO']:>2} resumo={r['RESUMO']:>2} fabricado={r['FABRICADO']:>3}")
        if falhou:
            print("\ncitação fabricada encontrada — laudo não sustenta o veredito")

    return 0 if not falhou else 1


def main(argv: list[str]) -> int:
    argv = apontar_raiz(argv)
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=None, help="conferir outra árvore (fixture)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--schema", action="store_true")
    g.add_argument("--prompts", action="store_true")
    g.add_argument("--report", action="store_true")
    g.add_argument("--audit", action="store_true", help="estado da auditoria externa")
    g.add_argument("--verify-quotes", action="store_true",
                   help="confere se as citações dos laudos VALIDO existem nas respostas")
    g.add_argument("--record", nargs=argparse.REMAINDER, help="repassa para scripts/record-eval.py")
    ap.add_argument("--skill", default=None)
    ap.add_argument("--batch", type=int, default=None)
    ap.add_argument("--laudo", default=None, help="com --verify-quotes: verifica só este arquivo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.record is not None:
        cmd = [sys.executable, str(RAIZ / "scripts" / "record-eval.py")] + args.record
        return subprocess.call(cmd)
    if args.list:
        return cmd_list(args.skill, args.batch)
    if args.check:
        return cmd_check(args.skill)
    if args.schema:
        code, erros = validar_schema()
        print(f"skills validadas contra evals.schema.json: {'OK' if code == 0 else 'PROBLEMAS'}")
        for e in erros:
            print(f"  - {e}")
        return code
    if args.prompts:
        return cmd_prompts(args.skill, args.batch)
    if args.verify_quotes:
        return cmd_verify_quotes(args.laudo, args.json)
    if args.audit:
        return cmd_audit()
    if args.report:
        return cmd_report()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
