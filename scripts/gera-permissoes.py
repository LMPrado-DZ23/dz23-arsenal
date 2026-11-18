#!/usr/bin/env python3
"""gera-permissoes.py -- regenera security/PERMISSIONS.md de security/permissoes.json.

Fonte de verdade é o JSON; o .md é gerado para leitura. Editar à mão volta a quebrar o gate
via --check.

Uso:
    python scripts/gera-permissoes.py            # reescreve security/PERMISSIONS.md
    python scripts/gera-permissoes.py --check    # exit 1 se divergir
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REG = RAIZ / "security" / "permissoes.json"
ALVO = RAIZ / "security" / "PERMISSIONS.md"


def _c(s) -> str:
    if isinstance(s, list):
        s = ", ".join(s)
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def gerar() -> str:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    skills = reg["skills"]
    linhas = [
        "# Permissões das skills — dz23-arsenal",
        "",
        "> **Gerado** por `scripts/gera-permissoes.py` de `security/permissoes.json`. Não edite à "
        "mão — o gate (`permissoes:indice`) reprova divergência.",
        "",
        "Regra 7 do mandato: toda skill que executa comando, altera arquivo, usa navegador, acessa "
        "rede ou controla o computador declara permissões, riscos, entradas, saídas, dry-run, "
        "rollback e necessidade de aprovação. "
        f"**{len(skills)}** skills declaradas; o verificador exige uma por skill existente.",
        "",
        "Permissões possíveis: `" + "` · `".join(reg.get("permissoes_validas", [])) + "`.",
        "",
    ]
    for nome in sorted(skills):
        d = skills[nome]
        linhas.append(f"## {nome}")
        linhas.append("")
        linhas.append(f"- **Permissões:** {_c(d.get('permissoes'))}")
        linhas.append(f"- **Riscos:** {_c(d.get('riscos'))}")
        linhas.append(f"- **Entradas:** {_c(d.get('entradas'))}")
        linhas.append(f"- **Saídas:** {_c(d.get('saidas'))}")
        linhas.append(f"- **Dry-run:** {_c(d.get('dry_run'))}")
        linhas.append(f"- **Rollback:** {_c(d.get('rollback'))}")
        linhas.append(f"- **Aprovação:** {_c(d.get('aprovacao'))}")
        linhas.append("")
    return "\n".join(linhas) + "\n"


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if not REG.is_file():
        print(f"FALHA: {REG} ausente")
        return 1
    gerado = gerar()
    if args.check:
        atual = ALVO.read_text(encoding="utf-8") if ALVO.is_file() else ""
        if atual.replace("\r\n", "\n") != gerado.replace("\r\n", "\n"):
            print("FALHA: security/PERMISSIONS.md diverge de permissoes.json — rode gera-permissoes.py")
            return 1
        print("OK: PERMISSIONS.md em sincronia com permissoes.json")
        return 0
    ALVO.write_text(gerado, encoding="utf-8", newline="\n")
    print("security/PERMISSIONS.md regenerado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
