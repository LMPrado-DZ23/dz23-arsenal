#!/usr/bin/env python3
"""check-sbom.py -- o SBOM diz a verdade sobre a cadeia COMMITADA, e sabe reprovar.

Independente do gerador de propósito: relê os package.json por conta própria e compara com o SBOM
no disco. Política do repo (ver .gitignore): lockfiles npm não são versionados; a fonte de verdade
committada são as faixas de versão do package.json. Logo o SBOM lista as dependências DIRETAS
declaradas -- não a árvore resolvida de um lockfile efêmero (que no Windows-CI nem existe, pois lá
não roda npm install). Exige:

  1. Formato: bomFormat=CycloneDX, lista de components, sem bom-ref duplicado.
  2. Cada biblioteca tem version (a faixa) e purl coerente (pkg:npm/<nome>@<faixa>).
  3. Drift: o conjunto de bibliotecas no SBOM bate EXATAMENTE com as deps diretas dos
     package.json de hoje. Mudar uma dependência sem regenerar o SBOM reprova.

Uso:
    python scripts/check-sbom.py            # exit 1 se houver problema
    python scripts/check-sbom.py --json
    python scripts/check-sbom.py --selftest # controle negativo
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SBOM = RAIZ / "supply-chain" / "sbom.json"
PKGS = [RAIZ / "mcp" / "pentagi-mcp" / "package.json",
        RAIZ / "mcp" / "dz23-subagents-universal-mcp" / "package.json"]


def _deps_do_pkg(pkg: Path) -> set[str]:
    """Conjunto de pkg:npm/<nome>@<faixa> das deps diretas de um package.json."""
    out: set[str] = set()
    if not pkg.is_file():
        return out
    pj = json.loads(pkg.read_text(encoding="utf-8"))
    deps = {**(pj.get("dependencies") or {}), **(pj.get("devDependencies") or {})}
    for nome, faixa in deps.items():
        out.add(f"pkg:npm/{nome}@{faixa}")
    return out


def valida(sbom: dict, esperado_npm: set[str]) -> list[str]:
    problemas: list[str] = []
    if sbom.get("bomFormat") != "CycloneDX":
        problemas.append("bomFormat não é CycloneDX")
    comps = sbom.get("components")
    if not isinstance(comps, list) or not comps:
        return problemas + ["components ausente ou vazio"]

    refs_vistos: dict[str, int] = {}
    for c in comps:
        r = c.get("bom-ref")
        if r:
            refs_vistos[r] = refs_vistos.get(r, 0) + 1
    for r, n in refs_vistos.items():
        if n > 1:
            problemas.append(f"bom-ref duplicado: {r} ({n}x) — CycloneDX inválido")

    libs: set[str] = set()
    for c in comps:
        if c.get("type") != "library":
            continue
        ref = c.get("bom-ref", c.get("name", "?"))
        nome, ver = c.get("name"), c.get("version")
        if not ver:
            problemas.append(f"{ref}: sem version (faixa)")
        purl = c.get("purl", "")
        if nome and ver and purl != f"pkg:npm/{nome}@{ver}":
            problemas.append(f"{ref}: purl incoerente ({purl!r})")
        if purl:
            libs.add(purl)

    for p in sorted(esperado_npm - libs):
        problemas.append(f"package.json declara {p} mas o SBOM não — regenere (drift)")
    for p in sorted(libs - esperado_npm):
        problemas.append(f"SBOM lista {p} que nenhum package.json declara — regenere (drift)")
    return problemas


def _selftest() -> int:
    tmp = Path(tempfile.mkdtemp())
    pkg = tmp / "package.json"
    pkg.write_text(json.dumps({"dependencies": {"zod": "^3.25.0"}}), encoding="utf-8")
    esperado = _deps_do_pkg(pkg)
    bom_ok = {"bomFormat": "CycloneDX", "components": [
        {"type": "library", "bom-ref": "pkg:npm/zod@^3.25.0", "name": "zod", "version": "^3.25.0",
         "purl": "pkg:npm/zod@^3.25.0"},
    ]}
    if valida(bom_ok, esperado):
        print("FALHA selftest: SBOM válido foi reprovado (falso positivo)")
        return 1
    casos = [
        ("version faltando", lambda b: b["components"][0].pop("version")),
        ("purl incoerente", lambda b: b["components"][0].update(purl="pkg:npm/zod@9")),
        ("drift: a mais", lambda b: b["components"].append(
            {"type": "library", "name": "evil", "version": "1", "purl": "pkg:npm/evil@1"})),
        ("drift: a menos", lambda b: b["components"].clear()),
        ("bom-ref duplicado", lambda b: b["components"].append(dict(b["components"][0]))),
    ]
    for desc, mut in casos:
        b = json.loads(json.dumps(bom_ok))
        mut(b)
        if not valida(b, esperado):
            print(f"FALHA selftest: mutação '{desc}' não detectada")
            return 1
    print("OK selftest: SBOM válido aprova; 5 mutações reprovam")
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
    if not SBOM.is_file():
        print(f"FALHA: {SBOM} ausente — rode gera-sbom.py")
        return 1
    esperado: set[str] = set()
    for pk in PKGS:
        esperado |= _deps_do_pkg(pk)
    problemas = valida(json.loads(SBOM.read_text(encoding="utf-8")), esperado)
    if args.json:
        print(json.dumps({"ok": not problemas, "problemas": problemas}, ensure_ascii=False, indent=2))
        return 0 if not problemas else 1
    if problemas:
        for p in problemas:
            print(f"FALHA: {p}")
        return 1
    print(f"OK: SBOM coerente com {len(esperado)} deps diretas dos package.json committados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
