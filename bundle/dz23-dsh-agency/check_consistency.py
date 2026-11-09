#!/usr/bin/env python3
"""Audita a consistência interna da biblioteca DSH — complemento determinístico
ao check_sizes.py. Em vez de auditar entregáveis (papel do 81), audita os
próprios arquivos da agência.

Verifica:
  C1  numeração dos perfis contígua e sem duplicata (1..N)
  C2  a contagem declarada nos documentos bate com o maior perfil
  C3  toda referência 'NN Nome' a um perfil existe (parênteses viram aviso)
  C4  todo link markdown aponta para um arquivo existente
  C5  nenhum link para o núcleo técnico descontinuado
  C6  núcleo + overlay e núcleo + cada perfil cabem no limite rígido
  C7  o preset autônomo do engenheiro cabe no limite rígido

Sai com código != 0 se qualquer verificação falhar. Avisos não derrubam o
código de saída, exceto com `--strict` (aviso vira falha). Só biblioteca padrão.

Uso:
    python check_consistency.py            # avisos não falham
    python check_consistency.py --strict   # aviso vira falha
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

D = pathlib.Path(__file__).resolve().parent
HARD = 65536

CORE = "DSH_AGENT_SHARED_CORE_UNIVERSAL.txt"
OVERLAY = "DSH_AGENCY_DIRECTOR_OVERLAY.txt"
CANON = "DSH_COMPLETE_SPECIALIST_AGENCY.md"
PRESET = "preset-engenheiro-de-sistemas.md"
CATALOGS = [
    "DSH_SPECIALIST_AGENT_CATALOG.md",
    "DSH_SPECIALIST_AGENT_CATALOG_EXPANDED.md",
    "DSH_SPECIALIST_AGENT_CATALOG_VERTICALS.md",
]

HEADER = re.compile(r"^#{2,3}\s+(\d{2})\s+—\s*(.+?)\s*$", re.M)
CLOSE_HEADER = re.compile(r"^#{1,2}\s")  # fecha bloco de perfil só em nível 1–2; ### e #### internos ficam
REF_NAMED = re.compile(r"\b(\d{2})\s+(?=[A-ZÀ-Ý])[A-Za-zÀ-ÿ]")  # "04 Backend" — sinal forte de referência
REF_PARENS = re.compile(r"\((\d{2}(?:[/,]\d{2})*)\)")     # "(05/08/10)" — sinal fraco
LINK = re.compile(r"\]\(([^)]+\.(?:md|txt|py))\)")

_ap = argparse.ArgumentParser(description="Audita a consistência interna da biblioteca DSH.")
_ap.add_argument("--strict", action="store_true", help="trata aviso como falha")
STRICT: bool = _ap.parse_args().strict

fails: list[str] = []
warns: list[str] = []


def read(name: str) -> str:
    return (D / name).read_text(encoding="utf-8")


def nbytes(s: str) -> int:
    return len(s.encode("utf-8"))


def check(ok: bool, label: str, detail: str = "") -> None:
    print(f"{'PASS ' if ok else 'FALHA'} {label}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(label)


def warn(msg: str) -> None:
    print(f"AVISO {msg}")
    warns.append(msg)
    if STRICT:
        fails.append(f"AVISO (strict) {msg}")


def profile_blocks(text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    cur: list[str] | None = None
    for line in text.splitlines():
        if HEADER.match(line):
            if cur:
                blocks.append(cur)
            cur = [line]
        elif cur is not None:
            if CLOSE_HEADER.match(line):
                blocks.append(cur)
                cur = None
            else:
                cur.append(line)
    if cur:
        blocks.append(cur)
    return blocks


# --- coleta de perfis ---
nums: dict[int, int] = {}
for cat in CATALOGS:
    for m in HEADER.finditer(read(cat)):
        n = int(m.group(1))
        nums[n] = nums.get(n, 0) + 1
top = max(nums) if nums else 0

# C1 — numeração
dups = sorted(n for n, c in nums.items() if c > 1)
missing = [n for n in range(1, top + 1) if n not in nums]
check(not dups and not missing, f"C1 numeração 1..{top} contígua e única",
      f"duplicados={dups} faltando={missing}")

# C2 — contagem declarada. Convenção autoritativa: "**N papéis**" no canônico
#      (também aceita "reúne N agentes" e "chega a **N agentes**" no expandido).
canon = read(CANON)
declared = {int(x) for x in re.findall(r"\*\*(\d+) pap[ée]is\*\*", canon)}
declared |= {int(x) for x in re.findall(r"reúne (\d+) agentes", canon)}
declared |= {int(x) for x in re.findall(r"chega a \*\*(\d+) agentes\*\*", read(CATALOGS[1]))}
if not declared:
    check(False, "C2 declaração de contagem encontrada",
          "nenhum padrão casou — esperado '**N papéis**', 'reúne N agentes' ou 'chega a **N agentes**'")
else:
    check(declared == {top}, f"C2 contagem declarada == maior perfil ({top})",
          f"declaradas={sorted(declared)}")

# C3 — referências cruzadas: 'NN Nome' é sinal forte (falha); '(NN)' é fraco (aviso)
named_refs: set[int] = set()
paren_refs: set[int] = set()
for name in CATALOGS + [CANON, OVERLAY, "DSH_QUICKSTART.md", "DSH_INTEGRATIONS.md"]:
    t = read(name)
    named_refs |= {int(m.group(1)) for m in REF_NAMED.finditer(t)}
    for m in REF_PARENS.finditer(t):
        paren_refs |= {int(x) for x in re.split(r"[/,]", m.group(1))}
bad_named = sorted(r for r in named_refs if r not in nums)
check(not bad_named, "C3 referências 'NN Nome' existem", f"inexistentes={bad_named}")
suspect = sorted(r for r in paren_refs if r not in nums)
if suspect:
    warn(f"C3 números entre parênteses fora da faixa de perfis (confira se são referência): {suspect}")

# C4 — links markdown
C4_FILES = CATALOGS + [CANON, OVERLAY, PRESET, "DSH_QUICKSTART.md", "DSH_DECISION_LOG_TEMPLATE.md",
                       "README.md", "DSH_INTEGRATIONS.md"]
broken: list[str] = []
for name in C4_FILES:
    for m in LINK.finditer(read(name)):
        if not (D / m.group(1)).exists():
            broken.append(f"{name} -> {m.group(1)}")
check(not broken, "C4 links markdown resolvem", f"quebrados={broken}")

# C5 — sem link para o núcleo descontinuado
corelink = [name for name in CATALOGS + [CANON] if "](DSH_AGENT_SHARED_CORE.txt)" in read(name)]
check(not corelink, "C5 sem link para o núcleo descontinuado", f"em={corelink}")

# C6 — limite rígido (núcleo + overlay e núcleo + cada perfil)
core = read(CORE)
over: list[str] = []
if nbytes(core + "\n\n" + read(OVERLAY)) > HARD:
    over.append("Diretor")
for cat in CATALOGS:
    for b in profile_blocks(read(cat)):
        if nbytes(core + "\n\n" + "\n".join(b)) > HARD:
            over.append(b[0].strip()[:30])
check(not over, f"C6 núcleo+perfil <= {HARD} bytes", f"excedem={over}")

# C7 — o preset é autônomo (usado SOZINHO, sem núcleo), então medimos só ele
check(nbytes(read(PRESET)) <= HARD, f"C7 preset do engenheiro <= {HARD} bytes",
      f"{nbytes(read(PRESET))} bytes")

print()
if fails:
    print(f"RESULTADO: {len(fails)} FALHA(S): {fails}")
elif warns:
    print(f"RESULTADO: OK — biblioteca consistente ({len(warns)} aviso(s); use --strict para tratá-los como falha)")
else:
    print("RESULTADO: OK — biblioteca consistente")
sys.exit(1 if fails else 0)
