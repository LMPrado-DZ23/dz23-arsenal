"""check-docs-runnable.py -- todo bloco de comando na documentacao deve ser executavel.

Achei na rodada 25 atuando como mantenedor novo: segui o CONTRIBUTING.md ao pe da letra e criei
uma skill que o gate recusou em sete checks, porque o texto mandava copiar um validador que nao e
copiavel e mostrava um evals.json que o schema rejeita. Nenhuma checagem automatizada viu isso --
nenhuma delas *e* um humano lendo o guia. Este script fecha parte dessa lacuna: extrai blocos de
comando das docs e confere que cada arquivo citado existe, com a ancora certa (caminho escrito em
skills/<x>/... resolve relativo a repo, mas `scripts/y.py` dentro de uma secao de skill resolve
dentro da skill).

Nao executa nada: executar comando de doc teria efeito colateral (cp, rm, git). Verifica apenas
se as referencias de arquivo sao verdadeiras -- que e onde a rodada 25 quebrou.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# Blocos ```bash / ```sh / ```console / ```powershell
RE_BLOCO = re.compile(r"```(?:bash|sh|shell|console|pwsh|powershell)\n(.*?)```", re.S)
# arquivos que os comandos citam
RE_ARQUIVO = re.compile(r"(?<![\w./-])((?:scripts|docs|evals|external|mcp|bundle|skills)/[\w./\-]+\.(?:py|sh|ps1|md|json))")
# placeholder de caminho dentro de comando: <nome>, $VAR
RE_PLACEHOLDER = re.compile(r"<[^>\s]+>|\$\{?\w+")

DOC_ALVOS = ("README.md", "CONTRIBUTING.md", "ROADMAP.md", "CHANGELOG.md",
             "SECURITY.md", "CODE_OF_CONDUCT.md")


def resolver(ref: str, base: pathlib.Path) -> bool:
    """True se o caminho existe (na base da doc ou na raiz)."""
    for cand in ((base / ref), (RAIZ / ref)):
        if cand.exists():
            return True
    # skills/<x>/... ja vem absoluto relativo a raiz; tentar tambem sem prefixo duplicado
    return (RAIZ / ref).exists()


def checar_doc(caminho: pathlib.Path) -> list[dict]:
    problemas: list[dict] = []
    try:
        texto = caminho.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [{"arquivo": str(caminho.relative_to(RAIZ)), "linha": 0,
                 "problema": f"ilegivel: {exc}"}]
    base = caminho.parent
    offset_linha = 0

    for m in RE_BLOCO.finditer(texto):
        bloco = m.group(1)
        linha_ini = offset_linha + texto[:m.start()].count("\n") + 1
        for i, linha in enumerate(bloco.splitlines()):
            if linha.strip().startswith("#"):
                continue          # comentario dentro do bloco nao e comando
            tem_placeholder = bool(RE_PLACEHOLDER.search(linha))
            # Comando com tratamento explicito de ausencia (`|| echo ...`, `2>/dev/null`) nao e
            # alegacao de que o arquivo existe -- e instrucao de contingencia. cli/verify.md usa
            # exatamente isso para dizer "nao ha variante shell; use o one-liner".
            tem_fallback = "||" in linha or "2>/dev/null" in linha
            for am in RE_ARQUIVO.finditer(linha):
                ref = am.group(1)
                if tem_placeholder and not resolver(ref, base):
                    # `skills/<nome>/scripts/x.py` e modelo, nao alegacao sobre um caminho
                    continue
                if tem_fallback and not resolver(ref, base):
                    continue
                if not resolver(ref, base):
                    problemas.append({
                        "arquivo": str(caminho.relative_to(RAIZ)),
                        "linha": linha_ini + i,
                        "referencia": ref,
                        "problema": "arquivo citado em bloco de comando nao existe",
                        "contexto": linha.strip()[:110],
                    })
    return problemas


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    alvos = [RAIZ / n for n in DOC_ALVOS if (RAIZ / n).is_file()]
    alvos += sorted((RAIZ / "docs").glob("*.md")) if (RAIZ / "docs").is_dir() else []
    alvos += sorted((RAIZ / "cli").glob("*.md")) if (RAIZ / "cli").is_dir() else []

    todos: list[dict] = []
    conferidos = 0
    for f in alvos:
        try:
            t = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in RE_BLOCO.finditer(t):
            conferidos += len([l for l in m.group(1).splitlines() if l.strip()])
        todos += checar_doc(f)

    if args.json:
        print(json.dumps({"ok": not todos, "blocos_conferidos": conferidos,
                          "problemas": todos}, ensure_ascii=False, indent=2))
    else:
        print(f"linhas de comando conferidas em {len(alvos)} documentos: {conferidos}")
        if todos:
            for p in todos:
                print(f"DIVERGÊNCIA {p['arquivo']}:{p['linha']}: {p['referencia']} "
                      f"-- {p['problema']}")
                if p.get("contexto"):
                    print(f"    em: {p['contexto']}")
            print(f"\ntotal: {len(todos)} referência(s) de comando quebrada(s)")
        else:
            print("toda referência de arquivo em bloco de comando existe")

    return 1 if todos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
