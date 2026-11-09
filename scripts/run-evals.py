#!/usr/bin/env python3
"""run-evals.py — harness de evals do arsenal.

O que ele FAZ (determinístico, sem LLM):
  --list     lista os cenários
  --check    lint + auditoria de coerência de cada eval contra o próprio SKILL.md/references
  --record   grava um veredito vindo de sessão real (LLM/humano) em evals/results/
  --report   mostra o estado de execução consolidado

O que ele NÃO FAZ: executar o comportamento da skill. Isso exige uma sessão de agente real; o
harness apenas (a) prova que o eval é coerente e executável, e (b) guarda o veredito de quem executou.

Exit:
  --check  : 0 = nenhum erro (avisos podem existir) · 1 = erro de coerência
  --report : 0 = todos os cenários têm resultado · 1 = há cenário sem resultado
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "skills"
RESULTADOS = RAIZ / "evals-results"

# palavras que não ajudam a localizar a regra no texto da skill
STOP = set("""a o as os um uma de da do das dos e ou que em no na nos nas para por com sem ao aos
se ser é são estar está como quando onde qual quais seu sua seus suas este esta isso isto
não mais menos muito pouco todo toda todos todas ele ela eles elas você vocês nós
the a an of to in on and or is are be for with without not no do does this that it its
must should shall can could will would may might""".split())


def carregar(skill: Path) -> dict:
    f = skill / "evals" / "evals.json"
    if not f.is_file():
        return {"casos": [], "erro": "evals/evals.json ausente"}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"casos": [], "erro": f"JSON inválido: {exc}"}


def corpus(skill: Path) -> str:
    """Todo o texto da skill (SKILL.md + references + templates)."""
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


def termos(texto: str, minimo: int = 5) -> set[str]:
    achados = re.findall(r"[a-záàâãéêíóôõúç0-9][a-záàâãéêíóôõúç0-9\-]{3,}", texto.lower())
    return {t for t in achados if t not in STOP and len(t) >= minimo}


def auditar(skill: Path) -> dict:
    dados = carregar(skill)
    casos = dados.get("casos") or dados.get("cases") or []
    texto = corpus(skill)
    problemas: list[str] = []
    avisos: list[str] = []
    detalhes: list[dict] = []

    if not casos:
        problemas.append("nenhum caso encontrado")

    ids = [c.get("id") for c in casos]
    if len(ids) != len(set(ids)):
        problemas.append("id duplicado entre casos")

    for c in casos:
        cid = c.get("id", "?")
        for campo in ("id", "input", "expected", "fails_if"):
            if not c.get(campo):
                problemas.append(f"{cid}: campo '{campo}' vazio")
        entrada = str(c.get("input", ""))
        esperado = str(c.get("expected", ""))
        falha = str(c.get("fails_if", ""))

        # contradição: expected e fails_if idênticos ou quase
        if esperado and falha and esperado.strip().lower() == falha.strip().lower():
            problemas.append(f"{cid}: expected == fails_if (eval impossível de distinguir)")
        elif esperado and falha and (esperado.lower() in falha.lower() or falha.lower() in esperado.lower()):
            avisos.append(f"{cid}: expected e fails_if se sobrepõem textualmente")

        # cobertura: a regra citada no expected aparece na skill?
        termos_exp = termos(esperado)
        achados = {t for t in termos_exp if t in texto}
        cobertura = len(achados) / len(termos_exp) if termos_exp else 1.0
        if termos_exp and cobertura < 0.34:
            problemas.append(
                f"{cid}: só {len(achados)}/{len(termos_exp)} termos do expected aparecem na skill "
                f"(regra possivelmente não existe): {sorted(termos_exp - achados)[:6]}"
            )
        elif termos_exp and cobertura < 0.6:
            avisos.append(f"{cid}: cobertura baixa ({len(achados)}/{len(termos_exp)})")

        # eval possivelmente impossível: input nega medição e expected exige entrega de número
        neg = re.search(r"\b(sem|nenhum|nenhuma|não há|nao ha)\b.{0,30}(medi|medição|medicao|número|numero)", entrada.lower())
        exig = re.search(r"\b(entrega|entrega|informa|declare|declara)\b.{0,40}(baseline|p50|p95|p99|número|numero)", esperado.lower())
        if neg and exig:
            avisos.append(f"{cid}: input nega medição e expected pede número — verificar se é resolvível")

        detalhes.append({
            "id": cid,
            "cobertura": round(cobertura, 2),
            "termos_fora": sorted(termos_exp - achados)[:8],
        })

    return {
        "skill": skill.name,
        "casos": len(casos),
        "problemas": problemas,
        "avisos": avisos,
        "detalhes": detalhes,
        "arquivo_erro": dados.get("erro"),
    }


def resultado_execucao(skill: Path) -> dict | None:
    f = RESULTADOS / f"{skill.name}.json"
    if not f.is_file():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def cmd_check() -> int:
    total_casos = total_problemas = total_avisos = 0
    relatorio = []
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        r = auditar(skill)
        total_casos += r["casos"]
        total_problemas += len(r["problemas"])
        total_avisos += len(r["avisos"])
        relatorio.append(r)
        marca = "OK" if not r["problemas"] else "PROBLEMA"
        print(f"{skill.name:<40} {r['casos']:>3} casos  {marca}")
        for p in r["problemas"]:
            print(f"    ERRO  {p}")
        for a in r["avisos"]:
            print(f"    aviso {a}")

    print()
    print(f"casos analisados: {total_casos} | erros: {total_problemas} | avisos: {total_avisos}")
    (RAIZ / "evals-audit.json").write_text(
        json.dumps({"data": date.today().isoformat(), "relatorio": relatorio}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    print("relatório: evals-audit.json")
    return 0 if total_problemas == 0 else 1


def cmd_list(filtro: str | None) -> int:
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        if filtro and filtro not in skill.name:
            continue
        dados = carregar(skill)
        casos = dados.get("casos") or dados.get("cases") or []
        print(f"\n## {skill.name} ({len(casos)} casos)")
        for c in casos:
            print(f"  - {c.get('id')}: {str(c.get('input', ''))[:80]}")
    return 0


def cmd_record(skill_nome: str, arquivo: str) -> int:
    skill = SKILLS / skill_nome
    if not skill.is_dir():
        print(f"INVALID skill inexistente: {skill_nome}", file=sys.stderr)
        return 2
    dados = json.loads(Path(arquivo).read_text(encoding="utf-8"))
    RESULTADOS.mkdir(exist_ok=True)
    alvo = RESULTADOS / f"{skill_nome}.json"
    alvo.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"gravado: {alvo.relative_to(RAIZ)}")
    return 0


def cmd_report() -> int:
    print(f"{'skill':<40}{'casos':>6}{'executados':>11}{'PASS':>6}{'FAIL':>6}{'NOT_TESTED':>12}")
    print("-" * 82)
    faltando = 0
    for skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        dados = carregar(skill)
        casos = dados.get("casos") or dados.get("cases") or []
        res = resultado_execucao(skill) or {}
        resultados = res.get("results", {})
        executados = [v for v in resultados.values() if v in ("PASS", "PARTIAL", "FAIL")]
        passa = sum(1 for v in resultados.values() if v == "PASS")
        falha = sum(1 for v in resultados.values() if v == "FAIL")
        sem = len(casos) - len(executados)
        faltando += sem
        print(f"{skill.name:<40}{len(casos):>6}{len(executados):>11}{passa:>6}{falha:>6}{sem:>12}")
    print()
    print(f"cenários sem resultado: {faltando}")
    return 0 if faltando == 0 else 1


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
    g.add_argument("--report", action="store_true")
    g.add_argument("--record", nargs=2, metavar=("SKILL", "ARQUIVO"))
    ap.add_argument("--filtro", default=None)
    args = ap.parse_args(argv)

    if args.list:
        return cmd_list(args.filtro)
    if args.check:
        return cmd_check()
    if args.report:
        return cmd_report()
    if args.record:
        return cmd_record(*args.record)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
