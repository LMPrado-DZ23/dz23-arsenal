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

print()
if ruins:
    print("PROBLEMAS:")
    for r in ruins:
        print("  -", r)
    sys.exit(1)
print("OK: consulta-design resolve em portugues, casa a categoria certa e recusa chutar")
