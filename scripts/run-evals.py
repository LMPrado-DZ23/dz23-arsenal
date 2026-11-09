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
SKILLS = RAIZ / "skills"
RESULTADOS = RAIZ / "evals-results"
PROMPTS = RAIZ / "evals-prompts"
SCHEMA = RAIZ / "evals.schema.json"

CURTO = {
    "dz23-autonomous-improvement-ultimate": "autonomous",
    "dz23-backend-data-architect": "backend",
    "dz23-codebase-cartographer": "cartographer",
    "dz23-devops-cloud-deployer": "devops",
    "dz23-e2e-browser-verifier": "e2e",
    "dz23-performance-scalability-engine": "performance",
    "dz23-reverse-engineer-anything": "reverse-engineer",
    "dz23-spec-to-system-engine": "spec",
    "dz23-ultimate-pro-max": "ultimate-pro-max",
}

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
        if pasta.is_dir():
            for md in pasta.glob("*.md"):
                texto = md.read_text(encoding="utf-8", errors="replace")
                m = re.search(r"\*\*Veredito:\*\*\s*\*{0,2}(PASS|PARTIAL|FAIL|NOT_TESTED|BLOCKED|NOT_RECOVERED)",
                              texto)
                if m:
                    vereditos.append(m.group(1))
        exec_ = len(vereditos)
        total_exec += exec_
        sem = len(casos) - exec_
        faltando += max(0, sem)
        conta = lambda v: sum(1 for x in vereditos if x == v)  # noqa: E731
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


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--schema", action="store_true")
    g.add_argument("--prompts", action="store_true")
    g.add_argument("--report", action="store_true")
    g.add_argument("--audit", action="store_true", help="estado da auditoria externa")
    g.add_argument("--record", nargs=argparse.REMAINDER, help="repassa para scripts/record-eval.py")
    ap.add_argument("--skill", default=None)
    ap.add_argument("--batch", type=int, default=None)
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
    if args.audit:
        return cmd_audit()
    if args.report:
        return cmd_report()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
