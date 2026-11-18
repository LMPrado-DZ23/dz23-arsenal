#!/usr/bin/env python3
"""check-cobertura-incorporadas.py -- skill incorporada não fica verde em silêncio (achado do Qwen).

As skills incorporadas (não `dz23-*`) são isentas do ledger 144 das DZ23 de propósito (não mover o
denominador). Mas isenção virou invisibilidade: 7 delas declaravam 6 evals cada com 0 execução e o
gate passava. Isso contradiz 'evidência ou silêncio'.

Este check exige, para cada skill incorporada com evals declarados, UMA de duas coisas:
  1. EVIDÊNCIA EXECUTADA: acervo consultável (`dados/`) OU fixture de replay que a referencia; ou
  2. DECLARAÇÃO HONESTA: entrada em eval-harness/cobertura-incorporadas.json com status NOT_TESTED
     e um motivo não-vazio.

Reprova: skill incorporada com evals e sem nenhuma das duas (verde silencioso); entrada de manifesto
órfã (skill inexistente) ou redundante (skill que JÁ tem evidência executada — declaração morta);
status fora do conjunto. Não toca no denominador das DZ23.

Uso:
    python scripts/check-cobertura-incorporadas.py            # exit 1 se houver problema
    python scripts/check-cobertura-incorporadas.py --json
    python scripts/check-cobertura-incorporadas.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "skills"
MANIFESTO = RAIZ / "eval-harness" / "cobertura-incorporadas.json"
REPLAYS = RAIZ / "eval-harness" / "replays"
STATUS_OK = {"NOT_TESTED", "BLOCKED"}


def _incorporadas_com_evals(skills_dir: Path) -> set[str]:
    out = set()
    if not skills_dir.is_dir():
        return out
    for d in skills_dir.iterdir():
        if not d.is_dir() or d.name.startswith("dz23-"):
            continue
        ev = d / "evals" / "evals.json"
        if not ev.is_file():
            continue
        try:
            if json.loads(ev.read_text(encoding="utf-8")).get("cases"):
                out.add(d.name)
        except (OSError, json.JSONDecodeError):
            out.add(d.name)  # evals.json ilegível conta como "tem evals" (não isenta)
    return out


def _cobertas(skills_dir: Path, replays_dir: Path) -> set[str]:
    """Skills com evidência executada: acervo (dados/) ou fixture de replay que as referencia."""
    cobertas = set()
    if skills_dir.is_dir():
        for d in skills_dir.iterdir():
            if d.is_dir() and (d / "dados").is_dir():
                cobertas.add(d.name)
    if replays_dir.is_dir():
        for p in replays_dir.glob("*.json"):
            try:
                cobertas.add(json.loads(p.read_text(encoding="utf-8")).get("skill"))
            except (OSError, json.JSONDecodeError):
                pass
    cobertas.discard(None)
    return cobertas


def valida(incorporadas: set[str], cobertas: set[str], manifesto: dict) -> list[str]:
    declaradas = (manifesto or {}).get("declaradas") or {}
    problemas: list[str] = []

    for s in sorted(incorporadas):
        if s in cobertas:
            continue  # tem evidência executada
        d = declaradas.get(s)
        if not d:
            problemas.append(f"{s}: skill incorporada com evals e SEM evidência executada nem "
                             f"declaração NOT_TESTED (verde silencioso)")
            continue
        if d.get("status") not in STATUS_OK:
            problemas.append(f"{s}: status inválido {d.get('status')!r} (use NOT_TESTED/BLOCKED)")
        if not (d.get("motivo") or "").strip():
            problemas.append(f"{s}: declaração sem motivo")

    for s, d in declaradas.items():
        if s not in incorporadas:
            problemas.append(f"declaração órfã: {s} não é skill incorporada com evals")
        elif s in cobertas:
            problemas.append(f"declaração morta: {s} já tem evidência executada — remova do manifesto")
    return problemas


def _selftest() -> int:
    inc = {"a", "b", "c"}
    cob = {"a"}  # 'a' coberta por evidência
    man = {"declaradas": {"b": {"status": "NOT_TESTED", "motivo": "ok"}}}
    # 'c' não coberta e não declarada -> deve reprovar
    if not valida(inc, cob, man):
        print("FALHA selftest: 'c' sem cobertura nem declaração passou")
        return 1
    man_ok = {"declaradas": {"b": {"status": "NOT_TESTED", "motivo": "ok"},
                             "c": {"status": "NOT_TESTED", "motivo": "ok"}}}
    if valida(inc, cob, man_ok):
        print("FALHA selftest: estado válido reprovado")
        return 1
    casos = [
        ("motivo vazio", {"declaradas": {"b": {"status": "NOT_TESTED", "motivo": "ok"},
                                         "c": {"status": "NOT_TESTED", "motivo": "  "}}}),
        ("status inválido", {"declaradas": {"b": {"status": "NOT_TESTED", "motivo": "ok"},
                                            "c": {"status": "PRONTO", "motivo": "x"}}}),
        ("declaração órfã", {"declaradas": {"b": {"status": "NOT_TESTED", "motivo": "ok"},
                                            "c": {"status": "NOT_TESTED", "motivo": "ok"},
                                            "zzz": {"status": "NOT_TESTED", "motivo": "x"}}}),
        ("declaração morta", {"declaradas": {"a": {"status": "NOT_TESTED", "motivo": "x"},
                                             "b": {"status": "NOT_TESTED", "motivo": "ok"},
                                             "c": {"status": "NOT_TESTED", "motivo": "ok"}}}),
    ]
    for desc, m in casos:
        if not valida(inc, cob, m):
            print(f"FALHA selftest: mutação '{desc}' não detectada")
            return 1
    print("OK selftest: estado válido aprova; 5 mutações reprovam")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    incorporadas = _incorporadas_com_evals(SKILLS)
    cobertas = _cobertas(SKILLS, REPLAYS)
    manifesto = {}
    if MANIFESTO.is_file():
        try:
            manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FALHA: manifesto ilegível: {exc}")
            return 1
    problemas = valida(incorporadas, cobertas, manifesto)
    if args.json:
        print(json.dumps({"ok": not problemas, "incorporadas": len(incorporadas),
                          "cobertas": sorted(incorporadas & cobertas), "problemas": problemas},
                         ensure_ascii=False, indent=2))
        return 0 if not problemas else 1
    if problemas:
        for p in problemas:
            print(f"FALHA: {p}")
        return 1
    n_cob = len(incorporadas & cobertas)
    n_dec = len(incorporadas) - n_cob
    print(f"OK: {len(incorporadas)} skills incorporadas com evals -- {n_cob} com evidência executada, "
          f"{n_dec} declaradas NOT_TESTED (nenhuma em verde silencioso)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
