#!/usr/bin/env python3
"""Valida a estrutura da skill dz23-postgres-prod-preflight.

Checa: frontmatter, VERSION == version, CHANGELOG com a seção da versão, evals no schema do arsenal,
README presente e nenhuma pasta obrigatória vazia.

Exit 0 = ok · 1 = problema
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# --- checagens comuns do arsenal -------------------------------------------
# A skill instalada em ~/.agents/skills precisa achar o checkout (que pode estar em
# outro disco) para rodar as checagens compartilhadas. Contar niveis de diretorio nao
# funciona la: parents[3] aponta para ~/.agents. O localizador sobe a arvore, le o
# ponteiro .dz23-arsenal ou respeita DZ23_ARSENAL.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
try:
    from _achar_arsenal import importar_validador_comum
except ImportError:
    print("WARN: _achar_arsenal ausente - checagens comuns puladas")
    importar_validador_comum = None
if importar_validador_comum is not None:
    _validar_comum = importar_validador_comum(pathlib.Path(__file__).resolve())
    if _validar_comum is None:
        print("WARN: arsenal nao localizado - checagens comuns puladas")
    else:
        _erros_comuns = _validar_comum(RAIZ, exigir_version_file=True)
        if _erros_comuns:
            # assert NAO serve aqui: `python -O` remove a instrucao e o validador passa a
            # imprimir OK com referencia quebrada (reproduzido nas dez skills desta sessao).
            # Um gate que some por causa de uma flag de interpretador e pior que ausencia
            # dele, porque continua parecendo verificado.
            for e in _erros_comuns:
                print(f"FALHA: {e}", file=sys.stderr)
            raise SystemExit(1)


def frontmatter(texto: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", texto, re.S)
    if not m:
        return {}
    dados = {}
    for linha in m.group(1).splitlines():
        if ":" in linha and not linha.startswith((" ", "-")) and not linha.startswith("  "):
            k, v = linha.split(":", 1)
            dados[k.strip()] = v.strip().strip(">").strip()
    return dados


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    erros: list[str] = []

    skill = RAIZ / "SKILL.md"
    if not skill.is_file():
        erros.append("SKILL.md ausente")
        print("\n".join(erros))
        return 1
    texto = skill.read_text(encoding="utf-8", errors="replace")
    fm = frontmatter(texto)
    for chave in ("name", "version", "description", "user-invocable"):
        if chave not in fm:
            erros.append(f"frontmatter sem '{chave}'")
    if fm.get("name") != "dz23-postgres-prod-preflight":
        erros.append(f"name inesperado: {fm.get('name')}")

    versao = (RAIZ / "VERSION").read_text(encoding="utf-8").strip() if (RAIZ / "VERSION").is_file() else ""
    if not versao:
        erros.append("VERSION ausente ou vazio")
    if versao and fm.get("version") and versao != fm["version"]:
        erros.append(f"VERSION={versao} != frontmatter={fm['version']}")

    ch = RAIZ / "CHANGELOG.md"
    if not ch.is_file():
        erros.append("CHANGELOG.md ausente")
    elif versao and f"[{versao}]" not in ch.read_text(encoding="utf-8"):
        erros.append(f"CHANGELOG sem seção [{versao}]")

    for obrig in ("README.md", "evals/evals.json"):
        if not (RAIZ / obrig).is_file():
            erros.append(f"{obrig} ausente")

    ev = RAIZ / "evals" / "evals.json"
    if ev.is_file():
        try:
            dados = json.loads(ev.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            erros.append(f"evals.json inválido: {exc}")
            dados = {}
        if "schema_version" not in dados:
            erros.append("evals.json sem schema_version")
        casos = dados.get("cases", [])
        if not casos:
            erros.append("evals.json sem casos")
        ids = [c.get("id") for c in casos]
        if len(ids) != len(set(ids)):
            erros.append("evals.json com id duplicado")
        for c in casos:
            for campo in ("id", "title", "input", "expected", "fails_if"):
                if not c.get(campo):
                    erros.append(f"caso {c.get('id', '?')}: campo '{campo}' vazio")

    for pasta in ("references", "templates", "scripts"):
        d = RAIZ / pasta
        if not d.is_dir() or not any(d.iterdir()):
            erros.append(f"{pasta}/ vazia")

    if erros:
        print(f"PROBLEMAS: {len(erros)}")
        for e in erros:
            print(f"  - {e}")
        return 1

    print(f"OK — dz23-postgres-prod-preflight v{versao} · {len(dados.get('cases', []))} evals · "
          f"{len(list((RAIZ / 'references').iterdir()))} referências")
    return 0


if __name__ == "__main__":
    sys.exit(main())
