"""consulta-performance.py -- acervo de priorizacao de performance React/Next do arsenal.

Molde identico ao consulta-backend.py e ao consulta-design.py, porque as duas liçoes daquela
construcao sao gerais, nao locais:
  - casar por PALAVRA INTEIRA (substring solta fazia 'ux formulario' responder 'Animation');
  - sem correspondencia => recusar e listar valores disponiveis; nunca despejar a tabela inteira
    como resposta quando o consultor nao sabe.
Aqui ha ainda _colunas_validas(), escrita depois de um `busca_em` errado silenciar um dataset inteiro.

O que este acervo responde NAO e "como otimizar" -- e "por onde comecar", que e o erro tipico: agente
ataca re-render (prioridade 5) quando o gargalo e waterfall de await (prioridade 1). A tabela de
prioridade existe para impedir essa ordem errada, e a de metrica->categoria liga o sintoma medido
(LCP ruim) ao tipo de regra que mexe nele.

Uso:
  python scripts/consulta-performance.py listar
  python scripts/consulta-performance.py prioridade bundle
  python scripts/consulta-performance.py metrica lcp
  python scripts/consulta-performance.py categoria rerender
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys

# Fonte canonica do acervo: skills/dz23-performance-scalability-engine/dados/ (viaja com a
# instalacao). Este arquivo e o mesmo codigo resolvendo pelo caminho da skill -- uma copia unica dos
# CSVs; check-copies confere que os dois .py nao divergem.
# Na habilidade instalada o acervo fica AO LADO do script (skills/<nome>/dados/), porque e so isso que
# `install-all` copia para ~/.agents/skills/. Apontar para dados-performance/ na raiz do repo funciona
# no checkout e falha no uso real -- ver nota equivalente em consulta-backend.py.
RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
DADOS = pathlib.Path(__file__).resolve().parent.parent / "dados"

DATASETS = {
    "prioridade": {
        "arquivo": "prioridade-por-categoria.csv",
        "busca_em": ["category", "when_it_matters", "prefix"],
        "titulo": "Prioridade de ataque por categoria de otimizacao",
    },
    "metrica": {
        "arquivo": "metrica-para-categoria.csv",
        "busca_em": ["metric", "most_relevant_categories"],
        "titulo": "Metrica Web Vitals -> categorias relevantes",
    },
    "categoria": {
        "arquivo": "prioridade-por-categoria.csv",
        "busca_em": ["category", "prefix"],
        "titulo": "Categoria por nome ou prefixo de regra",
    },
}

# Ponte PT->EN fechada: so palavras que existem como celula na fonte. Sem tradutor generico.
# Cuidado com o radical: _casa() exige palavra inteira e nao desfaz plural -- foi uma das duas
# correcoes do consultor de design, e ela vale tambem aqui. Escrever 'waterfall' nao casa
# 'Eliminating Waterfalls'; o mapa precisa conter a palavra COMO ELA ESTA na tabela. Medido: a
# primeira versao deste mapa tinha quatro entradas no singular que nunca casavam nada, e so
# apareceram porque cada termo foi testado de fato em vez de confiado.
TERMOS = {
    "prioridade": {"cachear": "waterfalls", "sequencial": "waterfalls", "await": "waterfalls",
                   "cascata": "waterfalls", "cachos": "waterfalls",
                   "tamanho": "bundle size", "peso": "bundle size",
                   "primeira carga": "bundle size", "biblioteca": "bundle size",
                   "pacote": "bundle size",
                   "servidor": "server-side performance", "ssr": "server-side performance",
                   "backend": "server-side performance",
                   "cliente": "client-side data fetching", "hook": "client-side data fetching",
                   "re-render": "re-render optimization", "rerender": "re-render optimization",
                   "estado": "re-render optimization",
                   "lista grande": "rendering performance", "animacao": "rendering performance",
                   "hidratacao": "rendering performance",
                   "lento no loop": "javascript performance",
                   "alocacao": "javascript performance", "avancado": "advanced patterns"},
    "metrica": {"maior conteudo": "lcp", "imagem grande": "lcp", "hero lento": "lcp",
                "interacao": "inp", "clique lento": "inp", "resposta": "inp",
                "pulo de layout": "cls", "layout shift": "cls", "salto": "cls",
                "travamento": "tbt", "bloqueio": "tbt", "main thread": "tbt",
                "legado": "fid"},
    "categoria": {"cascata": "waterfalls", "pacote": "bundle", "peso": "bundle",
                  "renderizacao": "rendering"},
    # 'vital' foi removido daqui: categoria le prioridade-por-categoria.csv, onde nenhuma celula diz
    # "web vitals" -- quem responde por metrica e o dataset 'metrica'. O termo estava no mapa errado e
    # so apareceu ao exercitar as 42 chaves uma a uma; testar os tres termos que eu havia escolhido
    # para a prova o teria mantido vivo como decoracao silenciosa.
}


def _norma(s: str) -> str:
    s = s.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                 ("ã", "a"), ("õ", "o"), ("ç", "c")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def _casa(agulha: str, texto: str) -> bool:
    a, t = _norma(agulha), _norma(texto)
    if not a or not t:
        return False
    if a == t:
        return True
    if re.search(rf"(?<![\w]){re.escape(a)}(?![\w])", t):
        return True
    termos = [_norma(w) for w in a.split() if len(_norma(w)) > 2]
    if len(termos) > 1:
        return all(re.search(rf"(?<![\w]){re.escape(x)}(?![\w])", t) for x in termos)
    return False


def _ler(nome: str) -> list[dict]:
    p = DADOS / nome
    if not p.is_file():
        raise SystemExit(f"FALHA: {p.relative_to(RAIZ)} ausente. Ver dados-performance/.")
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _colunas_validas() -> list[str]:
    ruins = []
    for chave, cfg in DATASETS.items():
        p = DADOS / cfg["arquivo"]
        if not p.is_file():
            continue
        with p.open(encoding="utf-8-sig", newline="") as fh:
            cab = next(csv.reader(fh), [])
        faltando = [c for c in cfg["busca_em"] if c not in cab]
        if faltando:
            ruins.append(f"{chave}: colunas {faltando} ausentes em {cfg['arquivo']} (tem: {cab})")
    return ruins


def cmd_listar(_a) -> int:
    print(f"acervo em {DADOS.relative_to(RAIZ)}:")
    vistos = set()
    total = 0
    for chave, cfg in DATASETS.items():
        p = DADOS / cfg["arquivo"]
        if not p.is_file():
            print(f"  {chave:<12}{cfg['arquivo']:<36}AUSENTE")
            continue
        novo = cfg["arquivo"] not in vistos
        vistos.add(cfg["arquivo"])
        with p.open(encoding="utf-8-sig", newline="") as fh:
            n = len(list(csv.DictReader(fh)))
        if novo:
            total += n
        prefixo = "  " + chave if novo else "  (mesmo arquivo)"
        print(f"{prefixo:<16}{cfg['arquivo']:<34}{n:>3} registros   {cfg['titulo']}")
    print(f"\ntotal: {total} linhas de decisao")
    print("comandos: prioridade | metrica | categoria | listar")
    print("cada linha cita origem_arquivo e origem_secao.")
    return 0


def cmd_consulta(chave: str):
    def fn(args) -> int:
        cfg = DATASETS[chave]
        linhas = _ler(cfg["arquivo"])
        achados = [r for r in linhas
                   if any(_casa(args.termo, str(r.get(c, ""))) for c in cfg["busca_em"])]
        if not achados:
            equivalente = TERMOS.get(chave, {}).get(_norma(args.termo))
            if equivalente:
                achados = [r for r in linhas
                           if any(_casa(equivalente, str(r.get(c, ""))) for c in cfg["busca_em"])]
        if not achados:
            col = cfg["busca_em"][0]
            valores = sorted({str(r.get(col, "")).strip()[:38] for r in linhas if r.get(col)})
            print(f"sem correspondencia para '{args.termo}' em {cfg['titulo']} "
                  f"({len(linhas)} registros). Nao vou aproximar nem despejar a tabela inteira.")
            print("  valores desta tabela: " + "; ".join(valores[:9]))
            return 1
        for r in achados[: args.top]:
            print(f"[{r.get('No')}] " + "  |  ".join(
                f"{k}: {str(v)[:104]}" for k, v in r.items()
                if k not in ("No", "origem_arquivo", "origem_secao")))
            print(f"      origem: {r.get('origem_arquivo')} :: {r.get('origem_secao')}")
        if len(achados) > args.top:
            print(f"-- {len(achados)} resultados, mostrando {args.top}")
        return 0
    return fn


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar").set_defaults(fn=cmd_listar)
    for chave, cfg in DATASETS.items():
        p = sub.add_parser(chave, help=cfg["titulo"])
        p.add_argument("termo")
        p.add_argument("--top", type=int, default=3)
        p.set_defaults(fn=cmd_consulta(chave))
    args = ap.parse_args(argv)
    quebradas = _colunas_validas()
    if quebradas:
        print("FALHA de esquema -- o consultor aponta para colunas que nao existem:")
        for q in quebradas:
            print("  -", q)
        return 1
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
