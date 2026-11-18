"""Audita afirmacoes qualitativas feitas nesta sessao: cada uma ainda e verdadeira?

Numero quebra alto (algum check reclama). Afirmacao do tipo 'X agora falha quando Y' quebra
em silencio: alguem remove a guarda, o texto continua no CHANGELOG e passa a ser descricao de
um sistema que nao existe. Este arquivo re-executa a experiencia por tras de cada frase.
"""
import json
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
PY = sys.executable
sys.path.insert(0, str(RAIZ / "scripts"))


def exec_(args, cwd=None, stdin=None):
    p = subprocess.run([PY, *args], capture_output=True, cwd=str(cwd or RAIZ),
                       input=stdin, timeout=240)
    return p.returncode, (p.stdout.decode("utf-8", "replace")
                          + p.stderr.decode("utf-8", "replace"))


resultados = []


def afirma(texto, fn):
    try:
        ok = fn()
    except Exception as exc:  # noqa: BLE001
        ok = False
        texto += f"  [excecao: {type(exc).__name__}]"
    resultados.append((texto, bool(ok)))
    print(f"  {'OK      ' if ok else 'CAIU!!!!'} {texto}")


print("=== gates-fantasma: cada um foi fechado com prova; a prova ainda vale? ===")

# D1: --verify-quotes sem AUDIT-STATUS deve falhar.
def d1():
    arq = RAIZ / "evals-results/_audit-notes/AUDIT-STATUS.json"
    backup = arq.read_bytes()
    deslocado = arq.with_name(arq.name + ".off")
    try:
        arq.rename(deslocado)
        rc, s = exec_(["scripts/run-evals.py", "--verify-quotes"])
        return rc == 1 and "ausente" in s
    finally:
        # Restaurar por caminho explicito, nunca com with_suffix(): na primeira versao isto
        # era `arq.with_suffix(".off")`, que apaga '.json' e produz AUDIT-STATUS.off -- um
        # arquivo novo na arvore versionada que o finally nao desfazia. A suíte vazou um
        # resíduo assim no repo real antes de eu perceber.
        if deslocado.exists():
            deslocado.replace(arq)
        if not arq.exists():
            arq.write_bytes(backup)
afirma("verify-quotes falha sem AUDIT-STATUS.json", d1)

# check-audit-inputs sem argumento: usage, nao traceback.
afirma("check-audit-inputs sem arg -> exit 2 com usage",
       lambda: (lambda r: r[0] == 2 and "Traceback" not in r[1])(
           exec_(["scripts/check-audit-inputs.py"])))

# check-numbers denuncia regra orfa.
def orfa():
    import shutil
    readme = RAIZ / "README.md"
    b = readme.read_bytes()
    try:
        t = readme.read_text(encoding="utf-8")
        readme.write_text(t.replace("Coleção de 10 skills", "Coleção de X skills"),
                          encoding="utf-8")
        rc, s = exec_(["scripts/check-numbers.py"])
        return "REGRA ÓRFÃ" in s or rc != 0
    finally:
        readme.write_bytes(b)
afirma("check-numbers pega regra orfa quando o numero sai do README", orfa)

# claims: referencia quebrada em SKILL.md e pega pelo gate.
def claims_pega():
    import shutil
    alvo = RAIZ / "skills/dz23-e2e-browser-verifier/SKILL.md"
    b = alvo.read_bytes()
    try:
        alvo.write_bytes(b + "\nVer `references/relatorio-de-cobertura.md`.\n".encode())
        rc, s = exec_(["scripts/verifica_claims.py", "--texto", str(alvo), "--raiz", ".",
                      "--min", "1.0"])
        return rc != 0 and "falho" in s.lower()
    finally:
        alvo.write_bytes(b)
afirma("verifica_claims reprova referencia quebrada", claims_pega)

# python -O nao desliga validador (rodada 19).
def modo_o():
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        esp = pathlib.Path(td) / "skill"
        shutil.copytree(RAIZ / "skills/dz23-e2e-browser-verifier", esp)
        sm = esp / "SKILL.md"
        sm.write_bytes(sm.read_bytes() + "\nVer `references/painel-de-metricas.md`.\n".encode())
        rc, s = exec_([str(esp / "scripts/validate_skill.py")], cwd=RAIZ)
        return rc != 0
afirma("validador nao aprova sob python -O", modo_o)

# skill instalada se auto-valida sem o checkout (rodada 7).
def instala_sem_repo():
    import os
    import tempfile
    sk = pathlib.Path(os.path.expanduser("~/.agents/skills"))
    alvo = sk / ".dz23-arsenal"
    if not alvo.is_file():
        return False
    guardado = alvo.read_bytes()
    v = sk / "dz23-codebase-cartographer/SKILL.md"
    vb = v.read_bytes()
    try:
        alvo.write_text("D:\\repo\\inexistente\\para\\teste\n", encoding="utf-8")
        v.write_bytes(vb + "\nVer `references/mapa-de-fluxo-legado.md`.\n".encode())
        rc, s = exec_([str(sk / "dz23-codebase-cartographer/scripts/validate_skill.py")])
        return rc != 0 and "WARN" not in s
    finally:
        alvo.write_bytes(guardado)
        v.write_bytes(vb)
afirma("skill instalada reprova mesmo sem o repo (rodada 7)", instala_sem_repo)

# CRLF: indice limpo apesar do working tree.
def crlf():
    import shutil
    bash = shutil.which("bash") or r"C:\Program Files\Git\bin\bash.exe"
    p = subprocess.run([bash, "-c",
                        'cd "$1" && git grep -Il --cached -P "\\r$" -- "*.md" "*.py" '
                        '"*.sh" "*.yml" "*.json" "*.txt" || true', "x", str(RAIZ)],
                       capture_output=True, timeout=120)
    return not p.stdout.decode("utf-8", "replace").strip()
afirma("indice sem CRLF (passo de CI do jeito certo)", crlf)

# audit-zips nao confunde EOL com divergencia (rodada 9).
def eol_audit():
    import shutil
    import tempfile
    sk = pathlib.Path.home() / ".agents/skills/dz23-codebase-cartographer"
    alvo = sk / "references/data-and-flow.md"
    if not alvo.is_file():
        return False
    b = alvo.read_bytes()
    try:
        alvo.write_bytes(b.replace(b"\r\n", b"\n"))
        rc, s = exec_(["scripts/audit-zips.py"])
        return "cartographer" not in s.split("CONTEUDO_DIVERGENTE")[-1][:200]
    finally:
        alvo.write_bytes(b)
afirma("audit-zips ignora diferenca so de EOL", eol_audit)

print("\n" + "=" * 64)
caiu = [t for t, ok in resultados if not ok]
if caiu:
    print(f"{len(caiu)} alegacao(oes) nao sustentada(s):")
    for c in caiu:
        print("   -", c)
    sys.exit(1)
print(f"todas as {len(resultados)} alegacoes desta sessao seguem sustentadas por execucao")
