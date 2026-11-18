"""gera-indice-skills.py -- regenera a tabela comparativa de skills/README.md a partir do disco.

Nao e script de formatacao: existe porque o indice era mantido a mao e apodreceu inteiro. Medido
nesta sessao, as 9 linhas da tabela divergiam do disco (versoes atrasadas em ate 4 patches, contagem
de scripts errada em todas, evals de ultimate-pro-max dizendo 0 quando sao 13) e uma decima skill
nao tinha linha nenhuma. Quem le esse indice para decidir qual skill usar recebe retrato de um
repositorio que nao existe mais.

A regra que evita reincidencia esta em check-numbers.py: a contagem e as colunas numericas passam a
ser conferidas contra o filesystem a cada gate. Editar a tabela a mao volta a ser visivel.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ALVO = RAIZ / "skills" / "README.md"

# Categoria e complexidade sao julgamento humano, nao fato de disco: preservam-se da tabela
# atual e ficam explicitamente marcadas onde a skill nova nao tem entrada.
CATEGORIAS = {
    "dz23-autonomous-improvement-ultimate": ("Orquestração", "advanced"),
    "dz23-backend-data-architect": ("Backend/DB", "advanced"),
    "dz23-codebase-cartographer": ("Exploração", "intermediate"),
    "dz23-devops-cloud-deployer": ("DevOps", "advanced"),
    "dz23-e2e-browser-verifier": ("QA/E2E", "advanced"),
    "dz23-performance-scalability-engine": ("Performance", "advanced"),
    "dz23-postgres-prod-preflight": ("Banco/Segurança", "intermediate"),
    "dz23-reverse-engineer-anything": ("Eng. reversa", "advanced"),
    "dz23-spec-to-system-engine": ("Especificação", "advanced"),
    "dz23-ultimate-pro-max": ("UI/UX", "advanced"),
}


def mede(sk: pathlib.Path) -> dict:
    refs = len(list((sk / "references").glob("*.md"))) if (sk / "references").is_dir() else 0
    tpl = len(list((sk / "templates").glob("*.md"))) if (sk / "templates").is_dir() else 0
    scr = len([p for p in (sk / "scripts").iterdir() if p.is_file()]) \
        if (sk / "scripts").is_dir() else 0
    ev = sk / "evals" / "evals.json"
    casos = 0
    if ev.is_file():
        try:
            dados = json.loads(ev.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            dados = {}
        cases = dados.get("cases", [])
        casos = len([c for c in cases if isinstance(c, dict)]) if isinstance(cases, list) else 0
    versao = (sk / "VERSION").read_text(encoding="utf-8").strip() if (sk / "VERSION").is_file() else "?"
    return {"refs": refs, "tpl": tpl, "scr": scr, "casos": casos, "versao": versao}


def construir() -> str:
    skills = sorted(p for p in (RAIZ / "skills").iterdir() if p.is_dir())
    total = len(skills)
    linhas = []
    for sk in skills:
        m = mede(sk)
        cat, cx = CATEGORIAS.get(sk.name, ("—", "—"))
        curto = sk.name.replace("dz23-", "")
        linhas.append(
            f"| [{curto}]({sk.name}/) | {m['versao']} | {cat} | {cx} | "
            f"{m['refs']} | {m['tpl']} | {m['scr']} | {m['casos']} |")

    soma_refs = sum(mede(s)["refs"] for s in skills)
    soma_ev = sum(mede(s)["casos"] for s in skills)
    topo = ALVO.read_text(encoding="utf-8").splitlines()[0] if ALVO.is_file() \
        else "# Skills DZ23 — índice"
    return f"""{topo}

{total} skills de engenharia, cada uma com uma responsabilidade clara. Todas seguem o mesmo padrão:
`SKILL.md` com as regras, `references/` para conhecimento sob demanda, `templates/` para artefatos,
`scripts/` quando há código executável e `evals/` com cenários de avaliação.

## Tabela comparativa

| Skill | Versão | Categoria | Complexidade | Refs | Templates | Scripts | Evals |
|---|---|---|---|---|---|---|---|
{chr(10).join(linhas)}

Totais do disco: **{soma_refs} referências** e **{soma_ev} cenários de eval** declarados.

> Esta tabela é gerada -- `python scripts/gera-indice-skills.py` -- e conferida pelo
> `check-numbers.py` a cada gate. Versões, contagens de refs/templates/scripts/evals vêm do
> filesystem. Categoria e complexidade são julgamento humano e ficam em
> `scripts/gera-indice-skills.py`; editar a tabela aqui não dura um commit.
"""


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="só diz se está desatualizado")
    args = ap.parse_args(argv)

    novo = construir()
    atual = ALVO.read_text(encoding="utf-8") if ALVO.is_file() else ""
    if args.check:
        if atual.strip() != novo.strip():
            print("DESATUALIZADO: skills/README.md não bate com o disco\n"
                  "Rode: python scripts/gera-indice-skills.py")
            return 1
        print("índice de skills em dia com o disco")
        return 0
    ALVO.write_text(novo, encoding="utf-8", newline="\n")
    print(f"skills/README.md regenerado ({len(novo.splitlines())} linhas)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
