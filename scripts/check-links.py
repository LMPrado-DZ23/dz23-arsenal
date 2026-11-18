#!/usr/bin/env python3
"""check-links.py — verifica links relativos .md e caminhos citados nos READMEs do arsenal."""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
PAT = re.compile(r"\]\(([^)#]+?\.md)\)")
IGNORAR = re.compile(r"(^|[\\/])\.git([\\/]|$)|(^|[\\/])node_modules([\\/]|$)|"
                     r"(^|[\\/])__pycache__([\\/]|$)")


def _norm(caminho) -> str:
    """Separador canônico para comparação.

    A versão anterior testava `IGNORAR.search(str(md))` com um regex de barras solas. Em Windows
    `str(Path(...))` devolve backslash, nada casava, e o verificador desia dentro de
    node_modules conferindo links de bibliotecas de terceiros -- 76 "links quebrados" que não são
    conteúdo deste repositório. Achei ao instalar as dependências do MCP PentAGI, ou seja: o bug
    só existia numa máquina onde alguém realmente instalou algo. Corrigido normalizando o caminho
    (e cobrindo `__pycache__`, mesma classe de ruído).
    """
    return str(caminho).replace("\\", "/")


def main() -> int:
    quebrados = []
    total = 0
    for md in RAIZ.rglob("*.md"):
        if IGNORAR.search(_norm(md)):
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
    if total == 0:
        # Zero links conferidos não é "nenhum quebrado". Acontece com caminho errado, pasta
        # vazia ou checkout parcial, e o passo do CI sairia verde sem ter lido nada -- o mesmo
        # gate-fantasma que motivou a v1.5.0, aqui alcançado por um `--raiz`/argumento ruim.
        print(f"NENHUM link relativo encontrado em {RAIZ} -- isso não é aprovação",
              file=sys.stderr)
        return 1
    print("QUEBRADOS: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
