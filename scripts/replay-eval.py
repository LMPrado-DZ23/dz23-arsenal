#!/usr/bin/env python3
"""replay-eval.py -- roda o harness de replay: re-gradua as respostas registradas.

Para cada fixture em eval-harness/replays/: aplica o grader determinístico à resposta registrada
(deve reproduzir o veredito esperado) E à resposta negativa sintética (deve dar FAIL -- prova que o
grader DISCRIMINA, não carimba). Relata MATCH/DIFF e a proveniência/camada.

Uso:
    python scripts/replay-eval.py             # relatório legível
    python scripts/replay-eval.py --json
Exit: 0 se tudo reproduz e discrimina · 1 caso contrário
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _replay import carrega, verdito_derivado  # noqa: E402


def avalia() -> list[dict]:
    linhas = []
    for path, r in carrega():
        bom = verdito_derivado(r.get("response", ""), r.get("grader", {}))
        ruim = verdito_derivado(r.get("response_negativo", ""), r.get("grader", {}))
        reproduz = bom == r.get("expected_verdict")
        discrimina = ruim == "FAIL"
        linhas.append({
            "fixture": path.name,
            "skill": r.get("skill"),
            "eval_id": r.get("eval_id"),
            "camada": r.get("camada"),
            "esperado": r.get("expected_verdict"),
            "derivado": bom,
            "negativo": ruim,
            "status": "MATCH" if (reproduz and discrimina) else "DIFF",
        })
    return linhas


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    linhas = avalia()
    difs = [l for l in linhas if l["status"] != "MATCH"]
    if args.json:
        print(json.dumps({"ok": not difs, "total": len(linhas), "match": len(linhas) - len(difs),
                          "replays": linhas}, ensure_ascii=False, indent=2))
        return 0 if not difs else 1

    if not linhas:
        print("Nenhum replay em eval-harness/replays/")
        return 0
    print(f"{'fixture':<38}{'camada':<16}{'esperado':<10}{'derivado':<10}{'neg':<6}status")
    print("-" * 92)
    for l in linhas:
        print(f"{l['fixture']:<38}{l['camada']:<16}{l['esperado']:<10}{l['derivado']:<10}"
              f"{l['negativo']:<6}{l['status']}")
    print(f"\n{len(linhas) - len(difs)}/{len(linhas)} reproduzem e discriminam")
    if difs:
        for l in difs:
            print(f"  DIFF {l['fixture']}: derivado={l['derivado']} esperado={l['esperado']} "
                  f"negativo={l['negativo']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
