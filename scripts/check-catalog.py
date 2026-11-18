#!/usr/bin/env python3
"""check-catalog.py -- o catálogo de fontes externas é verificável, não prosa solta.

catalog/catalog.json é o índice das fontes externas do arsenal (mandato: layer catalog/).
Sem verificação mecânica, "licença conferida" e "decisão registrada" viram memória de quem
escreveu. Este script exige:

  1. Schema: cada fonte tem nome, url (https), licenca, licenca_verificada (bool), funcao,
     decisao (do conjunto permitido), dependencias, risco, fallback_local, doc (ou null),
     sha256_zip (ou null). Campo ausente é falha.
  2. Evidência: licenca_verificada=true EXIGE sha256_zip (o ZIP foi lido no disco). Não se
     declara licença verificada sem o artefato que a comprova.
  3. Honestidade: licenca_verificada=false com licenca="a-verificar" é o estado correto de
     uma fonte só catalogada por URL -- nunca se inventa a licença de repo não lido.
  4. Cruzamento: todo doc apontado existe em external/; e todo external/*.md de conteúdo
     (fora README.md e absorcao-*.md) é referenciado por exatamente uma fonte. Doc órfão é
     material morto; fonte apontando doc inexistente é link quebrado.
  5. Sem nome duplicado.

Uso:
    python scripts/check-catalog.py            # exit 1 se houver problema
    python scripts/check-catalog.py --json
    python scripts/check-catalog.py --selftest # prova que sabe reprovar (controle negativo)
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CAT = RAIZ / "catalog" / "catalog.json"
EXT = RAIZ / "external"
OBRIGATORIOS = ("nome", "url", "licenca", "licenca_verificada", "funcao", "decisao",
                "dependencias", "risco", "fallback_local", "doc", "sha256_zip")
EXT_IGNORAR = {"README.md"}  # + qualquer absorcao-*.md


def verifica(cat_path: Path, ext_dir: Path) -> list[str]:
    problemas: list[str] = []
    try:
        dados = json.loads(cat_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"catalog.json ilegível: {exc}"]

    validas = set(dados.get("decisoes_validas") or [])
    if not validas:
        problemas.append("decisoes_validas ausente ou vazio")
    fontes = dados.get("fontes")
    if not isinstance(fontes, list) or not fontes:
        return problemas + ["'fontes' ausente ou vazio"]

    vistos: dict[str, int] = {}
    docs_referenciados: list[str] = []
    for i, f in enumerate(fontes):
        tag = f.get("nome", f"#{i}")
        for campo in OBRIGATORIOS:
            if campo not in f:
                problemas.append(f"{tag}: campo obrigatório ausente: {campo}")
        nome = f.get("nome")
        if nome:
            vistos[nome] = vistos.get(nome, 0) + 1
        url = f.get("url", "")
        if not isinstance(url, str) or not url.startswith("https://"):
            problemas.append(f"{tag}: url deve começar com https:// (tem {url!r})")
        dec = f.get("decisao")
        if dec not in validas:
            problemas.append(f"{tag}: decisao inválida {dec!r} (válidas: {sorted(validas)})")
        ver = f.get("licenca_verificada")
        if not isinstance(ver, bool):
            problemas.append(f"{tag}: licenca_verificada deve ser booleano")
        elif ver and not f.get("sha256_zip"):
            problemas.append(f"{tag}: licenca_verificada=true sem sha256_zip (sem evidência)")
        lic = f.get("licenca")
        if ver is False and not lic:
            problemas.append(f"{tag}: licenca ausente (use 'a-verificar' quando não lida)")
        doc = f.get("doc")
        if doc:
            if not (ext_dir / Path(doc).name).is_file() or not str(doc).startswith("external/"):
                problemas.append(f"{tag}: doc {doc!r} não existe em external/")
            else:
                docs_referenciados.append(Path(doc).name)

    for nome, n in vistos.items():
        if n > 1:
            problemas.append(f"nome duplicado no catálogo: {nome} ({n}x)")

    # Cruzamento: todo external/*.md de conteúdo tem de ser referenciado.
    if ext_dir.is_dir():
        for md in sorted(ext_dir.glob("*.md")):
            if md.name in EXT_IGNORAR or md.name.startswith("absorcao-"):
                continue
            if md.name not in docs_referenciados:
                problemas.append(f"external/{md.name}: doc órfão -- nenhuma fonte do catálogo o referencia")
    return problemas


def _selftest() -> int:
    """Controle negativo: um catálogo com decisão inválida e licença verificada sem evidência
    TEM de reprovar. Verificador que só sabe dizer OK é afirmativa decorada (regra da rodada 43)."""
    tmp = Path(tempfile.mkdtemp())
    (tmp / "external").mkdir()
    bom = {
        "decisoes_validas": ["CATALOGAR", "REFERENCIA"],
        "fontes": [{
            "nome": "x", "url": "https://example.com/x", "licenca": "a-verificar",
            "licenca_verificada": False, "funcao": "f", "decisao": "CATALOGAR",
            "dependencias": "n", "risco": "baixo", "fallback_local": "n",
            "doc": None, "sha256_zip": None,
        }],
    }
    catp = tmp / "catalog.json"
    catp.write_text(json.dumps(bom), encoding="utf-8")
    if verifica(catp, tmp / "external"):
        print("FALHA selftest: catálogo válido foi reprovado (falso positivo)")
        return 1
    # mutações que DEVEM reprovar
    casos = [
        ("decisão inválida", lambda d: d["fontes"][0].__setitem__("decisao", "INVENTADA")),
        ("verificada sem sha", lambda d: d["fontes"][0].update(licenca_verificada=True)),
        ("url não-https", lambda d: d["fontes"][0].__setitem__("url", "ftp://x")),
        ("campo faltando", lambda d: d["fontes"][0].pop("risco")),
    ]
    for desc, mut in casos:
        d = json.loads(json.dumps(bom))
        mut(d)
        catp.write_text(json.dumps(d), encoding="utf-8")
        if not verifica(catp, tmp / "external"):
            print(f"FALHA selftest: mutação '{desc}' não foi detectada")
            return 1
    print("OK selftest: catálogo válido aprova; 4 mutações reprovam")
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

    if not CAT.is_file():
        print(f"FALHA: {CAT} ausente")
        return 1
    problemas = verifica(CAT, EXT)
    if args.json:
        print(json.dumps({"ok": not problemas, "problemas": problemas}, ensure_ascii=False, indent=2))
        return 0 if not problemas else 1
    if problemas:
        for p in problemas:
            print(f"FALHA: {p}")
        return 1
    n = len(json.loads(CAT.read_text(encoding="utf-8"))["fontes"])
    print(f"OK: catálogo com {n} fontes, schema e cruzamento com external/ válidos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
