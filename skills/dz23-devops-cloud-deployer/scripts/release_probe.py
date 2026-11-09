#!/usr/bin/env python3
# Minimal reimplementation — o helper original do Manus (sandbox /home/ubuntu/)
# não está acessível. Este arquivo reproduz o comportamento descrito em
# _sources/manus-verification.md.
# Para a versão completa, ver README da skill.
"""Sonda de health/readiness pós-deploy.

Uso:
    python scripts/release_probe.py --url https://app.exemplo.com/healthz \
        --expect-revision <git_sha> [--allow-host app.exemplo.com] [--out probe.json]

Exit 0 = PASS · 1 = FAIL · 2 = input inválido.
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import stat
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

MAX_BODY = 256 * 1024
DEFAULT_TIMEOUT = 10.0


def fail(msg: str, code: int = 1) -> "NoReturn":  # type: ignore[name-defined]
    print(f"FAIL {msg}")
    raise SystemExit(code)


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Probe de /healthz e /readyz pós-deploy.")
    ap.add_argument("--url", required=True, help="URL absoluta http(s) do endpoint de health")
    ap.add_argument("--expect-revision", required=True, help="git_sha esperado na resposta")
    ap.add_argument("--allow-host", action="append", default=[], help="host permitido (repetível)")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--out", default="", help="arquivo de saída (0600) para o resumo")
    return ap.parse_args(argv)


def validate(args: argparse.Namespace) -> urllib.parse.SplitResult:
    parsed = urllib.parse.urlparse(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        fail("URL inválida: use http(s)://host/caminho", 2)
    if parsed.username or parsed.password:
        fail("credencial embutida na URL é proibida", 2)
    if parsed.query:
        fail("query string não é permitida", 2)
    allow = {h.lower() for h in args.allow_host}
    if not allow:
        fail("--allow-host é obrigatório (allowlist de origin)", 2)
    if parsed.hostname.lower() not in allow:
        fail(f"host não autorizado: {parsed.hostname}", 2)
    if args.timeout <= 0 or args.timeout > 60:
        fail("--timeout deve estar entre 0 e 60 s", 2)
    if args.retries < 0 or args.retries > 5:
        fail("--retries deve estar entre 0 e 5", 2)
    return parsed


def probe(url: str, timeout: float) -> tuple[int, str, str]:
    req = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:  # noqa: S310
            body = resp.read(MAX_BODY + 1)
            if len(body) > MAX_BODY:
                fail(f"corpo acima do limite ({MAX_BODY} bytes)")
            return resp.status, resp.headers.get("Content-Type", ""), body.decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        fail(f"HTTP {exc.code}")
    except urllib.error.URLError as exc:
        fail(f"falha de rede/TLS: {exc.reason}")
    except TimeoutError:
        fail("timeout")
    raise SystemExit(1)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    validate(args)

    status, ctype, body = probe(args.url, args.timeout)
    if status != 200:
        fail(f"HTTP {status} (esperado 200)")
    if "json" not in (ctype or "").lower():
        fail(f"media type inesperado: {ctype or '(vazio)'}")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        fail("JSON inválido")
    if not isinstance(payload, dict):
        fail("JSON raiz não é objeto")

    ready = payload.get("ready", payload.get("readiness"))
    if ready is not True:
        fail(f"readiness não é booleano true: {ready!r}")
    revision = payload.get("revision") or payload.get("git_sha") or payload.get("version")
    if not isinstance(revision, str) or revision != args.expect_revision:
        fail(f"revision divergente: esperado {args.expect_revision!r}, recebido {revision!r}")

    summary = {"url": args.url, "status": status, "ready": True, "revision": revision}
    print("PASS " + json.dumps(summary))

    if args.out:
        out_path = os.path.abspath(args.out)
        parent = os.path.dirname(out_path) or "."
        os.makedirs(parent, mode=0o700, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=parent)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)  # 0600
        os.replace(tmp, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
