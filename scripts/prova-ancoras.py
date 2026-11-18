"""Prova negativa do checa-ancoras: recriar os tres defeitos que cometi e exigir denuncia."""
import pathlib
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def monta() -> pathlib.Path:
    tmp = pathlib.Path(tempfile.mkdtemp())
    for n in ("scripts", "skills"):
        shutil.copytree(RAIZ / n, tmp / n, symlinks=False)
    for f in ("ROADMAP.md", "CHANGELOG.md", "README.md", "arsenal.json"):
        if (RAIZ / f).is_file():
            shutil.copy2(RAIZ / f, tmp / f)
    return tmp


def roda(tmp):
    p = subprocess.run([PY, str(tmp / "scripts/checa-ancoras.py")], capture_output=True,
                       cwd=str(tmp), timeout=120)
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")


CASOS = {
    # defeito real da rodada 36: entradas novas empilhadas depois da mais antiga
    "changelog fora de ordem (meu erro da r36)": lambda t: (t / "CHANGELOG.md").write_text(
        (t / "CHANGELOG.md").read_text(encoding="utf-8").replace(
            "## [1.5.14]", "## [0.9.0-TESTE]", 1), encoding="utf-8"),
    # defeito real da rodada 37: edicao que nao casou e deixou buraco na numeracao
    "buraco na numeracao de dividas (r37)": lambda t: (t / "ROADMAP.md").write_text(
        (t / "ROADMAP.md").read_text(encoding="utf-8").replace(
            "| 7 | Sem `evals/results/`", "| 70 | Sem `evals/results/`", 1), encoding="utf-8"),
    # topo do changelog de skill sem bater com VERSION
    "skill com versao nova sem entrada": lambda t: [
        (f := p / "VERSION").write_text("9.9.9\n", encoding="utf-8")
        for p in (t / "skills").iterdir()
        if p.is_dir() and (p / "VERSION").is_file()][:1],
}

falhas = []
print("=== baseline ===")
tmp = monta()
rc, s = roda(tmp)
print(f"  exit={rc} (esperado 0)")
if rc != 0:
    falhas.append(f"baseline ja falha: {s[:200]}")
shutil.rmtree(tmp, ignore_errors=True)

for rotulo, mut in CASOS.items():
    tmp = monta()
    try:
        mut(tmp)
        rc, s = roda(tmp)
        denunciou = rc != 0
        print(f"  {'OK      ' if denunciou else 'OCO!!!!!'} {rotulo} -> exit={rc}")
        if not denunciou:
            falhas.append(f"{rotulo}: o verificador NAO percebeu")
        else:
            alvo = [l.strip()[:110] for l in s.splitlines() if l.startswith("PROBLEMA")]
            for a in alvo[:2]:
                print(f"            {a}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

print()
if falhas:
    print("PROBLEMAS:")
    for f in falhas:
        print("  -", f)
    sys.exit(1)
print("os tres defeitos cometidos nesta sessao sao todos denunciados")
