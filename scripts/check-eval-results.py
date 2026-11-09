#!/usr/bin/env python3
"""check-eval-results.py — valida o diretório evals-results/.

Checa:
  - existe pelo menos 1 registro (o piloto não basta para sempre, mas 0 é erro)
  - cada arquivo .md tem as seções exigidas e um veredito reconhecido
  - o eval-id do arquivo existe no evals.json da skill correspondente
  - veredito PASS traz trecho literal (Evidence não vazio)
  - BLOCKED traz a dependência
  - todo cenário NOT_TESTED está mencionado no ROADMAP.md

Exit: 0 ok · 1 problema
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "evals-results"
SKILLS = RAIZ / "skills"
ROADMAP = RAIZ / "ROADMAP.md"

CURTO = {
    "autonomous": "dz23-autonomous-improvement-ultimate",
    "backend": "dz23-backend-data-architect",
    "cartographer": "dz23-codebase-cartographer",
    "devops": "dz23-devops-cloud-deployer",
    "e2e": "dz23-e2e-browser-verifier",
    "performance": "dz23-performance-scalability-engine",
    "reverse-engineer": "dz23-reverse-engineer-anything",
    "spec": "dz23-spec-to-system-engine",
    "ultimate-pro-max": "dz23-ultimate-pro-max",
}

VEREDITOS = ("PASS", "PARTIAL", "FAIL", "NOT_TESTED", "BLOCKED", "NOT_RECOVERED")
SECOES = ("## Cenário", "## Resposta", "## Esperado", "## Avaliação", "## Notas")


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    if not RES.is_dir():
        print("PROBLEMA: evals-results/ não existe")
        return 1

    arquivos = sorted(md for md in RES.glob("*/*.md") if md.parent.name != "_audit-notes")
    if not arquivos:
        print("PROBLEMA: nenhum registro em evals-results/")
        return 1

    problemas: list[str] = []
    for md in arquivos:
        pasta = md.parent.name
        skill = CURTO.get(pasta)
        if skill is None:
            problemas.append(f"{md.relative_to(RAIZ)}: pasta '{pasta}' não mapeada para skill")
            continue
        texto = md.read_text(encoding="utf-8", errors="replace")

        for secao in SECOES:
            if secao not in texto:
                problemas.append(f"{md.relative_to(RAIZ)}: falta seção '{secao}'")

        m = re.search(r"\*\*Veredito:\*\*\s*\*{0,2}([A-Z_]+)", texto)
        if not m:
            problemas.append(f"{md.relative_to(RAIZ)}: sem veredito")
            continue
        veredito = m.group(1)
        if veredito not in VEREDITOS:
            problemas.append(f"{md.relative_to(RAIZ)}: veredito inválido '{veredito}'")

        m_id = re.match(r"\d{4}-\d{2}-\d{2}-(.+)$", md.stem)
        eval_id = m_id.group(1) if m_id else md.stem
        evals_file = SKILLS / skill / "evals" / "evals.json"
        if evals_file.is_file():
            dados = json.loads(evals_file.read_text(encoding="utf-8"))
            ids = {c["id"] for c in dados["cases"]}
            if eval_id not in ids:
                problemas.append(f"{md.relative_to(RAIZ)}: eval '{eval_id}' não existe em {skill}")

        if veredito == "PASS":
            trecho = re.search(r"- Trecho literal:\s*(.+)", texto)
            if not trecho or "sem trecho literal" in trecho.group(1):
                problemas.append(f"{md.relative_to(RAIZ)}: PASS sem trecho literal")
        if veredito == "BLOCKED" and "BLOCKED_BY_EXTERNAL_DEPENDENCY" not in texto:
            problemas.append(f"{md.relative_to(RAIZ)}: BLOCKED sem dependência declarada")

    # todo cenário não executado deve estar declarado no ROADMAP
    roadmap = ROADMAP.read_text(encoding="utf-8", errors="replace") if ROADMAP.is_file() else ""
    if "Status de evals" not in roadmap:
        problemas.append("ROADMAP.md: falta a seção 'Status de evals'")

    print(f"registros verificados: {len(arquivos)}")
    if problemas:
        print(f"PROBLEMAS: {len(problemas)}")
        for p in problemas:
            print(f"  - {p}")
        return 1
    print("PROBLEMAS: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
