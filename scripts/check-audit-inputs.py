#!/usr/bin/env python3
"""check-audit-inputs.py — confere se uma auditoria citou os `input` LITERALMENTE.

Motivo: a auditoria externa de 2026-11-09 parafraseou os cenários em vez de copiá-los. Em pelo menos
três casos a paráfrase removeu a armadilha que o eval existe para testar — o veredito passa a não
significar nada para aquele eval.

Uso:
    python scripts/check-audit-inputs.py audit-results/audit-2026-11-09.md
    python scripts/check-audit-inputs.py <laudo> --json

Saída: tabela por eval com classificação
  LITERAL          o input citado contém todos os termos do original (tolerância de acento/typo)
  PARÁFRASE        mesma situação em outras palavras, armadilha preservada
  CENÁRIO DIFERENTE  mudou o fato decisivo (ex.: DECIMAL onde o original diz FLOAT)
e lista de termos inventados (presentes no laudo, ausentes no input).

Exit: 0 se todos LITERAL/PARÁFRASE · 1 se houver CENÁRIO DIFERENTE · 2 falha de leitura
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PKG = RAIZ / "audit-package" / "evals"

# termos que, se aparecerem no input citado e não no original, indicam cenário trocado
SINAL_CRITICO = {
    "decimal", "float", "int", "bigint", "money", "centavos",
    "drop", "delete", "truncate", "alter",
    "mock", "stub", "fake",
    "http", "evento", "fila", "transação",
}


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def tokens(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9_]{4,}", norm(t))}


def extrair_inputs_do_laudo(texto: str) -> dict[int, str]:
    achados: dict[int, str] = {}
    blocos = re.split(r"\n#{3,4} Eval (\d+)", texto)
    for i in range(1, len(blocos), 2):
        num = int(blocos[i])
        corpo = blocos[i + 1]
        m = re.search(r"\*\*Input:?\*\*\s*(.+?)(?=\n\s*\n|\n\*\*)", corpo, re.S)
        if m:
            achados[num] = " ".join(m.group(1).split())
    return achados


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("laudo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    laudo_path = Path(args.laudo)
    if not laudo_path.is_absolute():
        laudo_path = RAIZ / laudo_path
    if not laudo_path.is_file():
        print(f"ERRO: laudo não encontrado: {laudo_path}", file=sys.stderr)
        return 2

    pacote = {}
    for f in sorted(PKG.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        pacote[int(f.name.split("-")[0])] = d

    citados = extrair_inputs_do_laudo(laudo_path.read_text(encoding="utf-8", errors="replace"))
    if not citados:
        print("ERRO: nenhum bloco '### Eval NN' com '**Input:**' no laudo", file=sys.stderr)
        return 2

    linhas = []
    for num, citado in sorted(citados.items()):
        d = pacote.get(num)
        if not d:
            continue
        real = d["input"]
        tr, tc = tokens(real), tokens(citado)
        cobertura = len(tr & tc) / len(tr) if tr else 1.0
        inventados = tc - tr
        criticos = sorted(inventados & SINAL_CRITICO)

        if cobertura >= 0.95:
            classe = "LITERAL"
        elif criticos or cobertura < 0.4:
            classe = "CENÁRIO DIFERENTE"
        else:
            classe = "PARÁFRASE"

        linhas.append({
            "num": num, "eval_id": d["eval_id"], "classe": classe,
            "cobertura": round(cobertura, 3), "termos_inventados": sorted(inventados),
            "termos_criticos": criticos, "real": real, "citado": citado,
        })

    if args.json:
        print(json.dumps(linhas, indent=2, ensure_ascii=False))
    else:
        contagem: dict[str, int] = {}
        print(f"{'#':>3} {'eval':<34} {'cobre':>6}  classe")
        print("-" * 78)
        for l in linhas:
            contagem[l["classe"]] = contagem.get(l["classe"], 0) + 1
            print(f"{l['num']:>3} {l['eval_id']:<34} {l['cobertura']:>5.0%}  {l['classe']}")
        print()
        for k in ("LITERAL", "PARÁFRASE", "CENÁRIO DIFERENTE"):
            print(f"{k:<20} {contagem.get(k, 0)}")
        dif = [l for l in linhas if l["classe"] == "CENÁRIO DIFERENTE"]
        if dif:
            print("\nCenários diferentes (o veredito não se aplica ao input original):")
            for l in dif:
                print(f"\n  {l['num']:02d} {l['eval_id']}")
                print(f"    original : {l['real']}")
                print(f"    no laudo : {l['citado']}")
                if l["termos_criticos"]:
                    print(f"    termos que mudam o cenário: {l['termos_criticos']}")

    return 1 if any(l["classe"] == "CENÁRIO DIFERENTE" for l in linhas) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
