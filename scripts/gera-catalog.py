#!/usr/bin/env python3
"""gera-catalog.py -- gera docs de catálogo/proveniência/licença de catalog/catalog.json.

Fonte única de verdade: catalog/catalog.json. Deste arquivo saem, sem edição à mão:
  - catalog/CATALOG.md    (índice legível)
  - THIRD-PARTY.md        (proveniência de terceiros; mandato: entregável)
  - LICENSE-MATRIX.md     (compatibilidade de licença com o MIT do repo; mandato: entregável)

Índice mantido à mão apodrece (foi o que aconteceu com skills/README.md). O gate (`catalogo:indice`)
reprova divergência via --check.

Uso:
    python scripts/gera-catalog.py            # reescreve os três
    python scripts/gera-catalog.py --check    # exit 1 se algum divergir
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CAT = RAIZ / "catalog" / "catalog.json"
CATALOG_MD = RAIZ / "catalog" / "CATALOG.md"
THIRD_PARTY_MD = RAIZ / "THIRD-PARTY.md"
LICENSE_MATRIX_MD = RAIZ / "LICENSE-MATRIX.md"


def _celula(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def _compat_mit(licenca: str, verificada: bool) -> str:
    """Compatibilidade da licença da fonte com o MIT do repo (determinístico, sem opinião)."""
    low = (licenca or "").lower()
    if "ausente" in low:
        return "não — sem LICENSE (REJEITAR p/ cópia)"
    if "a-verificar" in low or "a verificar" in low or "declarada em" in low:
        return "a verificar"
    if "openroots" in low or "ora-" in low:
        # ORA (OpenRoots Agent License): source-available com piso de receita, royalty acima do
        # limite e vedação de treino de IA. Fica fora da matriz permissiva: só entra por ponteiro.
        return "não — source-available com royalty (só REFERENCIA)"
    if "gpl" in low:
        return "copyleft — isolar (não redistribuir junto)"
    if any(k in low for k in ("mit", "apache", "isc", "bsd", "cc0")):
        return "sim (permissiva)"
    return "a verificar"


def _catalog_md(fontes: list[dict]) -> str:
    verificadas = [f for f in fontes if f.get("licenca_verificada")]
    L = ["# Catálogo de fontes externas — dz23-arsenal", "",
         "> **Gerado** por `scripts/gera-catalog.py` a partir de `catalog/catalog.json`. "
         "Não edite à mão — o gate (`catalogo:indice`) reprova divergência.", "",
         f"{len(fontes)} fontes · {len(verificadas)} com licença **verificada** "
         f"(LICENSE lido, sha256 registrado) · as demais **a-verificar** "
         f"(catalogadas por URL, nada copiado).", "",
         "Decisões: INCORPORAR · ADAPTAR · INTEGRAR_POR_ADAPTADOR · CATALOGAR · REFERENCIA · REJEITAR.", "",
         "| Fonte | Licença | Verif. | Decisão | Função | Dependências | Risco | Fallback local |",
         "|---|---|:--:|---|---|---|---|---|"]
    for f in fontes:
        verif = "✅" if f.get("licenca_verificada") else "—"
        nome = f"[{_celula(f['nome'])}]({_celula(f['url'])})"
        L.append("| " + " | ".join([
            nome, _celula(f["licenca"]), verif, _celula(f["decisao"]), _celula(f["funcao"]),
            _celula(f["dependencias"]), _celula(f["risco"]), _celula(f["fallback_local"])]) + " |")
    L += ["", "## Notas", "",
          "- **Verif. ✅** = o arquivo `LICENSE` foi lido no ZIP em disco e o sha256 está "
          "registrado no JSON. **—** = fonte apenas catalogada por URL; a licença fica "
          "`a-verificar` até ser lida. Nada de terceiros é redistribuído aqui.",
          "- Fontes com documento próprio em `external/` trazem o cuidado detalhado "
          "(gap que preenchem, riscos, instalação).",
          "- **OpenBot** e agentes com acesso ao computador: nunca habilitar "
          "`danger-full-access` automático; exigir consentimento explícito; não baixar "
          "nem executar binário sem checksum; sem `curl | bash`.", ""]
    return "\n".join(L) + "\n"


def _third_party_md(fontes: list[dict]) -> str:
    L = ["# Terceiros (proveniência) — dz23-arsenal", "",
         "> **Gerado** por `scripts/gera-catalog.py` de `catalog/catalog.json`. O gate reprova "
         "divergência. **Nada de terceiros é redistribuído neste repositório** sem licença lida e "
         "proveniência registrada; as fontes `a-verificar` são apenas apontadas por URL.", "",
         "| Fonte | URL | Licença | Verificada | Decisão | Doc |", "|---|---|---|:--:|---|---|"]
    for f in sorted(fontes, key=lambda x: (not x.get("licenca_verificada"), x["nome"].lower())):
        verif = "sim" if f.get("licenca_verificada") else "não (a-verificar)"
        doc = f.get("doc") or "—"
        L.append("| " + " | ".join([
            _celula(f["nome"]), _celula(f["url"]), _celula(f["licenca"]), verif,
            _celula(f["decisao"]), _celula(doc)]) + " |")
    L += ["", "Regra de incorporação (mandato, regra 3): identificar licença, registrar repositório "
          "e commit, verificar compatibilidade jurídica, documentar modificações, registrar "
          "dependências e revisar segurança antes de copiar qualquer coisa de terceiro.", ""]
    return "\n".join(L) + "\n"


def _license_matrix_md(fontes: list[dict]) -> str:
    L = ["# Matriz de licenças — dz23-arsenal (repo MIT)", "",
         "> **Gerado** por `scripts/gera-catalog.py` de `catalog/catalog.json`. O gate reprova "
         "divergência. Compatibilidade avaliada contra a licença **MIT** deste repositório.", "",
         "| Fonte | Licença | Verificada | Compatível com MIT? | Decisão |", "|---|---|:--:|---|---|"]
    for f in sorted(fontes, key=lambda x: x["nome"].lower()):
        verif = "✅" if f.get("licenca_verificada") else "—"
        L.append("| " + " | ".join([
            _celula(f["nome"]), _celula(f["licenca"]), verif,
            _celula(_compat_mit(f["licenca"], f.get("licenca_verificada", False))),
            _celula(f["decisao"])]) + " |")
    L += ["", "- **sim (permissiva):** MIT/Apache-2.0/ISC/BSD/CC0 — compatível com redistribuição MIT.",
          "- **copyleft — isolar:** GPL/variantes; usar por dependência/ferramenta externa, não "
          "redistribuir junto do código MIT.",
          "- **a verificar:** licença não lida ainda (fonte só catalogada por URL).",
          "- **não — sem LICENSE:** arquivo de licença ausente no artefato → REJEITAR para cópia.", ""]
    return "\n".join(L) + "\n"


def gerar_todos() -> dict[Path, str]:
    fontes = json.loads(CAT.read_text(encoding="utf-8"))["fontes"]
    return {
        CATALOG_MD: _catalog_md(fontes),
        THIRD_PARTY_MD: _third_party_md(fontes),
        LICENSE_MATRIX_MD: _license_matrix_md(fontes),
    }


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
    alvos = gerar_todos()
    if args.check:
        divergentes = []
        for p, novo in alvos.items():
            atual = p.read_text(encoding="utf-8") if p.is_file() else ""
            if atual.replace("\r\n", "\n") != novo.replace("\r\n", "\n"):
                divergentes.append(p.name)
        if divergentes:
            print(f"FALHA: {', '.join(divergentes)} diverge(m) de catalog.json — rode gera-catalog.py")
            return 1
        print("OK: CATALOG.md, THIRD-PARTY.md e LICENSE-MATRIX.md em sincronia com catalog.json")
        return 0
    for p, novo in alvos.items():
        p.write_text(novo, encoding="utf-8", newline="\n")
    print(f"Regenerados: {', '.join(p.name for p in alvos)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
