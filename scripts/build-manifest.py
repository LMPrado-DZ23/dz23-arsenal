#!/usr/bin/env python3
"""build-manifest.py — gera arsenal.json (inventário legível por máquina) e INDEX.md.

Uso:
    python scripts/build-manifest.py            # escreve arsenal.json e INDEX.md
    python scripts/build-manifest.py --check    # só verifica se estão atualizados (exit 1 se não)

Fonte de verdade: os próprios arquivos (`VERSION`, frontmatter do `SKILL.md`, `evals/evals.json`).
Nada é inferido de memória: se não está no arquivo, não entra no manifesto.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
IGNORAR = re.compile(r"(/__pycache__/|/\.git/|\.bak-|_sources|\.DS_Store|\.pyc$)")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def ler_versao(pasta: Path) -> str:
    v = pasta / "VERSION"
    if v.is_file():
        return v.read_text(encoding="utf-8", errors="replace").strip()
    s = pasta / "SKILL.md"
    if s.is_file():
        for linha in s.read_text(encoding="utf-8", errors="replace").splitlines()[:12]:
            if linha.lower().startswith("version:"):
                return linha.split(":", 1)[1].strip().strip('"\'')
    pkg = pasta / "package.json"
    if pkg.is_file():
        try:
            return json.loads(pkg.read_text(encoding="utf-8")).get("version", "?")
        except json.JSONDecodeError:
            return "?"
    return "?"


def frontmatter(pasta: Path) -> dict[str, str]:
    s = pasta / "SKILL.md"
    if not s.is_file():
        return {}
    texto = s.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---", texto, re.S)
    if not m:
        return {}
    saida = {}
    for linha in m.group(1).splitlines():
        if ":" in linha and not linha.startswith((" ", "\t")):
            k, v = linha.split(":", 1)
            saida[k.strip()] = v.strip()
    return saida


def contar(pasta: Path, sub: str, filtro: str = "*") -> int:
    d = pasta / sub
    if not d.is_dir():
        return 0
    return len([p for p in d.iterdir() if p.is_file() and (filtro == "*" or p.match(filtro))])


def evals_de(pasta: Path) -> int:
    f = pasta / "evals" / "evals.json"
    if not f.is_file():
        return 0
    try:
        return len(json.loads(f.read_text(encoding="utf-8")).get("cases", []))
    except (json.JSONDecodeError, OSError):
        return 0


def arquivos_de(pasta: Path) -> int:
    return len([p for p in pasta.rglob("*") if p.is_file() and not IGNORAR.search("/" + str(p.relative_to(pasta)))])


def montar() -> dict:
    skills = []
    for pasta in sorted(p for p in (RAIZ / "skills").iterdir() if p.is_dir()):
        fm = frontmatter(pasta)
        skills.append({
            "name": pasta.name,
            "version": ler_versao(pasta),
            "description": fm.get("description", "").strip() or None,
            "user_invocable": fm.get("user-invocable", "").lower() == "true",
            "files": arquivos_de(pasta),
            "references": contar(pasta, "references"),
            "templates": contar(pasta, "templates"),
            "scripts": contar(pasta, "scripts"),
            "evals": evals_de(pasta),
            "sha256_skill_md": sha256(pasta / "SKILL.md") if (pasta / "SKILL.md").is_file() else None,
        })

    externos = []
    for p in sorted((RAIZ / "external").glob("*.md")):
        if p.name == "README.md":
            continue
        texto = p.read_text(encoding="utf-8", errors="replace")
        repo = re.search(r"\*\*Repo:\*\*\s*(\S+)", texto)
        autor = re.search(r"\*\*Autor:\*\*\s*(.+)", texto)
        externos.append({
            "file": f"external/{p.name}",
            "autor": autor.group(1).strip() if autor else None,
            "repo": repo.group(1).strip() if repo else None,
        })

    prompts = sorted(f"prompts/{p.name}" for p in (RAIZ / "prompts").glob("*.md") if p.name != "README.md")

    return {
        "schema": 1,
        "generated_by": "scripts/build-manifest.py",
        "generated_at": date.today().isoformat(),
        "counts": {
            "skills": len(skills),
            "external": len(externos),
            "prompts": len(prompts),
            "mcp": 1 if (RAIZ / "mcp").is_dir() else 0,
            "bundle": 1 if (RAIZ / "bundle").is_dir() else 0,
        },
        "skills": skills,
        "external": externos,
        "prompts": prompts,
        "bundles": [
            {"path": "mcp/dz23-subagents-universal-mcp", "version": ler_versao(RAIZ / "mcp" / "dz23-subagents-universal-mcp")},
            {"path": "bundle/dz23-dsh-agency", "version": ler_versao(RAIZ / "bundle" / "dz23-dsh-agency")},
        ],
    }


def gerar_index(man: dict) -> str:
    linhas = [
        "# Índice do arsenal",
        "",
        f"> Gerado por `scripts/build-manifest.py` em {man['generated_at']}. **Não editar à mão** — rode o script.",
        "",
        f"**{man['counts']['skills']} skills · {man['counts']['external']} externas · "
        f"{man['counts']['prompts']} prompt(s) · 1 MCP · 1 bundle**",
        "",
        "## Skills",
        "",
        "| Skill | Versão | Arquivos | Refs | Templates | Scripts | Evals |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in man["skills"]:
        linhas.append(
            f"| [{s['name']}](skills/{s['name']}/) | {s['version']} | {s['files']} | "
            f"{s['references']} | {s['templates']} | {s['scripts']} | {s['evals']} |"
        )

    linhas += ["", "## MCP e bundle", "", "| Item | Versão |", "|---|---|"]
    for b in man["bundles"]:
        linhas.append(f"| [{b['path'].split('/')[-1]}]({b['path']}/) | {b['version']} |")

    linhas += ["", "## Skills externas", "", "| Skill | Autor | Repositório |", "|---|---|---|"]
    for e in man["external"]:
        nome = Path(e["file"]).stem
        linhas.append(f"| [{nome}]({e['file']}) | {e['autor'] or '—'} | {e['repo'] or '—'} |")

    if man["prompts"]:
        linhas += ["", "## Prompts de origem", ""]
        for p in man["prompts"]:
            linhas.append(f"- [`{Path(p).name}`]({p})")

    linhas += ["", "## Estado de verificação", "",
               "Evals declarados **não são evals executados**. O número da coluna *Evals* é o total de cenários",
               "escritos em `evals/evals.json`; o resultado de cada um está registrado no `CHANGELOG.md` da skill.",
               "", "Consulte também [`ROADMAP.md`](ROADMAP.md) para o estado honesto do projeto.", ""]
    return "\n".join(linhas)


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="não escreve; falha se estiver desatualizado")
    args = ap.parse_args(argv)

    man = montar()
    json_txt = json.dumps(man, indent=2, ensure_ascii=False) + "\n"
    index_txt = gerar_index(man)

    alvo_json = RAIZ / "arsenal.json"
    alvo_index = RAIZ / "INDEX.md"

    if args.check:
        problemas = []
        if not alvo_json.is_file() or alvo_json.read_text(encoding="utf-8") != json_txt:
            problemas.append("arsenal.json desatualizado")
        if not alvo_index.is_file() or alvo_index.read_text(encoding="utf-8") != index_txt:
            problemas.append("INDEX.md desatualizado")
        if problemas:
            print("DESATUALIZADO: " + "; ".join(problemas))
            print("Rode: python scripts/build-manifest.py")
            return 1
        print("manifesto em dia")
        return 0

    alvo_json.write_text(json_txt, encoding="utf-8", newline="\n")
    alvo_index.write_text(index_txt, encoding="utf-8", newline="\n")
    print(f"arsenal.json: {len(man['skills'])} skills, {len(man['external'])} externas, "
          f"{len(man['prompts'])} prompt(s)")
    print("INDEX.md gerado")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
