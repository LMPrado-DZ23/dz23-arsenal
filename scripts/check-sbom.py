#!/usr/bin/env python3
"""check-sbom.py -- o SBOM diz a verdade sobre a cadeia real, e sabe reprovar.

Independente do gerador de propósito: reparseia os lockfiles por conta própria e compara com o
SBOM no disco. Se o gera-sbom.py tiver um bug, este verificador pega. Exige:

  1. Formato: bomFormat=CycloneDX, lista de components.
  2. Cada componente de biblioteca tem version, purl coerente (pkg:npm/<nome>@<ver>) e
     integrity sha512 não-vazio (evidência de origem; supply-chain sem hash é afirmação).
  3. Drift: o conjunto de bibliotecas no SBOM bate EXATAMENTE com o que os lockfiles declaram
     hoje. Adicionar/atualizar dependência sem regenerar o SBOM reprova.

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
LOCKS = [RAIZ / "mcp" / "pentagi-mcp" / "package-lock.json",
         RAIZ / "mcp" / "dz23-subagents-universal-mcp" / "package-lock.json"]


def _npm_do_lock(lock: Path) -> set[str]:
    """Conjunto de pkg:npm/<nome>@<ver> declarados num package-lock.json."""
    out: set[str] = set()
    if not lock.is_file():
        return out
    dados = json.loads(lock.read_text(encoding="utf-8"))
    for caminho, info in (dados.get("packages") or {}).items():
        if caminho == "":
            continue
        nome = caminho.split("node_modules/")[-1]
        ver = info.get("version")
        if ver:
            out.add(f"pkg:npm/{nome}@{ver}")
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
            problemas.append(f"{ref}: sem version")
        purl = c.get("purl", "")
        if nome and ver and purl != f"pkg:npm/{nome}@{ver}":
            problemas.append(f"{ref}: purl incoerente ({purl!r})")
        integ = next((p["value"] for p in c.get("properties", []) if p.get("name") == "npm:integrity"), "")
        if not integ or "sha512-" not in integ:
            problemas.append(f"{ref}: sem integrity sha512 (origem não comprovada)")
        if purl:
            libs.add(purl)

    faltando = esperado_npm - libs
    sobrando = libs - esperado_npm
    for p in sorted(faltando):
        problemas.append(f"lockfile declara {p} mas o SBOM não — regenere (drift)")
    for p in sorted(sobrando):
        problemas.append(f"SBOM lista {p} que nenhum lockfile declara — regenere (drift)")
    return problemas


def _selftest() -> int:
    tmp = Path(tempfile.mkdtemp())
    lock = tmp / "package-lock.json"
    lock.write_text(json.dumps({"packages": {
        "": {"name": "root"},
        "node_modules/zod": {"version": "3.25.0", "integrity": "sha512-AAAA"},
    }}), encoding="utf-8")
    esperado = _npm_do_lock(lock)
    bom_ok = {"bomFormat": "CycloneDX", "components": [
        {"type": "library", "bom-ref": "pkg:npm/zod@3.25.0", "name": "zod", "version": "3.25.0",
         "purl": "pkg:npm/zod@3.25.0", "properties": [{"name": "npm:integrity", "value": "sha512-AAAA"}]},
    ]}
    if valida(bom_ok, esperado):
        print("FALHA selftest: SBOM válido foi reprovado (falso positivo)")
        return 1
    casos = [
        ("sem integrity", lambda b: b["components"][0].update(properties=[])),
        ("version faltando", lambda b: b["components"][0].pop("version")),
        ("drift: componente a mais", lambda b: b["components"].append(
            {"type": "library", "name": "evil", "version": "1.0.0", "purl": "pkg:npm/evil@1.0.0",
             "properties": [{"name": "npm:integrity", "value": "sha512-X"}]})),
        ("drift: componente a menos", lambda b: b["components"].clear()),
    ]
    for desc, mut in casos:
        b = json.loads(json.dumps(bom_ok))
        mut(b)
        if not valida(b, esperado):
            print(f"FALHA selftest: mutação '{desc}' não detectada")
            return 1
    print("OK selftest: SBOM válido aprova; 4 mutações reprovam")
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
    for lk in LOCKS:
        esperado |= _npm_do_lock(lk)
    problemas = valida(json.loads(SBOM.read_text(encoding="utf-8")), esperado)
    if args.json:
        print(json.dumps({"ok": not problemas, "problemas": problemas}, ensure_ascii=False, indent=2))
        return 0 if not problemas else 1
    if problemas:
        for p in problemas:
            print(f"FALHA: {p}")
        return 1
    print(f"OK: SBOM coerente com {len(esperado)} componentes npm dos lockfiles, integrity presente")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
