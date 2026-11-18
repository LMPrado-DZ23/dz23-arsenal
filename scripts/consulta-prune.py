#!/usr/bin/env python3
"""consulta-prune.py -- acervo das familias de teste podavel do prune-tests.

O conhecimento vive DENTRO da skill (dados/familias-de-poda.csv), tabulado da propria taxonomia
(references/taxonomia-do-que-podar.md). Consulta por familia em portugues, mapa fechado de sinonimos,
palavra inteira; responde 'sem correspondencia' quando nao ha. NUNCA remove teste -- so classifica.

Uso:
  python scripts/consulta-prune.py listar
  python scripts/consulta-prune.py familia implementacao
  python scripts/consulta-prune.py busca snapshot
"""
import argparse
import csv
import pathlib
import re
import sys


def _acha_raiz() -> pathlib.Path:
    aqui = pathlib.Path(__file__).resolve()
    for alvo in (a.parent for a in [aqui.parent, aqui.parent.parent.parent]):
        if (alvo / "skills").is_dir():
            return alvo
    return aqui.parent.parent


RAIZ = _acha_raiz()
DADOS = RAIZ / "skills" / "prune-tests" / "dados"
ARQ = DADOS / "familias-de-poda.csv"

SINONIMOS = {
    "passado": "Depende do passado", "historia": "Depende do passado", "removido": "Depende do passado",
    "404": "Depende do passado", "legado": "Depende do passado", "sumiu": "Depende do passado",
    "nada": "Depende do nada", "framework": "Depende do nada", "navegador": "Depende do nada",
    "mock": "Depende do nada", "tipo": "Depende do nada", "snapshot": "Depende do nada",
    "implementacao": "Depende da implementacao", "privado": "Depende da implementacao",
    "interno": "Depende da implementacao", "refactor": "Depende da implementacao",
    "ordem": "Depende da implementacao", "helper": "Depende da implementacao",
    "duplicado": "Teste duplicado", "duplicata": "Teste duplicado", "redundante": "Teste duplicado",
    "repetido": "Teste duplicado",
}


def _carrega() -> list[dict]:
    if not ARQ.is_file():
        raise SystemExit(f"FALHA: {ARQ} ausente. Rode install-all ou gere o acervo.")
    with ARQ.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _palavras(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def cmd_listar(_args) -> int:
    linhas = _carrega()
    inv: dict[str, list[str]] = {}
    for pt, canon in SINONIMOS.items():
        inv.setdefault(canon, []).append(pt)
    print(f"acervo em {ARQ.relative_to(RAIZ)} -- {len(linhas)} familias de teste podavel:")
    for r in linhas:
        termos = ", ".join(sorted(inv.get(r["familia"], []))[:3])
        print(f"  {r['familia']:<24} PT: {termos}")
    print("pergunta unica: o teste depende do comportamento intencional? NUNCA remove -- classifica.")
    return 0


def cmd_familia(args) -> int:
    termo = " ".join(args.termo).strip().lower()
    pals = _palavras(termo)
    canon = None
    for pt, c in SINONIMOS.items():
        if pt == termo or (_palavras(pt) and set(_palavras(pt)) <= pals):
            canon = c
            break
    if canon is None:
        print(f"sem correspondencia para '{termo}'. Veja 'listar' para as familias e termos PT.")
        return 1
    for r in [r for r in _carrega() if r["familia"] == canon]:
        print(f"[{r['familia']}]")
        print(f"  sinal:   {r['sinal']}")
        print(f"  por que: {r['por_que']}")
        print(f"  acao:    {r['acao']}")
        print(f"  origem:  {r['origem_arquivo']} :: {r['origem_secao']}")
    return 0


def cmd_busca(args) -> int:
    termo = " ".join(args.termo).strip().lower()
    pals = _palavras(termo)
    if not pals:
        print("sem termo de busca.")
        return 1
    achados = [r for r in _carrega()
               if pals & _palavras(f"{r['sinal']} {r['por_que']} {r['acao']}")]
    if not achados:
        print(f"sem correspondencia para '{termo}'.")
        return 1
    print(f"{len(achados)} familia(s) com '{termo}':")
    for r in achados:
        print(f"  [{r['familia']}] {r['acao']}")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Acervo das familias de teste podavel do prune-tests.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar", help="lista as familias e termos PT")
    pf = sub.add_parser("familia", help="detalha uma familia (termo PT)")
    pf.add_argument("termo", nargs="+")
    pb = sub.add_parser("busca", help="busca por palavra em sinal/por_que/acao")
    pb.add_argument("termo", nargs="+")
    args = ap.parse_args(argv)
    return {"listar": cmd_listar, "familia": cmd_familia, "busca": cmd_busca}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
