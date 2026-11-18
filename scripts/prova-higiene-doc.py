"""Prova negativa do check-doc-hygiene: residuo nu deve ser denunciado."""
import pathlib
import shutil
import subprocess
import sys
import tempfile

raiz = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    raiz = pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with tempfile.TemporaryDirectory() as td:
    base = pathlib.Path(td) / "repo"
    shutil.copytree(raiz / "scripts", base / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__"))
    for n in ("docs", "skills", "external", "cli", "prompts", "evals-results"):
        if (raiz / n).is_dir():
            shutil.copytree(raiz / n, base / n,
                            ignore=shutil.ignore_patterns("node_modules", "__pycache__"))
    for f in ("README.md", "ROADMAP.md", "CHANGELOG.md", "CONTRIBUTING.md", "INDEX.md",
              ".gate-contagem", "arsenal.json", "evals.schema.json"):
        if (raiz / f).is_file():
            shutil.copy2(raiz / f, base / f)

    CASOS = {
        # exatamente o artefato que eu produzi na rodada 57
        "aspas triplas + concat": '\n""" + "## [1.5.99] \\u2014 2026-11-18"\n',
        "template nao expandido": "\nRenderizar \u0024{NOME_DO_CAMPO} no titulo.\n",
        "marcador de merge": "<<<<<<< HEAD\nnossa linha\n=======\nlinha deles\n>>>>>>> ramificacao\n",
        "escape unicode literal": "caractere especial \u005cu00e9 escrito assim\n",
        "CJK nu em prosa": "O texto ficou conte\u4f53当前es errado aqui\n",
        # controle positivo: citacao com crase NAO deve falhar
        "citacao em crase (deve passar)": "\nO bug produzia ``\"\"\" + \"...\"`` no arquivo.\n",
    }

    for rotulo, lixo in CASOS.items():
        alvo = base / "CONTRIBUTING.md"
        original = (raiz / "CONTRIBUTING.md").read_bytes()
        try:
            alvo.write_bytes(original + lixo.encode("utf-8"))
            r = subprocess.run([PY, "scripts/check-doc-hygiene.py"], capture_output=True,
                               cwd=str(base), timeout=600)
            out = (r.stdout + r.stderr).decode("utf-8", "replace")
            linhas = [l.strip()[:118] for l in out.splitlines()
                      if "PROBLEMA" in l or "aviso" in l.lower()]
            esperado_falha = "deve passar" not in rotulo
            resultado = r.returncode != 0
            marca = "OK     " if resultado == esperado_falha else "ERRADO "
            print(f"  {marca} {rotulo:<30} exit={r.returncode} "
                  f"(esperava {'falha' if esperado_falha else 'passar'})")
            for l in linhas[:2]:
                print(f"          {l}")
        finally:
            alvo.write_bytes(original)
