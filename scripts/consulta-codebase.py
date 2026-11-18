"""consulta-codebase.py -- acervo de decisoes sobre code tour e leitura de codigo alheio.

Molde identico a consulta-backend.py / consulta-performance.py, carregando as quatro licoes medidas
na construcao daqueles (nao sao estilo, sao defeitos que aconteceram):
  1. casar por PALAVRA INTEIRA -- substring solta fez 'ux formulario' responder 'Animation'.
  2. mapa PT->EN FECHADO e EXAUSTIVO na prova -- a primeira versao tinha entradas no radical
     ('waterfall' contra 'Waterfalls') que nunca casavam; so apareceram quando todas as chaves
     foram executadas, nao as escolhidas para a amostra.
  3. _colunas_validas() -- um `busca_em` errado silenciou um dataset inteiro sem avisar.
  4. DADOS ao lado do script (skills/<nome>/dados/), porque install-all copia so a pasta da skill;
     apontar para a raiz do repo funcionava no checkout e falhava em ~/.agents/skills/.

Sem correspondencia, responde 'sem correspondencia' + valores existentes. Nunca aproxima: um acervo
que devolve a linha errada engana mais que um acervo ausente, porque o agente passa a confiar.

Uso:
  python scripts/consulta-codebase.py listar
  python scripts/consulta-codebase.py profundidade onboarding
  python scripts/consulta-codebase.py antipadrao "flat file"
  python scripts/consulta-codebase.py quando-nao refatorar
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys

# O acervo viaja com a skill (skills/dz23-codebase-cartographer/dados/). Ver nota em
# consulta-backend.py: resolver pela raiz do repo funciona no checkout e quebra na instalacao.
# RAIZ e o checkout do arsenal, resolvido pelo lugar onde este arquivo esta: em scripts/ no repo
# (um nivel acima) ou dentro de skills/<nome>/scripts/ (tres acima). Antes disto a conta era fixa e
# so valia para um dos dois, entao rodar pela copia da skill procurava dados/ fora da pasta certa.
def _acha_raiz() -> pathlib.Path:
    aqui = pathlib.Path(__file__).resolve()
    for alvo in (alvo.parent for alvo in [aqui.parent, aqui.parent.parent.parent]):
        if (alvo / "skills").is_dir():
            return alvo
    return aqui.parent.parent


RAIZ = _acha_raiz()
SKILL = RAIZ / "skills" / "dz23-codebase-cartographer"
DADOS = SKILL / "dados"

DATASETS = {
    "profundidade": {
        "arquivo": "leitor-e-profundidade.csv",
        "busca_em": ["request_shape", "persona", "suggested_depth"],
        "titulo": "Que tipo de leitor o pedido indica e quantos passos o tour deve ter",
    },
    "antipadrao": {
        "arquivo": "antipadroes-de-code-tour.csv",
        "busca_em": ["anti_pattern", "fix"],
        "titulo": "Antipadroes de code tour e a correcao de cada um",
    },
    "quando-nao": {
        "arquivo": "quando-nao-usar-code-tour.csv",
        "busca_em": ["instead_of_code_tour", "use"],
        "titulo": "Quando NAO fazer code tour e o que usar no lugar",
    },
}

# Ponte PT->EN fechada. Cada valor abaixo foi COPIADO de uma celula que existe na tabela correspondente
# (listas em dados/*.csv), nao escrito de memoria -- a primeira versao desta lista tinha nove entradas
# apontando para personas plausiveis e inexistentes ('debugger', 'pm', 'executive', 'verified anchors');
# as tabelas usam bug-fixer, pr-reviewer, rca-investigator e 'Verify every file and line first'. A
# checagem exaustiva em prova-consulta-codebase.py executa todas as chaves por isso: sinonimo morto faz
# o usuario acreditar que a ponte existe, que e pior do que ela nunca ter sido prometida.
TERMOS = {
    "profundidade": {"iniciante": "new-joiner", "recem-chegado": "new-joiner",
                     "onboarding": "new-joiner", "integracao": "new-joiner",
                     "integração": "new-joiner", "novo na base": "new-joiner",
                     "rapido": "vibecoder", "vibe": "vibecoder", "superficial": "vibecoder",
                     "tour rapido": "vibecoder",
                     "arquitetura": "architect", "arquiteto": "architect",
                     "design do sistema": "architect",
                     "pull request": "pr-reviewer", "revisar pr": "pr-reviewer",
                     "quebrou": "rca-investigator", "por que quebrou": "rca-investigator",
                     "causa raiz": "rca-investigator",
                     "seguranca": "security-reviewer", "revisao de seguranca": "security-reviewer",
                     "como funciona": "feature-explainer", "explicar funcionalidade": "feature-explainer",
                     "depurar": "bug-fixer", "corrigir bug": "bug-fixer", "trilhar o bug": "bug-fixer"},
    "antipadrao": {"lista de arquivos": "flat file listing",
                   "listagem plana": "flat file listing",
                   "generico": "generic descriptions", "vago": "generic descriptions",
                   "chute": "guessed anchors", "suposto": "guessed anchors",
                   "ancora sem verificar": "guessed anchors",
                   "passos demais": "too many steps for a quick tour",
                   "longo demais": "too many steps for a quick tour",
                   "primeiro passo": "first step is content-only",
                   "persona errada": "persona mismatch",
                   "publico errado": "persona mismatch", "historia": "tell a story"},
    "quando-nao": {"refatorar": "the task is implementation or refactoring",
                   "implementar": "the task is implementation or refactoring",
                   "documentacao": "the user wants prose docs, not a .tour artifact",
                   "pergunta rapida": "a one-off explanation in chat is enough",
                   "simples": "a one-off explanation in chat is enough",
                   "onboarding amplo": "the task is broad codebase onboarding without a tour artifact"},
}


def _norma(s: str) -> str:
    s = s.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                 ("ã", "a"), ("õ", "o"), ("ç", "c")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def _casa(agulha: str, texto: str) -> bool:
    """Igualdade, prefixo ou palavra inteira. Nunca substring de palavra maior."""
    a, t = _norma(agulha), _norma(texto)
    if not a or not t:
        return False
    if a == t:
        return True
    if t.startswith(a):
        return True
    if re.search(rf"(?<![\w]){re.escape(a)}(?![\w])", t):
        return True
    termos = [_norma(w) for w in a.split() if len(_norma(w)) > 2]
    if len(termos) > 1:
        return all(re.search(rf"(?<![\w]){re.escape(x)}(?![\w])", t) for x in termos)
    return False


def _pontua(agulha: str, registro: dict, colunas: list[str]) -> int:
    """Forca do casamento: igualdade exata numa coluna vale mais que mencao lateral."""
    pontos = 0
    for c in colunas:
        v = str(registro.get(c, ""))
        if not v.strip():
            continue
        if _norma(agulha) == _norma(v):
            pontos = max(pontos, 100)
        elif _casa(agulha, v):
            pontos = max(pontos, 50)
    return pontos


def _ler(nome: str) -> list[dict]:
    p = DADOS / nome
    if not p.is_file():
        raise SystemExit(
            f"FALHA: {p.relative_to(RAIZ) if p.is_relative_to(RAIZ) else p} ausente. "
            f"O acervo deveria estar em skills/dz23-codebase-cartographer/dados/ -- verifique a "
            f"instalacao (install-all.ps1 -Force).")
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
    print(f"acervo em skills/dz23-codebase-cartographer/dados/")
    total = 0
    for chave, cfg in DATASETS.items():
        p = DADOS / cfg["arquivo"]
        if not p.is_file():
            print(f"  {chave:<14}{cfg['arquivo']:<36}AUSENTE")
            continue
        with p.open(encoding="utf-8-sig", newline="") as fh:
            n = len(list(csv.DictReader(fh)))
        total += n
        print(f"  {chave:<14}{cfg['arquivo']:<36}{n:>3} registros   {cfg['titulo']}")
    print(f"\ntotal: {total} decisoes tabuladas")
    print("comandos: " + " | ".join(DATASETS) + " | listar")
    print("cada linha cita origem_arquivo e origem_secao.")
    return 0


def cmd_consulta(chave: str):
    def fn(args) -> int:
        cfg = DATASETS[chave]
        linhas = _ler(cfg["arquivo"])
        pontuadas = [(_pontua(args.termo, r, cfg["busca_em"]), r) for r in linhas]
        achados = sorted([x for x in pontuadas if x[0] > 0], key=lambda x: -x[0])
        if not achados:
            equivalente = TERMOS.get(chave, {}).get(_norma(args.termo))
            if equivalente:
                achados = [(_pontua(equivalente, r, cfg["busca_em"]), r) for r in linhas
                           if _pontua(equivalente, r, cfg["busca_em"]) > 0]
        if not achados:
            col = cfg["busca_em"][0]
            valores = sorted({str(r.get(col, "")).strip()[:44] for r in linhas if r.get(col)})
            print(f"sem correspondencia para '{args.termo}' em {cfg['titulo']} "
                  f"({len(linhas)} registros). Nao vou aproximar nem despejar a tabela inteira.")
            print("  valores desta tabela: " + "; ".join(valores[:9]))
            return 1
        for _, r in achados[: args.top]:
            print(f"[{r.get('No')}] " + "  |  ".join(
                f"{k}: {str(v)[:104]}" for k, v in r.items()
                if k not in ("No", "origem_arquivo", "origem_secao")))
            print(f"      origem: {r.get('origem_arquivo')} :: {r.get('origem_secao')}")
        if len(achados) > args.top:
            print(f"-- {len(achados)} resultados, mostrando {args.top}")
        return 0
    return fn


def cmd_busca(args) -> int:
    """Busca uma palavra em todo o acervo (todos os datasets). Alinhado aos consultores novos."""
    termo = " ".join(args.termo)
    achados = []
    for chave, cfg in DATASETS.items():
        try:
            linhas = _ler(cfg["arquivo"])
        except SystemExit:
            continue
        for r in linhas:
            if any(_casa(termo, str(r.get(c, ""))) for c in cfg["busca_em"]):
                achados.append((chave, r))
    if not achados:
        print(f"sem correspondencia para '{termo}' no acervo. Nao vou aproximar.")
        return 1
    for chave, r in achados[: args.top]:
        print(f"[{chave}] " + "  |  ".join(
            f"{k}: {str(v)[:90]}" for k, v in r.items()
            if k not in ("No", "origem_arquivo", "origem_secao")))
    if len(achados) > args.top:
        print(f"-- {len(achados)} resultados, mostrando {args.top}")
    return 0


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
    pb = sub.add_parser("busca", help="busca uma palavra em todo o acervo")
    pb.add_argument("termo", nargs="+")
    pb.add_argument("--top", type=int, default=8)
    pb.set_defaults(fn=cmd_busca)
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
