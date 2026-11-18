#!/usr/bin/env python3
"""quality-gate.py — roda todos os checks do arsenal. Um comando, um veredito.

Uso:
    python scripts/quality-gate.py            # relatório legível
    python scripts/quality-gate.py --json     # saída para CI
    python scripts/quality-gate.py --fix      # regenera manifesto/índice antes de checar

Exit: 0 = tudo passou · 1 = alguma falha · 2 = erro de ambiente
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def rodar(nome: str, cmd: list[str]) -> dict:
    try:
        p = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, timeout=300)
        saida = (p.stdout or "").strip().splitlines()
        erro = (p.stderr or "").strip().splitlines()
        return {
            "check": nome,
            "ok": p.returncode == 0,
            "exit": p.returncode,
            "resumo": saida[-1] if saida else (erro[-1] if erro else ""),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"check": nome, "ok": False, "exit": -1, "resumo": f"erro: {exc}"}


def validar_skills(py: str) -> list[dict]:
    """Roda o validate_skill.py de cada skill que tiver um.

    Skill sem validador NÃO é "passou": é cobertura ausente. Antes isto devolvia
    ok=True com "sem validate_skill.py (pulado)", então a skill mais importante do
    arsenal (a de loop autônomo) podia degradar silenciosamente sem quebrar o CI.
    """
    resultados = []
    for skill in sorted(p for p in (RAIZ / "skills").iterdir() if p.is_dir()):
        v = skill / "scripts" / "validate_skill.py"
        if not v.is_file():
            resultados.append({
                "check": f"validate:{skill.name}",
                "ok": False,
                "exit": 1,
                "resumo": "sem validate_skill.py — cobertura ausente, não é aprovação",
            })
            continue
        r = rodar(f"validate:{skill.name}", [py, str(v)])
        resultados.append(r)
    return resultados


def total_de_checks_gerado() -> int | None:
    """Última contagem real produzida pelo próprio gate, lida de .gate-contagem.

    O check-numbers precisa saber quantos checks existem para conferir a documentação, mas
    não pode chamar o gate (recursão: ele é um dos checks) nem parsear este fonte (um
    parser de Python por regex contou 24 contra 31 reais — silenciosamente errado). Então
    o gate publica o número quando roda, e o conferidor lê o que foi medido. Se o arquivo
    não existe, devolve None e a regra de contagem é pulada — ausência nunca vira 0.
    """
    arq = RAIZ / ".gate-contagem"
    if not arq.is_file():
        return None
    try:
        dados = json.loads(arq.read_text(encoding="utf-8"))
        n = dados.get("total")
        return int(n) if isinstance(n, int) and n > 0 else None
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return None


def publicar_contagem(total: int) -> None:
    try:
        (RAIZ / ".gate-contagem").write_text(
            json.dumps({"total": total}, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")
    except OSError:
        pass  # contagem é conveniência; falhar o gate por isso seria ridículo


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args(argv)

    py = sys.executable
    resultados: list[dict] = []

    if args.fix:
        resultados.append(rodar("manifesto:gerar", [py, "scripts/build-manifest.py"]))

    resultados += validar_skills(py)
    resultados.append(rodar("manifesto:check", [py, "scripts/build-manifest.py", "--check"]))
    resultados.append(rodar("numeros", [py, "scripts/check-numbers.py"]))
    resultados.append(rodar("links", [py, "scripts/check-links.py", "."]))
    resultados.append(rodar("estrutura", [py, "scripts/check-structure.py"]))
    resultados.append(rodar("licencas", [py, "scripts/check-licenses.py"]))
    resultados.append(rodar("evals:coerencia", [py, "scripts/run-evals.py", "--check"]))
    resultados.append(rodar("evals:schema", [py, "scripts/run-evals.py", "--schema"]))
    resultados.append(rodar("evals:registros", [py, "scripts/check-eval-results.py"]))
    resultados.append(rodar("evals:citacoes", [py, "scripts/run-evals.py", "--verify-quotes"]))
    # Auto-testes dos instrumentos novos: se o verificador quebrar, o gate avisa antes de
    # alguém confiar num passRate errado.
    resultados.append(rodar("gate:autoteste", [py, "scripts/gate_candidatos.py", "--selftest"]))
    resultados.append(rodar("claims:autoteste", [py, "scripts/verifica_claims.py", "--selftest"]))
    # Referências citadas nos SKILL.md têm de existir. Roda sobre as 10 skills; --min não é
    # usado aqui porque um caminho quebrado já é falha por si só (exit 1 quando há falho).
    for skill in sorted(p for p in (RAIZ / "skills").iterdir() if p.is_dir()):
        sm = skill / "SKILL.md"
        if sm.is_file():
            resultados.append(rodar(f"claims:{skill.name}",
                                    [py, "scripts/verifica_claims.py",
                                     "--texto", str(sm), "--raiz", str(RAIZ)]))

    falhas = [r for r in resultados if not r["ok"]]
    publicar_contagem(len(resultados))
    if args.json:
        print(json.dumps({"ok": not falhas, "total": len(resultados),
                          "falhas": len(falhas), "checks": resultados}, indent=2, ensure_ascii=False))
        return 0 if not falhas else 1

    print("# Quality gate — dz23-arsenal\n")
    print(f"{'check':<42}{'resultado':<10}resumo")
    print("-" * 100)
    for r in resultados:
        marca = "OK" if r["ok"] else "FALHA"
        print(f"{r['check']:<42}{marca:<10}{r['resumo'][:52]}")
    print()
    print(f"{len(resultados) - len(falhas)}/{len(resultados)} checks passaram")
    if falhas:
        print("\nFALHAS:")
        for r in falhas:
            print(f"  - {r['check']}: {r['resumo']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
