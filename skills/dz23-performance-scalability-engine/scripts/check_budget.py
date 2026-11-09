#!/usr/bin/env python3
# Parser de evidência — não executa medição. O usuário precisa rodar
# Lighthouse/k6/EXPLAIN e colar em benchmark-comparison.md.
"""Compara o budget declarado com o benchmark medido (ambos em markdown).

Não roda Lighthouse, k6 ou EXPLAIN; não instala nada; não acessa rede.
Só lê os artefatos que o usuário preencheu.

Uso:
    python scripts/check_budget.py --budget performance-budget.md \
        --benchmark benchmark-comparison.md [--format human|json]

Formato do budget (tabela markdown, uma métrica por linha):
    | Métrica | Budget | Estado |
    |---|---|---|
    | LCP p75 | ≤ 2,5 s | |
    | p95 API | ≤ 500 ms | |

Formato do benchmark (tabela "Depois", ou linhas "métrica: valor"):
    | Métrica | p50 | p95 | p99 |
    | LCP p75 | 1,9 s | ... | ... |

Exit 0 = PASS (todas as métricas dentro do budget)
Exit 1 = FAIL (alguma métrica estourou)
Exit 2 = input inválido
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NUM = r"-?\d+(?:[.,]\d+)?"
UNIT_FACTOR = {
    "ms": 1.0, "s": 1000.0, "seg": 1000.0, "segundo": 1000.0, "segundos": 1000.0,
    "kb": 1.0, "kib": 1.0, "mb": 1024.0,
    "%": 1.0, "": 1.0,
}


def fail(msg: str, code: int = 2) -> "NoReturn":  # type: ignore[name-defined]
    print(f"INVALID {msg}", file=sys.stderr)
    raise SystemExit(code)


def to_number(text: str) -> tuple[float, str] | None:
    m = re.search(rf"({NUM})\s*([a-zA-Z%]*)", text)
    if not m:
        return None
    raw = m.group(1).replace(",", ".")
    unit = m.group(2).lower()
    try:
        value = float(raw)
    except ValueError:
        return None
    factor = UNIT_FACTOR.get(unit)
    if factor is None:
        return None
    return value * factor, unit


def parse_table_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) or c == "" for c in cells):
            continue  # separador
        rows.append(cells)
    return rows


def parse_budget(path: Path) -> dict[str, dict]:
    rows = parse_table_rows(path)
    if not rows:
        fail(f"{path.name}: nenhuma tabela markdown encontrada")
    header = [h.lower() for h in rows[0]]
    try:
        i_metric = header.index("métrica") if "métrica" in header else header.index("metrica")
    except ValueError:
        fail(f"{path.name}: coluna 'Métrica' ausente")
    i_budget = next((i for i, h in enumerate(header) if "budget" in h), None)
    if i_budget is None:
        fail(f"{path.name}: coluna 'Budget' ausente")
    budget: dict[str, dict] = {}
    for row in rows[1:]:
        if len(row) <= max(i_metric, i_budget):
            continue
        metric = row[i_metric].strip()
        if not metric:
            continue
        parsed = to_number(row[i_budget])
        if not parsed:
            continue
        limit, unit = parsed
        budget[metric.lower()] = {"metric": metric, "limit": limit, "unit": unit,
                                  "raw": row[i_budget]}
    if not budget:
        fail(f"{path.name}: nenhum budget numérico reconhecido")
    return budget


def parse_benchmark(path: Path) -> dict[str, float]:
    measured: dict[str, float] = {}
    rows = parse_table_rows(path)
    if rows:
        header = [h.lower() for h in rows[0]]
        col = 2 if len(header) > 2 and "p95" in header[2] else 1
        for row in rows[1:]:
            if len(row) <= col:
                continue
            parsed = to_number(row[col])
            if parsed:
                measured[row[0].strip().lower()] = parsed[0]
    if not measured:
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(rf"^\s*[-*]?\s*([A-Za-z0-9 ._/%-]+):\s*({NUM}\s*[a-zA-Z%]*)", line)
            if m:
                parsed = to_number(m.group(2))
                if parsed:
                    measured[m.group(1).strip().lower()] = parsed[0]
    if not measured:
        fail(f"{path.name}: nenhuma medição reconhecida (tabela ou lista 'métrica: valor')")
    return measured


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(description="Compara budget × benchmark (parser, não mede).")
    ap.add_argument("--budget", required=True)
    ap.add_argument("--benchmark", required=True)
    ap.add_argument("--format", choices=("human", "json"), default="human")
    args = ap.parse_args(argv)

    budget_path = Path(args.budget)
    bench_path = Path(args.benchmark)
    for p in (budget_path, bench_path):
        if not p.is_file():
            fail(f"arquivo não encontrado: {p}")

    budget = parse_budget(budget_path)
    measured = parse_benchmark(bench_path)

    results = []
    missing = []
    for key, spec in budget.items():
        if key in measured:
            atual = measured[key]
            status = "PASS" if atual <= spec["limit"] else "FAIL"
            results.append({"metric": spec["metric"], "budget_raw": spec["raw"],
                            "budget": spec["limit"], "actual": atual, "status": status})
        else:
            missing.append(spec["metric"])
            results.append({"metric": spec["metric"], "budget_raw": spec["raw"],
                            "budget": spec["limit"], "actual": None, "status": "NOT_TESTED"})

    fails = [r for r in results if r["status"] == "FAIL"]
    payload = {"budget_file": str(budget_path), "benchmark_file": str(bench_path),
               "results": results, "missing": missing,
               "summary": {"pass": sum(1 for r in results if r["status"] == "PASS"),
                           "fail": len(fails),
                           "not_tested": len(missing)},
               "executed_measurement": False}

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"{'métrica':<28}{'budget':>12}{'atual':>12}  status")
        for r in results:
            atual = "—" if r["actual"] is None else f"{r['actual']:.2f}"
            print(f"{r['metric']:<28}{r['budget_raw']:>12}{atual:>12}  {r['status']}")
        print(f"\nPASS={payload['summary']['pass']} FAIL={payload['summary']['fail']} "
              f"NOT_TESTED={payload['summary']['not_tested']}")
        print("executed_measurement=false")

    if fails:
        print(f"BUDGET_FAIL {len(fails)} métrica(s) acima do budget", file=sys.stderr)
        return 1
    if missing:
        print(f"BUDGET_PARTIAL {len(missing)} métrica(s) sem medição", file=sys.stderr)
        return 0
    print("BUDGET_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
