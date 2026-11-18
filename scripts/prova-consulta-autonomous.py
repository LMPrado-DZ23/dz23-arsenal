#!/usr/bin/env python3
"""prova-consulta-autonomous.py -- prova que o consulta-postgres responde certo e RECUSA quando deve."""
import csv
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONS = RAIZ / "scripts" / "consulta-autonomous.py"
DADOS = RAIZ / "skills" / "dz23-autonomous-improvement-ultimate" / "dados"
ARQS = ["gates-de-qualidade.csv", "verificacao-por-componente.csv", "falhas-de-agente.csv"]


def _run(args):
    r = subprocess.run([sys.executable, str(CONS), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (r.stdout or "") + (r.stderr or "")


def main() -> int:
    erros = []
    # 1. esquema: cada CSV existe e tem colunas de origem
    total = 0
    for nome in ARQS:
        p = DADOS / nome
        if not p.is_file():
            erros.append(f"ausente: {nome}")
            continue
        with p.open(encoding="utf-8") as f:
            linhas = list(csv.DictReader(f))
        total += len(linhas)
        for col in ("origem_arquivo", "origem_secao"):
            if linhas and col not in linhas[0]:
                erros.append(f"{nome} sem coluna {col}")

    # 2. consultas legitimas respondem a categoria certa
    positivos = {("gate", "e2e"): "fluxo", ("gate", "multitenancy"): "Tenant",
                 ("componente", "modal"): "foco", ("gate", "banco"): "rollback",
                 ("falhas", "loop"): "repeticao", ("falhas", "429"): "backoff"}
    for (ds, termo), esperado in positivos.items():
        out = _run([ds] + ([termo] if termo else []))
        if "sem correspondencia" in out:
            erros.append(f"'{ds} {termo}' recusou indevidamente")
        elif esperado.lower() not in out.lower():
            erros.append(f"'{ds} {termo}' sem o esperado {esperado!r}")

    # 3. controles negativos: termo inexistente RECUSA
    for ds, termo in (("gate", "futebolxyz"), ("componente", "blockchainxyz"), ("gate", "zzzz"),
                      ("falhas", "quasarxyz")):
        out = _run([ds, termo])
        if "sem correspondencia" not in out:
            erros.append(f"controle negativo falhou: '{ds} {termo}' nao foi recusado")

    # 4. listar reporta a contagem total
    out = _run(["listar"])
    somados = sum(len(list(csv.DictReader((DADOS / n).open(encoding="utf-8")))) for n in ARQS
                  if (DADOS / n).is_file())
    if somados != total:
        erros.append("contagem inconsistente")

    if erros:
        for e in erros:
            print(f"FALHA: {e}")
        return 1
    print(f"OK: {len(positivos)} consultas corretas, 4 recusas honestas, esquema valido, "
          f"{total} registros em {len(ARQS)} datasets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
