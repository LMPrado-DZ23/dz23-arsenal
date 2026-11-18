"""consulta-espec.py -- acervo de decisoes que merecem um ADR, da ECC architecture-decision-records.

Molde dos quatro itens anteriores (backend, performance, design, codebase), carregando as licoes medidas
na construcao deles -- nao sao estilo, sao defeitos que aconteceram e custaram rodadas:
  1. casar por PALAVRA INTEIRA (substring solta fazia 'ux formulario' responder 'Animation').
  2. mapa PT->EN FECHADO e EXAUSTIVO na prova -- a primeira versao do consulta-performance tinha entradas
     no radical ('waterfall' contra 'Waterfalls') que nunca casavam; so apareceram quando todas as chaves
     foram executadas, nao amostradas.
  3. _colunas_validas() -- um `busca_em` errado silenciou um dataset inteiro sem avisar.
  4. DADOS ao lado do script + RAIZ resolvida subindo ate achar skills/ -- apontar para a raiz do repo
     funcionava no checkout e quebrava em ~/.agents/skills/.
  5. hash de integridade CANONICO (EOL-independente): .gitattributes normaliza CSV para LF no indice mas o
     gerador escreve CRLF no disco Windows; hashear bytes crus fez o CI reprovar o item 4 enquanto local
     passava verde. Normalizar \\r\\n -> \\n antes do sha256 e obrigatorio aqui desde ja.

Sem correspondencia, responde 'sem correspondencia' + valores existentes. Nunca aproxima.

Uso:
  python scripts/consulta-espec.py listar
  python scripts/consulta-espec.py categoria seguranca
  python scripts/consulta-espec.py vale "monolith vs microservices"
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys


def _acha_skill() -> pathlib.Path:
    """O diretorio da skill e o primeiro ancestral que contem `dados/categorias-de-decisao-adr.csv`.

    Contar niveis fixos foi o bug dos itens anteriores: rodando de skills/<nome>/scripts/ a arvore certa e
    parent.parent (a skill), mas de scripts/ do repo e outra conta, e apontar para a raiz quebrava na
    instalacao em ~/.agents/skills/. Procurar o arquivo de dados e autoexplicativo e funciona em qualquer
    uma das tres origens -- se nenhum ancestral tem o acervo, a mensagem diz isso em vez de mentir exit 0.
    """
    alvo = pathlib.Path(__file__).resolve().parent
    for _ in range(6):
        if (alvo / "dados" / "categorias-de-decisao-adr.csv").is_file():
            return alvo
        if alvo.parent == alvo:
            break
        alvo = alvo.parent
    raise SystemExit(
        "FALHA: nao encontrei dados/categorias-de-decisao-adr.csv em nenhum ancestral deste script. "
        "O acervo deveria estar ao lado, dentro da skill -- verifique install-all.ps1 -Force.")


SKILL = _acha_skill()
RAIZ = SKILL.parent.parent          # checkout do arsenal (skills/<nome> sobe dois ate a raiz)
DADOS = SKILL / "dados"

DATASETS = {
    "categoria": {
        "arquivo": "categorias-de-decisao-adr.csv",
        "busca_em": ["category", "examples"],
        "titulo": "Que tipo de decisao merece um ADR registrado",
    },
    "vale": {
        "arquivo": "categorias-de-decisao-adr.csv",
        "busca_em": ["examples", "category"],
        "titulo": "Uma escolha concreta cabe em qual categoria de ADR?",
    },
}

# Ponte PT->EN fechada. Cada valor foi conferido contra uma celula REAL da tabela (a prova executa todas
# as chaves); nada veio de memoria. O acervo e pequeno (8 linhas) justamente para evitar sinonimo morto.
TERMOS = {
    "categoria": {"tecnologia": "technology choices", "stack": "technology choices",
                  "framework": "technology choices", "linguagem": "technology choices",
                  "arquitetura": "architecture patterns", "padrao": "architecture patterns",
                  "microsservico": "architecture patterns", "microservico": "architecture patterns",
                  "monolito": "architecture patterns", "cqrs": "architecture patterns",
                  "api": "api design", "versamento": "api design", "autenticacao": "api design",
                  "dados": "data modeling", "modelo": "data modeling", "schema": "data modeling",
                  "cache": "data modeling", "normalizacao": "data modeling",
                  "infra": "infrastructure", "infraestrutura": "infrastructure",
                  "deploy": "infrastructure", "ci": "infrastructure", "monitoramento": "infrastructure",
                  "seguranca": "security", "criptografia": "security", "segredo": "security",
                  "teste": "testing", "cobertura": "testing", "e2e": "testing",
                  "processo": "process", "branch": "process", "revisao": "process",
                  "release": "process"},
    "vale": {"banco": "database", "nuvem": "cloud provider", "fila": "event-driven",
             "graphql": "REST vs GraphQL", "rest": "REST vs GraphQL",
             "criptografia": "encryption approach", "estrategia": "strategy"},
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
    if a == t or t.startswith(a):
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
        raise SystemExit(
            f"FALHA: {p.name} ausente. O acervo deveria estar em skills/dz23-spec-to-system-engine/dados/ "
            f"-- verifique a instalacao (install-all.ps1 -Force).")
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
    print("acervo em skills/dz23-spec-to-system-engine/dados/")
    vistos = set()
    total = 0
    for chave, cfg in DATASETS.items():
        p = DADOS / cfg["arquivo"]
        if not p.is_file():
            print(f"  {chave:<12}{cfg['arquivo']:<38}AUSENTE")
            continue
        novo = cfg["arquivo"] not in vistos
        vistos.add(cfg["arquivo"])
        with p.open(encoding="utf-8-sig", newline="") as fh:
            n = len(list(csv.DictReader(fh)))
        if novo:
            total += n
        prefixo = "  " + chave if novo else "  (mesmo arquivo)"
        print(f"{prefixo:<16}{cfg['arquivo']:<36}{n:>3} registros   {cfg['titulo']}")
    print(f"\ntotal: {total} decisoes tabuladas")
    print("comandos: categoria | vale | listar")
    print("cada linha cita origem_arquivo e origem_secao.")
    return 0


def cmd_consulta(chave: str):
    def fn(args) -> int:
        cfg = DATASETS[chave]
        linhas = _ler(cfg["arquivo"])
        achados = [(max(_casa(args.termo, str(r.get(c, ""))) * 100 for c in cfg["busca_em"]), r)
                   for r in linhas]
        achados = sorted([x for x in achados if x[0] > 0], key=lambda x: -x[0])
        if not achados:
            equivalente = TERMOS.get(chave, {}).get(_norma(args.termo))
            if equivalente:
                achados = [(max(_casa(equivalente, str(r.get(c, ""))) * 100 for c in cfg["busca_em"]), r)
                           for r in linhas
                           if any(_casa(equivalente, str(r.get(c, ""))) for c in cfg["busca_em"])]
        if not achados:
            col = cfg["busca_em"][0]
            valores = sorted({str(r.get(col, "")).strip()[:44] for r in linhas if r.get(col)})
            print(f"sem correspondencia para '{args.termo}' em {cfg['titulo']} "
                  f"({len(linhas)} registros). Nao vou aproximar nem despejar a tabela inteira.")
            print("  valores desta tabela: " + "; ".join(valores[:9]))
            return 1
        for _, r in achados[: args.top]:
            print(f"[{r.get('No')}] category: {r.get('category')}")
            print(f"      exemplos: {str(r.get('examples'))[:120]}")
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
