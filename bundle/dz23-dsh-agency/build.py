#!/usr/bin/env python3
"""Gera `agents/` com os 88 prompts prontos para colar no campo
`agent-instructions` do DSH: núcleo universal + overlays/perfis.

Só biblioteca padrão. Sai com código 1 se qualquer arquivo passar do limite
rígido do DSH, e nesse caso NÃO cria/sobrescreve `agents/`.

Uso:
    python build.py                 # gera agents/ (88 arquivos)
    python build.py --check         # só valida, não escreve
    python build.py --list          # lista nomes + bytes estimados
    python build.py --stdout 04     # imprime o agente 04 na stdout
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HARD = 65536
BASE = pathlib.Path(__file__).resolve().parent
CORE = BASE / "DSH_AGENT_SHARED_CORE_UNIVERSAL.txt"
OVERLAY = BASE / "DSH_AGENCY_DIRECTOR_OVERLAY.txt"
CATALOGS = [
    BASE / "DSH_SPECIALIST_AGENT_CATALOG.md",
    BASE / "DSH_SPECIALIST_AGENT_CATALOG_EXPANDED.md",
    BASE / "DSH_SPECIALIST_AGENT_CATALOG_VERTICALS.md",
]
HEADER = re.compile(r"^#{2,3}\s+(\d{2})\s+—\s*(.+?)\s*$")
CLOSE = re.compile(r"^#{1,2}\s")
OUT = pathlib.Path("agents")


def parse_profiles(text: str) -> list[dict]:
    """Mesma lógica de check_sizes.py: perfil começa em '## NN — Nome' e
    termina no próximo cabeçalho de nível 1–2."""
    profiles: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        m = HEADER.match(line)
        if m:
            if cur:
                profiles.append(cur)
            cur = {"num": int(m.group(1)), "name": m.group(2), "lines": [line]}
        elif cur is not None:
            if CLOSE.match(line):
                profiles.append(cur)
                cur = None
            else:
                cur["lines"].append(line)
    if cur:
        profiles.append(cur)
    return profiles


def kebab(name: str) -> str:
    ascii_name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def nbytes(s: str) -> int:
    return len(s.encode("utf-8"))


def load() -> tuple[str, str, list[dict]]:
    core = CORE.read_text(encoding="utf-8")
    overlay = OVERLAY.read_text(encoding="utf-8")
    profiles: list[dict] = []
    for cat in CATALOGS:
        profiles.extend(parse_profiles(cat.read_text(encoding="utf-8")))
    profiles.sort(key=lambda p: p["num"])
    return core, overlay, profiles


def entries(core: str, overlay: str, profiles: list[dict]) -> list[dict]:
    items = [{
        "num": 0,
        "name": "Diretor",
        "filename": "00-diretor.txt",
        "content": core + "\n\n" + overlay,
    }]
    for p in profiles:
        body = "\n".join(p["lines"])
        items.append({
            "num": p["num"],
            "name": p["name"],
            "filename": f'{p["num"]:02d}-{kebab(p["name"])}.txt',
            "content": core + "\n\n" + body,
        })
    for it in items:
        it["bytes"] = nbytes(it["content"])
    return items


def print_table(items: list[dict]) -> int:
    bad = 0
    print(f"{'agente':<52}{'bytes':>8}  status")
    print("-" * 68)
    for it in items:
        ok = it["bytes"] <= HARD
        if not ok:
            bad += 1
        label = f'{it["num"]:02d} {it["name"]}'
        print(f'{label[:50]:<52}{it["bytes"]:>8}  {"ok" if ok else "FALHA"}')
    print("-" * 68)
    print(f"total: {len(items)} agentes | limite: {HARD} bytes | falhas: {bad}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description="Gera agents/ com núcleo + perfil para o DSH.")
    ap.add_argument("--check", action="store_true", help="só valida (não escreve)")
    ap.add_argument("--list", action="store_true", help="lista nomes e bytes estimados")
    ap.add_argument("--stdout", type=int, metavar="NN", help="imprime o agente NN na stdout")
    args = ap.parse_args()

    core, overlay, profiles = load()
    items = entries(core, overlay, profiles)

    if args.stdout is not None:
        target = next((it for it in items if it["num"] == args.stdout), None)
        if target is None:
            print(f"agente {args.stdout:02d} não encontrado", file=sys.stderr)
            return 1
        sys.stdout.write(target["content"])
        return 0

    if args.list:
        for it in items:
            print(f'{it["filename"]:<56}{it["bytes"]:>8}')
        print(f"total: {len(items)}")
        return 0 if all(it["bytes"] <= HARD for it in items) else 1

    bad = print_table(items)
    if bad:
        print("RESULTADO: FALHA — nenhum arquivo foi escrito.")
        return 1
    if args.check:
        # A versão anterior deste ramo só imprimia OK depois de checar limites de bytes --
        # chamava-se "--check" sem comparar nada com `agents/`. Os 88 arquivos versionados
        # podiam (e podem) divergir das fontes em silêncio. Agora a comparação é o check.
        destino = pathlib.Path.cwd() / OUT
        if not destino.is_dir():
            print(f"RESULTADO: FALHA — {destino} não existe; rode `python build.py`.")
            return 1
        ausentes, diferentes = [], []
        for it in items:
            alvo = destino / it["filename"]
            if not alvo.is_file():
                ausentes.append(it["filename"])
                continue
            # comparar normalizando EOL: um CRLF residual herdado de antes da correção de
            # newline="\n" não deve ser tratado como conteúdo diferente, mas qualquer outra
            # diferença é.
            gravado = alvo.read_bytes().replace(b"\r\n", b"\n")
            esperado = it["content"].encode("utf-8").replace(b"\r\n", b"\n")
            if gravado != esperado:
                diferentes.append(it["filename"])
        extras = sorted(p.name for p in destino.glob("*.txt")
                        if p.name not in {it["filename"] for it in items})
        if ausentes or diferentes or extras:
            for n in ausentes:
                print(f"FALTA agents/{n} — gere com `python build.py`")
            for n in diferentes:
                print(f"DIVERGE agents/{n} — conteúdo difere do gerado pelas fontes")
            for n in extras:
                print(f"SOBRA agents/{n} — não é produzido por nenhuma fonte")
            total = len(ausentes) + len(diferentes) + len(extras)
            print(f"RESULTADO: FALHA — {total} arquivo(s) de agents/ fora de sincronia.")
            return 1
        crlf = [it["filename"] for it in items
                if b"\r\n" in (destino / it["filename"]).read_bytes()]
        if crlf:
            print(f"AVISO: {len(crlf)} arquivo(s) com CRLF no disco; renomeie gerando de novo.")
        print(f"RESULTADO: OK — agents/ bate com as fontes ({len(items)} arquivos).")
        return 0

    cwd_out = pathlib.Path.cwd() / OUT
    tmp = pathlib.Path.cwd() / (OUT.name + ".tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    for it in items:
        # newline="\n" não é cosmético: em Windows o modo texto converte "\n" em "\r\n" na
        # escrita, e rodar este gerador deixava os 88 arquivos versionados como "modificados"
        # no git status -- reproduzido nesta sessão. O conteúdo era idêntico ignorando EOL, mas
        # ninguém distingue isso de edição real, e contra o `*.txt text eol=lf` do
        # .gitattributes o resultado é um diff falso de 88 arquivos toda vez que alguém gera.
        (tmp / it["filename"]).write_text(it["content"], encoding="utf-8", newline="\n")
    if cwd_out.exists():
        shutil.rmtree(cwd_out)
    tmp.rename(cwd_out)
    print(f"RESULTADO: OK — {len(items)} arquivos escritos em {cwd_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
