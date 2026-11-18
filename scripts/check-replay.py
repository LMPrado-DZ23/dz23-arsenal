#!/usr/bin/env python3
"""check-replay.py -- o harness de replay é íntegro e sabe reprovar.

Exige, para cada fixture em eval-harness/replays/:
  1. Schema: todos os campos; camada do conjunto permitido; proveniência completa (model,
     environment, timestamp, method); expected_verdict válido.
  2. Grader não-vazio: um grader sem nenhuma checagem (contains/regex) carimbaria qualquer
     resposta -- é inválido.
  3. Reprodutibilidade: a resposta registrada reproduz o veredito esperado.
  4. Discriminação: a resposta negativa sintética dá FAIL (o grader não é carimbo).
  5. Cruzamento: (skill, eval_id) existe no evals.json da skill; fonte_resposta existe no disco.

Uso:
    python scripts/check-replay.py            # exit 1 se houver problema
    python scripts/check-replay.py --json
    python scripts/check-replay.py --selftest # controle negativo
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _replay import (CAMADAS, CAMPOS, PROV_CAMPOS, RAIZ, aplica_grader,  # noqa: E402
                     carrega, verdito_derivado)

VEREDITOS = {"PASS", "PARTIAL", "FAIL", "BLOCKED"}


def _eval_ids(skill: str) -> set[str]:
    ev = RAIZ / "skills" / skill / "evals" / "evals.json"
    if not ev.is_file():
        return set()
    try:
        d = json.loads(ev.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    return {c.get("id") for c in d.get("cases", []) if c.get("id")}


def valida_um(r: dict) -> list[str]:
    tag = f"{r.get('skill','?')}/{r.get('eval_id','?')}"
    probs = []
    for campo in CAMPOS:
        if campo not in r or r.get(campo) in (None, ""):
            probs.append(f"{tag}: campo ausente/vazio: {campo}")
    if r.get("camada") not in CAMADAS:
        probs.append(f"{tag}: camada inválida {r.get('camada')!r}")
    prov = r.get("provenance") or {}
    for c in PROV_CAMPOS:
        if not prov.get(c):
            probs.append(f"{tag}: proveniência sem {c}")
    if r.get("expected_verdict") not in VEREDITOS:
        probs.append(f"{tag}: expected_verdict inválido {r.get('expected_verdict')!r}")
    grader = r.get("grader") or {}
    if not (grader.get("contains") or grader.get("regex")):
        probs.append(f"{tag}: grader sem checagem (contains/regex) -- carimbaria tudo")
    # reprodutibilidade + discriminação
    if "response" in r and "grader" in r:
        if verdito_derivado(r["response"], grader) != r.get("expected_verdict"):
            probs.append(f"{tag}: resposta registrada NÃO reproduz o veredito {r.get('expected_verdict')}")
    if "response_negativo" in r and aplica_grader(r.get("response_negativo", ""), grader):
        probs.append(f"{tag}: resposta negativa passou no grader -- não discrimina")
    # cruzamento
    ids = _eval_ids(r.get("skill", ""))
    if ids and r.get("eval_id") not in ids:
        probs.append(f"{tag}: eval_id não existe no evals.json da skill")
    fonte = r.get("fonte_resposta")
    if fonte and not (RAIZ / fonte).is_file():
        probs.append(f"{tag}: fonte_resposta inexistente: {fonte}")
    return probs


def _selftest() -> int:
    bom = {
        "skill": "x", "eval_id": "y", "camada": "1-reproduzivel",
        "provenance": {"model": "m", "environment": "e", "timestamp": "t", "method": "md"},
        "fonte_resposta": "", "response": "tem exit 0 aqui", "response_negativo": "nada util",
        "grader": {"contains": ["exit 0"], "not_contains": [], "regex": []},
        "expected_verdict": "PASS",
    }
    # Sem fonte_resposta/campo vazio dispararia; para o selftest focamos nas regras mecânicas.
    base = dict(bom); base["fonte_resposta"] = "scripts/_replay.py"
    probs = [p for p in valida_um(base) if "eval_id não existe" not in p]
    if probs:
        print(f"FALHA selftest: fixture válido reprovado: {probs}")
        return 1
    casos = [
        ("camada inválida", lambda r: r.update(camada="99")),
        ("grader vazio", lambda r: r.update(grader={"contains": [], "regex": []})),
        ("não reproduz", lambda r: r.update(response="sem o termo")),
        ("não discrimina", lambda r: r.update(response_negativo="tem exit 0 tambem")),
        ("proveniência incompleta", lambda r: r["provenance"].pop("model")),
        ("veredito inválido", lambda r: r.update(expected_verdict="TALVEZ")),
    ]
    for desc, mut in casos:
        r = json.loads(json.dumps(base))
        mut(r)
        if not [p for p in valida_um(r) if "eval_id não existe" not in p]:
            print(f"FALHA selftest: mutação '{desc}' não detectada")
            return 1
    print("OK selftest: fixture válido aprova; 6 mutações reprovam")
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
    fixtures = carrega()
    if not fixtures:
        print("FALHA: nenhum replay em eval-harness/replays/")
        return 1
    problemas = []
    for _p, r in fixtures:
        problemas += valida_um(r)
    if args.json:
        print(json.dumps({"ok": not problemas, "total": len(fixtures), "problemas": problemas},
                         ensure_ascii=False, indent=2))
        return 0 if not problemas else 1
    if problemas:
        for p in problemas:
            print(f"FALHA: {p}")
        return 1
    print(f"OK: {len(fixtures)} replays íntegros (schema, reproduzem, discriminam, eval existe)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
