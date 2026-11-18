"""Prova do consulta-design: casos legitimos resolvem e o falso positivo nao volta."""
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEVE_ACHAR = [
    (["ux", "formulario"], "Forms"),
    (["ux", "forms"], "Forms"),
    (["cores", "saude"], "Health"),
    (["estilo", "vidro"], "Glassmorphism"),
    (["produto", "financas"], "Fintech"),
    (["estilo", "glassmorphism"], "Glassmorphism"),
    (["produto", "fintech"], "Fintech"),
    (["ux", "acessibilidade"], "Accessibility"),
]
DEVE_NEGAR = [
    (["ux", "formulario"], "Animation"),      # o falso positivo historico
    (["ux", "formul"], None),                  # radical incompleto: zero, sem chute
    (["estilo", "xyzabc"], None),
]

ruins = []
print("=== casos que devem resolver ===")
for args, esperado in DEVE_ACHAR:
    p = subprocess.run([PY, "scripts/consulta-design.py", *args, "--top", "3"],
                       capture_output=True, cwd=str(RAIZ), timeout=120)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    achou = esperado.lower() in out.lower() and p.returncode == 0
    print(f"  {'OK   ' if achou else 'ERRADO'} {' '.join(args):<24} esperava '{esperado}'")
    if not achou:
        ruins.append(f"{args}: nao encontrou '{esperado}' (exit {p.returncode})")

print("\n=== casos que devem negar ===")
for args, vedado in DEVE_NEGAR:
    p = subprocess.run([PY, "scripts/consulta-design.py", *args, "--top", "5"],
                       capture_output=True, cwd=str(RAIZ), timeout=120)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    if vedado:
        limpo = vedado.lower() not in out.lower()
        print(f"  {'OK   ' if limpo else 'ERRADO'} {' '.join(args):<24} nao deve conter '{vedado}'")
        if not limpo:
            ruins.append(f"{args}: ainda vaza '{vedado}'")
    else:
        zero = p.returncode != 0 and ("zero" in out.lower() or "nenhum" in out.lower()
                                      or "sem " in out.lower())
        print(f"  {'OK   ' if zero else 'ERRADO'} {' '.join(args):<24} deve reportar ausencia")
        if not zero:
            ruins.append(f"{args}: deveria dizer que nao ha correspondencia")

# --- exaustao dos mapas de sinonimos -----------------------------------------------------------
# Nao basta testar os termos escolhidos para esta prova: foi exatamente assim que 15 entradas do
# SINONIMOS_GRAFICO/MOTION apontaram para valores inexistentes ("button feedback", "budget vs
# actual") e continuaram verdes -- a amostra manual nunca perguntava por eles. Todo o mapa e
# executado contra o catalogo real da tabela. Um sinonimo morto faz o usuario acreditar que a ponte
# em portugues existe.
print("\n=== cada termo dos mapas PT->EN resolve no catalogo real? ===")
import csv
import importlib.util

espec = importlib.util.spec_from_file_location(
    "cdesign", str(RAIZ / "scripts/consulta-design.py"))
mod = importlib.util.module_from_spec(espec)
espec.loader.exec_module(mod)

MAPAS = [
    ("SINONIMOS_GRAFICO", mod.SINONIMOS_GRAFICO, "charts.csv", "Data Type"),
    ("SINONIMOS_MOTION", mod.SINONIMOS_MOTION, "motion.csv", "Category"),
]
total_termos = 0
for nome_mapa, mp, arq, col in MAPAS:
    with (mod.DADOS / arq).open(encoding="utf-8-sig", newline="") as fh:
        reais = {r[col].strip().lower() for r in csv.DictReader(fh)}
    mortos = [(k, v) for k, v in mp.items() if v.strip().lower() not in reais]
    total_termos += len(mp)
    print(f"  {'OK   ' if not mortos else 'ERRADO'} {nome_mapa:<20}"
          f"{len(mp) - len(mortos)}/{len(mp)} resolvem em {col}")
    for k, v in mortos:
        print(f"         MORTO: '{k}' -> '{v}' nao e um valor de {arq}")
        ruins.append(f"{nome_mapa}: sinonimo '{k}' aponta para '{v}', inexistente no catalogo")

print()
if ruins:
    print("PROBLEMAS:")
    for r in ruins:
        print("  -", r)
    sys.exit(1)
print(f"OK: consulta-design resolve em portugues ({total_termos} sinonimos vivos), casa a "
      "categoria certa e recusa chutar")
