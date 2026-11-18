#!/usr/bin/env python3
"""prova-encoding-gate.py -- prova que o quality-gate.py sobrevive a um locale cp1252.

O bug real desta sessao nao foi "cada script quebra isolado": foi o proprio
quality-gate.py capturando a saida dos sub-processos sem encoding explicito. No
Windows, subprocess.run(..., text=True, capture_output=True) decodifica como
cp1252 a saida UTF-8 dos scripts filhos -- e um byte invalido em cp1252 (0x81,
0x8D, 0x90, 0x9D) estoura UnicodeDecodeError, derrubando o gate inteiro. A
correcao foi fixar encoding="utf-8", errors="replace" em rodar().

Esta prova exercita o COMPORTAMENTO do gate, nao cada script isolado: roda o
proprio quality-gate.py --json com PYTHONIOENCODING=cp1252 no ambiente (o locale
hostil que originalmente quebrava) e exige:
  - exit 0 (todos os checks passaram sob o locale cp1252);
  - nenhum UnicodeDecodeError/UnicodeEncodeError no stderr;
  - stdout e JSON valido;
  - a contagem de checks foi preservada (ok=true, total plausivel).

Recursao: o gate roda esta prova como um de seus checks; esta prova roda o gate.
A variavel ARSENAL_GATE_ENCODING_SELFTEST=1 quebra o ciclo -- quando setada (a
rodada interna), a prova vira no-op aprovado, entao o gate roda ponta a ponta
exatamente um nivel de profundidade.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GATE = RAIZ / "scripts" / "quality-gate.py"
FLAG = "ARSENAL_GATE_ENCODING_SELFTEST"
# Piso defensivo: o gate ja tinha 95 checks quando esta prova nasceu. Se a contagem
# despencar, algo foi silenciosamente removido -- a prova denuncia em vez de aprovar.
MIN_CHECKS = 80


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    # Rodada interna: nao recorrer. Aprova e sai -- o gate externo ja esta medindo.
    if os.environ.get(FLAG) == "1":
        print("OK: rodada interna do selftest de encoding (no-op para evitar recursao)")
        return 0

    if not GATE.is_file():
        print(f"FALHA: {GATE} ausente")
        return 1

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"  # o locale hostil que quebrava o gate
    env[FLAG] = "1"                     # a rodada interna pula esta prova

    try:
        p = subprocess.run(
            [sys.executable, str(GATE), "--json"],
            cwd=str(RAIZ), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=600, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"FALHA: nao consegui rodar o gate sob cp1252: {exc}")
        return 1

    erros = []

    # 1. nenhum erro de decodificacao/codificacao vazou
    for marca in ("UnicodeDecodeError", "UnicodeEncodeError"):
        if marca in (p.stderr or ""):
            erros.append(f"{marca} no stderr do gate sob cp1252")

    # 2. stdout e JSON valido
    dados = None
    try:
        dados = json.loads(p.stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        erros.append(f"stdout do gate nao e JSON valido sob cp1252: {exc}")

    # 3. exit 0 e checks preservados
    if p.returncode != 0:
        erros.append(f"gate saiu {p.returncode} sob cp1252 (esperado 0)")
    if isinstance(dados, dict):
        if not dados.get("ok"):
            erros.append(f"gate reportou ok=false sob cp1252 ({dados.get('falhas')} falhas)")
        total = dados.get("total")
        if not isinstance(total, int) or total < MIN_CHECKS:
            erros.append(f"contagem de checks implausivel sob cp1252: {total} (<{MIN_CHECKS})")

    if erros:
        for e in erros:
            print(f"FALHA: {e}")
        return 1
    print(f"OK: gate rodou ponta a ponta sob PYTHONIOENCODING=cp1252 -- "
          f"exit 0, JSON valido, {dados.get('total')} checks, sem erro de encoding")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
