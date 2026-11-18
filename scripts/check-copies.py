#!/usr/bin/env python3
"""check-copies.py — as cópias embutidas nas skills não podem divergir da fonte.

Contexto: `skill_validator.py` e `_achar_arsenal.py` vivem em `scripts/` **e** dentro de
cada skill. A cópia por skill existe de propósito — uma skill instalada em
`~/.agents/skills` precisa se auto-validar sem depender do checkout continuar no caminho
do ponteiro (ver ROADMAP, dívida 8). O custo é a duplicação: dez cópias que precisam
bater com uma fonte, e nada garantia isso até aqui.

Não é um problema de "não duplique". É de "se duplicou, verifique". Um gate de hash custa
doze linhas e transforma a duplicação em risco controlado; fundir de volta em import
cruzado entre skills recriaria a dependência que acabamos de eliminar.

Uso:
    python scripts/check-copies.py           # exit 1 se alguma cópia divergiu
    python scripts/check-copies.py --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def apontar_raiz(argv: list[str]) -> list[str]:
    """Consome `--raiz <pasta>` e reposiciona o global RAIZ.

    Sem isso, apontar o verificador para uma fixture é impossível: ele sempre enxerga o repo
    de onde o arquivo foi copiado. Um ataque a estes scripts caiu nessa armadilha -- rodar com
    `cwd=fixture` não muda nada, porque a raiz vem de `__file__`, e o resultado é verde sem
    medir absolutamente nada.
    """
    global RAIZ
    restante = list(argv)
    for i, a in enumerate(restante):
        if a == "--raiz" and i + 1 < len(restante):
            RAIZ = Path(restante[i + 1]).resolve()
            del restante[i:i + 2]
            break
        if a.startswith("--raiz="):
            RAIZ = Path(a.split("=", 1)[1]).resolve()
            del restante[i]
            break
    return restante


# Arquivo-fonte cujo conteúdo deve aparecer idêntico dentro de cada skill.
MODULOS_EMBUTIDOS = ("skill_validator.py", "_achar_arsenal.py")

# Consultores que existem em dois lugares: `scripts/` (gate e CI) e dentro da skill (instalacao
# autocontida -- ver checa-autocontencao.py). As duas copias NAO podem ser byte identicas: cada uma
# resolve o acervo por um caminho proprio, porque no checkout o dado fica em `<raiz>/dados-x/` e na
# habilidade instalada precisa estar ao lado do script. Entao compara-se apenas o codigo, ignorando as
# linhas que definem caminho. Editar uma copia e esquecer a outra cria duas fontes de verdade para a
# mesma consulta; isto quebra nesse caso, e nao quebra pela diferenca legitima de localizacao.
CONSULTORES_EMBUTIDOS = {
    "consulta-design.py": "dz23-ultimate-pro-max",
    "consulta-backend.py": "dz23-backend-data-architect",
    "consulta-performance.py": "dz23-performance-scalability-engine",
}

# Prefixos cuja LINHA inteira pode diferir entre as duas copias, por definir onde mora o dado.
_CAMINHO = ("RAIZ =", "DADOS =", "def _acha_dados", "aqui = pathlib", "if (aqui /",
            "return RAIZ /", "return aqui")


def _codigo(texto: str) -> list[str]:
    """So instrucoes executaveis: sem comentario, sem docstring, sem linha de caminho."""
    linhas, dentro_doc = [], False
    for bruta in texto.splitlines():
        ls = bruta.strip()
        if ls.startswith('"""'):
            if ls.count('"""') == 1:
                dentro_doc = not dentro_doc
            continue
        if dentro_doc or not ls or ls.startswith("#"):
            continue
        if ls.startswith(_CAMINHO):
            continue
        linhas.append(ls)
    return linhas


def sha(p: Path) -> str:
    """Hash de conteúdo, ignorando fim de linha.

    Comparar bytes crus faz uma cópia materializada com CRLF parecer conteúdo divergente -- e o
    conserto sugerido seria reescrever um arquivo que já é idêntico semânticamente. Reproduzido
    nesta sessão: convertendo uma das vinte cópias para CRLF, o verificador saía com
    "DIVERGÊNCIA ... conteudo difere", exatamente o mesmo defeito que derrubou o CI na rodada 47
    via build-manifest. É a regra do arsenal: EOL nunca é divergência de conteúdo (audit-zips,
    audita-sensibilidade, build.py --check). Binário continua byte a byte.
    """
    dados = p.read_bytes()
    try:
        texto = dados.decode("utf-8")
    except UnicodeDecodeError:
        return hashlib.sha256(dados).hexdigest()
    return hashlib.sha256(texto.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def main(argv: list[str]) -> int:
    argv = apontar_raiz(argv)
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--raiz", default=None, help="conferir outra árvore (fixture)")
    args = ap.parse_args(argv)

    problemas: list[dict] = []
    conferidas = 0
    pasta_skills = RAIZ / "skills"
    if not pasta_skills.is_dir():
        # Um checkout parcial (clone interrompido, worktree sem skills/) não pode derrubar
        # o gate com FileNotFoundError: o verificador que morre é indistinguível do repo que
        # falhou, e quem lê passa a ignorar ambos. Declara-se a condição e sai com erro.
        msg = {"modulo": "-", "skill": "-",
               "problema": f"{pasta_skills} ausente -- nada para conferir"}
        if args.json:
            print(json.dumps({"ok": False, "conferidas": 0, "problemas": [msg]},
                             ensure_ascii=False, indent=2))
        else:
            print(f"PROBLEMA: {msg['problema']}")
        return 1
    skills = sorted(p for p in pasta_skills.iterdir() if p.is_dir())

    for modulo in MODULOS_EMBUTIDOS:
        fonte = RAIZ / "scripts" / modulo
        if not fonte.is_file():
            problemas.append({"modulo": modulo, "skill": "-",
                              "problema": "fonte ausente em scripts/"})
            continue
        h_fonte = sha(fonte)
        for sk in skills:
            copia = sk / "scripts" / modulo
            if not copia.is_file():
                problemas.append({"modulo": modulo, "skill": sk.name,
                                  "problema": "cópia ausente na skill"})
                continue
            conferidas += 1
            if sha(copia) != h_fonte:
                problemas.append({"modulo": modulo, "skill": sk.name,
                                  "problema": "conteúdo difere de scripts/" + modulo})

    # Consultores: mesma logica, mas comparando codigo (caminho do acervo e legitimamente distinto).
    for modulo, skill_esperada in CONSULTORES_EMBUTIDOS.items():
        fonte = RAIZ / "scripts" / modulo
        copia = pasta_skills / skill_esperada / "scripts" / modulo
        if not fonte.is_file():
            problemas.append({"modulo": modulo, "skill": "-",
                              "problema": "fonte ausente em scripts/"})
            continue
        if not copia.is_file():
            problemas.append({"modulo": modulo, "skill": skill_esperada,
                              "problema": "consultor ausente na skill -- a instalacao ficaria com "
                                          "instrucao de rodar script que nao viaja junto"})
            continue
        conferidas += 1
        try:
            a = _codigo(fonte.read_text(encoding="utf-8", errors="replace"))
            b = _codigo(copia.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            problemas.append({"modulo": modulo, "skill": skill_esperada,
                              "problema": f"ilegivel: {exc}"})
            continue
        if a != b:
            import difflib
            delta = [l for l in difflib.unified_diff(a, b, lineterm="", n=0)
                     if l[:1] in "+-" and l[:3] not in ("---", "+++")][:4]
            problemas.append({"modulo": modulo, "skill": skill_esperada,
                              "problema": "codigo divergiu da copia em scripts/ (fora do caminho "
                                          "do acervo): " + " | ".join(x.strip()[:60] for x in delta)})

    if args.json:
        print(json.dumps({"ok": not problemas, "conferidas": conferidas,
                          "problemas": problemas}, ensure_ascii=False, indent=2))
    else:
        print(f"cópia(s) conferida(s): {conferidas} "
              f"({len(MODULOS_EMBUTIDOS)} módulos × {len(skills)} skills, "
              f"+{len(CONSULTORES_EMBUTIDOS)} consultores)")
        if problemas:
            for p in problemas:
                print(f"DIVERGÊNCIA {p['modulo']} em {p['skill']}: {p['problema']}")
            print(f"\ntotal: {len(problemas)} problema(s)")
            print("Corrija copiando a fonte: "
                  "Copy-Item scripts/<modulo> skills/<skill>/scripts/ -Force")
        else:
            print("todas as cópias batem com a fonte")

    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
