"""Confere que check-copies detecta divergencia de LOGICA entre as copias do consultor, e tolera a
diferenca legitima de caminho.

Necessario porque esta sessao produziu duas vezes o mesmo auto-engano: injetei mudanca usando um
padrao que nao existia no arquivo (`def cmd_listar(_args)` quando a assinatura real era
`def cmd_listar(_a) -> int:`), o replace virou no-op, o verificador ficou verde, e eu anotei 'nao
detecta defeito'. Verde obtido por edicao que nao aconteceu nao mede o sistema; mede a edicao. Aqui o
padrao e assertado antes de qualquer conclusao.
"""
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

CASOS = [
    # (rotulo, arquivo-alvo, padrao que DEVE existir, substituicao, deve_falhar)
    ("logica divergente na copia da skill",
     "skills/dz23-backend-data-architect/scripts/consulta-backend.py",
     "def cmd_listar(_a) -> int:",
     "def cmd_listar(_a) -> int:\n    _extra_inventado = 42",
     True),
    ("so o caminho do acervo difere (tolerar)",
     "skills/dz23-performance-scalability-engine/scripts/consulta-performance.py",
     'DADOS = pathlib.Path(__file__).resolve().parent.parent / "dados"',
     'DADOS = pathlib.Path(__file__).resolve().parent.parent / "dados2"',
     False),
    ("fonte em scripts/ ausente",
     "scripts/consulta-design.py",
     "def main(",
     "def main_quebrado(",
     True),
]

ruins = []
for rotulo, rel, antigo, novo, deve_falhar in CASOS:
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        for n in ("scripts", "skills"):
            shutil.copytree(RAIZ / n, base / n, ignore=shutil.ignore_patterns("__pycache__"))
        p = base / rel
        t = p.read_text(encoding="utf-8")
        if antigo not in t:
            ruins.append(f"{rotulo}: PADRAO INEXISTENTE -- teste malformado, nao resultado")
            print(f"  ERRADO {rotulo:<40} padrao nao casou (revise o teste, nao o codigo)")
            continue
        p.write_text(t.replace(antigo, novo, 1), encoding="utf-8")
        r = subprocess.run([PY, "scripts/check-copies.py"], capture_output=True,
                           cwd=str(base), timeout=300)
        out = (r.stdout + r.stderr).decode("utf-8", "replace")
        falhou = r.returncode != 0
        ok = falhou == deve_falhar
        print(f"  {'OK   ' if ok else 'ERRADO'} {rotulo:<40} exit={r.returncode} "
              f"(esperava {'falha' if deve_falhar else 'passar'})")
        if falhou and deve_falhar:
            alvo = [l.strip()[:112] for l in out.splitlines() if "DIVERG" in l.upper()]
            for a in alvo[:2]:
                print("       ", a)
        if not ok:
            ruins.append(f"{rotulo}: esperado exit {'!=0' if deve_falhar else '0'}, veio {r.returncode}")

print()
if ruins:
    print("PROBLEMAS:")
    for x in ruins:
        print("  -", x)
    sys.exit(1)
print("OK: check-copies pega divergencia de logica e tolera diferenca de caminho entre as copias")
