#!/usr/bin/env python3
"""dz23-install.py -- instalador multiplataforma das skills DZ23 (mandato, layer install/).

Windows, Linux e macOS num só arquivo (Python stdlib puro, zero rede). O que os install-all.sh/
.ps1 simples não têm e o mandato exige: detecção de dependências, modo offline comprovado, dry-run,
log sem segredos, e ROLLBACK preciso (manifesto do que foi instalado -> remove exatamente isso).

Offline por construção: só copia arquivos do checkout para o destino; nunca abre rede. Rollback só
remove o que o próprio install registrou no manifesto -- nunca apaga skill que não instalou.

Subcomandos:
    python scripts/dz23-install.py detect                      # dependências AVAILABLE/UNAVAILABLE
    python scripts/dz23-install.py install [--dry-run] [--force] [--dest DIR]
    python scripts/dz23-install.py rollback [--dry-run] [--dest DIR]
    python scripts/dz23-install.py --selftest                  # exercita install+rollback em tmp
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "skills"
MANIFESTO = ".dz23-install-manifest.json"
PONTEIRO = ".dz23-arsenal"
LOG = ".dz23-install.log"
DEPS = [("python", [sys.executable]), ("git", ["git"]), ("node", ["node"]), ("pwsh", ["pwsh"])]


def _dest_padrao() -> Path:
    return Path.home() / ".agents" / "skills"


def _log(dest: Path, linha: str, dry: bool) -> None:
    """Log sem segredos: só nomes de skill, contagens e tempo. Nunca env/token/caminho de home
    de terceiro -- apenas o destino já conhecido pelo usuário."""
    if dry:
        return
    try:
        with (dest / LOG).open("a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now(timezone.utc).isoformat()} {linha}\n")
    except OSError:
        pass


def detect() -> int:
    print("Dependências (AVAILABLE = encontrada no PATH):")
    for nome, cmd in DEPS:
        achado = shutil.which(cmd[0]) if cmd[0] != sys.executable else sys.executable
        estado = "AVAILABLE" if achado else "UNAVAILABLE"
        print(f"  {nome:<8} {estado:<12} {achado or '(ausente no PATH)'}")
    print("\nInstalação é OFFLINE: apenas cópia de arquivos, nenhuma rede. "
          "Só 'python' é obrigatório para rodar este instalador.")
    return 0


def _skills_do_repo() -> list[Path]:
    return sorted(p for p in SKILLS.iterdir() if p.is_dir()) if SKILLS.is_dir() else []


def install(dest: Path, dry: bool, force: bool) -> int:
    if not SKILLS.is_dir():
        print(f"ERRO: pasta de skills ausente: {SKILLS}", file=sys.stderr)
        return 1
    if not dest.exists():
        print(f"[dry-run] criaria {dest}" if dry else f"Criar: {dest}")
        if not dry:
            dest.mkdir(parents=True, exist_ok=True)

    instaladas: list[str] = []
    puladas = falhas = 0
    for sk in _skills_do_repo():
        nome = sk.name
        alvo = dest / nome
        if alvo.exists() and not force:
            print(f"SKIP (já existe): {nome}")
            puladas += 1
            continue
        if dry:
            print(f"[dry-run] copiaria {nome} -> {alvo}")
            continue
        try:
            if alvo.exists():
                shutil.rmtree(alvo)
            shutil.copytree(sk, alvo, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            print(f"OK: {nome}")
            instaladas.append(nome)
        except OSError as exc:
            print(f"FALHA: {nome} -> {exc}", file=sys.stderr)
            falhas += 1

    if not dry:
        (dest / PONTEIRO).write_text(str(RAIZ) + "\n", encoding="utf-8")
        # Manifesto = TODAS as skills geridas presentes no destino agora (recém-copiadas + as que
        # já estavam), não só as desta execução. Assim um segundo install idempotente não apaga o
        # registro, e o rollback remove o conjunto gerido completo. (Bug pego pelo selftest.)
        presentes = [sk.name for sk in _skills_do_repo() if (dest / sk.name).is_dir()]
        manifesto = {
            "versao": 1,
            "raiz": str(RAIZ),
            "data": datetime.now(timezone.utc).isoformat(),
            "ponteiro": PONTEIRO,
            "instaladas": presentes,
        }
        (dest / MANIFESTO).write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
        _log(dest, f"install instaladas={len(instaladas)} puladas={puladas} falhas={falhas}", dry)

    print(f"\nInstaladas: {len(instaladas)} | Puladas: {puladas} | Falhas: {falhas}")
    if not dry:
        print(f"Manifesto: {dest / MANIFESTO}  (rollback: python scripts/dz23-install.py rollback)")
    return 1 if falhas else 0


def rollback(dest: Path, dry: bool) -> int:
    mf = dest / MANIFESTO
    if not mf.is_file():
        print(f"Nada a reverter: {mf} ausente (nenhuma instalação registrada)")
        return 0
    dados = json.loads(mf.read_text(encoding="utf-8"))
    alvos = list(dados.get("instaladas") or [])
    removidas = 0
    for nome in alvos:
        alvo = dest / nome
        if not alvo.exists():
            continue
        if dry:
            print(f"[dry-run] removeria {alvo}")
            continue
        shutil.rmtree(alvo, ignore_errors=True)
        print(f"removida: {nome}")
        removidas += 1
    for extra in (PONTEIRO, LOG, MANIFESTO):
        p = dest / extra
        if p.exists():
            print(f"[dry-run] removeria {p}" if dry else f"removida: {extra}")
            if not dry:
                p.unlink()
    print(f"\nRevertidas {removidas}/{len(alvos)} skills registradas.")
    return 0


def _selftest() -> int:
    tmp = Path(tempfile.mkdtemp())
    dest = tmp / "skills"
    esperado = [p.name for p in _skills_do_repo()]
    if not esperado:
        print("FALHA selftest: repo sem skills para instalar")
        return 1

    # 1. dry-run não cria nada
    install(dest, dry=True, force=False)
    if dest.exists() and any(dest.iterdir()):
        print("FALHA selftest: dry-run criou arquivos")
        return 1

    # 2. install real popula destino + manifesto coerente + log sem segredo
    install(dest, dry=False, force=False)
    faltando = [n for n in esperado if not (dest / n).is_dir()]
    if faltando:
        print(f"FALHA selftest: skills não instaladas: {faltando}")
        return 1
    mf = json.loads((dest / MANIFESTO).read_text(encoding="utf-8"))
    if sorted(mf["instaladas"]) != sorted(esperado):
        print("FALHA selftest: manifesto não bate com o instalado")
        return 1
    if list((dest).rglob("__pycache__")) or list(dest.rglob("*.pyc")):
        print("FALHA selftest: bytecode copiado para o destino")
        return 1
    log_txt = (dest / LOG).read_text(encoding="utf-8").lower()
    for proibido in ("token", "senha", "secret", "api_key", "password"):
        if proibido in log_txt:
            print(f"FALHA selftest: log contém termo sensível {proibido!r}")
            return 1

    # 3. install idempotente: segunda vez pula tudo (sem --force)
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        install(dest, dry=False, force=False)
    if "Instaladas: 0" not in buf.getvalue():
        print("FALHA selftest: segundo install não foi idempotente")
        return 1

    # 4. rollback remove exatamente o registrado e limpa manifesto/ponteiro/log
    rollback(dest, dry=False)
    sobrou = [n for n in esperado if (dest / n).exists()]
    if sobrou:
        print(f"FALHA selftest: rollback deixou skills: {sobrou}")
        return 1
    if (dest / MANIFESTO).exists() or (dest / PONTEIRO).exists():
        print("FALHA selftest: rollback não limpou manifesto/ponteiro")
        return 1

    # 5. rollback sem manifesto é no-op seguro
    if rollback(dest, dry=False) != 0:
        print("FALHA selftest: rollback sem manifesto deveria ser no-op")
        return 1

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"OK selftest: dry-run inócuo, install de {len(esperado)} skills, manifesto coerente, "
          "log sem segredo, idempotência, rollback preciso, no-op seguro")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Instalador multiplataforma das skills DZ23.")
    ap.add_argument("--selftest", action="store_true", help="exercita install+rollback em tmp")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("detect")
    pi = sub.add_parser("install")
    pi.add_argument("--dry-run", action="store_true")
    pi.add_argument("--force", action="store_true")
    pi.add_argument("--dest")
    pr = sub.add_parser("rollback")
    pr.add_argument("--dry-run", action="store_true")
    pr.add_argument("--dest")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()
    if args.cmd == "detect":
        return detect()
    if args.cmd == "install":
        return install(Path(args.dest) if args.dest else _dest_padrao(),
                       bool(args.dry_run), bool(args.force))
    if args.cmd == "rollback":
        return rollback(Path(args.dest) if args.dest else _dest_padrao(), bool(args.dry_run))
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
