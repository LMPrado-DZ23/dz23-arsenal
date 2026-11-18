"""Prova negativa do checa-enderecamento: esconder uma referencia do SKILL.md deve acusar.

Dois formatos de violacao, porque a classe tem dois lados:
  A) referencia existente no disco e nao nomeada em nenhum lugar  -> 'sem citacao'
  B) referencia existente e nomeada so dentro de outro reference  -> 'so por cadeia'

A tentativa anterior de provar isto removeu uma LINHA inteira do SKILL.md que continha duas
citacoes; sobrou a citacao cruzada entre arquivos de references/ e o verificador agregado nao
reclamou -- comportamento correto dele, medicao errada minha. Aqui cada violacao e uma edicao
cirurgica sobre um nome especifico, com assert de que o arquivo realmente sumiu do alvo.
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def monta():
    base = pathlib.Path(tempfile.mkdtemp())
    for n in ("skills", "scripts"):
        shutil.copytree(RAIZ / n, base / n, symlinks=False,
                        ignore=shutil.ignore_patterns("__pycache__", "node_modules"))
    return base


def roda(base):
    p = subprocess.run([PY, str(base / "scripts/checa-enderecamento.py")], capture_output=True,
                       cwd=str(base), timeout=300)
    out = (p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")).strip()
    return p.returncode, out


problemas = []

# baseline
base = monta()
rc, out = roda(base)
print(f"baseline: exit={rc}")
if rc != 0:
    problemas.append(f"baseline ja falha: {out[-200:]}")

# --- A) referencia existente sem nenhuma citacao em lugar algum ------------------------------
alvo_nome = "installation.md"
sk_A = "dz23-e2e-browser-verifier"
base = monta()
sm = base / "skills" / sk_A / "SKILL.md"
t = sm.read_text(encoding="utf-8")
n = t.replace(f"`references/{alvo_nome}`", "`referencia-genérica`")
if n == t:
    problemas.append(f"A: nao achei citacao de {alvo_nome} para remover")
else:
    sm.write_text(n, encoding="utf-8")
    # tambem sumir com as citacoes internas dos outros references, senao fica alcancavel por cadeia
    rdir = base / "skills" / sk_A / "references"
    for f in rdir.glob("*.md"):
        tt = f.read_text(encoding="utf-8")
        nn = tt.replace(f"`references/{alvo_nome}`", "`referencia-genérica`").replace(
            f"`{alvo_nome}`", "`referencia-genérica`")
        if nn != tt:
            f.write_text(nn, encoding="utf-8")
    rc, out = roda(base)
    achou = re.search(rf"{alvo_nome}", out) and rc != 0
    print(f"A) referencia sem citacao alguma: exit={rc} | denunciada? {achou}")
    if not achou:
        problemas.append("A: verificador aprovou referencia invisivel a qualquer instrucao")

# --- B) referencia nomeada apenas dentro de outro reference ----------------------------------
base = monta()
sk_B = "dz23-codebase-cartographer"
nome_B = "hotspots-and-debt.md"
smB = base / "skills" / sk_B / "SKILL.md"
tB = smB.read_text(encoding="utf-8")
# tirar do SKILL.md, mantendo viva em references/verification-and-freshness.md (que a cita)
nB = re.sub(rf"[^\n]*{re.escape(nome_B)}[^\n]*\n?", "", tB, count=1)
assert nB != tB, "B: nada removido do SKILL.md"
smB.write_text(nB, encoding="utf-8")
ainda_viva = any(nome_B in f.read_text(encoding="utf-8")
                 for f in (base / "skills" / sk_B / "references").glob("*.md"))
rc, out = roda(base)
denunciou_cadeia = rc != 0 and "cadeia" in out
print(f"B) so por cadeia: referencia ainda citada em references/? {ainda_viva}")
print(f"   exit={rc} | denunciou alcance indireto? {denunciou_cadeia}")
if ainda_viva and not denunciou_cadeia:
    problemas.append("B: aceitou referencia alcancavel apenas abrindo outro guia")

print("\n" + "=" * 60)
if problemas:
    print("PROBLEMAS:")
    for x in problemas:
        print("  -", x)
    sys.exit(1)
print("OK: esconder uma referencia do SKILL.md passa a quebrar o gate")
