#!/usr/bin/env python3
"""check-links.py — verifica links relativos .md e caminhos citados nos READMEs do arsenal."""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
PAT = re.compile(r"\]\(([^)#]+?\.md)\)")
IGNORAR = re.compile(r"(/\.git/|/node_modules/)")


def main() -> int:
    quebrados = []
    total = 0
    for md in RAIZ.rglob("*.md"):
        if IGNORAR.search(str(md)):
            continue
        try:
            texto = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in PAT.finditer(texto):
            alvo_rel = m.group(1).strip()
            if alvo_rel.startswith(("http://", "https://", "mailto:")):
                continue
            total += 1
            alvo = (md.parent / alvo_rel).resolve()
            if not alvo.exists():
                quebrados.append((str(md.relative_to(RAIZ)), alvo_rel))

    print(f"links .md relativos verificados: {total}")
    if quebrados:
        print(f"QUEBRADOS: {len(quebrados)}")
        for arq, destino in quebrados:
            print(f"  {arq} -> {destino}")
        return 1
    print("QUEBRADOS: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
