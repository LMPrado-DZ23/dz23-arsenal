#!/usr/bin/env python3
"""Sonda HTTP read-only de performance: TTFB, bytes, compressão, cache e CDN.

Não envia payload de escrita, não executa JavaScript, não interpreta o corpo
como instrução. Serve para o baseline da camada 4 (infra) e parte da 2 (rede).

Uso:
    python scripts/web_vitals_probe.py <url> [--json] [--allow-host HOST]...
                                          [--timeout S] [--runs N]

Exit 0 = todos os achados OK
Exit 1 = achado de performance (sem compressão, sem cache, TTFB alto)
Exit 2 = input inválido
"""
from __future__ import annotations

import argparse
import json
import ssl
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

MAX_BODY = 512 * 1024
TTFB_BUDGET_MS = 800.0


def fail(msg: str, code: int = 2) -> "NoReturn":  # type: ignore[name-defined]
    print(f"INVALID {msg}", file=sys.stderr)
    raise SystemExit(code)


def probe(url: str, timeout: float) -> dict:
    req = urllib.request.Request(url, method="GET", headers={
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "br, gzip, deflate",
        "User-Agent": "dz23-perf-probe/1.0",
    })
    kwargs: dict = {"timeout": timeout}
    if urllib.parse.urlparse(url).scheme == "https":
        kwargs["context"] = ssl.create_default_context()
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, **kwargs) as resp:  # noqa: S310
            ttfb = (time.perf_counter() - start) * 1000
            body = resp.read(MAX_BODY)
            total = (time.perf_counter() - start) * 1000
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return {
                "status": resp.status,
                "ttfb_ms": round(ttfb, 1),
                "total_ms": round(total, 1),
                "bytes_read": len(body),
                "content_type": headers.get("content-type", ""),
                "content_encoding": headers.get("content-encoding", ""),
                "content_length": headers.get("content-length", ""),
                "cache_control": headers.get("cache-control", ""),
                "etag": headers.get("etag", ""),
                "vary": headers.get("vary", ""),
                "server": headers.get("server", ""),
                "via": headers.get("via", ""),
                "cdn_hints": [h for h in ("cf-ray", "x-vercel-id", "x-cache", "x-served-by", "age")
                              if h in headers],
            }
    except urllib.error.HTTPError as exc:
        return {"status": exc.code, "error": f"HTTP {exc.code}"}
    except urllib.error.URLError as exc:
        return {"error": f"rede/TLS: {exc.reason}"}
    except TimeoutError:
        return {"error": "timeout"}


def evaluate(result: dict) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    if "error" in result:
        findings.append(("FAIL", f"requisição falhou: {result['error']}"))
        return findings

    ttfb = result["ttfb_ms"]
    findings.append(("PASS" if ttfb <= TTFB_BUDGET_MS else "FAIL",
                     f"TTFB {ttfb:.1f} ms (budget ≤ {TTFB_BUDGET_MS:.0f} ms)"))

    ctype = result.get("content_type", "")
    compressible = any(t in ctype for t in ("text/", "javascript", "json", "svg"))
    enc = result.get("content_encoding", "")
    if compressible:
        findings.append(("PASS" if enc else "FAIL",
                         f"compressão: '{enc or 'nenhuma'}'"
                         + ("" if enc else " — texto sem Brotli/GZIP")))
        if enc and "vary" not in result or (enc and "accept-encoding" not in result.get("vary", "").lower()):
            if enc:
                findings.append(("WARN", f"Vary sem Accept-Encoding: '{result.get('vary') or 'ausente'}'"))

    cache = result.get("cache_control", "")
    etag = result.get("etag", "")
    if cache:
        findings.append(("PASS", f"cache-control: {cache}"))
    elif etag:
        findings.append(("WARN", "sem cache-control; só ETag (revalida em toda visita)"))
    else:
        findings.append(("FAIL", "sem cache-control e sem ETag"))

    hints = result.get("cdn_hints", [])
    if hints:
        findings.append(("PASS", f"indício de CDN: {', '.join(hints)}"))
    else:
        findings.append(("WARN", "nenhum header de CDN detectado"))

    return findings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Sonda HTTP read-only de performance.")
    ap.add_argument("url", help="URL http(s)")
    ap.add_argument("--json", action="store_true", help="saída JSON")
    ap.add_argument("--allow-host", action="append", default=[], help="hosts permitidos (repetível)")
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--runs", type=int, default=1, help="nº de requisições para p50/p95")
    args = ap.parse_args(argv)

    parsed = urllib.parse.urlparse(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        fail("URL inválida: use http(s)://host/caminho")
    if parsed.username or parsed.password:
        fail("credencial embutida na URL é proibida")
    allow = {h.lower() for h in args.allow_host}
    if allow and parsed.hostname.lower() not in allow:
        fail(f"host não autorizado: {parsed.hostname}")
    if args.timeout <= 0 or args.timeout > 120:
        fail("--timeout deve estar entre 0 e 120 s")
    if args.runs < 1 or args.runs > 20:
        fail("--runs deve estar entre 1 e 20")

    runs = [probe(args.url, args.timeout) for _ in range(args.runs)]
    last = runs[-1]
    findings = evaluate(last)

    payload = {
        "url": args.url,
        "runs": args.runs,
        "result": last,
        "findings": [{"state": s, "detail": d} for s, d in findings],
        "executed_javascript": False,
        "sent_write_payload": False,
    }

    if args.runs > 1:
        ttfb = [r["ttfb_ms"] for r in runs if "ttfb_ms" in r]
        if len(ttfb) > 1:
            payload["ttfb_p50_ms"] = round(statistics.median(ttfb), 1)
            payload["ttfb_p95_ms"] = round(sorted(ttfb)[max(0, int(len(ttfb) * 0.95) - 1)], 1)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"url       : {args.url}")
        print(f"status    : {last.get('status', '—')}")
        print(f"ttfb      : {last.get('ttfb_ms', '—')} ms · total: {last.get('total_ms', '—')} ms")
        print(f"bytes     : {last.get('bytes_read', '—')} (leitura limitada a {MAX_BODY})")
        print(f"encoding  : {last.get('content_encoding') or '(nenhum)'}")
        print(f"cache     : {last.get('cache_control') or '(nenhum)'}  etag: {last.get('etag') or '—'}")
        if payload.get("ttfb_p50_ms") is not None:
            print(f"p50/p95   : {payload['ttfb_p50_ms']} / {payload['ttfb_p95_ms']} ms")
        print("achados:")
        for state, detail in findings:
            print(f"  {state:<4} {detail}")
        print("executed_javascript=false sent_write_payload=false")

    return 1 if any(s == "FAIL" for s, _ in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
