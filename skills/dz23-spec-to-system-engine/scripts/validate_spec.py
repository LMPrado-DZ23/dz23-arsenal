#!/usr/bin/env python3
# Minimal reimplementation — o helper original do Manus (sandbox /home/ubuntu/)
# não está acessível. Este arquivo reproduz o comportamento descrito em
# _sources/manus-verification.md: valida estrutura, não semântica.
"""Valida um manifesto de spec (JSON) contra schema/spec.schema.json.

Uso:
    python scripts/validate_spec.py <manifest.json | pasta>

Exit 0 = SPEC_STRUCTURE_VALID
Exit 1 = erro de estrutura
Exit 2 = input inválido
Exit 3 = SPEC_STRUCTURE_BLOCKED (ambiguidade aberta)

Não executa texto, runner, source_ref ou action_ref. Não grava arquivo de
saída (nada de `--out`): apenas relata em stdout.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "spec.schema.json"
MAX_BYTES = 1024 * 1024  # 1 MiB
REDACTED = "<valor omitido>"

TRUTH = "behavior_verified=false authorization_granted=false runner_refs_verified=false"


def fail(msg: str, code: int) -> "NoReturn":  # type: ignore[name-defined]
    print(f"INVALID {msg}")
    raise SystemExit(code)


def no_dup_keys(pairs):
    seen = set()
    for key, _ in pairs:
        if key in seen:
            raise ValueError(f"chave duplicada: {key}")
        seen.add(key)
    return dict(pairs)


def reject_constants(token: str):
    raise ValueError(f"valor não finito: {token}")


def load_manifest(arg: str) -> Path:
    p = Path(arg)
    if p.is_dir():
        candidate = p / "REQUIREMENTS.json"
        if not candidate.is_file():
            fail(f"diretório sem REQUIREMENTS.json: {p}", 2)
        return candidate
    if not p.is_file():
        fail(f"arquivo não encontrado: {p}", 2)
    return p


def read_text(path: Path) -> str:
    if os.path.islink(path):
        fail("input é symlink", 2)
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        fail(f"não foi possível ler o tamanho do arquivo: {exc.strerror}", 2)
    if size > MAX_BYTES:
        fail(f"input > 1 MiB ({size} bytes)", 1)

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        # O_NOFOLLOW em symlink devolve ELOOP
        fail(f"não foi possível abrir o arquivo: {exc.strerror}", 2)
    with os.fdopen(fd, "r", encoding="utf-8") as handle:
        return handle.read()


def collect_ids(data: dict) -> list[str]:
    ids: list[str] = []
    for req in data.get("requirements", []) or []:
        if isinstance(req, dict):
            ids.append(str(req.get("id", "")))
            for ca in req.get("acceptance", []) or []:
                if isinstance(ca, dict):
                    ids.append(str(ca.get("id", "")))
    for task in data.get("tasks", []) or []:
        if isinstance(task, dict):
            ids.append(str(task.get("id", "")))
    return ids


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        fail("uso: validate_spec.py <manifest.json | pasta>", 2)

    path = load_manifest(argv[0])
    text = read_text(path)

    try:
        data = json.loads(text, object_pairs_hook=no_dup_keys, parse_constant=reject_constants)
    except ValueError as exc:
        fail(str(exc), 1)
    except json.JSONDecodeError as exc:
        fail(f"JSON inválido (linha {exc.lineno}, coluna {exc.colno})", 1)

    if not isinstance(data, dict):
        fail("JSON raiz não é objeto", 1)

    # boolean passa como integer em jsonschema — barrar explicitamente
    if isinstance(data.get("schema_version"), bool):
        fail("schema_version deve ser integer, não boolean", 1)

    # IDs nunca podem conter whitespace/newline
    for ident in collect_ids(data):
        if ident != ident.strip() or any(ch.isspace() for ch in ident):
            fail(f"ID contém whitespace/newline ({REDACTED})", 1)

    try:
        import jsonschema
    except ImportError:
        fail("dependência ausente: jsonschema (instale no venv do projeto)", 2)

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        for err in errors[:20]:
            where = "/".join(str(x) for x in err.path) or "<raiz>"
            print(f"INVALID {where}: {err.message}")
        raise SystemExit(1)

    reqs = data.get("requirements", [])
    tasks = data.get("tasks", [])

    req_ids = [r["id"] for r in reqs]
    task_ids = [t["id"] for t in tasks]
    if len(set(req_ids)) != len(req_ids):
        fail("IDs de requisito duplicados", 1)
    if len(set(task_ids)) != len(task_ids):
        fail("IDs de tarefa duplicados", 1)

    known_tasks = set(task_ids)
    for req in reqs:
        for tid in req.get("tasks", []):
            if tid not in known_tasks:
                fail(f"{req['id']} referencia tarefa inexistente ({REDACTED})", 1)

    referenced = {tid for req in reqs for tid in req.get("tasks", [])}
    orphans = [tid for tid in task_ids if tid not in referenced]
    for task in tasks:
        deps = task.get("depends_on", [])
        if task["id"] in deps:
            fail(f"auto-dependência em {task['id']} ({REDACTED})", 1)
        for dep in deps:
            if dep not in known_tasks:
                fail(f"{task['id']} depende de tarefa inexistente ({REDACTED})", 1)

    # ciclo no DAG — sem ecoar os valores dos IDs
    graph = {t["id"]: list(t.get("depends_on", [])) for t in tasks}
    order = {tid: idx + 1 for idx, tid in enumerate(task_ids)}
    state: dict[str, int] = {}

    def visit(node: str, depth: int) -> None:
        mark = state.get(node, 0)
        if mark == 1:
            fail(f"ciclo no DAG (nó #{order.get(node, '?')} repetido, profundidade {depth}) ({REDACTED})", 1)
        if mark == 2:
            return
        state[node] = 1
        for dep in graph.get(node, []):
            visit(dep, depth + 1)
        state[node] = 2

    for node in graph:
        visit(node, 0)

    blocked = [r["id"] for r in reqs if r.get("status") == "BLOCKED"]
    if blocked:
        print(f"SPEC_STRUCTURE_BLOCKED requisitos={len(blocked)} ({REDACTED})")
        print(TRUTH)
        print(f"orphan_tasks={len(orphans)}")
        raise SystemExit(3)

    print("SPEC_STRUCTURE_VALID")
    print(TRUTH)
    print(f"requirements={len(reqs)} tasks={len(tasks)} orphan_tasks={len(orphans)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
