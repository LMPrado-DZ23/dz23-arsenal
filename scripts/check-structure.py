#!/usr/bin/env python3
"""check-structure.py — valida a estrutura de todas as skills do arsenal.

Checa o que o `validate_skill.py` de cada skill pode não checar (ou nem existir):

  - arquivos obrigatórios: SKILL.md, VERSION, CHANGELOG.md, README.md
  - frontmatter: name, version, description, user-invocable
  - name do frontmatter == nome da pasta
  - VERSION == version do frontmatter
  - CHANGELOG tem uma seção com a versão atual
  - README tem a seção "Arsenal" (doc do repositório)
  - evals/evals.json: schema, e cada caso com id/input/expected/fails_if; ids únicos
  - nenhuma skill vazia (0 references e 0 templates e 0 scripts = suspeita)

Exit: 0 = tudo ok · 1 = problemas encontrados
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def frontmatter(skill: Path) -> dict[str, str]:
    s = skill / "SKILL.md"
    if not s.is_file():
        return {}
    texto = s.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---", texto, re.S)
    if not m:
        return {}
    fm = {}
    for linha in m.group(1).splitlines():
        if ":" in linha and not linha.startswith((" ", "\t", "-")):
            k, v = linha.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def versao(skill: Path) -> str:
    v = skill / "VERSION"
    return v.read_text(encoding="utf-8", errors="replace").strip() if v.is_file() else ""


def checar(skill: Path) -> list[str]:
    erros: list[str] = []
    nome = skill.name

    for obrig in ("SKILL.md", "VERSION", "CHANGELOG.md", "README.md"):
        if not (skill / obrig).is_file():
            erros.append(f"{nome}: falta {obrig}")

    fm = frontmatter(skill)
    for chave in ("name", "version", "description", "user-invocable"):
        if chave not in fm:
            erros.append(f"{nome}: frontmatter sem '{chave}'")

    if fm.get("name") and fm["name"] != nome:
        erros.append(f"{nome}: frontmatter name='{fm['name']}' != pasta")

    v = versao(skill)
    if v and fm.get("version") and v != fm["version"]:
        erros.append(f"{nome}: VERSION={v} != frontmatter={fm['version']}")

    ch = skill / "CHANGELOG.md"
    if ch.is_file() and v:
        texto = ch.read_text(encoding="utf-8", errors="replace")
        # aceita "[1.2.0]" ou "v1.2.0"
        if not re.search(rf"(\[{re.escape(v)}\]|v{re.escape(v)})", texto):
            erros.append(f"{nome}: CHANGELOG sem seção da versão {v}")

    rd = skill / "README.md"
    if rd.is_file():
        if "## Arsenal" not in rd.read_text(encoding="utf-8", errors="replace"):
            erros.append(f"{nome}: README sem seção '## Arsenal'")

    ev = skill / "evals" / "evals.json"
    if ev.is_file():
        try:
            dados = json.loads(ev.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            erros.append(f"{nome}: evals.json inválido ({exc})")
            return erros
        casos = dados.get("cases")
        if not isinstance(casos, list) or not casos:
            erros.append(f"{nome}: evals.json sem 'cases'")
        else:
            if "schema_version" not in dados:
                erros.append(f"{nome}: evals.json sem schema_version")
            ids = [c.get("id") for c in casos]
            if len(ids) != len(set(ids)):
                erros.append(f"{nome}: evals com id duplicado")
            for c in casos:
                for chave in ("id", "input", "expected", "fails_if"):
                    if not c.get(chave):
                        erros.append(f"{nome}: eval '{c.get('id', '?')}' sem '{chave}'")

    tem_extras = any((skill / d).is_dir() and any((skill / d).iterdir())
                     for d in ("references", "templates", "scripts"))
    if not tem_extras:
        erros.append(f"{nome}: skill sem references/templates/scripts (suspeita de esqueleto vazio)")

    return erros


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    skills_dir = RAIZ / "skills"
    if not skills_dir.is_dir():
        print("INVALID pasta skills/ ausente", file=sys.stderr)
        return 2

    skills = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    todos: list[str] = []
    for skill in skills:
        todos += checar(skill)

    print(f"skills verificadas: {len(skills)}")
    if todos:
        print(f"PROBLEMAS: {len(todos)}")
        for e in todos:
            print(f"  - {e}")
        return 1
    print("PROBLEMAS: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
