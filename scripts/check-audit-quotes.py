#!/usr/bin/env python3
"""check-audit-quotes.py — confere se as citações de um laudo existem na resposta.

Motivo: a auditoria de 2026-11-09 citou trechos que não estão nas respostas. A re-auditoria apontou isso;
este script mede sem depender de quem afirma.

Classes por citação:
  VERBATIM   aparece na resposta (tolerância de acento/espaço)
  ADAPTADO   aparece com alteração pequena (>= 70% dos trechos de 6 palavras)
  FABRICADO  não aparece (< 30%)

Aceita os dois formatos de cabeçalho usados nos laudos: `## Eval NN` e `### Eval NN`.
Remove embrulhos de código inline (`` ` `` e `` `` ``) antes de comparar.

Uso:
    python scripts/check-audit-quotes.py audit-results/audit-2026-11-09.md
    python scripts/check-audit-quotes.py <laudo> --json
    python scripts/check-audit-quotes.py --selftest

Importável: `verificar_laudo(caminho)` devolve dict com contagem e casos fabricados.
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

RE_HEADER = re.compile(r"(?:^|\n)#{2,4} Eval (\d+)")
RE_WRAP = re.compile(r"^[`\s]+|[`\s]+$")


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t).split())


def limpar_citacao(c: str) -> str:
    """Remove embrulho de code-span, negrito e aspas das pontas."""
    c = c.strip()
    c = re.sub(r"^>\s?", "", c)
    c = RE_WRAP.sub("", c)
    c = c.strip("*_ \t")
    c = RE_WRAP.sub("", c)
    return c.strip()


def shingles(texto: str, n: int = 4) -> list[str]:
    words = norm(texto).split()
    if len(words) < n:
        return [" ".join(words)] if words else []
    return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]


def classificar(citacao: str, resposta: str) -> tuple[str, float]:
    # anotação do auditor entre parênteses não é citação da resposta
    bruto = citacao.strip()
    if bruto.startswith("(") or bruto.endswith(")"):
        # desbalanceado = continuação de anotação multi-linha
        if bruto.count("(") != bruto.count(")"):
            return "RESUMO", 0.0
    if bruto.startswith("(") and bruto.endswith(")") and bruto.count("(") == bruto.count(")"):
        return "RESUMO", 0.0
    ncit = norm(re.sub(r"\([^()]{0,400}\)", " ", citacao))
    nresp = norm(re.sub(r"\([^()]{0,400}\)", " ", resposta))
    if not ncit:
        return "VAZIA", 0.0
    if ncit in nresp:
        return "VERBATIM", 1.0
    frag = shingles(citacao)
    if not frag:
        return "FABRICADO", 0.0
    taxa = sum(1 for f in frag if f in nresp) / len(frag)
    return ("ADAPTADO", taxa) if taxa >= 0.7 else ("FABRICADO", taxa)


RE_SECAO_RESPOSTA = re.compile(
    r"(?:^|\n)(?:#{2,4}\s*(?:Resposta|Evidência da resposta)\b|\*\*Evidência da resposta:?\*\*)",
    re.I)
RE_FIM_SECAO = re.compile(r"(?:^|\n)(?:#{2,4}\s|\*\*[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")


def secao_resposta(corpo: str) -> str:
    """Isola a parte do bloco que cita a RESPOSTA.

    Sem isso, o verificador acusa como "fabricada" a citação do input antigo ou do expected —
    que por definição não está na resposta. Falso positivo que apareceu na Camada 4.
    """
    m = RE_SECAO_RESPOSTA.search(corpo)
    if not m:
        return corpo
    resto = corpo[m.end():]
    fim = RE_FIM_SECAO.search(resto)
    return resto[:fim.start()] if fim else resto


def extrair_citacoes(corpo: str, restringir: bool = True) -> list[str]:
    trecho = secao_resposta(corpo) if restringir else corpo

    brutas = [limpar_citacao(l) for l in trecho.splitlines() if l.strip().startswith(">")]
    citacoes = [re.sub(r"\s+", " ", c).strip() for c in brutas]
    citacoes = [c for c in citacoes if len(norm(c)) >= 25]
    if not citacoes:  # fallback: aspas longas no trecho
        citacoes = [m.group(1) for m in re.finditer(r'"([^"\n]{30,})"', trecho)]
    return citacoes


def carregar_respostas() -> dict[int, str]:
    respostas = {}
    for f in sorted((PKG / "responses").glob("*.txt")):
        respostas[int(f.name.split("-")[0])] = f.read_text(encoding="utf-8", errors="replace")
    return respostas


def verificar_laudo(caminho: Path | str) -> dict:
    """Verifica um laudo e devolve {laudo, citacoes: [...], resumo: {...}}."""
    caminho = Path(caminho)
    if not caminho.is_absolute():
        caminho = RAIZ / caminho
    if not caminho.is_file():
        raise FileNotFoundError(f"laudo não encontrado: {caminho}")

    texto = caminho.read_text(encoding="utf-8", errors="replace")
    respostas = carregar_respostas()
    blocos = RE_HEADER.split(texto)

    citacoes = []
    for i in range(1, len(blocos), 2):
        num = int(blocos[i])
        resp = respostas.get(num, "")
        linhas = extrair_citacoes(blocos[i + 1])
        j = 0
        while j < len(linhas):
            c = linhas[j]
            classe, taxa = classificar(c, resp)
            # linha quebrada no laudo: tenta juntar com a seguinte antes de acusar fabricação
            if classe == "FABRICADO" and j + 1 < len(linhas):
                junto = f"{c} {linhas[j + 1]}"
                classe2, taxa2 = classificar(junto, resp)
                if classe2 != "FABRICADO":
                    citacoes.append({"num": num, "classe": classe2, "taxa": round(taxa2, 2),
                                     "citacao": junto[:160], "juntada": True})
                    j += 2
                    continue
            citacoes.append({"num": num, "classe": classe, "taxa": round(taxa, 2),
                             "citacao": c[:160]})
            j += 1

    resumo = {k: sum(1 for c in citacoes if c["classe"] == k)
              for k in ("VERBATIM", "ADAPTADO", "RESUMO", "FABRICADO")}
    evals = sorted({c["num"] for c in citacoes})
    fabricados = sorted({c["num"] for c in citacoes if c["classe"] == "FABRICADO"})
    return {"laudo": str(caminho.relative_to(RAIZ)) if caminho.is_relative_to(RAIZ) else str(caminho),
            "citacoes": citacoes, "resumo": resumo, "evals": evals,
            "evals_com_fabricacao": fabricados,
            "ok": not fabricados and bool(citacoes)}


# ---------------------------------------------------------------- selftest
CASOS = [
    ("verbatim simples", "Trocar por BIGINT em centavos.", "Trocar por BIGINT em centavos.", "VERBATIM"),
    ("acento/embrulho", "Não fecha por centavos.", "`` Não fecha por centavos. ``", "VERBATIM"),
    ("fabricado", "O código recusa e registra BLOCKED.",
     "A skill anunciou que ia medir o RTO em 15 minutos com RPO de 5.", "FABRICADO"),
]


def selftest() -> int:
    falhas = 0
    print(f"{'caso':<22} {'esperado':<12} {'obtido':<12} ok")
    print("-" * 56)
    for desc, resp, cit, esperado in CASOS:
        obtido, _ = classificar(limpar_citacao(cit), resp)
        ok = obtido == esperado
        falhas += 0 if ok else 1
        print(f"{desc:<22} {esperado:<12} {obtido:<12} {'ok' if ok else 'FALHA'}")

    amostra_sec = ("## Eval 07 — x\n\n### Resposta (trecho literal)\n\n"
                   "> Texto que existe na resposta e tem tamanho suficiente.\n\n"
                   "### Julgamento\n\n> Trecho do expected que NAO esta na resposta, longo o bastante.\n")
    cits = extrair_citacoes(amostra_sec.split("Eval 07 — x", 1)[1])
    ok_sec = len(cits) == 1 and "existe na resposta" in cits[0]
    falhas += 0 if ok_sec else 1
    print(f"{'isola seção Resposta':<22} {'1 citação':<12} {str(len(cits)) + ' citação(ões)':<12} "
          f"{'ok' if ok_sec else 'FALHA'}")

    # formato de cabeçalho: ## e ###
    amostra = "## Eval 05 — x\n\n> Trecho qualquer com tamanho suficiente para contar.\n\n" \
              "### Eval 12 — y\n\n> Outro trecho com tamanho suficiente para contar.\n"
    nums = [int(m) for m in RE_HEADER.findall(amostra)]
    ok_h = nums == [5, 12]
    falhas += 0 if ok_h else 1
    print(f"{'cabeçalho ## e ###':<22} {'[5, 12]':<12} {str(nums):<12} {'ok' if ok_h else 'FALHA'}")
    print(f"\ncasos: {len(CASOS) + 1} · falhas: {falhas}")
    return 0 if falhas == 0 else 1


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("laudo", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.laudo:
        print("ERRO: informe o laudo (ou use --selftest)", file=sys.stderr)
        return 2

    try:
        r = verificar_laudo(args.laudo)
    except FileNotFoundError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        por_eval: dict[int, dict[str, int]] = {}
        for c in r["citacoes"]:
            d = por_eval.setdefault(c["num"], {"VERBATIM": 0, "ADAPTADO": 0, "RESUMO": 0, "FABRICADO": 0})
            d[c["classe"]] += 1
        print(f"{'#':>3} {'verbatim':>9} {'adaptado':>9} {'resumo':>7} {'fabricado':>10}")
        print("-" * 44)
        for num in sorted(por_eval):
            d = por_eval[num]
            print(f"{num:>3} {d['VERBATIM']:>9} {d['ADAPTADO']:>9} {d['RESUMO']:>7} {d['FABRICADO']:>10}")
        print()
        print(f"citações: {len(r['citacoes'])} · {r['resumo']}")
        print(f"evals com citação fabricada: {len(r['evals_com_fabricacao'])} de {len(r['evals'])}")
        if r["resumo"]["RESUMO"]:
            print(f"(RESUMO = anotação entre parênteses do auditor, não citação)")
        if not r["resumo"]["RESUMO"]:
            pass
        if not r["citacoes"]:
            print("AVISO: nenhuma citação longa encontrada — o laudo pode usar outro formato")

    if not r["citacoes"]:
        return 2
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
