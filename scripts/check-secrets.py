"""check-secrets.py -- procura credenciais reais em conteudo versionado.

Nao existia. Medido nesta sessao: colando `GITHUB_TOKEN=ghp_...` e `ANTHROPIC_API_KEY=sk-ant-...`
em mcp/dz23-subagents-universal-mcp/.env.example, o quality-gate dava 46/46 verde. Os quatro
scripts que mencionam "segredo" no fonte falam de outra coisa (scan DevSecOps descrito em prosa,
design tokens, tokenizacao de texto para comparar citacoes) -- nenhum deles abre um arquivo em
busca de credencial. E a regra deste workspace manda nao gravar segredo nem no vault, quanto mais
num repositorio publico: dz23-arsenal e PUBLICO (verificado via API do GitHub).

Por que padrao e nao entropia: Shannon sobre arquivos pequenos gera falso positivo em hash, base64
de documento e UUID legitimo. Aqui cada padrao tem prefixo proprio de um emissor real, e a lista e
curta e justificavel. Um valor duvidoso sai como AVISO, nunca como falha; so formato de credencial
conhecida reprova.

Escopo: conteudo versionado (git ls-files), com fallback rglob sem dependencias quando nao ha git.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# Credenciais com prefixo emitido por quem as gera -- formato reconhecivel, sem ambiguidade.
PATRONES = [
    (r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", "GitHub personal/access/refresh token"),
    (r"\bgithub_pat_[A-Za-z0-9_]{22,}\b", "GitHub fine-grained token"),
    (r"\bsk-ant-api[0-9A-Za-z\-]{20,}\b", "Anthropic API key"),
    (r"\bsk-[A-Za-z0-9]{20,}\b", "OpenAI-style secret key"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{12,}\b", "Slack token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"),
    (r"\bAIza[0-9A-Za-z_\-]{30,}\b", "Google API key"),
    (r"\bdda8-[0-9a-f]{8}-[0-9a-f]{12,}\b", "Datadog key"),
    (r"\bsq0c[a-zA-Z0-9]{14,}\b", "Stripe secret"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH |PGP |DSA )?PRIVATE KEY-----", "chave privada PEM"),
    (r"\beyJ[A-Za-z0-9_\-]{12,}\.[A-Za-z0-9_\-]{12,}\.[A-Za-z0-9_\-]{8,}\b", "JWT com assinatura"),
]

# Valores que parecem mas nao sao: placeholder documentado, exemplo deliberado, teste.
PLACEHOLDER = re.compile(
    r"(?i)(xxxx+|your[_\-]?[a-z]*key|<[a-z_ ]+>|placeholder|exemplo|dummy|changeme|"
    r"REPLACE|redacted|\*{3,}|0{8,}|deadbeef|sample|todo|fixme|none|null)")

# Arquivos onde string longa e esperada e nao indica credencial.
IGNORAR_NOME = re.compile(r"(^|/)(LICENSE|NOTICE|CHANGELOG\.md)$|\.(lock|min\.js|min\.css|map)$")

MAX_BYTES = 2 * 1024 * 1024


def _versionados() -> list[pathlib.Path]:
    r = subprocess.run(["git", "ls-files"], capture_output=True, cwd=str(RAIZ), timeout=120)
    if r.returncode == 0 and r.stdout.strip():
        return [RAIZ.joinpath(*n.split("/")) for n in
                r.stdout.decode("utf-8", "replace").splitlines()]
    ign = ("node_modules", "__pycache__", ".git", "dist", "build")
    return [p for p in RAIZ.rglob("*")
            if p.is_file() and not any(x in p.parts for x in ign)]


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--avisos", action="store_true", help="mostrar tambem os duvidosos")
    args = ap.parse_args(argv)

    compilados = [(re.compile(p), rotulo) for p, rotulo in PATRONES]
    problemas: list[dict] = []
    avisos: list[dict] = []
    conferidos = 0

    for arq in _versionados():
        try:
            if not arq.is_file() or arq.stat().st_size > MAX_BYTES:
                continue
            rel = str(arq.relative_to(RAIZ)).replace("\\", "/")
        except (OSError, ValueError):
            continue
        if IGNORAR_NOME.search(rel):
            continue
        try:
            dados = arq.read_bytes()
        except OSError:
            continue
        if b"\x00" in dados[:8192]:
            continue
        try:
            texto = dados.decode("utf-8")
        except UnicodeDecodeError:
            continue
        conferidos += 1
        linhas = texto.splitlines()
        for rx, rotulo in compilados:
            for i, linha in enumerate(linhas, 1):
                for m in rx.finditer(linha):
                    trecho = linha
                    if PLACEHOLDER.search(m.group(0)) or PLACEHOLDER.search(trecho[:120]):
                        avisos.append({"arquivo": rel, "linha": i, "tipo": rotulo,
                                        "motivo": "parece placeholder"})
                        continue
                    problemas.append({
                        "arquivo": rel, "linha": i, "tipo": rotulo,
                        "valor": m.group(0)[:12] + "…",
                    })

    # dedupe por (arquivo, linha) mantendo o primeiro tipo
    vistos: set[tuple[str, int]] = set()
    unicos = []
    for p in problemas:
        k = (p["arquivo"], p["linha"])
        if k not in vistos:
            vistos.add(k)
            unicos.append(p)
    problemas = unicos

    if args.json:
        print(json.dumps({"ok": not problemas, "conferidos": conferidos,
                          "problemas": problemas, "avisos": avisos[:20]},
                         ensure_ascii=False, indent=2))
    else:
        print(f"arquivos versionados conferidos: {conferidos}")
        for p in problemas:
            print(f"SEGREDO: {p['arquivo']}:{p['linha']}: {p['tipo']} ({p['valor']})")
        if args.avisos and avisos:
            for a in avisos[:10]:
                print(f"aviso    : {a['arquivo']}:{a['linha']}: {a['tipo']} -- {a['motivo']}")
        if not problemas:
            print("nenhuma credencial em formato reconhecido no conteudo versionado")

    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
