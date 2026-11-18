"""consulta-backend.py -- acervo de decisoes de backend/postgres/API do arsenal.

Molde: igual ao consulta-design.py (que por sua vez seguiu a licao da rodada 47 -- dado sem meio de
acesso e referencia morta). Le os CSVs de dados-backend/, cada linha com origem declarada.

Regras herdadas das duas correcoes feitas no consultor de design, ambas por falso positivo medido:
  - casa por PALAVRA INTEIRA, nunca substring solta. 'ux formulario' respondia 'Animation :: Duration
    Timing' porque 'for' vive dentro de 'performance'. Um acervo que responde a pergunta certa com a
    linha errada engana mais que um ausente, porque o agente passa a confiar.
  - sinonimos vem de MAPA FECHADO, nao de remover sufixo as cegas nem de traducao generica. Sem
    correspondencia, diz 'sem correspondencia' e sugere listar -- nunca aproxima.

Uso:
  python scripts/consulta-backend.py listar
  python scripts/consulta-backend.py indice "jsonb @>"
  python scripts/consulta-backend.py tipo dinheiro
  python scripts/consulta-backend.py migracao "not null"
  python scripts/consulta-backend.py http patch
  python scripts/consulta-backend.py api graphql
  python scripts/consulta-backend.py limite premium
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys

# Fonte canonica do acervo: skills/dz23-backend-data-architect/dados/ (viaja com a instalacao).
# Este arquivo em scripts/ e o mesmo codigo, resolvendo o dado pelo caminho da skill -- manter uma
# copia unica dos CSVs evita duas fontes de verdade; check-copies confere que os dois .py nao divergem.
# O acervo mora na PROPRIA skill (skills/<nome>/dados/), nao em dados-backend/ na raiz do repo.
# Motivo medido nesta sessao: `install-all` copia apenas a pasta da skill para
# ~/.agents/skills/<nome>/, entao um consultor que sobe dois niveis e procura `dados-backend/` funciona
# no checkout e falha na instalacao -- a habilidade continha a instrucao de rodar um script cujo dado
# nao existia onde ela ficou. Autonomia de conhecimento so vale se a skill levar o dado junto; apontar
# para fora era a classe da rodada 47 aplicada ao ambiente de execucao do usuario.
RAIZ = pathlib.Path(__file__).resolve().parent.parent.parent
DADOS = pathlib.Path(__file__).resolve().parent.parent / "dados"

# dataset -> (aliases em portugues, colunas de saida)
DATASETS = {
    "indice": {
        "arquivo": "indices-por-padrao-de-query.csv",
        "aliases": {"indice", "indices", "index", "indexes", "indexacao", "query",
                    "consultar", "desempenho de query"},
        "busca_em": ["query_pattern", "index_type"],
        "titulo": "Indice por padrao de query",
    },
    "tipo": {
        "arquivo": "tipos-de-dado.csv",
        "aliases": {"tipo", "tipos", "coluna", "schema", "dinheiro", "money", "moeda",
                    "timestamp", "data-hora", "uuid", "booleano", "texto"},
        "busca_em": ["use_case", "correct_type", "avoid"],
        "titulo": "Tipo de dado correto por caso de uso",
    },
    "migracao": {
        "arquivo": "antipadroes-de-migracao.csv",
        "aliases": {"migracao", "migracoes", "antipadrao", "anti-padrao", "ddl", "alter",
                    "drop", "column", "coluna", "zero-downtime", "rollback de schema"},
        "busca_em": ["anti-pattern", "why_it_fails", "better_approach"],
        "titulo": "Antipadroes de migracao",
    },
    "http": {
        "arquivo": "semantica-de-metodo-http.csv",
        "aliases": {"http", "metodo", "verb", "get", "post", "put", "patch", "delete",
                    "idempotencia", "seguro"},
        "busca_em": ["method", "safe", "idempotent", "use_for"],
        "titulo": "Semantica dos metodos HTTP",
    },
    "api": {
        "arquivo": "estilo-de-api-quando-usar.csv",
        "aliases": {"paginacao", "pagina", "offset", "cursor", "feed", "scroll", "busca"},
        # colunas REAIS do CSV (use_case, pagination_type). A primeira versao listava
        # ["style","when_to_use"], que nao existem no arquivo -- e como o codigo usava
        # r.get(c,"") sem validar, toda busca nesse dataset devolvia string vazia e portanto
        # 'sem correspondencia', silenciosamente. Coluna errada num consultor e pior que coluna
        # ausente: o acervo existe, tem a resposta, e o tool diz que nao ha nada.
        "busca_em": ["use_case", "pagination_type"],
        "titulo": "Paginação: offset vs cursor por caso de uso",
    },
    "limite": {
        "arquivo": "faixas-de-rate-limit.csv",
        "aliases": {"limite", "rate", "rate limit", "throttle", "tier", "plano",
                    "free tier", "premium"},
        "busca_em": ["tier", "limit", "window", "use_case"],
        "titulo": "Faixas de rate limit por plano",
    },
}


# Ponte PT->EN termo a termo, mapa FECHADO: so palavras que de fato aparecem como celula na fonte.
# Nao e tradutor nem dicionario geral -- e a lista minima para o usuario pedir em portugues uma
# linha escrita em ingles. Termo ausente aqui cai em 'sem correspondencia', que e a resposta certa.
TERMOS = {
    "tipo": {"dinheiro": "money", "moeda": "money", "valor monetario": "money",
             "prazo": "flags", "bandeira": "flags", "sim-nao": "flags",
             "identificador": "ids", "chave primaria": "ids",
             "texto livre": "strings", "data e hora": "timestamps", "fuso": "timestamps"},
    "indice": {"tempo de serie": "time-series", "historico": "time-series",
               "log": "time-series", "conteudo estruturado": "jsonb",
               "busca textual": "tsv", "busca full text": "tsv", "fulltext": "tsv",
               "igualdade": "where col = value", "faixa": "col > value",
               "composta": "a = x and b > y"},
    "migracao": {"nao nulo sem default": "adding not null column without default",
                 "indice inline": "inline index", "apagar coluna": "dropping column",
                 "editar migracao": "editing deployed migrations",
                 "sql manual": "manual sql", "tudo numa migracao": "schema + data"},
    "http": {"parcial": "patch", "substituir": "put", "buscar": "get",
             "criar": "post", "apagar": "delete", "listar": "get"},
    "api": {"admin": "admin dashboards", "pequeno": "small datasets",
            "feed": "infinite scroll", "scroll infinito": "infinite scroll",
            "grande volume": "large datasets", "publica": "public apis",
            "busca": "search results", "pagina numerada": "page numbers"},
    "limite": {"gratis": "free", "anonimo": "anonymous", "anônimo": "anonymous",
               "logado": "authenticated", "autenticado": "authenticated",
               "pago": "premium", "empresarial": "enterprise", "interno": "internal",
               "servico": "service-to-service", "microsservico": "service-to-service"},
}


def _norma(s: str) -> str:
    s = s.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                 ("ã", "a"), ("õ", "o"), ("ç", "c")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def _casa(agulha: str, texto: str) -> bool:
    """Palavra inteira ou frase contigua. Nunca substring de palavra maior."""
    a, t = _norma(agulha), _norma(texto)
    if not a or not t:
        return False
    if a == t:
        return True
    if re.search(rf"(?<![\w]){re.escape(a)}(?![\w])", t):
        return True
    # termos de uma frase multi-palavra, todos presentes como palavras
    termos = [_norma(w) for w in a.split() if len(_norma(w)) > 2]
    if len(termos) > 1 and termos:
        return all(re.search(rf"(?<![\w]){re.escape(x)}(?![\w])", t) for x in termos)
    return False


def _ler(nome: str) -> list[dict]:
    p = DADOS / nome
    if not p.is_file():
        raise SystemExit(
            f"FALHA: {p.relative_to(RAIZ)} ausente. O acervo em dados-backend/ nao foi gerado? "
            f"Ver dados-backend/PROVENIENCIA.md.")
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def cmd_listar(_a) -> int:
    if not DADOS.is_dir():
        print(f"FALHA: {DADOS.relative_to(RAIZ)} ausente")
        return 1
    print(f"acervo em {DADOS.relative_to(RAIZ)}:")
    total = 0
    for chave, cfg in DATASETS.items():
        p = DADOS / cfg["arquivo"]
        if not p.is_file():
            print(f"  {chave:<12}{cfg['arquivo']:<40}AUSENTE")
            continue
        with p.open(encoding="utf-8-sig", newline="") as fh:
            n = len(list(csv.DictReader(fh)))
        total += n
        print(f"  {chave:<12}{cfg['arquivo']:<40}{n:>3} registros   {cfg['titulo']}")
    print(f"\ntotal: {total} decisoes tabuladas")
    print("comandos: " + " | ".join(DATASETS) + " | listar")
    print("cada linha cita o arquivo e a secao de onde veio (colunas origem_*).")
    return 0


def cmd_consulta(chave: str):
    def fn(args) -> int:
        cfg = DATASETS[chave]
        linhas = _ler(cfg["arquivo"])
        alvo = _norma(args.termo)

        achados = [r for r in linhas
                   if any(_casa(args.termo, str(r.get(c, ""))) for c in cfg["busca_em"])]
        if not achados:
            # ponte por TERMO, nao por tema. A versao anterior, ao nao achar nada, devolvia a
            # tabela inteira quando a palavra era um alias de dominio -- ou seja, respondia tudo
            # quando nao sabia nada, a pior forma de falso positivo: parece cobertura. O plano e
            # explicito ("responde 'sem correspondencia' quando nao ha, nunca aproxima"), entao
            # so casa via SINONIMOS_de_termo, mapa fechado linha-a-linha.
            equivalente = TERMOS.get(chave, {}).get(alvo)
            if equivalente:
                achados = [r for r in linhas
                           if any(_casa(equivalente, str(r.get(c, ""))) for c in cfg["busca_em"])]
        if not achados:
            sugestoes = sorted({str(r.get(cfg["busca_em"][0], "")).strip()[:34]
                                for r in linhas if r.get(cfg["busca_em"][0])})
            print(f"sem correspondencia para '{args.termo}' em {cfg['titulo']} "
                  f"({len(linhas)} registros). Nao vou aproximar nem despejar a tabela inteira.")
            print("  valores desta tabela: " + "; ".join(sugestoes[:8]))
            return 1
        for r in achados[: args.top]:
            print(f"[{r.get('No')}] " + "  |  ".join(
                f"{k}: {str(v)[:110]}" for k, v in r.items()
                if k not in ("No", "origem_arquivo", "origem_secao")))
            print(f"      origem: {r.get('origem_arquivo')} :: {r.get('origem_secao')}")
        if len(achados) > args.top:
            print(f"-- {len(achados)} resultados, mostrando {args.top}")
        return 0
    return fn


def _colunas_validas() -> list[str]:
    """Confere que cada `busca_em` existe de fato no CSV correspondente.

    Nao e paranoia decorativa: foi assim que o dataset 'api' ficou mudo -- pedia colunas que nao
    existem no arquivo, e `.get(c, "")` transformava o erro em string vazia, que por sua vez virava
    'sem correspondencia'. O acervo tinha a resposta; o consultor dizia que nao havia nada. Uma
    checagem de esquema custa tres linhas e elimina a classe inteira.
    """
    ruins = []
    for chave, cfg in DATASETS.items():
        p = DADOS / cfg["arquivo"]
        if not p.is_file():
            continue
        with p.open(encoding="utf-8-sig", newline="") as fh:
            cabecalho = next(csv.reader(fh), [])
        faltando = [c for c in cfg["busca_em"] if c not in cabecalho]
        if faltando:
            ruins.append(f"{chave}: colunas {faltando} ausentes em {cfg['arquivo']} "
                         f"(tem: {cabecalho})")
    return ruins


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
        p.add_argument("--top", type=int, default=4)
        p.set_defaults(fn=cmd_consulta(chave))
    args = ap.parse_args(argv)
    quebradas = _colunas_validas()
    if quebradas:
        print("FALHA de esquema -- o consultor esta apontando para colunas que nao existem:")
        for q in quebradas:
            print("  -", q)
        return 1
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
