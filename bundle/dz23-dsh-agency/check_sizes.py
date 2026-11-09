#!/usr/bin/env python3
"""Verifica que núcleo + cada perfil (e núcleo + overlay do Diretor) cabem no
limite do campo `agent-instructions` do DSH. Só biblioteca padrão.

Sai com código != 0 se algum combinado passar do limite rígido. Avisa, sem
falhar, se passar do teto macio (sinaliza um perfil que está crescendo demais)
ou se houver perfil duplicado/faltando na sequência.

Uso:
    python check_sizes.py                 # usa a pasta do próprio script
    python check_sizes.py --dir . --warn 8192 --hard 65536
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

try:
    # evita mojibake (ex.: "n�cleo") no console do Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Cabeçalho de perfil: "## NN — Nome" ou "### NN — Nome".
HEADER = re.compile(r"^#{2,3}\s+(\d{2})\s+—\s*(.+?)\s*$")
# Fecha o bloco do perfil só em cabeçalho de nível 1–2; assim um ### ou ####
# interno ao perfil não corta a medição.
CLOSE_HEADER = re.compile(r"^#{1,2}\s")

CORE = "DSH_AGENT_SHARED_CORE_UNIVERSAL.txt"
OVERLAY = "DSH_AGENCY_DIRECTOR_OVERLAY.txt"
CATALOGS = [
    "DSH_SPECIALIST_AGENT_CATALOG.md",
    "DSH_SPECIALIST_AGENT_CATALOG_EXPANDED.md",
    "DSH_SPECIALIST_AGENT_CATALOG_VERTICALS.md",
]


def parse_profiles(text: str) -> list[dict]:
    profiles: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        m = HEADER.match(line)
        if m:
            if cur:
                profiles.append(cur)
            cur = {"num": int(m.group(1)), "name": m.group(2), "lines": [line]}
        elif cur is not None:
            if CLOSE_HEADER.match(line):  # só nível 1–2 fecha; ###/#### internos ficam
                profiles.append(cur)
                cur = None
            else:
                cur["lines"].append(line)
    if cur:
        profiles.append(cur)
    return profiles


def nbytes(s: str) -> int:
    return len(s.encode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Verifica tamanho de núcleo + perfil vs limite do DSH.")
    ap.add_argument("--dir", default=str(pathlib.Path(__file__).resolve().parent))
    ap.add_argument("--warn", type=int, default=8192, help="teto macio de aviso (bytes)")
    ap.add_argument("--hard", type=int, default=65536, help="limite rígido do DSH (bytes)")
    args = ap.parse_args()
    d = pathlib.Path(args.dir)

    core = (d / CORE).read_text(encoding="utf-8")
    rows: list[tuple[str, int]] = [("Diretor (núcleo+overlay)",
                                    nbytes(core + "\n\n" + (d / OVERLAY).read_text(encoding="utf-8")))]
    seen: dict[int, int] = {}
    for cat in CATALOGS:
        for p in parse_profiles((d / cat).read_text(encoding="utf-8")):
            body = "\n".join(p["lines"])
            rows.append((f'{p["num"]:02d} {p["name"]}', nbytes(core + "\n\n" + body)))
            seen[p["num"]] = seen.get(p["num"], 0) + 1

    worst = max(rows, key=lambda r: r[1])
    over_hard = [r for r in rows if r[1] > args.hard]
    over_warn = [r for r in rows if args.warn < r[1] <= args.hard]

    print(f"núcleo: {nbytes(core)} bytes | teto macio: {args.warn} | limite rígido: {args.hard}")
    print(f"combinados medidos: {len(rows)} | perfis: {len(seen)} | maior: {worst[0]} = {worst[1]} bytes")

    # a sequência esperada vai de 1 até o maior perfil encontrado (sem hardcode)
    top = max(seen) if seen else 0
    dups = sorted(n for n, c in seen.items() if c > 1)
    missing = [n for n in range(1, top + 1) if n not in seen]
    if dups:
        print(f"AVISO: perfis duplicados: {dups}")
    if missing:
        print(f"AVISO: perfis faltando (1-{top}): {missing}")
    for label, b in over_warn:
        print(f"  aviso (acima do teto macio): {label} = {b} bytes")
    for label, b in over_hard:
        print(f"  FALHA (acima do limite rígido): {label} = {b} bytes")

    if over_hard:
        print("RESULTADO: FALHA")
        return 1
    print("RESULTADO: OK — todos os combinados cabem no limite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
