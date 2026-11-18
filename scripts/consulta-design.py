"""consulta-design.py -- acessa o acervo de design incorporado em dados-design/.

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


def _acha_dados_design() -> pathlib.Path:
    """Resolvido por conteudo, na ordem: acervo local da skill -> repositorio localizado.

    O acervo de design sao ~3 MB de CSV/JSON com licenca ISC. Duplicar isso para dentro da skill incha
    o repositorio e o tarball; deixar so na raiz faz a habilidade instalada em ~/.agents/skills/ apontar
    para um arquivo que nao existe la -- foi o defeito medido nesta sessao nos tres consultores. Para os
    acervos pequenos (backend, performance) a solucao foi levar `dados/` junto. Aqui, o tamanho pede
    outra saida: localizar o checkout pelo mesmo mecanismo que os validadores das skills ja usam
    (`_achar_arsenal`, via ponteiro `.dz23-arsenal` ou env DZ23_ARSENAL), sem duplicar byte algum.

    A mensagem de erro cita as duas origens possiveis, porque 'ausente' sem dizer onde procurar manda o
    usuario cavar codigo.
    """
    aqui = pathlib.Path(__file__).resolve().parent.parent / "dados" / "ui-ux-pro-max-data"
    if (aqui / "styles.csv").is_file():
        return aqui
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        from _achar_arsenal import localizar_arsenal   # type: ignore
        repo = localizar_arsenal(pathlib.Path(__file__).resolve().parent)
    except Exception:                                   # modulo ausente ou ponteiro invalido
        repo = None
    if repo:
        candidato = pathlib.Path(repo) / "dados-design" / "ui-ux-pro-max-data"
        if (candidato / "styles.csv").is_file():
            return candidato
    return RAIZ / "dados-design" / "ui-ux-pro-max-data"


DADOS = _acha_dados_design()


def _ler(nome: str) -> list[dict]:
    p = DADOS / nome
    if not p.is_file():
        raise SystemExit(f"FALHA: {p.relative_to(RAIZ)} ausente. O acervo em dados-design/ nao foi "
                         f"instalado? Ver dados-design/VENDOR.md.")
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


# Mapas POR DOMINIO, nao um global. O SINONIMOS acima e compartilhado por estilo/produto/ux/cores;
# reusa-lo para grafico/motion criaria colisao real -- "entrada" ja significa "data entry" em UX.
# Cada valor abaixo foi copiado de um `Data Type`/`Category` QUE EXISTE na tabela (listados por
# `listar`). A primeira versao desta lista tinha 15 termos apontando para nomes plausiveis e
# inexistentes ("button feedback", "budget vs actual", "entrance animation") -- escritos de memoria,
# nao do catalogo. Um sinonimo morto e pior que ausencia de sinonimo: o usuario acredita que a ponte
# existe. A checagem em prova-consulta-design.py agora executa todas as chaves dos tres mapas.
SINONIMOS_GRAFICO = {
    "tendencia": "Trend Over Time", "evolucao": "Trend Over Time",
    "serie temporal": "Time-Series Forecast", "previsao": "Time-Series Forecast",
    "crescimento": "Trend Over Time", "tempo": "Trend Over Time",
    "comparacao": "Compare Categories", "comparar": "Compare Categories",
    "categorias": "Compare Categories", "ranking": "Compare Categories",
    "multiplas variaveis": "Multi-Variable Comparison",
    "proporcao": "Proportional / Percentage", "percentual": "Proportional / Percentage",
    "parte de um todo": "Part-to-Whole", "fatia": "Part-to-Whole",
    "distribuicao": "Distribution / Statistical",
    "estatistica": "Distribution / Statistical",
    "correlacao": "Correlation / Distribution",
    "geografico": "Geographic Data", "mapa": "Geographic Data",
    "funil": "Funnel / Flow", "fluxo": "Flow / Process Data",
    "processo": "Process Mining", "acumulativo": "Cumulative Changes",
    "anomalia": "Anomaly Detection", "intensidade": "Heatmap / Intensity",
    "hierarquia": "Hierarchical / Nested Data",
    "arvore": "Hierarchical / Nested Data",
    "treemap": "Hierarchical Proportional",
    "meta": "Performance vs Target", "desempenho alvo": "Performance vs Target",
    "alvo": "Performance vs Target",
    "tempo real": "Real-Time Streaming", "streaming": "Real-Time Streaming",
    "relacionamento": "Relationship / Connection Data",
    "grafo": "Relationship / Connection Data",
    "causa raiz": "Root Cause Analysis",
    "sentimento": "Sentiment / Emotion", "humor": "Sentiment / Emotion",
    "acoes": "Stock / Trading OHLC", "financas": "Stock / Trading OHLC",
    "tridimensional": "3D Spatial Data", "3d": "3D Spatial Data",
}

SINONIMOS_MOTION = {
    "passar o mouse": "Hover Micro-interaction", "hover": "Hover Micro-interaction",
    "botao": "Hover Micro-interaction", "clique": "Hover Micro-interaction",
    "carrossel": "Carousel / Auto-Rotation", "automático": "Carousel / Auto-Rotation",
    "automatico": "Carousel / Auto-Rotation",
    "transicao de pagina": "Page Transition", "pagina": "Page Transition",
    "navegacao de pagina": "Page Transition",
    "carregamento": "Loading / Skeleton", "skeleton": "Loading / Skeleton",
    "spinner": "Loading / Skeleton",
    "parallax": "Parallax Scroll", "profundidade": "Parallax Scroll",
    "revelar": "Scroll Reveal", "ao rolar": "Scroll Reveal",
    "rolagem": "Scroll Reveal", "scroll": "Scroll Reveal",
    "lista": "Stagger List", "escalonado": "Stagger List",
    "entrada em cascata": "Stagger List",
}


def cmd_grafico(args) -> int:
    """Tipo de grafico adequado ao tipo de dado -- 25 registros."""
    linhas = _ler("charts.csv")
    termo = SINONIMOS_GRAFICO.get(_norma(args.termo), args.termo)
    achados = [(max(_melhor(termo, str(r.get("Data Type", ""))),
                    _melhor(termo, " ".join(str(v) for v in r.values()))), r)
               for r in linhas]
    achados = [x for x in achados if x[0] > 0]
    achados.sort(key=lambda x: -x[0])
    if not achados:
        tipos = sorted({str(r.get("Data Type", "")).strip()[:40] for r in linhas})
        print(f"sem correspondencia para '{args.termo}' entre os {len(linhas)} tipos de dado "
              f"registrados. Nao vou aproximar.")
        print("  valores: " + "; ".join(tipos[:10]))
        return 1
    for _, r in achados[: args.top]:
        print(f"[{r.get('No')}] {r.get('Data Type')}")
        for campo in ("Best Chart Type", "Secondary Options", "Keywords", "Accessibility Notes"):
            v = str(r.get(campo, "")).strip()
            if v:
                print(f"    {campo}: {v[:260]}")
        print()
    return 0


def cmd_motion(args) -> int:
    """Padrao de animacao por gatilho e intensidade -- 17 registros."""
    linhas = _ler("motion.csv")
    termo = SINONIMOS_MOTION.get(_norma(args.termo), args.termo)
    achados = [(max(_melhor(termo, str(r.get("Category", ""))),
                    _melhor(termo, " ".join(str(v) for v in r.values()))), r)
               for r in linhas]
    achados = [x for x in achados if x[0] > 0]
    achados.sort(key=lambda x: -x[0])
    if not achados:
        cats = sorted({str(r.get("Category", "")).strip()[:40] for r in linhas})
        print(f"sem correspondencia para '{args.termo}' entre as {len(linhas)} categorias de "
              f"motion. Nao vou aproximar.")
        print("  valores: " + "; ".join(cats[:10]))
        return 1
    for _, r in achados[: args.top]:
        print(f"[{r.get('No')}] {r.get('Category')} ({r.get('Intensity Tier')})")
        for campo in ("Trigger", "Duration", "Easing", "Keywords", "CSS/JS Hint", "Framework"):
            v = str(r.get(campo, "")).strip()
            if v:
                print(f"    {campo}: {v[:240]}")
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
    p = sub.add_parser("grafico", help="tipo de grafico adequado ao tipo de dado")
    p.add_argument("termo"); comum(p); p.set_defaults(fn=cmd_grafico)
    p = sub.add_parser("motion", help="padrao de animacao por gatilho e intensidade")
    p.add_argument("termo"); comum(p); p.set_defaults(fn=cmd_motion)
    p = sub.add_parser("listar", help="o que existe no acervo")
    p.set_defaults(fn=cmd_listar)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
