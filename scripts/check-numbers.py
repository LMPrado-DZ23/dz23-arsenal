#!/usr/bin/env python3
"""check-numbers.py — confere se os números escritos na documentação batem com o disco.

O arsenal tem histórico de divergir aqui: o README dizia "9 skills" com 10 no disco,
"16 checks" com 17 no gate, "45/131" quando são 144 declarados, e o ROADMAP repetia
"executados: 3" depois da tabela já atualizada para 45. Número digitado apodrece.

Este script não corrige nada: ele lê as fontes canônicas (arsenal.json, quality-gate,
run-evals --report) e falha quando a prosa afirma outro número.

Uso:
    python scripts/check-numbers.py            # exit 1 se houver divergência
    python scripts/check-numbers.py --json     # mesma coisa, saída máquina
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PY = sys.executable


def _num(texto: str, padrao: str) -> int | None:
    m = re.search(padrao, texto, re.I)
    return int(m.group(1)) if m else None


def _run(cmd: list[str]) -> str:
    """Roda um subprocesso lendo bytes e decodificando como UTF-8.

    `text=True` usaria a codepage do Windows (cp1252) e arrebentaria na saída com
    acentos dos próprios scripts. Os scripts-alvo já se reconfiguram para UTF-8;
    aqui é o lado do leitor que precisa saber disso.
    """
    p = subprocess.run(cmd, capture_output=True, cwd=RAIZ, timeout=600)
    return p.stdout.decode("utf-8", errors="replace")


def estado_disco() -> dict:
    man = json.loads((RAIZ / "arsenal.json").read_text(encoding="utf-8"))
    c = man["counts"]
    declarados = sum(s["evals"] for s in man["skills"])

    saida_report = _run([PY, str(RAIZ / "scripts" / "run-evals.py"), "--report"])
    executados = _num(saida_report, r"(\d+)\s+registrados")

    # O nº de checks do gate NÃO pode vir de rodar o quality-gate: este script é um dos
    # checks dele, e a chamada recíproca se reproduz até estourar o timeout (observado:
    # 300 s). Lê-se a lista direto do fonte, contando as chamadas a rodar(...) fora do
    # bloco `--fix`, que não roda numa execução normal.
    total_checks = None
    fonte_gate = RAIZ / "scripts" / "quality-gate.py"
    if fonte_gate.is_file():
        texto = fonte_gate.read_text(encoding="utf-8", errors="replace")
        corpo = texto.split("if args.fix:", 1)
        depois_fix = corpo[1].split("resultados += validar_skills", 1)[-1] if len(corpo) > 1 else ""
        diretos = len(re.findall(r'resultados\.append\(rodar\(', depois_fix))
        n_skills = int(c.get("skills") or 0)  # validar_skills produz um check por skill
        total_checks = diretos + n_skills

    return {
        "skills": c["skills"],
        "external": c["external"],
        "mcp": c["mcp"],
        "bundle": c["bundle"],
        "prompts": c["prompts"],
        "evals_declarados": declarados,
        "evals_executados": executados,
        "quality_gate_checks": total_checks,
    }


# Afirmações que a documentação faz. Cada regra é (arquivo, regex-com-captura, campo-esperado, descricao).
REGRAS: list[tuple[str, str, str, str]] = [
    ("README.md", r"Coleção de (\d+) skills", "skills", "abertura do README"),
    ("README.md", r"badge/skills-(\d+)", "skills", "badge de skills"),
    ("README.md", r"Skills DZ23 \((\d+)\)", "skills", "título do índice"),
    ("README.md", r"(\d+) MCP", "mcp", "contagem de MCP"),
    ("README.md", r"(\d+) bundle", "bundle", "contagem de bundles"),
    ("README.md", r"(\d+) referências", "external", "referências externas"),
    ("README.md", r"quality-gate\.py\s+#\s+(\d+)\s+checks", "quality_gate_checks", "nº de checks do gate"),    ("ROADMAP.md", r"(\d+) skills DZ23", "skills", "tabela 'Onde estamos'"),
]


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    real = estado_disco()
    problemas: list[dict] = []

    for arquivo, padrao, campo, descricao in REGRAS:
        esperado = real.get(campo)
        caminho = RAIZ / arquivo
        if not caminho.is_file() or esperado is None:
            continue
        texto = caminho.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(padrao, texto, re.I):
            achado = int(m.group(1))
            if achado != esperado:
                linha = texto[: m.start()].count("\n") + 1
                problemas.append({
                    "arquivo": arquivo, "linha": linha, "afirma": achado,
                    "real": esperado, "campo": campo, "contexto": descricao,
                })

    # Declaração solta de evals: qualquer "N cenários" precisa bater com o disco.
    # Exceção legítima: número datado como auditoria histórica ("Auditoria de 2026-11-09:
    # 128 cenários então existentes"). Isso é registro do que foi medido naquele dia,
    # não afirmação sobre hoje — reescrever seria apagar histórico.
    for arquivo in ("README.md", "ROADMAP.md"):
        caminho = RAIZ / arquivo
        if not caminho.is_file():
            continue
        texto = caminho.read_text(encoding="utf-8", errors="replace")
        linhas = texto.splitlines()
        for m in re.finditer(r"(\d{2,3})\s*(?:cenários|cenarios)\b", texto):
            n = int(m.group(1))
            if n == real["evals_declarados"]:
                continue
            idx = texto[: m.start()].count("\n")
            contexto_linha = linhas[idx] if idx < len(linhas) else ""
            eh_historico = bool(
                re.search(r"(então existentes|entao existentes|à época|a epoca)", contexto_linha, re.I)
                or re.search(r"Auditoria de \d{4}-\d{2}-\d{2}", contexto_linha)
            )
            if eh_historico:
                continue
            problemas.append({
                "arquivo": arquivo, "linha": idx + 1, "afirma": n,
                "real": real["evals_declarados"], "campo": "evals_declarados",
                "contexto": "contagem de cenários de eval",
            })

    if args.json:
        print(json.dumps({"real": real, "problemas": problemas}, ensure_ascii=False, indent=2))
    else:
        print(f"disco: {real['skills']} skills · {real['mcp']} MCP · {real['bundle']} bundle · "
              f"{real['external']} externas · {real['evals_declarados']} evals declarados · "
              f"{real['evals_executados']} executados · {real['quality_gate_checks']} checks no gate")
        if problemas:
            for p in problemas:
                print(f"DIVERGÊNCIA {p['arquivo']}:{p['linha']}: diz {p['afirma']}, "
                      f"real é {p['real']} ({p['contexto']})")
            print(f"\ntotal: {len(problemas)} divergência(s)")
        else:
            print("nenhuma divergência numérica")

    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
