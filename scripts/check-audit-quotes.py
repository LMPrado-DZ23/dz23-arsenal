#!/usr/bin/env python3
"""check-audit-quotes.py — confere se as citações de um laudo existem na resposta.

Motivo: a re-auditoria de 2026-11-09 afirmou que o laudo original tinha citação fabricada em 9 de 11
casos. Esta ferramenta mede isso sem depender de quem afirma: extrai cada bloco citado (`> "..."`) do
laudo, normaliza e procura na resposta correspondente do pacote.

Classes por citação:
  VERBATIM   o texto citado aparece na resposta (tolerância de acento/espaço)
  ADAPTADO   aparece com alteração pequena (>= 70% dos trechos de 6 palavras presentes)
  FABRICADO  não aparece (ou aparece < 30%)

Uso:
    python scripts/check-audit-quotes.py audit-results/audit-2026-11-09.md
    python scripts/check-audit-quotes.py <laudo> --json

Exit: 0 todas VERBATIM/ADAPTADO · 1 há FABRICADO · 2 falha de leitura
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PKG = RAIZ / "audit-package"


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t).split())


def shingles(texto: str, n: int = 6) -> list[str]:
    words = norm(texto).split()
    if len(words) < n:
        return [" ".join(words)] if words else []
    return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]


def classificar(citacao: str, resposta: str) -> tuple[str, float]:
    ncit = norm(citacao)
    nresp = norm(resposta)
    if not ncit:
        return "VAZIA", 0.0
    if ncit in nresp:
        return "VERBATIM", 1.0
    frag = shingles(citacao)
    if not frag:
        return "FABRICADO", 0.0
    presentes = sum(1 for f in frag if f in nresp)
    taxa = presentes / len(frag)
    if taxa >= 0.7:
        return "ADAPTADO", taxa
    return "FABRICADO", taxa


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

    laudo = Path(args.laudo)
    if not laudo.is_absolute():
        laudo = RAIZ / laudo
    if not laudo.is_file():
        print(f"ERRO: laudo não encontrado: {laudo}", file=sys.stderr)
        return 2

    texto = laudo.read_text(encoding="utf-8", errors="replace")
    blocos = re.split(r"\n#{3,4} Eval (\d+)", texto)

    respostas = {}
    for f in sorted((PKG / "responses").glob("*.txt")):
        respostas[int(f.name.split("-")[0])] = f.read_text(encoding="utf-8", errors="replace")

    resultados = []
    for i in range(1, len(blocos), 2):
        num = int(blocos[i])
        corpo = blocos[i + 1]
        # citações: linhas começando com '>' ou blocos entre aspas longas
        citacoes = [re.sub(r"^\s*>\s?", "", l).strip() for l in corpo.splitlines() if l.strip().startswith(">")]
        citacoes = [c for c in citacoes if len(norm(c)) >= 25]
        if not citacoes:
            citacoes = [m.group(1) for m in re.finditer(r'"([^"\n]{30,})"', corpo)]

        resp = respostas.get(num, "")
        for cit in citacoes:
            classe, taxa = classificar(cit, resp)
            resultados.append({"num": num, "classe": classe, "taxa": round(taxa, 2), "citacao": cit[:160]})

    if not resultados:
        print("ERRO: nenhuma citação longa encontrada no laudo", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(resultados, indent=2, ensure_ascii=False))
    else:
        por_eval: dict[int, dict[str, int]] = {}
        for r in resultados:
            d = por_eval.setdefault(r["num"], {"VERBATIM": 0, "ADAPTADO": 0, "FABRICADO": 0})
            d[r["classe"]] += 1
        print(f"{'#':>3} {'verbatim':>9} {'adaptado':>9} {'fabricado':>10}")
        print("-" * 36)
        for num in sorted(por_eval):
            d = por_eval[num]
            print(f"{num:>3} {d['VERBATIM']:>9} {d['ADAPTADO']:>9} {d['FABRICADO']:>10}")
        total = {k: sum(1 for r in resultados if r["classe"] == k) for k in ("VERBATIM", "ADAPTADO", "FABRICADO")}
        evals_com_fab = len({r["num"] for r in resultados if r["classe"] == "FABRICADO"})
        print()
        print(f"citações: {len(resultados)} · {total}")
        print(f"evals com pelo menos uma citação fabricada: {evals_com_fab} de {len(por_eval)}")

    return 1 if any(r["classe"] == "FABRICADO" for r in resultados) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
