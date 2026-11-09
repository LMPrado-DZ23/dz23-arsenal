#!/usr/bin/env python3
"""record-eval.py — registra a execução de um eval em evals-results/.

Uso:
    python scripts/record-eval.py \
      --skill dz23-devops-cloud-deployer \
      --eval-id secret-in-image \
      --verdict PASS \
      --response-file /tmp/resposta.txt \
      --method "execucao real com Docker" \
      --notes "build + docker history --no-trunc"

    # ou com a resposta inline
    python scripts/record-eval.py --skill ... --eval-id ... --verdict PARTIAL \
      --response "trecho da resposta" --note "contexto"

Regras embutidas:
  - `--verdict PASS` exige `--response`/`--response-file` e `--evidence` (trecho literal).
  - `NOT_RECOVERED` é aceito sem resposta: significa "não há artefato da execução".
  - `BLOCKED` exige `--blocked-by` (a dependência que falta).

Cria `evals-results/<skill-curto>/<data>-<eval-id>.md`. Nunca sobrescreve sem `--force`.

Exit: 0 ok · 1 entrada inválida · 2 eval id inexistente na skill
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ / "evals-results"

CURTO = {
    "dz23-autonomous-improvement-ultimate": "autonomous",
    "dz23-backend-data-architect": "backend",
    "dz23-codebase-cartographer": "cartographer",
    "dz23-devops-cloud-deployer": "devops",
    "dz23-e2e-browser-verifier": "e2e",
    "dz23-performance-scalability-engine": "performance",
    "dz23-reverse-engineer-anything": "reverse-engineer",
    "dz23-spec-to-system-engine": "spec",
    "dz23-ultimate-pro-max": "ultimate-pro-max",
}

MODELO = """# Eval: {eval_id}

- **Skill:** {skill} v{versao}
- **Data:** {data}
- **Método:** {metodo}
- **Veredito:** **{veredito}**

## Cenário

{input}

## Resposta

{resposta}

## Esperado

{expected}

## Falhas (fails_if)

{fails_if}

## Avaliação

- Aderência ao expected: {aderencia}
- Defeitos encontrados: {defeitos}
- Trecho literal: {trecho}

## Notas

{notas}
"""


def versao_da_skill(pasta: Path) -> str:
    v = pasta / "VERSION"
    if v.is_file():
        return v.read_text(encoding="utf-8", errors="replace").strip()
    s = pasta / "SKILL.md"
    if s.is_file():
        for linha in s.read_text(encoding="utf-8", errors="replace").splitlines()[:12]:
            if linha.lower().startswith("version:"):
                return linha.split(":", 1)[1].strip().strip('"\'')
    return "?"


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True, help="nome da pasta da skill")
    ap.add_argument("--eval-id", required=True)
    ap.add_argument("--verdict", required=True,
                    choices=["PASS", "PARTIAL", "FAIL", "NOT_TESTED", "BLOCKED", "NOT_RECOVERED"])
    ap.add_argument("--response", default=None, help="resposta do agente (texto)")
    ap.add_argument("--response-file", default=None, help="arquivo com a resposta")
    ap.add_argument("--method", default="execução manual (sessão de agente)")
    ap.add_argument("--evidence", default=None, help="trecho literal que sustenta o veredito")
    ap.add_argument("--defects", default="nenhum")
    ap.add_argument("--notes", "--note", dest="notes", default="")
    ap.add_argument("--blocked-by", default=None)
    ap.add_argument("--data", default=None, help="YYYY-MM-DD (default: hoje)")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    skill_dir = RAIZ / "skills" / args.skill
    if not skill_dir.is_dir():
        print(f"ERRO: skill inexistente: {args.skill}", file=sys.stderr)
        return 1
    evals_file = skill_dir / "evals" / "evals.json"
    if not evals_file.is_file():
        print(f"ERRO: {skill_dir.name} não tem evals/evals.json", file=sys.stderr)
        return 1
    dados = json.loads(evals_file.read_text(encoding="utf-8"))
    caso = next((c for c in dados["cases"] if c["id"] == args.eval_id), None)
    if caso is None:
        print(f"ERRO: eval '{args.eval_id}' não existe em {args.skill}", file=sys.stderr)
        return 2

    # regras de honestidade
    if args.verdict == "PASS" and not (args.response or args.response_file):
        print("ERRO: PASS exige --response ou --response-file (evidência da execução)", file=sys.stderr)
        return 1
    if args.verdict == "PASS" and not args.evidence:
        print("ERRO: PASS exige --evidence (trecho literal da resposta)", file=sys.stderr)
        return 1
    if args.verdict == "BLOCKED" and not args.blocked_by:
        print("ERRO: BLOCKED exige --blocked-by (a dependência ausente)", file=sys.stderr)
        return 1

    resposta = args.response
    if args.response_file:
        resposta = Path(args.response_file).read_text(encoding="utf-8", errors="replace")
    resposta = (resposta or "").strip() or "_(sem resposta registrada)_"

    aderencia = {"PASS": "sim", "PARTIAL": "parcial", "FAIL": "não"}.get(args.verdict, "não avaliada")
    trecho = args.evidence or "_(sem trecho literal — veredito sem evidência citável)_"
    notas = args.notes or "—"
    if args.verdict == "BLOCKED":
        notas = f"**BLOCKED_BY_EXTERNAL_DEPENDENCY:** {args.blocked_by}. " + notas
    if args.verdict == "NOT_RECOVERED":
        notas = ("Artefato da execução não está mais disponível. Registrado como não recuperado em vez de "
                 "reconstruído de memória. ") + notas

    data = args.data or date.today().isoformat()
    pasta = RESULTADOS / CURTO.get(args.skill, args.skill)
    pasta.mkdir(parents=True, exist_ok=True)
    alvo = pasta / f"{data}-{args.eval_id}.md"

    if alvo.exists() and not args.force:
        print(f"ERRO: {alvo.relative_to(RAIZ)} já existe. Use --force para sobrescrever (perde o histórico).",
              file=sys.stderr)
        return 1

    alvo.write_text(
        MODELO.format(
            eval_id=args.eval_id, skill=args.skill, versao=versao_da_skill(skill_dir), data=data,
            metodo=args.method, veredito=args.verdict, input=caso["input"], resposta=resposta,
            expected=caso["expected"], fails_if=caso["fails_if"],
            aderencia=aderencia, defeitos=args.defects,
            trecho=trecho, notas=notas,
        ),
        encoding="utf-8", newline="\n",
    )
    print(f"registrado: {alvo.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
