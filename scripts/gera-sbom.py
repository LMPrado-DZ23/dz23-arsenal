#!/usr/bin/env python3
"""gera-sbom.py -- gera o SBOM (CycloneDX) da FONTE DE VERDADE COMMITADA: os package.json.

Mandato, layer supply-chain/: um SBOM que diz a verdade sobre a cadeia de dependências. Este repo
tem política deliberada (ver .gitignore: 'Lockfiles npm nao sao versionados neste repo ... a
reprodutibilidade vem das versoes no package.json, nao de um lock gerado local'). Então o SBOM
versionado é construído do que é COMMITADO -- as dependências DIRETAS declaradas em cada
package.json, com a faixa de versão declarada -- e NÃO de um package-lock.json efêmero (que só
existe após npm install e muda por máquina). A árvore resolvida completa + integrity é artefato de
CI, não entra no SBOM commitado, justamente para o --check ser determinístico em qualquer SO.

Fontes (committadas):
  - mcp/pentagi-mcp/package.json                     (deps diretas, com faixa declarada)
  - mcp/dz23-subagents-universal-mcp/package.json    (zero dependências -- cadeia mínima)
  - scripts Python do arsenal: stdlib pura (jsonschema só no CI, fora do runtime)

Determinístico: sem timestamp, sem lockfile, componentes ordenados por bom-ref.

Uso:
    python scripts/gera-sbom.py            # reescreve supply-chain/sbom.json e SBOM.md
    python scripts/gera-sbom.py --check    # exit 1 se o disco divergir do gerado
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DEST = RAIZ / "supply-chain"
NODE_PROJ = [
    ("pentagi-mcp", RAIZ / "mcp" / "pentagi-mcp"),
    ("dz23-subagents-universal-mcp", RAIZ / "mcp" / "dz23-subagents-universal-mcp"),
]


def _pkg(proj_dir: Path) -> dict:
    return json.loads((proj_dir / "package.json").read_text(encoding="utf-8"))


def _componentes_npm(proj_nome: str, pj: dict) -> list[dict]:
    """Dependências DIRETAS de um package.json, com a faixa de versão declarada (não resolvida)."""
    comps: list[dict] = []
    deps = {**(pj.get("dependencies") or {}), **(pj.get("devDependencies") or {})}
    devset = set(pj.get("devDependencies") or {})
    for nome, faixa in sorted(deps.items()):
        comps.append({
            "type": "library",
            "bom-ref": f"pkg:npm/{nome}@{faixa}",
            "name": nome,
            "version": faixa,
            "purl": f"pkg:npm/{nome}@{faixa}",
            "properties": [
                {"name": "dz23:projeto", "value": proj_nome},
                {"name": "dz23:fonte", "value": "package.json (faixa declarada; lockfile não versionado)"},
                {"name": "npm:dev", "value": str(nome in devset).lower()},
            ],
        })
    return comps


def montar() -> dict:
    components: list[dict] = []
    for proj_nome, proj_dir in NODE_PROJ:
        if not (proj_dir / "package.json").is_file():
            continue
        pj = _pkg(proj_dir)
        nome, ver = pj.get("name", proj_dir.name), pj.get("version", "0.0.0")
        components.append({
            "type": "application",
            "bom-ref": f"pkg:npm/{nome}@{ver}",
            "name": nome,
            "version": ver,
            "purl": f"pkg:npm/{nome}@{ver}",
            "properties": [{"name": "dz23:projeto", "value": proj_nome},
                           {"name": "dz23:papel", "value": "mcp-server"}],
        })
        components += _componentes_npm(proj_nome, pj)
    # Superfície Python: stdlib pura, asserção explícita (não é "sem SBOM", é "zero deps").
    components.append({
        "type": "application",
        "bom-ref": "dz23:scripts-python",
        "name": "dz23-arsenal-scripts",
        "version": "0",
        "properties": [
            {"name": "dz23:projeto", "value": "scripts"},
            {"name": "dz23:runtime-deps", "value": "stdlib-apenas"},
            {"name": "dz23:nota", "value": "jsonschema instalado só no CI, fora do runtime"},
        ],
    })
    # Dedup por bom-ref: o mesmo nome@versão pode aparecer em caminhos node_modules aninhados
    # do lockfile; bom-ref duplicado é CycloneDX inválido. Mantém a primeira ocorrência.
    unicos: dict[str, dict] = {}
    for c in components:
        unicos.setdefault(c["bom-ref"], c)
    components = sorted(unicos.values(), key=lambda c: c["bom-ref"])
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {"type": "application", "bom-ref": "dz23-arsenal",
                          "name": "dz23-arsenal", "purl": "pkg:github/LMPrado-DZ23/dz23-arsenal"},
            "tools": [{"name": "gera-sbom.py", "vendor": "dz23-arsenal"}],
            "properties": [{"name": "dz23:nota",
                            "value": "Gerado dos lockfiles reais; sem timestamp para o --check ser determinístico."}],
        },
        "components": components,
    }


def _md(bom: dict) -> str:
    comps = bom["components"]
    apps = [c for c in comps if c["type"] == "application"]
    libs = [c for c in comps if c["type"] == "library"]
    por_proj: dict[str, int] = {}
    for c in libs:
        proj = next((p["value"] for p in c.get("properties", []) if p["name"] == "dz23:projeto"), "?")
        por_proj[proj] = por_proj.get(proj, 0) + 1
    linhas = [
        "# SBOM — dz23-arsenal",
        "",
        "> **Gerado** por `scripts/gera-sbom.py` dos `package.json` committados. Não edite à mão — o "
        "gate (`sbom:verifica`) reprova divergência. Formato CycloneDX 1.5.",
        "",
        f"- **{len(libs)}** dependências diretas de npm (faixa declarada no `package.json`).",
        f"- **{len(apps)}** componentes de aplicação (os MCP + a superfície Python stdlib-only).",
        "",
        "## Política de versão (deliberada neste repo)",
        "",
        "Lockfiles npm **não são versionados** aqui (ver `.gitignore`): a reprodutibilidade vem das "
        "faixas no `package.json`, não de um lock gerado por máquina. Por isso o SBOM committado "
        "lista as **dependências diretas declaradas**; a árvore resolvida completa + integrity "
        "sha512 é artefato de CI (gerado por `npm install`), não entra aqui — assim o `--check` é "
        "determinístico em qualquer SO.",
        "",
        "## Dependências diretas por projeto",
        "",
        "| Projeto | Deps diretas (npm) |",
        "|---|---:|",
    ]
    for proj in sorted(por_proj):
        linhas.append(f"| {proj} | {por_proj[proj]} |")
    linhas += [
        "",
        "## Cadeia mínima, por desenho",
        "",
        "- `dz23-subagents-universal-mcp`: **zero dependências** de terceiros (toda a lógica em "
        "stdlib Node) — menor superfície de ataque possível.",
        "- Scripts Python do arsenal: **stdlib apenas** no runtime; `jsonschema` entra só no CI.",
        "- Dependabot acompanha os `package.json`; Gitleaks e CodeQL cobrem segredo e SAST.",
        "",
    ]
    return "\n".join(linhas) + "\n"


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    bom = montar()
    sbom_txt = json.dumps(bom, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    md_txt = _md(bom)
    sbom_path = DEST / "sbom.json"
    md_path = DEST / "SBOM.md"

    if args.check:
        falhas = []
        for p, novo in ((sbom_path, sbom_txt), (md_path, md_txt)):
            atual = p.read_text(encoding="utf-8") if p.is_file() else ""
            if atual.replace("\r\n", "\n") != novo.replace("\r\n", "\n"):
                falhas.append(p.name)
        if falhas:
            print(f"FALHA: {', '.join(falhas)} diverge(m) dos package.json — rode gera-sbom.py")
            return 1
        print(f"OK: SBOM em sincronia com os package.json ({len(bom['components'])} componentes)")
        return 0

    DEST.mkdir(exist_ok=True)
    sbom_path.write_text(sbom_txt, encoding="utf-8", newline="\n")
    md_path.write_text(md_txt, encoding="utf-8", newline="\n")
    print(f"SBOM regenerado: {len(bom['components'])} componentes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
