#!/usr/bin/env python3
"""quality-gate.py — roda todos os checks do arsenal. Um comando, um veredito.

Uso:
    python scripts/quality-gate.py            # relatório legível
    python scripts/quality-gate.py --json     # saída para CI
    python scripts/quality-gate.py --fix      # regenera manifesto/índice antes de checar

Exit: 0 = tudo passou · 1 = alguma falha · 2 = erro de ambiente
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def rodar(nome: str, cmd: list[str]) -> dict:
    try:
        p = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, timeout=300)
        saida = (p.stdout or "").strip().splitlines()
        erro = (p.stderr or "").strip().splitlines()
        return {
            "check": nome,
            "ok": p.returncode == 0,
            "exit": p.returncode,
            "resumo": saida[-1] if saida else (erro[-1] if erro else ""),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"check": nome, "ok": False, "exit": -1, "resumo": f"erro: {exc}"}


def validar_skills(py: str) -> list[dict]:
    """Roda o validate_skill.py de cada skill que tiver um."""
    resultados = []
    for skill in sorted(p for p in (RAIZ / "skills").iterdir() if p.is_dir()):
        v = skill / "scripts" / "validate_skill.py"
        if not v.is_file():
            resultados.append({
                "check": f"validate:{skill.name}",
                "ok": True,
                "exit": 0,
                "resumo": "sem validate_skill.py (pulado)",
            })
            continue
        r = rodar(f"validate:{skill.name}", [py, str(v)])
        resultados.append(r)
    return resultados


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args(argv)

    py = sys.executable
    resultados: list[dict] = []

    if args.fix:
        resultados.append(rodar("manifesto:gerar", [py, "scripts/build-manifest.py"]))

    resultados += validar_skills(py)
    resultados.append(rodar("manifesto:check", [py, "scripts/build-manifest.py", "--check"]))
    resultados.append(rodar("links", [py, "scripts/check-links.py", "."]))
    resultados.append(rodar("estrutura", [py, "scripts/check-structure.py"]))
    resultados.append(rodar("evals:coerencia", [py, "scripts/run-evals.py", "--check"]))
    resultados.append(rodar("evals:schema", [py, "scripts/run-evals.py", "--schema"]))
    resultados.append(rodar("evals:registros", [py, "scripts/check-eval-results.py"]))

    falhas = [r for r in resultados if not r["ok"]]
    if args.json:
        print(json.dumps({"ok": not falhas, "total": len(resultados),
                          "falhas": len(falhas), "checks": resultados}, indent=2, ensure_ascii=False))
        return 0 if not falhas else 1

    print("# Quality gate — dz23-arsenal\n")
    print(f"{'check':<42}{'resultado':<10}resumo")
    print("-" * 100)
    for r in resultados:
        marca = "OK" if r["ok"] else "FALHA"
        print(f"{r['check']:<42}{marca:<10}{r['resumo'][:52]}")
    print()
    print(f"{len(resultados) - len(falhas)}/{len(resultados)} checks passaram")
    if falhas:
        print("\nFALHAS:")
        for r in falhas:
            print(f"  - {r['check']}: {r['resumo']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
