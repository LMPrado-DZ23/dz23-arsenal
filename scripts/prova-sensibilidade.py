"""Prova de que a guarda anti-violacao-imaginaria funciona.

Substitui a violacao do check-eval-results por uma que nao casa com nada (prosa 'Total pendente 99'
quando o ROADMAP guarda tabela '**Total pendente** | **99**') e exige que a auditoria reporte
SETUP!/medicao vazia em vez de OCO. Distingue as duas coisas: um verificador pode ser correto e o
meu teste e que estava inventando a violacao.

A tentativa anterior de fazer esta troca via aqui-string do PowerShell nao provou nada: as aspas
escapadas eram corrompidas pelo shell antes de chegar ao Python, entao `antiga in src` dava False e
o script executava a versao boa sem que eu percegesse. Aqui a ancora e lida do proprio arquivo e o
casamento e afirmado.
"""
import pathlib
import re
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
PY = sys.executable
ALVO = RAIZ / "scripts/audita-sensibilidade.py"

src = ALVO.read_text(encoding="utf-8")

# localizar o bloco por regex sobre o texto real, nao por literal copiado a mao
m = re.search(r'^    "check-eval-results": \(.*?\n(?=    "checa-ancoras")', src, re.S | re.M)
assert m, "bloco check-eval-results nao localizado no fonte"
original = m.group(0)
print("=== bloco real substituido ===")
print("".join("    | " + l + "\n" for l in original.splitlines()[:4]))

imaginaria = '''    "check-eval-results": ("scripts/check-eval-results.py", lambda b: (
        b / "ROADMAP.md").write_text(
            (b / "ROADMAP.md").read_text(encoding="utf-8")
            .replace("Total pendente 99", "Total pendente 3"),
            encoding="utf-8")),
'''

broken = src[: m.start()] + imaginaria + src[m.end():]
assert broken != src, "substituicao nao produziu diferenca"
assert "Total pendente 99" in broken, "violacao imaginaria nao injetada"

with tempfile.TemporaryDirectory() as td:
    mod = pathlib.Path(td) / "a.py"
    mod.write_text(broken, encoding="utf-8")
    p = subprocess.run([PY, str(mod), str(RAIZ)], capture_output=True, cwd=str(RAIZ),
                       timeout=900)
    out = (p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace"))
    linhas = [l.strip()[:120] for l in out.splitlines()
              if any(k in l for k in ("eval-results", "SETUP", "OCO", "sem efeito", "vazia"))]
    print(f"\nexit={p.returncode}")
    for l in linhas[:6]:
        print("  ", l)

denunciou = "sem efeito" in out or "medicao vazia" in out
confundiu = "OCO" in out and "eval-results" in out and not denunciou
print("\n" + "=" * 58)
if denunciou and not confundiu:
    print("OK: violacao imaginaria reportada como medicao vazia, nao como verificador oco")
    sys.exit(0)
if confundiu:
    print("FALHA DA GUARDA: chamou de OCO um caso em que a violacao nao mudou conteudo algum")
    sys.exit(1)
print("INCONCLUSIVO: a prova nao chegou a exercitar a guarda")
sys.exit(2)
