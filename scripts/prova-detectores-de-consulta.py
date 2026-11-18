"""Valida que as provas de consultor DETECTAM defeito, nao so passem quando tudo esta certo.

Necessario porque uma das minhas proprias tentativas de provar isso falhou em silencio: troquei um
sinonimo por um padrao que nao existia no arquivo (`"orcamento": "Budget vs Actual"` -- a chave nem
estava la), o replace virou no-op, a prova ficou verde e eu quase conclui que o detector nao funcionava.
Verde obtido por edicao que nao aconteceu nao informa nada sobre o sistema; informa sobre a edicao.

Aqui a injecao e feita por regex contra o par real lido do proprio modulo, com assert de que o texto
mudou. Se nao mudar, o script erra alto em vez de reportar falso resultado.
"""
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# (script da prova, arquivo do consultor, regex que acha UM par real do mapa)
ALVOS = [
    ("scripts/prova-consulta-design.py", "scripts/consulta-design.py",
     r'("tendencia": )"Trend Over Time"'),
    ("scripts/prova-consulta-backend.py", "scripts/consulta-backend.py",
     r'("dinheiro": )"money"'),
    ("scripts/prova-consulta-performance.py", "scripts/consulta-performance.py",
     r'("cascata": )"waterfalls"'),
]

ruins = []
for prova, consultor, padrao in ALVOS:
    src = (RAIZ / consultor).read_text(encoding="utf-8")
    m = re.search(padrao, src)
    if not m:
        ruins.append(f"{consultor}: padrao de injecao nao casou -- teste malformado, nao resultado")
        print(f"  ERRADO {consultor:<34} padrao nao encontrado (nao confunda com 'detector fraco')")
        continue
    alterado = src[:m.start()] + m.group(1) + '"Valor Inventado Que Nao Existe"' + src[m.end():]
    assert alterado != src, "injecao sem efeito"

    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        for n in ("scripts", "dados-design", "dados-backend", "dados-performance"):
            if (RAIZ / n).is_dir():
                shutil.copytree(RAIZ / n, base / n,
                                ignore=shutil.ignore_patterns("__pycache__"))
        (base / consultor).write_text(alterado, encoding="utf-8")
        r = subprocess.run([PY, prova], capture_output=True, cwd=str(base), timeout=900)
        out = (r.stdout + r.stderr).decode("utf-8", "replace")
        pegou = r.returncode != 0 and any(k in out.upper() for k in ("MORTO", "PROBLEMA"))
        print(f"  {'OK   ' if pegou else 'ERRADO'} {consultor:<34} exit={r.returncode} "
              f"detectou={pegou}")
        if not pegou:
            ruins.append(f"{prova}: sinonimo inventado passou verde -- detector nao funciona")

print()
if ruins:
    print("PROBLEMAS:")
    for x in ruins:
        print("  -", x)
    sys.exit(1)
print("OK: as tres provas de consultor detectam sinonimo inventado (nao so passam quando limpas)")
