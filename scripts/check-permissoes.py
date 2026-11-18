#!/usr/bin/env python3
"""check-permissoes.py -- toda skill que executa declara suas permissões (mandato, regra 7).

Uma skill que roda comando, altera arquivo, usa navegador, acessa rede ou controla o computador
precisa declarar permissões, riscos, entradas, saídas, dry-run, rollback e aprovação. Sem
verificação, uma skill nova entra sem declaração e ninguém percebe. Este script exige:

  1. Cobertura: TODA pasta em skills/ tem entrada em security/permissoes.json. Skill sem
     declaração é falha -- é exatamente o caso que a regra 7 existe para impedir.
  2. Sem entrada órfã: toda entrada aponta para uma skill que existe.
  3. Completude: cada entrada tem os 7 campos obrigatórios, nenhum vazio.
  4. Vocabulário: 'permissoes' é lista não-vazia, só com valores do conjunto permitido.

Uso:
    python scripts/check-permissoes.py            # exit 1 se houver problema
    python scripts/check-permissoes.py --json
    python scripts/check-permissoes.py --selftest # controle negativo
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REG = RAIZ / "security" / "permissoes.json"
SKILLS = RAIZ / "skills"


def valida(reg: dict, nomes_skills: set[str]) -> list[str]:
    problemas: list[str] = []
    validas = set(reg.get("permissoes_validas") or [])
    obrig = list(reg.get("campos_obrigatorios") or [])
    if not validas:
        problemas.append("permissoes_validas ausente")
    if not obrig:
        problemas.append("campos_obrigatorios ausente")
    skills = reg.get("skills")
    if not isinstance(skills, dict):
        return problemas + ["'skills' ausente ou não é objeto"]

    declaradas = set(skills.keys())
    for s in sorted(nomes_skills - declaradas):
        problemas.append(f"skill sem declaração de permissões: {s} (regra 7)")
    for s in sorted(declaradas - nomes_skills):
        problemas.append(f"declaração órfã: {s} não é uma skill existente")

    for nome, d in skills.items():
        if not isinstance(d, dict):
            problemas.append(f"{nome}: declaração não é objeto")
            continue
        for campo in obrig:
            v = d.get(campo)
            if campo not in d or v in (None, "", []):
                problemas.append(f"{nome}: campo obrigatório vazio/ausente: {campo}")
        perms = d.get("permissoes")
        if isinstance(perms, list) and perms:
            for p in perms:
                if p not in validas:
                    problemas.append(f"{nome}: permissão inválida {p!r}")
        elif "permissoes" in obrig:
            problemas.append(f"{nome}: 'permissoes' deve ser lista não-vazia")
    return problemas


def _selftest() -> int:
    reg_ok = {
        "permissoes_validas": ["shell", "filesystem-write", "none"],
        "campos_obrigatorios": ["permissoes", "riscos", "entradas", "saidas", "dry_run", "rollback", "aprovacao"],
        "skills": {"a": {"permissoes": ["shell"], "riscos": "r", "entradas": "e", "saidas": "s",
                         "dry_run": "d", "rollback": "rb", "aprovacao": "ap"}},
    }
    if valida(reg_ok, {"a"}):
        print("FALHA selftest: registro válido reprovado (falso positivo)")
        return 1
    casos = [
        ("skill sem declaração", lambda r, n: ("add", "b")),
        ("declaração órfã", lambda r, n: r["skills"].update(z={"permissoes": ["shell"], "riscos": "r",
            "entradas": "e", "saidas": "s", "dry_run": "d", "rollback": "rb", "aprovacao": "ap"})),
        ("campo faltando", lambda r, n: r["skills"]["a"].pop("rollback")),
        ("permissão inválida", lambda r, n: r["skills"]["a"].update(permissoes=["voar"])),
        ("permissoes vazio", lambda r, n: r["skills"]["a"].update(permissoes=[])),
    ]
    for desc, mut in casos:
        r = json.loads(json.dumps(reg_ok))
        nomes = {"a"}
        res = mut(r, nomes)
        if isinstance(res, tuple) and res[0] == "add":
            nomes = {"a", res[1]}  # skill existe no disco mas não no registro
        if not valida(r, nomes):
            print(f"FALHA selftest: mutação '{desc}' não detectada")
            return 1
    print("OK selftest: registro válido aprova; 5 mutações reprovam")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if not REG.is_file():
        print(f"FALHA: {REG} ausente")
        return 1
    nomes = {p.name for p in SKILLS.iterdir() if p.is_dir()} if SKILLS.is_dir() else set()
    problemas = valida(json.loads(REG.read_text(encoding="utf-8")), nomes)
    if args.json:
        print(json.dumps({"ok": not problemas, "problemas": problemas}, ensure_ascii=False, indent=2))
        return 0 if not problemas else 1
    if problemas:
        for p in problemas:
            print(f"FALHA: {p}")
        return 1
    print(f"OK: {len(nomes)} skills, todas com permissões declaradas e completas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
