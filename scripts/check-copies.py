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

# Arquivo-fonte cujo conteúdo deve aparecer idêntico dentro de cada skill.
MODULOS_EMBUTIDOS = ("skill_validator.py", "_achar_arsenal.py")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
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

    if args.json:
        print(json.dumps({"ok": not problemas, "conferidas": conferidas,
                          "problemas": problemas}, ensure_ascii=False, indent=2))
    else:
        print(f"cópia(s) conferida(s): {conferidas} "
              f"({len(MODULOS_EMBUTIDOS)} módulos × {len(skills)} skills)")
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
