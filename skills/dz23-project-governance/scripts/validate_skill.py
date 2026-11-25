from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _achar_arsenal import importar_validador_comum  # noqa: E402


def fail(message: str) -> None:
    print(f"FALHA: {message}", file=sys.stderr)
    raise SystemExit(1)


common = importar_validador_comum(Path(__file__).resolve())
if common is None:
    fail("validador comum do arsenal não localizado")
errors = common(ROOT)
if errors:
    for error in errors:
        print(f"FALHA: {error}", file=sys.stderr)
    raise SystemExit(1)

skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
for marker in ("## 1. Ceremony level", "## 3. Decision gate and approval", "## 4. Rituals and artifacts", "## 7. Security and anti-patterns"):
    if marker not in skill:
        fail(f"seção obrigatória ausente: {marker}")
if "name: dz23-project-governance" not in skill:
    fail("nome incorreto no frontmatter")
if "version: 1.0.0" not in skill:
    fail("versão 1.0.0 ausente no frontmatter")

evals = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
if evals.get("skill") != "dz23-project-governance":
    fail("skill incorreta em evals/evals.json")
cases = evals.get("cases", [])
if len(cases) < 8:
    fail("menos de 8 cenários de avaliação")
for case in cases:
    for field in ("id", "title", "input", "expected", "fails_if"):
        if not isinstance(case.get(field), str) or not case[field].strip():
            fail(f"caso {case.get('id')!r} sem {field}")

for path in ROOT.rglob("*.md"):
    if not path.read_text(encoding="utf-8").strip():
        fail(f"arquivo Markdown vazio: {path.relative_to(ROOT)}")

print(f"PASS: dz23-project-governance v1.0.0; {len(cases)} evals; checks específicos OK")
