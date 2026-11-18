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

    # Ferramentas do MCP: medido por sessão JSON-RPC real sobre stdio, não lido de doc.
    # Importa a contagem que um cliente novo efetivamente vê (instalação mínima, sem
    # workspace/sandbox). O README afirmava "28 tools" — número do registro completo —
    # enquanto `tools/list` devolve 24, e a diferença era invisível para quem escreve a
    # documentação de memória. None quando não há node: ausência pula a regra, não aprova.
    mcp_tools = _contar_ferramentas_mcp()

    # O nº de checks do gate não pode vir de rodar o quality-gate (recursão: este script é
    # um dos checks) nem de parsear o fonte dele — um parser por regex contou 24 contra os
    # 31 reais, silenciosamente errado. Lê-se a contagem que o próprio gate publicou na
    # última execução real. Sem arquivo, None: ausência não vira zero nem aprovação.
    total_checks = None
    arq_contagem = RAIZ / ".gate-contagem"
    if arq_contagem.is_file():
        try:
            n = json.loads(arq_contagem.read_text(encoding="utf-8")).get("total")
            total_checks = int(n) if isinstance(n, int) and n > 0 else None
        except (json.JSONDecodeError, OSError, ValueError, TypeError):
            total_checks = None

    return {
        "skills": c["skills"],
        "external": c["external"],
        "mcp": c["mcp"],
        "bundle": c["bundle"],
        "prompts": c["prompts"],
        "evals_declarados": declarados,
        "evals_executados": executados,
        "quality_gate_checks": total_checks,
        "mcp_tools_padrao": mcp_tools,
    }


def _contar_ferramentas_mcp() -> int | None:
    """Quantas tools o MCP expõe sem configuração extra. None se não der para medir."""
    import os
    import subprocess as sp
    pasta = RAIZ / "mcp" / "dz23-subagents-universal-mcp"
    if not (pasta / "src" / "index.js").is_file():
        return None
    node = _qual_node()
    if node is None:
        return None
    linhas = [
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                               "clientInfo": {"name": "check-numbers", "version": "0"}}}),
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ]
    try:
        p = sp.run([node, "src/index.js", "--stdio"],
                   input=("\n".join(linhas) + "\n").encode("utf-8"),
                   capture_output=True, cwd=str(pasta), timeout=90,
                   env={**os.environ, "DZ23_WORKSPACE_ROOTS": "",
                        "DZ23_SANDBOX_ENABLED": "false"})
    except (OSError, sp.TimeoutExpired):
        return None
    if p.returncode != 0:
        return None
    for bruto in p.stdout.decode("utf-8", errors="replace").splitlines():
        bruto = bruto.strip()
        if not bruto.startswith("{"):
            continue
        try:
            msg = json.loads(bruto)
        except json.JSONDecodeError:
            continue
        if msg.get("id") == 2:
            tools = (msg.get("result") or {}).get("tools")
            if isinstance(tools, list):
                return len(tools)
    return None


def _qual_node() -> str | None:
    import shutil
    return shutil.which("node")


# Afirmações que a documentação faz. Cada regra é (arquivo, regex-com-captura, campo-esperado, descricao).
REGRAS: list[tuple[str, str, str, str]] = [
    ("README.md", r"Coleção de (\d+) skills", "skills", "abertura do README"),
    ("README.md", r"badge/skills-(\d+)", "skills", "badge de skills"),
    ("README.md", r"Skills DZ23 \((\d+)\)", "skills", "título do índice"),
    ("README.md", r"(\d+) MCP", "mcp", "contagem de MCP"),
    ("README.md", r"(\d+) bundle", "bundle", "contagem de bundles"),
    ("README.md", r"(\d+) referências", "external", "referências externas"),
    # Ferramentas do MCP: duas alegações diferentes na mesma linha do README, ambas medidas
    # por tools/list real (uma com instalação mínima, outra não — ver _contar_ferramentas_mcp).
    ("README.md", r"Sub-agentes com (\d+) tools expostas", "mcp_tools_padrao",
     "ferramentas visíveis sem configuração extra"),
    # Sem regra para "N checks do gate": o README agora diz "o total sai da própria saída",
    # então não há número digitado a conferir. A regra existiu, ficou órfã quando o número
    # saiu do texto, e é exatamente o caso que o detector de regra órfã abaixo passou a
    # denunciar em vez de dar verde mentiroso.
    ("ROADMAP.md", r"(\d+) skills DZ23", "skills", "tabela 'Onde estamos'"),
]

# Regras cujo valor pode ser None sem culpa (ferramenta ausente no ambiente). Diferente de
# regra órfã: aqui o padrão casa, só não havia como medir.
_PERMITE_NENHUM_MEDICAO = {"mcp_tools_padrao"}


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
    regras_sem_alvo: list[str] = []

    for arquivo, padrao, campo, descricao in REGRAS:
        esperado = real.get(campo)
        caminho = RAIZ / arquivo
        if not caminho.is_file() or esperado is None:
            continue
        texto = caminho.read_text(encoding="utf-8", errors="replace")
        matches = list(re.finditer(padrao, texto, re.I))
        if not matches:
            # Regra sem alvo é autoengano: parece que conferimos algo e não conferimos.
            # Aconteceu de verdade — a regra de "N checks" ficou órfã quando o número foi
            # removido do README. Melhor reclamar aqui do que dar verde mentiroso.
            regras_sem_alvo.append(f"{arquivo}: nenhuma ocorrência de {padrao!r} ({descricao})")
            continue
        for m in matches:
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
        print(json.dumps({"real": real, "problemas": problemas,
                          "regras_sem_alvo": regras_sem_alvo}, ensure_ascii=False, indent=2))
    else:
        print(f"disco: {real['skills']} skills · {real['mcp']} MCP · {real['bundle']} bundle · "
              f"{real['external']} externas · {real['evals_declarados']} evals declarados · "
              f"{real['evals_executados']} executados · {real['quality_gate_checks']} checks no gate")
        for r in regras_sem_alvo:
            print(f"REGRA ÓRFÃ: {r}")
        if problemas:
            for p in problemas:
                print(f"DIVERGÊNCIA {p['arquivo']}:{p['linha']}: diz {p['afirma']}, "
                      f"real é {p['real']} ({p['contexto']})")
        if not problemas and not regras_sem_alvo:
            print("nenhuma divergência numérica")

    return 1 if (problemas or regras_sem_alvo) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
