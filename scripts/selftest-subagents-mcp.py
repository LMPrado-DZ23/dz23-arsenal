"""selftest-subagents-mcp.py -- roda a suite propria da dz23-subagents-universal-mcp e cobra o veredito.

Por que isto existe (gap medido pelo auditor): a MCP tem uma suíte real de 293 testes em node:test com zero
dependencias externas, mas o gate do ARSENAL nunca a executava -- so pentagi-mcp tinha check aqui. Cobertura
ausente do mesmo tipo que a rodada 46 achou nos scripts embutidos: os validadores existiam, ninguem os rodava
no lugar certo. Rodar a suite dela e mais honesto do que escrever um selftest paralelo que duplicaria os casos
e envelheceria separado.

Criterio de aceite (nao basta "exit 0"):
- node presente; se nao, NOT_TESTED declarada (nao PASS silencioso) -- mesma disciplina das rodadas de ambiente.
- a saida TAP do node --test precisa reportar fail 0 E tests > 0. Um runner que nao descobriu nenhum teste daria
  pass 0/fail 0 e exit 0; por isso o piso de contagem e obrigatorio, senao o check vira decorativo.
- timeout proprio: suite pesada (~13s aqui) nao pode travar o gate inteiro indefinidamente.

Nao instala nada nem toca na rede: a suite roda com stdlib do node (ver package.json: dependencies = []).
"""
import json
import pathlib
import shutil
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MCP = RAIZ / "mcp" / "dz23-subagents-universal-mcp"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    if not MCP.is_dir():
        print("FALHA: pasta da MCP ausente:", MCP.relative_to(RAIZ))
        return 1

    node = shutil.which("node")
    if not node:
        # Ambiente sem node: declarar NOT_TESTED, nao fingir PASS. O CI publica node; localmente pode faltar.
        print("NOT_TESTED: node nao esta no PATH; a suite da MCP nao foi executada.")
        return 0

    pkg = json.loads((MCP / "package.json").read_text(encoding="utf-8"))
    versao = pkg.get("version", "?")

    try:
        p = subprocess.run([node, "--test"], capture_output=True, cwd=str(MCP), timeout=180)
    except subprocess.TimeoutExpired:
        print("FALHA: node --test estourou 180s na MCP subagents.")
        return 1

    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    tests = _num(out, "tests")
    fails = _num(out, "fail")
    if tests is None or fails is None:
        print("FALHA: nao consegui ler o resumo TAP da suite (tests/fail ausentes). Ver formato do node --test.")
        return 1
    if tests == 0:
        print("FALHA: runner nao descobriu nenhum teste (tests 0) -- suite vazia nao e aprovacao.")
        return 1
    ok = p.returncode == 0 and fails == 0
    print(f"dz23-subagents-universal-mcp v{versao}: tests {tests} | pass {_num(out,'pass')} | "
          f"fail {fails} | skipped {_num(out,'skipped') or 0}")
    if not ok:
        # mostrar as linhas de falha para o dev nao ter que caçar
        for l in out.splitlines():
            if l.strip().startswith("✖") or "not ok" in l.lower():
                print("   ", l.strip()[:150])
        print(f"FALHA: exit={p.returncode}, fail={fails}")
        return 1
    print(f"OK: {tests} testes proprios da MCP passaram (rodados pelo gate do arsenal)")
    return 0


def _num(texto: str, chave: str):
    import re
    # node --test imprime "ℹ tests 293" / "# fail 0" -- SEM dois-pontos. O marcador pode ser U+2139 ou '#'.
    m = re.search(rf"(?:\u2139|#)\s*{chave}\s+(\d+)", texto)
    return int(m.group(1)) if m else None


if __name__ == "__main__":
    sys.exit(main())
