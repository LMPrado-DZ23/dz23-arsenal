#!/usr/bin/env python3
"""Scanner read-only de repositório para o codebase map.

Não modifica nada, não executa código do repositório, não acessa rede.

Uso:
    python scripts/repo_probe.py <path-do-repo> [--json] [--max-files N]

Exit 0 = relatório gerado · 1 = path inválido · 2 = uso inválido
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv",
    "__pycache__", ".next", ".nuxt", ".turbo", ".cache", "coverage", "out", ".idea",
}
LANG_BY_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
    ".py": "Python", ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin",
    ".cs": "C#", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift", ".c": "C",
    ".cpp": "C++", ".h": "C/C++", ".sql": "SQL", ".sh": "Shell", ".ps1": "PowerShell",
}
MANIFESTS = [
    "package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml",
    "pom.xml", "build.gradle", "composer.json", "Gemfile", "*.csproj", "mix.exs",
]
RUNTIME_FILES = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml",
                 "Procfile", "vercel.json", "fly.toml", "netlify.toml"]
CI_DIRS = [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", ".circleci", "azure-pipelines.yml"]
TEST_HINTS = ("test", "spec", "e2e", "__tests__", "playwright.config", "jest.config", "vitest.config")
MIGRATION_DIRS = ["migrations", "migrate", "alembic", "db/migrate", "prisma/migrations", "sql/migrations"]


def git(path: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(path), *args],
            capture_output=True, text=True, timeout=20, check=False,
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def walk(path: Path, max_files: int) -> list[Path]:
    files: list[Path] = []
    for root, dirs, names in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in names:
            files.append(Path(root) / name)
            if len(files) >= max_files:
                return files
    return files


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Scanner read-only de repositório.")
    ap.add_argument("path", help="diretório do repositório")
    ap.add_argument("--json", action="store_true", help="saída JSON")
    ap.add_argument("--max-files", type=int, default=20000, help="teto de arquivos varridos")
    args = ap.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"INVALID path não é diretório: {root}", file=sys.stderr)
        return 1
    if args.max_files <= 0:
        print("INVALID --max-files deve ser positivo", file=sys.stderr)
        return 2

    files = walk(root, args.max_files)
    lang = Counter()
    lines_total = 0
    sizes: list[tuple[int, str]] = []
    for f in files:
        suffix = f.suffix.lower()
        if suffix in LANG_BY_EXT:
            lang[LANG_BY_EXT[suffix]] += 1
        try:
            size = f.stat().st_size
        except OSError:
            continue
        sizes.append((size, str(f.relative_to(root))))
        if suffix in LANG_BY_EXT and size < 2_000_000:
            try:
                lines_total += f.read_text(encoding="utf-8", errors="ignore").count("\n")
            except OSError:
                pass

    manifests = [p for m in MANIFESTS for p in root.glob(m)]
    runtime = [p.name for p in root.glob("*") if p.name in RUNTIME_FILES]
    ci = [str(p.relative_to(root)) for c in CI_DIRS for p in root.glob(c)]
    tests = [str(f.relative_to(root)) for f in files if any(h in str(f).lower() for h in TEST_HINTS)][:40]
    migrations = [m for m in MIGRATION_DIRS if (root / m).is_dir()]

    entry_candidates: list[str] = []
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            main = data.get("main")
            if main:
                entry_candidates.append(f"package.json:main → {main}")
            for name, cmd in (data.get("scripts") or {}).items():
                if name in ("start", "dev", "serve"):
                    entry_candidates.append(f"package.json:scripts.{name} → {cmd}")
        except (ValueError, OSError):
            entry_candidates.append("package.json ilegível")
    for cand in ("src/main.ts", "src/index.ts", "src/app.ts", "src/server.ts", "index.js",
                 "src/index.js", "src/main.tsx", "src/App.tsx",
                 "main.py", "app.py", "server.py", "manage.py", "wsgi.py", "asgi.py",
                 "app/main.py", "src/main.py",
                 "cmd/main.go", "main.go", "src/main.rs"):
        if (root / cand).is_file():
            entry_candidates.append(cand)

    report = {
        "repo": str(root),
        "commit": git(root, "rev-parse", "HEAD"),
        "branch": git(root, "branch", "--show-current"),
        "tracked_files": int(git(root, "ls-files") .count("\n") + 1) if git(root, "ls-files") else None,
        "scanned_files": len(files),
        "hit_file_cap": len(files) >= args.max_files,
        "lines_scanned": lines_total,
        "languages": dict(lang.most_common()),
        "manifests": [p.name for p in manifests],
        "runtime": runtime,
        "ci": ci,
        "migrations": migrations,
        "test_files_sample": tests,
        "entry_candidates": entry_candidates,
        "largest_files": [{"path": p, "bytes": s} for s, p in sorted(sizes, reverse=True)[:10]],
        "read_only": True,
        "executed_code": False,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0

    print(f"repo      : {report['repo']}")
    print(f"commit    : {report['commit'] or '(não é repo git)'}  branch: {report['branch'] or '-'}")
    print(f"arquivos  : {report['scanned_files']} varridos" + (" (teto atingido)" if report["hit_file_cap"] else ""))
    print(f"linhas    : {report['lines_scanned']}")
    print(f"linguagens: {', '.join(f'{k}({v})' for k, v in report['languages'].items()) or 'nenhuma detectada'}")
    print(f"manifests : {', '.join(report['manifests']) or 'nenhum'}")
    print(f"runtime   : {', '.join(report['runtime']) or 'nenhum'}")
    print(f"CI        : {', '.join(report['ci']) or 'nenhum'}")
    print(f"migrações : {', '.join(report['migrations']) or 'nenhuma'}")
    print(f"testes    : {len(tests)} arquivos (amostra)")
    print(f"entry     : {', '.join(report['entry_candidates']) or 'não identificado'}")
    print("\nmaiores:")
    for item in report["largest_files"][:5]:
        print(f"  {item['bytes']:>9} B  {item['path']}")
    print("\nREAD_ONLY=true EXECUTED_CODE=false")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
