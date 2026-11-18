#!/usr/bin/env python3
"""_replay.py -- motor do harness de eval por replay. Importado por replay-eval.py e check-replay.py.

Ideia (adaptada do grader-replay do modern-web-guidance, Apache-2.0): um veredito de eval deixa de
ser uma AFIRMAÇÃO de uma vez e passa a ser REPRODUTÍVEL -- a resposta registrada é re-graduada por
um grader determinístico (checagens mecânicas), e o veredito derivado é comparado ao registrado.

Honestidade do que isto prova e do que NÃO prova:
  - PROVA: reprodutibilidade (mesma entrada -> mesmo veredito, mecanicamente) e que o grader
    DISCRIMINA (a resposta boa dá PASS, uma resposta ruim sintética dá FAIL).
  - NÃO PROVA: juízo independente. A resposta é do próprio autor (Camada 1); o replay a torna
    reproduzível, não isenta do viés do autor. Juízo independente é Camada 3 (juiz externo),
    fora do alcance desta sessão e declarado como NOT_TESTED.

Só evals com rubrica genuinamente MECÂNICA entram aqui. Rubrica subjetiva (qualidade de texto em
português) não é graduável de forma determinística e NÃO recebe fixture de replay.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR = RAIZ / "eval-harness" / "replays"
CAMADAS = {"1-reproduzivel", "2-adversarial", "3-independente", "4-uso-real"}
CAMPOS = ("skill", "eval_id", "camada", "provenance", "fonte_resposta", "response",
          "response_negativo", "grader", "expected_verdict")
PROV_CAMPOS = ("model", "environment", "timestamp", "method")


def carrega() -> list[tuple[Path, dict]]:
    if not DIR.is_dir():
        return []
    out = []
    for p in sorted(DIR.glob("*.json")):
        out.append((p, json.loads(p.read_text(encoding="utf-8"))))
    return out


def aplica_grader(texto: str, grader: dict) -> bool:
    """True sse a resposta satisfaz TODAS as checagens mecânicas do grader."""
    t = texto or ""
    for termo in grader.get("contains", []):
        if termo not in t:
            return False
    for termo in grader.get("not_contains", []):
        if termo in t:
            return False
    for padrao in grader.get("regex", []):
        if not re.search(padrao, t):
            return False
    return True


def verdito_derivado(resposta: str, grader: dict) -> str:
    return "PASS" if aplica_grader(resposta, grader) else "FAIL"
