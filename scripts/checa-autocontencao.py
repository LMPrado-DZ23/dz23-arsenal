"""checa-autocontencao.py -- toda skill que MANDA RODAR um script tem de levar esse script junto.

Defeito medido nesta sessao, depois de incorporar dois acervos: `dz23-performance-scalability-engine`
e `dz23-backend-data-architect` passaram a instruir o agente a executar
`python scripts/consulta-<dominio>.py`, mas esses scripts vivem em `scripts/` do REPOSITORIO, nao na
pasta da skill. O `install-all` copia apenas o conteudo de `skills/<nome>/` para
`~/.agents/skills/<nome>/`. Resultado: a habilidade instalada contem uma instrucao para rodar um
arquivo que nao existe onde ela esta. No checkout funciona (porque la os dois caminhos existem), no
uso real nao.

E a mesma familia das rodadas 47 e 55 -- conteudo correto, inalcancavel -- so que agora em relacao ao
ambiente de execucao do usuario, nao ao indice da propria skill. Um check local verde nao cobria isso
porque media o repo, e quem usa a skill nao esta no repo.

Regra aplicada: se o SKILL.md (ou qualquer reference/template) manda rodar `scripts/x.py`, entao
`skills/<nome>/scripts/x.py` precisa existir. Scripts compartilhados do repo podem ser citados desde
que com caminho explicito e fallback declarado; apontar para `scripts/` sem levar o arquivo e o caso
que este verificador reprova.
"""
from __future__ import annotations

import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "skills"

# `python scripts/foo.py`, `python3 ./scripts/foo.py`, `py scripts\foo.py`
CHAMADA = re.compile(r"(?i)\b(?:python3?|py)\s+(?:[\w./\\-]*?)(scripts[/\\][\w\-]+\.py)")


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    problemas: list[str] = []
    conferidas = 0
    citacoes = 0

    for sk in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        docs = [p for p in sk.rglob("*.md")]
        corpo_por_arquivo = {p: p.read_text(encoding="utf-8", errors="replace") for p in docs}
        achou_algo = False
        for origem, texto in corpo_por_arquivo.items():
            for m in CHAMADA.finditer(texto):
                achou_algo = True
                alvo = m.group(1).replace("\\", "/")
                nome = alvo.rsplit("/", 1)[-1]
                citacoes += 1
                if (sk / "scripts" / nome).is_file():
                    continue
                # excecao honesta: a skill pode mandar usar uma FERRAMENTA do ambiente (ocr, rea,
                # playwright), nao um script proprio. So perdoa se o texto diz claramente que e
                # ferramenta externa -- senao e a lacuna que este arquivo existe para pegar.
                contexto = texto[max(0, m.start() - 260):m.start() + 260].lower()
                externo = any(k in contexto for k in ("ferramenta externa", "cli externa",
                                                      "por cli", "via cli", "nao faz parte"))
                if externo and not (RAIZ / "scripts" / nome).is_file():
                    continue
                onde = "existe em scripts/ do repo, mas NAO vai na instalacao da skill" \
                    if (RAIZ / "scripts" / nome).is_file() else "nao existe em lugar nenhum"
                problemas.append(
                    f"{sk.name}: `{origem.relative_to(sk)}` manda rodar {alvo} -- "
                    f"{onde}; skills/{sk.name}/scripts/{nome} ausente")
        if achou_algo:
            conferidas += 1

    print(f"skills que instruem executar scripts: {conferidas} | chamadas conferidas: {citacoes}")
    for p in problemas:
        print("PROBLEMA:", p)
    if not problemas:
        print("toda skill leva consigo os scripts que manda rodar")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
