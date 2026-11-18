#!/usr/bin/env python3
"""gera-catalog.py -- regenera catalog/CATALOG.md a partir de catalog/catalog.json.

Índice mantido à mão apodrece (foi o que aconteceu com skills/README.md). O catálogo de fontes
externas é gerado do JSON, que é a fonte de verdade; editar o .md à mão volta a quebrar o gate
via --check.

Uso:
    python scripts/gera-catalog.py            # reescreve catalog/CATALOG.md
    python scripts/gera-catalog.py --check    # exit 1 se o .md no disco divergir do gerado
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CAT = RAIZ / "catalog" / "catalog.json"
ALVO = RAIZ / "catalog" / "CATALOG.md"


def _celula(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def gerar() -> str:
    dados = json.loads(CAT.read_text(encoding="utf-8"))
    fontes = dados["fontes"]
    verificadas = [f for f in fontes if f.get("licenca_verificada")]
    linhas: list[str] = []
    linhas.append("# Catálogo de fontes externas — dz23-arsenal")
    linhas.append("")
    linhas.append("> **Gerado** por `scripts/gera-catalog.py` a partir de `catalog/catalog.json`. "
                  "Não edite à mão — o gate (`catalogo:indice`) reprova divergência.")
    linhas.append("")
    linhas.append(f"{len(fontes)} fontes · {len(verificadas)} com licença **verificada** "
                  f"(LICENSE lido, sha256 registrado) · as demais **a-verificar** "
                  f"(catalogadas por URL, nada copiado).")
    linhas.append("")
    linhas.append("Decisões: INCORPORAR · ADAPTAR · INTEGRAR_POR_ADAPTADOR · CATALOGAR · "
                  "REFERENCIA · REJEITAR.")
    linhas.append("")
    linhas.append("| Fonte | Licença | Verif. | Decisão | Função | Dependências | Risco | Fallback local |")
    linhas.append("|---|---|:--:|---|---|---|---|---|")
    for f in fontes:
        verif = "✅" if f.get("licenca_verificada") else "—"
        nome = f"[{_celula(f['nome'])}]({_celula(f['url'])})"
        linhas.append("| " + " | ".join([
            nome, _celula(f["licenca"]), verif, _celula(f["decisao"]), _celula(f["funcao"]),
            _celula(f["dependencias"]), _celula(f["risco"]), _celula(f["fallback_local"]),
        ]) + " |")
    linhas.append("")
    linhas.append("## Notas")
    linhas.append("")
    linhas.append("- **Verif. ✅** = o arquivo `LICENSE` foi lido no ZIP em disco e o sha256 está "
                  "registrado no JSON. **—** = fonte apenas catalogada por URL; a licença fica "
                  "`a-verificar` até ser lida. Nada de terceiros é redistribuído aqui.")
    linhas.append("- Fontes com documento próprio em `external/` trazem o cuidado detalhado "
                  "(gap que preenchem, riscos, instalação).")
    linhas.append("- **OpenBot** e agentes com acesso ao computador: nunca habilitar "
                  "`danger-full-access` automático; exigir consentimento explícito; não baixar "
                  "nem executar binário sem checksum; sem `curl | bash`.")
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

    if not CAT.is_file():
        print(f"FALHA: {CAT} ausente")
        return 1
    gerado = gerar()
    if args.check:
        atual = ALVO.read_text(encoding="utf-8") if ALVO.is_file() else ""
        if atual.replace("\r\n", "\n") != gerado.replace("\r\n", "\n"):
            print("FALHA: catalog/CATALOG.md diverge de catalog.json — rode gera-catalog.py")
            return 1
        print("OK: CATALOG.md em sincronia com catalog.json")
        return 0
    ALVO.write_text(gerado, encoding="utf-8", newline="\n")
    print(f"catalog/CATALOG.md regenerado ({len(json.loads(CAT.read_text(encoding='utf-8'))['fontes'])} fontes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
