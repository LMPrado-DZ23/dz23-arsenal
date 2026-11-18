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
    """Hash de conteúdo SEMÂNTICO, com quebras de linha normalizadas.

    Hash de bytes crus grava um valor que depende de como o arquivo foi materializado no disco, e
    não do que o repositório contém. Reproduzido nesta sessão: `--check` passava na minha máquina e
    falhava em todo clone limpo (run 44248537821), porque meu working tree tinha CRLF em 15 arquivos
    versionados -- `core.autocrlf=false` preserva o que foi commitado, mas edições feitas por
    ferramentas Windows escrevem CRLF sem que o git reclame, já que o blob continua LF. O manifesto
    gravava o hash do disco; o clone produzia outro. Mesma disciplina de audit-zips, check-copies e
    build.py --check: EOL nunca é divergência de conteúdo neste arsenal.

    Só texto é normalizado. Binários seguem byte a byte, onde CRLF seria dado real.
    """
    h = hashlib.sha256()
    dados = p.read_bytes()
    try:
        texto = dados.decode("utf-8")
    except UnicodeDecodeError:
        return hashlib.sha256(dados).hexdigest()
    norm = texto.replace("\r\n", "\n").encode("utf-8")
    h.update(norm)
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
        # Notas de processo (ex.: absorcao-AAAA-MM-DD.md) não são referência externa:
        # não têm repo de terceiro e não entram no índice de skills/plataformas.
        if p.name.startswith("absorcao-"):
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

    # MCP e bundle sao enumerados a partir do disco. Antes havia uma lista hardcoded
    # que punha o MCP principal dentro de "bundles" e omitia o pentagi-mcp inteiro.
    def componentes(subpasta: str, chave: str) -> list[dict]:
        base = RAIZ / subpasta
        saida = []
        for pasta in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
            item = {"path": f"{subpasta}/{pasta.name}", "version": ler_versao(pasta)}
            pkg = pasta / "package.json"
            if pkg.is_file():
                try:
                    item["license"] = json.loads(pkg.read_text(encoding="utf-8")).get("license")
                except json.JSONDecodeError:
                    item["license"] = None
            tem_licenca = any((pasta / n).is_file() for n in ("LICENSE", "LICENSE.md", "LICENSE.txt"))
            item["tem_license_file"] = tem_licenca
            saida.append(item)
        return saida

    mcp = componentes("mcp", "mcp")
    bundles = componentes("bundle", "bundle")

    return {
        "schema": 2,
        "generated_by": "scripts/build-manifest.py",
        "counts": {
            "skills": len(skills),
            "external": len(externos),
            "prompts": len(prompts),
            "mcp": len(mcp),
            "bundle": len(bundles),
        },
        "skills": skills,
        "external": externos,
        "prompts": prompts,
        "mcp": mcp,
        "bundles": bundles,
    }


def corpo_comparavel(man: dict) -> str:
    """Serializacao estavel usada para comparar e para gravar.

    Nao inclui data nem hash de geracao: `generated_at` com `date.today()` fazia o
    `--check` falhar em qualquer dia diferente do ultimo push, sem nada ter mudado.
    A data vive no comentario do INDEX.md, fora do payload comparado.
    """
    return json.dumps(man, indent=2, ensure_ascii=False) + "\n"


def gerar_index(man: dict, data_geracao: str) -> str:
    c = man["counts"]
    contagens = [
        f"{c['skills']} skills",
        f"{c['external']} externas",
        f"{c['prompts']} prompt(s)",
        f"{c['mcp']} MCP",
        f"{c['bundle']} bundle(s)",
    ]
    linhas = [
        "# Índice do arsenal",
        "",
        f"> Gerado por `scripts/build-manifest.py` em {data_geracao}. **Não editar à mão** — rode o script.",
        "> A data acima é informativa e não entra na comparação do `--check`.",
        "",
        "**" + " · ".join(contagens) + "**",
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

    linhas += ["", "## MCP e bundles", "", "| Item | Caminho | Versão | Licença declarada |", "|---|---|---|---|"]
    for item in man["mcp"] + man["bundles"]:
        nome = item["path"].split("/")[-1]
        lic = item.get("license") or ("arquivo LICENSE" if item.get("tem_license_file") else "—")
        linhas.append(f"| [{nome}]({item['path']}/) | `{item['path']}` | {item['version']} | {lic} |")

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
    json_txt = corpo_comparavel(man)
    # A data so importa para quem le o INDEX; comparar por ela faria o gate depender do calendario.
    index_txt_atual = None
    alvo_json = RAIZ / "arsenal.json"
    alvo_index = RAIZ / "INDEX.md"

    if args.check:
        problemas = []
        if not alvo_json.is_file():
            problemas.append("arsenal.json ausente")
        else:
            try:
                atual = json.loads(alvo_json.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                problemas.append(f"arsenal.json ilegível: {exc}")
                atual = None
            if atual is not None and corpo_comparavel(atual) != json_txt:
                problemas.append("arsenal.json desatualizado em relação ao disco")
        if not alvo_index.is_file():
            problemas.append("INDEX.md ausente")
        else:
            texto = alvo_index.read_text(encoding="utf-8")
            m = re.search(r"build-manifest\.py` em (\S+)\.", texto)
            index_txt_atual = gerar_index(man, m.group(1) if m else "?")
            if texto != index_txt_atual:
                problemas.append("INDEX.md desatualizado em relação ao manifesto")
        if problemas:
            print("DESATUALIZADO: " + "; ".join(problemas))
            print("Rode: python scripts/build-manifest.py")
            return 1
        print(f"manifesto em dia ({man['counts']['skills']} skills, "
              f"{man['counts']['mcp']} MCP, {man['counts']['bundle']} bundle)")
        return 0

    index_txt = gerar_index(man, date.today().isoformat())
    alvo_json.write_text(json_txt, encoding="utf-8", newline="\n")
    alvo_index.write_text(index_txt, encoding="utf-8", newline="\n")
    print(f"arsenal.json: {len(man['skills'])} skills, {len(man['external'])} externas, "
          f"{len(man['prompts'])} prompt(s), {len(man['mcp'])} MCP, {len(man['bundles'])} bundle(s)")
    print("INDEX.md gerado")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
