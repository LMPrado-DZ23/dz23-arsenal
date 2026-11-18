#!/usr/bin/env python3
"""consulta-untangle.py -- acervo das 4 familias de defeito estrutural do untangle-codebase.

O conhecimento vive DENTRO da skill (dados/familias-de-defeito.csv), tabulado da propria taxonomia
(references/defect-taxonomy.md). Consulta por familia em portugues, mapa fechado de sinonimos,
casando por palavra inteira; responde 'sem correspondencia' quando nao ha, nunca aproxima.

Uso:
  python scripts/consulta-untangle.py listar
  python scripts/consulta-untangle.py familia elo-oculto
  python scripts/consulta-untangle.py busca wrapper
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
DADOS = RAIZ / "skills" / "untangle-codebase" / "dados"
ARQ = DADOS / "familias-de-defeito.csv"

# Mapa fechado PT -> familia canonica (exatamente como no CSV). Palavra inteira, nunca substring.
SINONIMOS = {
    "oculto": "Elo oculto", "elo oculto": "Elo oculto", "implicito": "Elo oculto",
    "copia": "Elo oculto", "duplicacao": "Elo oculto", "global": "Elo oculto",
    "desnecessario": "Elo desnecessario", "elo desnecessario": "Elo desnecessario",
    "acoplamento": "Elo desnecessario", "dependencia": "Elo desnecessario", "raso": "Elo desnecessario",
    "sobra": "Sobra", "morto": "Sobra", "wrapper": "Sobra", "yagni": "Sobra",
    "especulativo": "Sobra", "extensao": "Sobra",
    "especial": "Caso especial", "caso especial": "Caso especial", "excecao": "Caso especial",
    "retry": "Caso especial", "sleep": "Caso especial", "flag": "Caso especial",
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
    print(f"acervo em {ARQ.relative_to(RAIZ)} -- {len(linhas)} familias de defeito estrutural:")
    for r in linhas:
        termos = ", ".join(sorted(inv.get(r["familia"], []))[:3])
        print(f"  {r['familia']:<20} PT: {termos}")
    print("teste unificador: estas pecas deveriam mudar juntas?")
    return 0


def cmd_familia(args) -> int:
    termo = " ".join(args.termo).strip().lower()
    pals = _palavras(termo)
    canon = None
    for pt, c in SINONIMOS.items():
        if pt == termo or set(_palavras(pt)) <= pals and _palavras(pt):
            canon = c
            break
    if canon is None:
        print(f"sem correspondencia para '{termo}'. Veja 'listar' para as familias e termos PT.")
        return 1
    linhas = [r for r in _carrega() if r["familia"] == canon]
    for r in linhas:
        print(f"[{r['familia']}]")
        print(f"  sinal:    {r['sinal']}")
        print(f"  principio: {r['principio']}")
        print(f"  correcao: {r['correcao']}")
        print(f"  origem:   {r['origem_arquivo']} :: {r['origem_secao']}")
    return 0


def cmd_busca(args) -> int:
    termo = " ".join(args.termo).strip().lower()
    pals = _palavras(termo)
    if not pals:
        print("sem termo de busca.")
        return 1
    achados = [r for r in _carrega()
               if pals & _palavras(f"{r['sinal']} {r['principio']} {r['correcao']}")]
    if not achados:
        print(f"sem correspondencia para '{termo}'.")
        return 1
    print(f"{len(achados)} familia(s) com '{termo}':")
    for r in achados:
        print(f"  [{r['familia']}] {r['correcao']}")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Acervo das 4 familias de defeito do untangle-codebase.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar", help="lista as familias e termos PT")
    pf = sub.add_parser("familia", help="detalha uma familia (termo PT)")
    pf.add_argument("termo", nargs="+")
    pb = sub.add_parser("busca", help="busca por palavra em sinal/principio/correcao")
    pb.add_argument("termo", nargs="+")
    args = ap.parse_args(argv)
    return {"listar": cmd_listar, "familia": cmd_familia, "busca": cmd_busca}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
