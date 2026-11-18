"""consulta-design.py -- acessa o acervo de design incorporado em vendor/.

Por que existe: copiar 3 MB de CSV sem meio de consultar produz referencia morta -- foi exatamente a
classe de defeito que a rodada 47 achou (guia correto, versionado e invisivel ao agente). Dado
estruturado so vira decisao de projeto quando alguem consegue filtra-lo em uma chamada.

Todas as saidas citam a linha de origem (`No` da planilha), para que uma recomendacao possa ser
rastreada ate o registro -- mesma disciplina de evidencia do resto do arsenal. Nada aqui inventa
estilo: se o filtro nao casa, diz que nao ha correspondencia em vez de chutar.

Uso:
  python scripts/consulta-design.py estilo "glassmorphism"
  python scripts/consulta-design.py produto "fintech"
  python scripts/consulta-design.py ux formul--ario --severidade alta
  python scripts/consulta-design.py fontes --pesquisa display
  python scripts/consulta-design.py cores saude
  python scripts/consulta-design.py listar
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DADOS = RAIZ / "vendor" / "ui-ux-pro-max-data"


def _ler(nome: str) -> list[dict]:
    p = DADOS / nome
    if not p.is_file():
        raise SystemExit(f"FALHA: {p.relative_to(RAIZ)} ausente. O acervo em vendor/ nao foi "
                         f"instalado? Ver vendor/VENDOR.md.")
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _norma(s: str) -> str:
    s = s.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                 ("ã", "a"), ("õ", "o"), ("ç", "c"), ("&", " e ")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


# O acervo esta em ingles; as skills e o usuario falam portugues. Sem ponte, `ux formulario` retorna
# zero contra uma planilha que tem 12 categorias 'Forms' -- e o agente concluiria que nao ha orientacao
# sobre o assunto, quando o que falta e vocabulario. Nao e traducao generica: e mapa fechado das
# palavras que aparecem nos dados, para nao inventar correspondencia.
SINONIMOS = {
    "formulario": "form", "formularios": "forms", "form": "form", "entrada": "data entry",
    "acessibilidade": "accessibility", "animacao": "animation", "performance": "performance",
    "desempenho": "performance", "navegacao": "navigation", "feedback": "feedback",
    "conteudo": "content", "layout": "layout", "responsivo": "responsive",
    "movel": "mobile", "celular": "mobile", "onboarding": "onboarding", "dados": "data entry",
    "saude": "health", "financas": "fintech", "financeiro": "fintech", "banco": "banking",
    "educacao": "education", "varejo": "e-commerce", "loja": "e-commerce",
    "game": "gaming", "jogo": "gaming", "social": "social", "musica": "music",
    "viagem": "travel", "restaurante": "restaurant", "imobiliario": "real estate",
    "transparencia": "glassmorphism", "vidro": "glassmorphism", "minimalista": "minimalism",
    "retrono": "retro", "futurista": "cyberpunk", "brutalista": "brutalism",
    "corporativo": "corporate", "editorial": "editorial", "playful": "playful",
    "diversao": "playful", "industrial": "industrial", "organico": "organic",
}


def _expande(termo: str) -> list[str]:
    """Termos a tentar, na ordem: original e sinonimo mapeado.

    NAO remover sufixo 's' as cegas. A versao anterior fazia isso e `ux formulario` passou a casar
    com 'Animation :: Transform Per**for**mance', porque 'forma' e substring de 'performance' e o
    escore de substring vale 25 -- suficiente para aparecer como resposta. Um acervo de design que
    responde a pergunta certa com a linha errada e pior que um acervo ausente: o agente confia.
    Só há ponte quando a palavra inteira esta no mapa fechado acima.
    """
    t = _norma(termo)
    saida = [termo]
    if t in SINONIMOS:
        saida.append(SINONIMOS[t])
    return saida


def _melhor(agulha: str, texto: str) -> int:
    return max((_escore(a, texto) for a in _expande(agulha)), default=0)


def _escore(agulha: str, texto: str) -> int:
    """Pontuacao deterministica: igualdade > prefixo > palavra inteira.

    Nao ha escore de substring solta, e isso e deliberado. A versao anterior dava 25 pontos quando a
    agulha aparecia em qualquer ponto do texto, o que fez `ux formulario` responder com
    'Animation :: Duration Timing' -- porque 'for' esta dentro de 'performance' na descricao. Um
    acervo que responde a pergunta certa com a linha errada engana pior do que um acervo ausente,
    ja que o agente passa a confiar no resultado. Casar por palavra inteira resolve o caso legitimo
    ('forms' acha 'Forms') e elimina o falso positivo.
    """
    a, t = _norma(agulha), _norma(texto)
    if not t or not a:
        return 0
    if a == t:
        return 100
    if t.startswith(a):
        return 70
    if re.search(rf"\b{re.escape(a)}\b", t):
        return 50
    termos = [w for w in a.split() if len(w) > 3]
    hits = sum(1 for w in termos if re.search(rf"\b{re.escape(w)}\b", t))
    return 12 * hits if hits else 0


def cmd_estilo(args) -> int:
    linhas = _ler("styles.csv")
    ranqueados = []
    for r in linhas:
        blob = " ".join(str(r.get(k, "")) for k in
                        ("Style Category", "Keywords", "Type", "Best For"))
        e = _melhor(args.termo, str(r.get("Style Category", ""))) * 2 + _melhor(args.termo, blob)
        if e > 0:
            ranqueados.append((e, r))
    ranqueados.sort(key=lambda x: -x[0])
    if not ranqueados:
        print(f"sem estilo correspondendo a '{args.termo}' nas {len(linhas)} categorias "
              f"registradas. Use `listar` para ver as existentes -- nao vou sugerir parecido.")
        return 1
    for _, r in ranqueados[: args.top]:
        print(f"[{r.get('No')}] {r.get('Style Category')}  ({r.get('Type')})")
        for campo in ("Keywords", "Primary Colors", "Secondary Colors", "Effects & Animation",
                      "Best For", "Performance", "Accessibility"):
            v = str(r.get(campo, "")).strip()
            if v:
                print(f"    {campo}: {v[:300]}")
        print()
    return 0


def cmd_produto(args) -> int:
    linhas = _ler("ui-reasoning.csv")
    achados = []
    for r in linhas:
        e = max(_melhor(args.termo, str(r.get("UI_Category", ""))),
                _melhor(args.termo, " ".join(str(v) for v in r.values())))
        if e > 0:
            achados.append((e, r))
    achados.sort(key=lambda x: -x[0])
    if not achados:
        print(f"nenhum perfil de produto casando com '{args.termo}'.")
        return 1
    for _, r in achados[: args.top]:
        print(f"[{r.get('No')}] {r.get('UI_Category')}")
        for campo in ("Recommended_Pattern", "Style_Priority", "Color_Mood", "Typography_Mood",
                      "Key_Effects", "Anti_Pattern"):
            v = str(r.get(campo, "")).strip()
            if v:
                print(f"    {campo}: {v[:260]}")
        print()
    return 0


def cmd_ux(args) -> int:
    linhas = _ler("ux-guidelines.csv")
    out = []
    for r in linhas:
        blob = " ".join(str(r.get(k, "")) for k in ("Category", "Issue", "Description"))
        if args.filtro and _melhor(args.filtro, blob) == 0:
            continue
        if args.severidade and _norma(str(r.get("Severity", ""))) != _norma(args.severidade):
            continue
        out.append(r)
    if not out:
        print(f"zero diretrizes com esse filtro ({len(linhas)} no total). Afrouxe o termo.")
        return 1
    for r in out[: args.top]:
        print(f"[{r.get('No')}] {r.get('Category')} :: {r.get('Issue')} "
              f"({r.get('Platform')}, severidade {r.get('Severity')})")
        do = str(r.get("Do", "")).strip()
        nao = str(r.get("Don't", "") or r.get("Dont", "")).strip()
        if do:
            print(f"    FAZER: {do[:260]}")
        if nao:
            print(f"    EVITAR: {nao[:260]}")
        print()
    print(f"-- {len(out)} de {len(linhas)} diretrizes")
    return 0


def cmd_fontes(args) -> int:
    lic = DADOS / "google-font-licenses.json"
    if not lic.is_file():
        print("FALHA: catalogo de licencas de fonte ausente")
        return 1
    dados = json.loads(lic.read_text(encoding="utf-8"))
    fams = dados.get("families", [])
    out = [f for f in fams
           if not args.pesquisa or _escore(args.pesquisa, str(f.get("name", ""))) > 0]
    print(f"{len(out)} familias casando com o filtro "
          f"(de {len(fams)} registradas; licenca por familia, OFL na maioria)")
    for f in out[: args.top]:
        designers = ", ".join(f.get("designer") or []) if isinstance(f.get("designer"), list) \
            else str(f.get("designer", ""))
        print(f"  {f.get('name'):<34} {str(f.get('license','?')):<10} {designers[:40]}")
    if out:
        print("\nAntes de embutir qualquer fonte no build, confirme a licenca dela AQUI -- "
              "o catalogo existe para isso. Fonte OFL permite uso e redistribuicao; a lista acima "
              "ja separa as que tem licenca diferente.")
    return 0


def cmd_cores(args) -> int:
    p = DADOS / "colors.csv"
    if not p.is_file():
        print("FALHA: colors.csv ausente")
        return 1
    linhas = _ler("colors.csv")
    out = [(max(_melhor(args.termo, str(r.get("Product Type", ""))),
                _melhor(args.termo, " ".join(str(v) for v in r.values()))), r) for r in linhas]
    out = [x for x in out if x[0] > 0]
    out.sort(key=lambda x: -x[0])
    if not out:
        print(f"sem paleta registrada para '{args.termo}' em {len(linhas)} tipos de produto.")
        return 1
    for _, r in out[: args.top]:
        print(f"[{r.get('No')}] {r.get('Product Type')}")
        for k, v in r.items():
            if k not in ("No", "Product Type") and str(v).strip():
                print(f"    {k}: {str(v)[:200]}")
        print()
    return 0


def cmd_listar(_args) -> int:
    print(f"acervo em {DADOS.relative_to(RAIZ)}:")
    for p in sorted(DADOS.glob("*.csv")):
        with p.open(encoding="utf-8-sig", newline="") as fh:
            n = sum(1 for _ in fh) - 1
        print(f"  {p.name:<34}{n:>6} registros")
    for p in sorted(DADOS.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            n = len(d) if isinstance(d, list) else len(d.get("families", d.get("records", d)))
        except ValueError:
            n = 0
        print(f"  {p.name:<34}{n:>6} itens")
    print("\ncomandos: estilo | produto | ux | cores | fontes | listar")
    return 0


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def comum(p):
        p.add_argument("--top", type=int, default=3)

    p = sub.add_parser("estilo", help="categoria de estilo visual")
    p.add_argument("termo"); comum(p); p.set_defaults(fn=cmd_estilo)
    p = sub.add_parser("produto", help="perfil de recomendacao por tipo de produto")
    p.add_argument("termo"); comum(p); p.set_defaults(fn=cmd_produto)
    p = sub.add_parser("ux", help="diretriz de UX com fazer/evitar")
    p.add_argument("filtro", nargs="?"); p.add_argument("--severidade")
    comum(p); p.set_defaults(fn=cmd_ux)
    p = sub.add_parser("cores", help="paleta por tipo de produto")
    p.add_argument("termo"); comum(p); p.set_defaults(fn=cmd_cores)
    p = sub.add_parser("fontes", help="familias de fonte e sua licenca")
    p.add_argument("--pesquisa"); comum(p); p.set_defaults(fn=cmd_fontes)
    p = sub.add_parser("listar", help="o que existe no acervo")
    p.set_defaults(fn=cmd_listar)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
