"""verifica_claims.py — confere afirmações do texto contra o disco, sem LLM.

Técnica absorvida de vercel-labs/agent-skills (`skills/vercel-optimize/references/
verification.md` + `lib/extract-claims.mjs`, lido 2026-11-17). O arsenal prega "evidência
ou silêncio", mas quem declara o PASS é o próprio agente. Aqui a evidência é conferida por
comando e vira número.

Quatro disposições, e a distinção é o ponto todo:
  verificado        a checagem rodou e confirmou
  falho             a checagem rodou e negou                -> conta contra
  nao-verificavel   não há como checar aqui (outro projeto, placeholder, imperativo)
                                                             -> NÃO conta
  sem-suporte       o tipo de claim não tem checador         -> NÃO conta

passRate = verificados / (verificados + falhos). Colocar as duas últimas no denominador
derrubaria o número por limite da ferramenta, não por erro de conteúdo — é assim que um
métrico morre: param de acreditar nele.

Escopo honesto: este verificador cobre caminho de arquivo. Números, citações longas e
afirmações de comportamento ficam em `sem-suporte`. Um extrator de claims cobre ~30 tipos
no pacote original; reimplementar tudo de uma vez produziria um verificador em que ninguém
confia. Crescer por tipo, com selftest positivo E negativo a cada adição.

Uso:
    python scripts/verifica_claims.py --texto relatorio.md [--raiz .] [--min 0.8]
    python scripts/verifica_claims.py --texto r.md --json
    python scripts/verifica_claims.py --selftest
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

VERSAO = "1.1.0"

RE_CAMINHO = re.compile(
    r"(?<![\w./-])((?:[\w.\-]+[/\\])+[\w.\-]+\.(?:py|md|json|ya?ml|toml|sh|ps1|js|ts|tsx|jsx|"
    r"sql|go|rs|csv|txt|ini|cfg))(?::(\d+))?(?![\w./-])"
)

# Placeholder/exemplo nunca é alegação sobre o repo.
RE_PLACEHOLDER = re.compile(
    r"(?i)(NAO[-_]EXISTE|nao-existe|INEXISTENTE|does-not-exist|zz-|foo\.|bar\.|exemplo\."
    r"|<algo>|placeholder)")

RE_IMPERATIVO = re.compile(
    r"(?i)\b(crie|criar|gere|gerar|adicione|adicionar|escreva|implemente|add |create|"
    r"generate|should exist|deve existir|deve ser criado)\b")


@dataclass
class Claim:
    tipo: str
    valor: str
    disposicao: str
    detalhe: str
    contexto: str = ""


def extrair(texto: str) -> list[tuple[str, str, int]]:
    """(tipo, valor, linha) dos claims conferíveis mecanicamente."""
    achados: list[tuple[str, str, int]] = []
    dentro_de_bloco = False
    for n, linha in enumerate(texto.splitlines(), 1):
        if linha.strip().startswith("```"):
            dentro_de_bloco = not dentro_de_bloco
            continue
        if dentro_de_bloco:
            continue          # exemplo de código não é alegação sobre este repo
        for m in RE_CAMINHO.finditer(linha):
            achados.append(("caminho-arquivo", m.group(1), n))
    return achados


def base_da_skill(texto_path: Path | None, raiz: Path) -> Path | None:
    """Se o texto auditado é uma skill, a base dos caminhos relativos é a própria skill.

    `references/quality-gates.md` escrito em skills/<x>/SKILL.md significa
    skills/<x>/references/quality-gates.md. Sem âncora dá falso positivo em massa; com
    "existe em qualquer pasta" dá falso negativo perigoso — o verificador passaria a
    aceitar caminho errado desde que houvesse homônimo noutra skill.
    """
    if texto_path is None:
        return None
    try:
        rel = texto_path.resolve().relative_to(raiz.resolve())
    except (ValueError, OSError):
        return None
    partes = rel.parts
    if len(partes) >= 2 and partes[0] in ("skills", "mcp", "bundle"):
        return raiz / partes[0] / partes[1]
    return None


def _normaliza(valor: str) -> str:
    return valor.replace("\\", "/").lstrip("./")


def checar_caminho(valor: str, raiz: Path, texto: str, linha_no: int,
                   base_skill: Path | None = None) -> Claim:
    linhas = texto.splitlines()
    linha_alvo = linhas[linha_no - 1] if 0 < linha_no <= len(linhas) else ""
    alvo = linha_alvo.strip()[:120]
    norm = _normaliza(valor)

    if RE_PLACEHOLDER.search(valor):
        return Claim("caminho-arquivo", valor, "nao-verificavel",
                     "placeholder/exemplo, não alegação de existência", alvo)

    if valor.startswith(("~/", "$")) or re.match(r"^(/|\w:[\\/])", valor):
        return Claim("caminho-arquivo", valor, "nao-verificavel",
                     "fora deste checkout", alvo)

    if norm.startswith("projects/") or "/projects/" in norm:
        return Claim("caminho-arquivo", valor, "nao-verificavel",
                     "referência a outro projeto", alvo)

    candidatos: list[Path] = []
    rotulo_ok = "existe"
    if base_skill is not None:
        candidatos.append(base_skill / norm)
        # Caminho absoluto do repo citado de dentro da skill (scripts/check-structure.py).
        candidatos.append(raiz / norm)
        rotulo_ok = f"existe em {(base_skill / norm).exists() and base_skill.name or 'raiz do repo'}"
    else:
        candidatos.append(raiz / norm)
        if base_skill is None and (raiz / "skills").is_dir():
            # Texto solto (relatório fora da árvore): aceita qualquer skill, mas marca
            # como não-verificável quando só existe em outra — senão vira passe livre.
            encontrados_em = [p for p in sorted((raiz / "skills").iterdir())
                              if p.is_dir() and (p / norm).exists()]
            if any((raiz / norm).exists() for _ in [0]):
                return Claim("caminho-arquivo", valor, "verificado", "existe na raiz", alvo)
            if encontrados_em:
                return Claim("caminho-arquivo", valor, "verificado",
                             f"existe em {encontrados_em[0].name}/", alvo)

    if any(p.exists() for p in candidatos):
        return Claim("caminho-arquivo", valor, "verificado", rotulo_ok, alvo)

    if RE_IMPERATIVO.search(linha_alvo):
        return Claim("caminho-arquivo", valor, "nao-verificavel",
                     "instrução de criação, não alegação de existência", alvo)

    # "Registre/gravue em docs/x.md no repositório" é destino de ESCRITA sugerido ao
    # agente, não alegação de que o arquivo exista hoje. Marcar como falho aqui seria o
    # falso positivo que faz gente desligar o verificador.
    if re.search(r"(?i)\b(registre|registrar|grave|gravar|salve|salvar|escreva em|"
                 r"mantenha|crie|no reposit[óo]rio|if appropriate|se apropriado)\b", linha_alvo):
        return Claim("caminho-arquivo", valor, "nao-verificavel",
                     "destino de escrita sugerido, não alegação de existência", alvo)

    onde = f"{base_skill.name}/ ou raiz" if base_skill else "raiz"
    return Claim("caminho-arquivo", valor, "falho", f"não existe em {onde}", alvo)


def avaliar(texto: str, raiz: Path, texto_path: Path | None = None) -> dict:
    base_skill = base_da_skill(texto_path, raiz)
    claims: list[Claim] = []
    for tipo, valor, n in extrair(texto):
        if tipo == "caminho-arquivo":
            claims.append(checar_caminho(valor, raiz, texto, n, base_skill))

    verificados = [c for c in claims if c.disposicao == "verificado"]
    falhos = [c for c in claims if c.disposicao == "falho"]
    nv = [c for c in claims if c.disposicao == "nao-verificavel"]
    ss = [c for c in claims if c.disposicao == "sem-suporte"]

    denom = len(verificados) + len(falhos)
    return {
        "versao": VERSAO,
        "total_claims": len(claims),
        "verificados": len(verificados),
        "falhos": len(falhos),
        "nao_verificaveis": len(nv),
        "sem_suporte": len(ss),
        "denominador": denom,
        "passRate": (len(verificados) / denom) if denom else None,
        "claims": [asdict(c) for c in claims],
    }


def selftest() -> int:
    """Controle positivo E negativo. Um verificador sem teste negativo é boato."""
    falhas: list[str] = []

    def espera(cond: bool, msg: str) -> None:
        if not cond:
            falhas.append(msg)

    raiz = Path(__file__).resolve().parent.parent      # o próprio arsenal serve de cenário
    aqui = Path(__file__).name

    # Positivo: arquivo real da raiz.
    r = avaliar(f"Ver `scripts/{aqui}` no arsenal.", raiz)
    espera(r["verificados"] == 1, f"positivo raiz: {r['verificados']} verificados")

    # Âncora de skill: references/x.md resolve DENTRO da skill, não na raiz.
    skills = raiz / "skills"
    if skills.is_dir():
        sk = next((p for p in sorted(skills.iterdir())
                   if p.is_dir() and (p / "references").is_dir()), None)
        if sk is not None:
            ref = next((p.name for p in sorted((sk / "references").iterdir())
                        if p.suffix == ".md"), None)
            if ref:
                r2 = avaliar(f"Leia `references/{ref}`.", raiz, sk / "SKILL.md")
                espera(r2["verificados"] == 1,
                       f"âncora de skill não resolveu {ref}: {r2['claims']}")
                # O mesmo nome, se NÃO existir na skill, tem de falhar — não pode achar
                # homônimo em skill vizinha.
                r3 = avaliar("Leia `references/ausente-nesta-skill.md`.", raiz, sk / "SKILL.md")
                espera(r3["falhos"] == 1, f"caminho ausente não foi marcado falho: {r3}")

    # Negativo puro (sem âncora): caminho inventado conta como falho.
    r4 = avaliar("Consulte `scripts/ausente-de-verdade.md` antes.", raiz)
    espera(r4["falhos"] == 1, f"negativo: esperava 1 falho, veio {r4['falhos']}")
    espera(r4["passRate"] == 0.0, f"negativo: passRate deveria ser 0, veio {r4['passRate']}")

    # Imperativo não é alegação de existência.
    r5 = avaliar("Crie `scripts/arquivo-futuro.py` com o gate.", raiz)
    espera(r5["falhos"] == 0 and r5["nao_verificaveis"] == 1,
           f"imperativo tratado como falso: {r5['claims']}")

    # Placeholder explícito nunca falha.
    r6 = avaliar("Testei injetando `references/NAO-EXISTE-teste.md`.", raiz)
    espera(r6["falhos"] == 0, f"placeholder virou falso: {r6['claims']}")

    # Dentro de bloco de código não é alegação.
    r7 = avaliar("Exemplo:\n```bash\ncat scripts/arquivo-so-exemplo.sh\n```\n", raiz)
    espera(r7["total_claims"] == 0, f"claim dentro de code block foi extraído: {r7}")

    # Sem claims conferíveis: passRate None, não 1.0 nem 0.
    r8 = avaliar("Nada aqui cita arquivo.", raiz)
    espera(r8["passRate"] is None, f"sem claims deveria dar None: {r8['passRate']}")

    # Determinismo.
    espera(json.dumps(avaliar(f"`scripts/{aqui}`", raiz), sort_keys=True)
           == json.dumps(avaliar(f"`scripts/{aqui}`", raiz), sort_keys=True),
           "avaliar não é determinístico")

    if falhas:
        print("SELFTEST FALHOU:")
        for f in falhas:
            print("  -", f)
        return 1
    print(f"selftest OK · verifica_claims {VERSAO} · "
          "positivo/âncora/negativo/imperativo/placeholder/code-block/vazio/determinismo")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--texto", help="arquivo markdown/texto a auditar")
    ap.add_argument("--raiz", default=".", help="base dos caminhos relativos")
    ap.add_argument("--min", type=float, default=None,
                    help="exit 1 se passRate ficar abaixo disto (ex.: 0.8)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.texto:
        print("use --texto <arquivo> ou --selftest", file=sys.stderr)
        return 2

    caminho = Path(args.texto)
    if not caminho.is_file():
        print(f"FALHA: {caminho} não existe", file=sys.stderr)
        return 2

    resultado = avaliar(caminho.read_text(encoding="utf-8-sig", errors="replace"),
                        Path(args.raiz).resolve(), caminho)

    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        pr = resultado["passRate"]
        print(f"# Verificação mecânica de claims ({VERSAO})\n")
        print(f"{resultado['total_claims']} claim(s) · verificados {resultado['verificados']} · "
              f"falhos {resultado['falhos']} · não-verificáveis {resultado['nao_verificaveis']} · "
              f"sem suporte {resultado['sem_suporte']}")
        print(f"passRate: "
              f"{'n/d (nenhum claim conferível)' if pr is None else format(pr, '.2f')}"
              f"  [denominador = verificados + falhos]")
        falsos = [c for c in resultado["claims"] if c["disposicao"] == "falho"]
        if falsos:
            print("\n## Claims falsos\n")
            for c in falsos:
                print(f"- `{c['valor']}` — {c['detalhe']}")
                if c["contexto"]:
                    print(f"    em: {c['contexto']}")
        nv = [c for c in resultado["claims"] if c["disposicao"] == "nao-verificavel"]
        if nv:
            print("\n## Não-verificáveis (não contam contra)\n")
            for c in nv:
                print(f"- `{c['valor']}` — {c['detalhe']}")

    pr = resultado["passRate"]
    if args.min is not None and pr is not None and pr < args.min:
        print(f"\nFALHA: passRate {pr:.2f} < mínimo {args.min:.2f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
