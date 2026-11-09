#!/usr/bin/env python3
# Minimal reimplementation — o helper original do Manus (sandbox
# /home/ubuntu/) não está acessível. Este arquivo reproduz o
# comportamento descrito em _sources/manus-verification.md.
# Para a versão completa (46 testes), ver README da skill.
"""Compara duas amostras de latência e descreve o delta por percentil.

Não executa benchmark, não acessa rede, não instala nada. Só descreve
números já coletados.

Uso:
    python scripts/compare_samples.py antes.json depois.json [--json] [--out cmp.json]

Formato de entrada:
    {"metadata": {"workload": "...", "cohort": "...", "cache_state": "...",
                  "sample_source": "..."},
     "samples": [12.3, 15.1, ...]}   # latências em ms

Exit 0 = comparação estruturalmente válida
Exit 1 = falha de cálculo
Exit 2 = input inválido
Exit 3 = comparação bloqueada (metadata divergente)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

REQUIRED_META = ("workload", "cohort", "cache_state", "sample_source")
FLAGS = {
    "descriptive_comparison_only": True,
    "performance_pass": False,
    "benchmark_executed": False,
    "context_verified": False,
}


def fail(msg: str, code: int) -> "NoReturn":  # type: ignore[name-defined]
    print(f"INVALID {msg}", file=sys.stderr)
    raise SystemExit(code)


def percentile_nearest_rank(sorted_values: list[float], q: float) -> float:
    """Nearest-rank: índice = ceil(q * n), 1-based."""
    n = len(sorted_values)
    if n == 0:
        raise ValueError("amostra vazia")
    idx = max(1, math.ceil(q * n))
    return sorted_values[min(idx, n) - 1]


def load(path: Path) -> dict:
    if not path.is_file():
        fail(f"arquivo não encontrado: {path}", 2)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        fail(f"JSON inválido em {path.name}: {exc}", 2)
    if not isinstance(data, dict):
        fail(f"{path.name}: raiz não é objeto", 2)
    meta = data.get("metadata")
    if not isinstance(meta, dict):
        fail(f"{path.name}: falta 'metadata'", 2)
    for key in REQUIRED_META:
        if not meta.get(key):
            fail(f"{path.name}: metadata.{key} ausente", 2)
    samples = data.get("samples")
    if not isinstance(samples, list) or not samples:
        fail(f"{path.name}: 'samples' precisa ser lista não vazia", 2)
    clean: list[float] = []
    for value in samples:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            fail(f"{path.name}: amostra não numérica ({type(value).__name__})", 2)
        if not math.isfinite(value) or value < 0:
            fail(f"{path.name}: amostra inválida (não finita ou negativa)", 2)
        clean.append(float(value))
    return {"metadata": meta, "samples": clean}


def describe(samples: list[float]) -> dict:
    ordered = sorted(samples)
    return {
        "n": len(ordered),
        "min": ordered[0],
        "p50": percentile_nearest_rank(ordered, 0.50),
        "p75": percentile_nearest_rank(ordered, 0.75),
        "p95": percentile_nearest_rank(ordered, 0.95),
        "p99": percentile_nearest_rank(ordered, 0.99),
        "max": ordered[-1],
    }


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Compara amostras antes/depois (descritivo).")
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)

    before = load(Path(args.before))
    after = load(Path(args.after))

    diffs = {k: (before["metadata"].get(k), after["metadata"].get(k))
             for k in REQUIRED_META
             if before["metadata"].get(k) != after["metadata"].get(k)}
    if diffs:
        print("COMPARISON_BLOCKED metadata divergente:", file=sys.stderr)
        for key, (a, b) in diffs.items():
            print(f"  {key}: '{a}' != '{b}'", file=sys.stderr)
        print("DESCRIPTIVE_COMPARISON_ONLY performance_pass=false "
              "benchmark_executed=false context_verified=false")
        raise SystemExit(3)

    try:
        b = describe(before["samples"])
        a = describe(after["samples"])
    except ValueError as exc:
        fail(f"falha de cálculo: {exc}", 1)

    delta = {}
    for key in ("p50", "p75", "p95", "p99"):
        base = b[key]
        delta[key] = {
            "before": base,
            "after": a[key],
            "abs": round(a[key] - base, 3),
            "pct": round(((a[key] - base) / base) * 100, 2) if base else None,
        }

    payload = {"before": b, "after": a, "delta": delta, "metadata": before["metadata"], **FLAGS}

    if args.out:
        out = Path(args.out).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(out.parent, 0o700)
        except OSError:
            pass
        fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"COMPARISON_WRITTEN {out}")

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"workload   : {before['metadata'].get('workload')}")
        print(f"cohort     : {before['metadata'].get('cohort')} · cache: "
              f"{before['metadata'].get('cache_state')} · fonte: {before['metadata'].get('sample_source')}")
        print(f"n antes/depois: {b['n']} / {a['n']}")
        # rótulos ASCII: console Windows (cp1252) não imprime Δ
        print(f"{'pct':<6}{'antes':>10}{'depois':>10}{'delta':>10}{'delta%':>10}")
        for key in ("p50", "p75", "p95", "p99"):
            d = delta[key]
            pct = "-" if d["pct"] is None else f"{d['pct']:+.1f}%"
            print(f"{key:<6}{d['before']:>10.2f}{d['after']:>10.2f}{d['abs']:>+10.2f}{pct:>10}")
        print("DESCRIPTIVE_COMPARISON_ONLY performance_pass=false "
              "benchmark_executed=false context_verified=false")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
