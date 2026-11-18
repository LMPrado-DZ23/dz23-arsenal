"""Executa TODOS os exemplos de comando que os documentos promovem, e diz quais falham.

O pedido do auditor foi "alinhar backend/performance ao padrao texto-livre do design". Medido: o design
NAO e texto livre -- ambos usam subcomandos, e o unico exemplo em texto livre do repo e um placeholder
de documentacao (`<dominio> <termo>`), nao uma promessa funcional. Antes de reformar tres scripts com
base nessa leitura, o teste que decide e outro: os comandos que um agente copia e cola dos SKILL.md e
references realmente funcionam? Essa sim e a queixa real atras do apontamento (comando copiado falha).
"""
import pathlib
import re
import subprocess
import sys

raiz = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    raiz = pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHAMADA = re.compile(r"python3? scripts/consulta-(\w+)(?:\.py)? ([^\n`|]{0,60})")

exemplos = []
# CHANGELOG e PROVENIENCIA sao registro historico: um comando citado ali pode ter sido escrito antes
# da interface atual, e nao deve ser lido como instrucao vigente. Instrucao viva mora em SKILL.md e
# references/.
docs = [f for f in sorted(raiz.rglob("*.md"))
        if "CHANGELOG" not in f.name and "PROVENIENCIA" not in f.name]
for f in docs:
    if not f.is_file():
        continue
    t = f.read_text(encoding="utf-8", errors="replace")
    for m in CHAMADA.finditer(t):
        dom, resto = m.group(1), m.group(2).strip()
        if "<" in resto or ">" in resto or not resto:
            continue                      # placeholder de doc, nao comando executavel
        script = raiz / "scripts" / f"consulta-{dom}.py"
        if script.is_file():
            exemplos.append((str(f.relative_to(raiz)), script, resto))

print(f"comandos executaveis promovidos pelos documentos: {len(exemplos)}\n")
quebrados = []
for origem, script, args in exemplos:
    partes = [a.strip("\"'") for a in re.findall(r'"[^"]+"|\S+', args)]
    r = subprocess.run([PY, str(script), *partes], capture_output=True,
                       cwd=str(raiz), timeout=180)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    ok = r.returncode == 0
    marca = "OK   " if ok else "QUEBRA"
    print(f"  {marca} {script.name:<24} {' '.join(partes)[:34]:<36} exit={r.returncode}")
    if not ok:
        motivo = next((l.strip()[:74] for l in out.splitlines()
                       if "FALHA" in l or "usage" in l.lower() or "sem corresp" in l.lower()), "?")
        print(f"         {motivo}")
        quebrados.append(f"{origem}: `{' '.join(partes)}` -> {motivo}")

print(f"\nquebrados: {len(quebrados)}/{len(exemplos)}")
for q in quebrados:
    print("  -", q)
sys.exit(1 if quebrados else 0)
