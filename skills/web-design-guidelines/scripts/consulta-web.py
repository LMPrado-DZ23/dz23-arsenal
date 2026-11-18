#!/usr/bin/env python3
"""consulta-web.py -- acervo de regras de interface web (Vercel Web Interface Guidelines, MIT).

O conhecimento vive DENTRO da skill (dados/regras-por-categoria.csv), nao numa URL remota: a skill
sabe por conta propria, sem WebFetch. Consulta por categoria em portugues, mapa fechado de sinonimos,
casando por palavra inteira; responde 'sem correspondencia' quando nao ha, nunca aproxima.

Uso:
  python scripts/consulta-web.py listar
  python scripts/consulta-web.py categoria acessibilidade
  python scripts/consulta-web.py busca aria
"""
import argparse
import csv
import pathlib
import re
import sys


def _acha_raiz() -> pathlib.Path:
    # RAIZ e o ancestral que contem skills/. Mesmo padrao de consulta-codebase/espec: funciona de
    # scripts/ no repo, da copia da skill e da instalacao em ~/.agents/skills.
    aqui = pathlib.Path(__file__).resolve()
    for alvo in (a.parent for a in [aqui.parent, aqui.parent.parent.parent]):
        if (alvo / "skills").is_dir():
            return alvo
    return aqui.parent.parent


RAIZ = _acha_raiz()
DADOS = RAIZ / "skills" / "web-design-guidelines" / "dados"
ARQ = DADOS / "regras-por-categoria.csv"

# Mapa fechado PT -> categoria canonica (ingles, como no acervo). Sinonimo so entra se aponta para
# uma categoria que existe no CSV; palavra inteira, nunca substring.
SINONIMOS = {
    "acessibilidade": "Accessibility", "a11y": "Accessibility", "aria": "Accessibility",
    "foco": "Focus States", "focus": "Focus States",
    "formulario": "Forms", "formularios": "Forms", "form": "Forms", "forms": "Forms",
    "animacao": "Animation", "animacoes": "Animation", "motion": "Animation", "transicao": "Animation",
    "tipografia": "Typography", "fonte": "Typography", "texto": "Typography",
    "conteudo": "Content Handling", "overflow": "Content Handling", "truncamento": "Content Handling",
    "imagens": "Images", "imagem": "Images", "img": "Images",
    "performance": "Performance", "lcp": "Performance", "cls": "Performance", "inp": "Performance",
    "navegacao": "Navigation & State", "rota": "Navigation & State", "url": "Navigation & State",
    "toque": "Touch & Interaction", "touch": "Touch & Interaction", "mobile": "Touch & Interaction",
    "layout": "Safe Areas & Layout", "safe-area": "Safe Areas & Layout", "notch": "Safe Areas & Layout",
    "dark": "Dark Mode & Theming", "dark-mode": "Dark Mode & Theming", "tema": "Dark Mode & Theming",
    "i18n": "Locale & i18n", "locale": "Locale & i18n", "traducao": "Locale & i18n",
    "hidratacao": "Hydration Safety", "hydration": "Hydration Safety", "ssr": "Hydration Safety",
    "hover": "Hover & Interactive States",
    "copy": "Content & Copy", "copywriting": "Content & Copy", "mensagem": "Content & Copy",
    "antipadrao": "Anti-patterns (flag these)", "antipadroes": "Anti-patterns (flag these)",
    "antipattern": "Anti-patterns (flag these)",
}


def _carrega() -> list[dict]:
    if not ARQ.is_file():
        raise SystemExit(f"FALHA: {ARQ} ausente. Rode install-all.ps1 -Force ou gere o acervo.")
    with ARQ.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _palavras(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def cmd_listar(_args) -> int:
    linhas = _carrega()
    cats: dict[str, int] = {}
    for r in linhas:
        cats[r["categoria"]] = cats.get(r["categoria"], 0) + 1
    print(f"acervo em {ARQ.relative_to(RAIZ)} -- {len(linhas)} regras em {len(cats)} categorias:")
    inv = {}
    for pt, canon in SINONIMOS.items():
        inv.setdefault(canon, []).append(pt)
    for cat, n in cats.items():
        termos = ", ".join(sorted(inv.get(cat, []))[:3])
        print(f"  {cat:<28} {n:>3} regras   PT: {termos}")
    return 0


def cmd_categoria(args) -> int:
    termo = " ".join(args.termo).strip().lower()
    pals = _palavras(termo)
    canon = None
    for pt, c in SINONIMOS.items():
        if pt in pals or pt == termo:
            canon = c
            break
    if canon is None:
        print(f"sem correspondencia para '{termo}'. Veja 'listar' para as categorias e termos PT.")
        return 0
    linhas = [r for r in _carrega() if r["categoria"] == canon]
    print(f"{canon} ({len(linhas)} regras) -- fonte: web-interface-guidelines/command.md (MIT):")
    for r in linhas:
        print(f"  - {r['regra']}")
    return 0


def cmd_busca(args) -> int:
    termo = " ".join(args.termo).strip().lower()
    pals = _palavras(termo)
    if not pals:
        print("sem termo de busca.")
        return 0
    achados = [r for r in _carrega() if pals & _palavras(r["regra"])]
    if not achados:
        print(f"sem correspondencia para '{termo}'.")
        return 0
    print(f"{len(achados)} regra(s) com '{termo}':")
    for r in achados:
        print(f"  [{r['categoria']}] {r['regra']}")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Acervo de regras de interface web (Vercel WIG, MIT).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar", help="lista categorias e termos PT")
    pc = sub.add_parser("categoria", help="regras de uma categoria (termo PT)")
    pc.add_argument("termo", nargs="+")
    pb = sub.add_parser("busca", help="busca por palavra no texto das regras")
    pb.add_argument("termo", nargs="+")
    args = ap.parse_args(argv)
    return {"listar": cmd_listar, "categoria": cmd_categoria, "busca": cmd_busca}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
