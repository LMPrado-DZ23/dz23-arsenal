#!/usr/bin/env python3
# Minimal reimplementation — o helper original do Manus (sandbox
# /home/ubuntu/) não está acessível. Este arquivo reproduz o
# comportamento descrito em _sources/manus-verification.md.
# Para a versão completa (36 testes), ver README da skill.
"""Inventário de arquivos rastreados pelo Git — só metadata, nunca conteúdo.

Não abre arquivo, não executa código do repositório, não acessa rede.
Não é snapshot atômico (`atomic_snapshot=false`) e não avalia working tree
(`dirty_state=NOT_ASSESSED`).

Uso:
    python scripts/repo_inventory.py <path-do-repo> [--out inventory.json]
                                     [--untracked] [--force]

Exit 0 = inventário gerado
Exit 1 = INVENTORY_PARTIAL (limite atingido / entrada parcial)
Exit 2 = input inválido
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

MAX_ENTRIES = 50_000

# Excluídos mesmo se rastreados: nomes sensíveis ou gerados.
SENSITIVE_TOKENS = (
    ".env", "credentials", "credential", "secret", "token", ".pem", ".key", ".p12",
    ".pfx", "id_rsa", "state", ".tfstate", "dump", ".sql.gz",
)
GENERATED_DIRS = (
    "node_modules", "dist", "build", ".next", "coverage", "vendor", ".venv", "__pycache__",
)


def fail(msg: str, code: int) -> "NoReturn":  # type: ignore[name-defined]
    print(f"INVALID {msg}", file=sys.stderr)
    raise SystemExit(code)


def is_excluded(path: str) -> bool:
    low = path.lower()
    parts = low.replace("\\", "/").split("/")
    if any(d in parts for d in GENERATED_DIRS):
        return True
    name = parts[-1] if parts else ""
    return any(tok in name for tok in SENSITIVE_TOKENS)


def check_path(root: Path) -> None:
    if not root.exists():
        fail(f"path não existe: {root}", 2)
    if not root.is_dir():
        fail(f"path não é diretório: {root}", 2)
    if os.path.islink(root):
        fail("path é symlink", 2)
    probe = root / ".git"
    if not probe.exists():
        fail(f"não é repositório git: {root}", 2)


def git(root: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=60, check=False,
        )
        return out.stdout if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def list_files(root: Path, untracked: bool) -> list[str]:
    args = ["ls-files"] if not untracked else ["ls-files", "--cached", "--others", "--exclude-standard"]
    out = git(root, *args)
    if out is None:
        fail("git ls-files falhou", 1)
    return [line for line in out.splitlines() if line.strip()]


def write_json(out: Path, payload: dict, force: bool) -> None:
    parent = out.parent
    parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(parent, 0o700)
    except OSError:
        pass
    if out.exists() and not force:
        fail(f"saída já existe (use --force): {out}", 2)
    tmp = parent / (out.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Inventário de arquivos Git (metadata only).")
    ap.add_argument("path", help="diretório do repositório")
    ap.add_argument("--out", default="", help="arquivo JSON de saída (default: stdout)")
    ap.add_argument("--untracked", action="store_true", help="inclui arquivos não rastreados")
    ap.add_argument("--force", action="store_true", help="sobrescreve saída existente")
    args = ap.parse_args(argv)

    root = Path(args.path).resolve()
    check_path(root)

    files = list_files(root, args.untracked)
    partial = False
    if len(files) > MAX_ENTRIES:
        files = files[:MAX_ENTRIES]
        partial = True

    entries = []
    excluded = 0
    for rel in files:
        if is_excluded(rel):
            excluded += 1
            continue
        full = root / rel
        size = None
        try:
            size = full.stat().st_size
        except OSError:
            partial = True
        # metadata apenas: path + tamanho. Nenhuma leitura de conteúdo.
        entries.append({"path": rel, "size": size})

    payload = {
        "repo": str(root),
        "commit": (git(root, "rev-parse", "HEAD") or "").strip() or None,
        "branch": (git(root, "branch", "--show-current") or "").strip() or None,
        "mode": "untracked+tracked" if args.untracked else "tracked",
        "file_count": len(entries),
        "excluded_count": excluded,
        "files": entries,
        "atomic_snapshot": False,
        "dirty_state": "NOT_ASSESSED",
        "content_read": False,
        "partial": partial,
        "limits": {"max_entries": MAX_ENTRIES},
    }

    if args.out:
        write_json(Path(args.out).resolve(), payload, args.force)
        print(f"INVENTORY_WRITTEN {args.out}")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    print("atomic_snapshot=false dirty_state=NOT_ASSESSED content_read=false")
    if partial:
        print(f"INVENTORY_PARTIAL files={len(entries)} excluded={excluded}")
        return 1
    print(f"INVENTORY_OK files={len(entries)} excluded={excluded}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
