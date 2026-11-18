"""Prova empírica: cada `--check` do repo recusa quando o que ele deveria conferir muda?

Regex dizendo 'tem comparação' não prova nada -- foi assim que um build.py --check passou meses
imprimindo OK sem comparar nada. Aqui se corrompe o ESTADO correspondente e se exige exit != 0.
Um verificador que não reclama diante da violação que promete caçar é o gate-fantasma desta
sessão inteiro, em forma de teste. Um build.py --check passou meses imprimindo OK sem comparar
nada, e nenhuma leitura de código teria visto: só a violação real denuncia o verificador oco.

Rodar antes de confiar no verde do quality-gate, e sempre que um check novo for adicionado.
Não entra no próprio gate porque corrompe arquivos de propósito (e o gate roda esses mesmos
checks) -- é revisão por destruição controlada, com restauração garantida em finally.
"""
import pathlib
import shutil
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
PY = sys.executable
problemas = []


def roda(*args, cwd=None):
    p = subprocess.run([PY, *map(str, args)], capture_output=True, cwd=str(cwd or RAIZ),
                       timeout=300)
    return p.returncode, (p.stdout.decode("utf-8", "replace")
                          + p.stderr.decode("utf-8", "replace"))


def exige_falha(rotulo, alvo, corromper, restaurar, *args, cwd=None):
    """Corrompe `alvo`, roda o check e exige que reclame."""
    backup = alvo.read_bytes() if alvo.is_file() else None
    criado = False
    try:
        corromper()
        rc, s = roda(*args, cwd=cwd)
        if rc == 0:
            problemas.append(f"{rotulo}: saiu 0 com o estado corrompido -- {s.strip()[-120:]}")
            print(f"  OCO     {rotulo}")
        else:
            print(f"  OK      {rotulo}  (exit {rc})")
    finally:
        if backup is not None:
            alvo.write_bytes(backup)
        elif criado and alvo.exists():
            alvo.unlink()
        # sanity: restaurou mesmo?
        if backup is not None and alvo.read_bytes() != backup:
            problemas.append(f"{rotulo}: restauracao nao bateu")


print("=== cada --check contra seu proprio estado corrompido ===")

# 1) build-manifest --check: arsenal.json desatualizado
alvo = RAIZ / "arsenal.json"
def c1():
    import json
    d = json.loads(alvo.read_text(encoding="utf-8"))
    d["counts"]["skills"] = 999
    alvo.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
exige_falha("build-manifest --check (contagem mentirosa)", alvo, c1, None,
            "scripts/build-manifest.py", "--check")

# 2) gera-indice-skills --check: versão errada na tabela
alvo = RAIZ / "skills/README.md"
def c2():
    t = alvo.read_text(encoding="utf-8")
    alvo.write_text(t.replace("| 2.2.4 | UI/UX", "| 1.0.0 | UI/UX"), encoding="utf-8")
exige_falha("gera-indice-skills --check (versao errada)", alvo, c2, None,
            "scripts/gera-indice-skills.py", "--check")

# 3) bundle build --check: agent adulterado
alvo = RAIZ / "bundle/dz23-dsh-agency/agents/00-diretor.txt"
def c3():
    alvo.write_bytes(alvo.read_bytes() + b"\nintruso\n")
exige_falha("bundle build --check (agent adulterado)", alvo, c3, None,
            str(RAIZ / "bundle/dz23-dsh-agency/build.py"), "--check",
            cwd=RAIZ / "bundle/dz23-dsh-agency")

# 4) check-copies: divergir uma cópia embutida
alvo = RAIZ / "skills/dz23-e2e-browser-verifier/scripts/skill_validator.py"
def c4():
    alvo.write_bytes(alvo.read_bytes() + b"\n# drift\n")
exige_falha("check-copies (copia divergente)", alvo, c4, None,
            "scripts/check-copies.py")

# 5) check-numbers: número errado no README
alvo = RAIZ / "README.md"
def c5():
    alvo.write_bytes(alvo.read_bytes().replace("Coleção de 10 skills".encode(),
                                               "Coleção de 7 skills".encode()))
exige_falha("check-numbers (contagem do README)", alvo, c5, None,
            "scripts/check-numbers.py")

# 6) check-docs-runnable: comando apontando para arquivo inexistente
def c6():
    alvo.write_bytes(alvo.read_bytes() + "\n```bash\npython scripts/nao-existe-zz.py\n```\n".encode())
exige_falha("check-docs-runnable (comando quebrado)", alvo, c6, None,
            "scripts/check-docs-runnable.py")

# 7) check-links: link relativo para arquivo ausente
def c7():
    alvo.write_bytes(alvo.read_bytes() + "\nVeja [x](docs/arquivo-que-nao-existe-zz.md).\n".encode())
exige_falha("check-links (link quebrado)", alvo, c7, None, "scripts/check-links.py", ".")

# 8) check-structure: VERSION diferente do frontmatter
alvo = RAIZ / "skills/dz23-postgres-prod-preflight/VERSION"
def c8():
    alvo.write_text("9.9.9\n", encoding="utf-8")
exige_falha("check-structure (VERSION != frontmatter)", alvo, c8, None,
            "scripts/check-structure.py")

# 9) audit-zips: instalação divergente do repo
alvo = pathlib.Path.home() / ".agents/skills/dz23-e2e-browser-verifier/SKILL.md"
if alvo.is_file():
    def c9():
        alvo.write_bytes(alvo.read_bytes() + b"\n# drift de instalacao\n")
    exige_falha("audit-zips (instalacao divergente)", alvo, c9, None,
                "scripts/audit-zips.py")
else:
    print("  PULADO  audit-zips (sem instalacao nesta maquina)")

# 10) quality-gate --json: bem formado e coerente
import json
rc, s = roda("scripts/quality-gate.py", "--json")
try:
    d = json.loads(s)
    ok = d["ok"] is True and d["total"] == len(d.get("checks", d.get("resultados", []) or [])) or d["ok"]
    print(f"  {'OK      ' if d['ok'] else 'FALHA '} quality-gate --json (ok={d['ok']}, total={d['total']})")
    if not d["ok"]:
        problemas.append("quality-gate nao esta verde no estado atual")
except Exception as exc:  # noqa: BLE001
    problemas.append(f"quality-gate --json ilegivel: {exc}")
    print("  ERRO    quality-gate --json")

print("\n=== integridade final: arvore voltou ao HEAD? ===")
r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, cwd=str(RAIZ))
linhas_sujas = [l for l in r.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
# este próprio arquivo pode estar recém-criado e ainda não versionado: não é dano das provas
eu = str(pathlib.Path(__file__).resolve().relative_to(RAIZ)).replace("\\", "/")
sujo = "\n".join(l for l in linhas_sujas if eu not in l)
print(f"  git status: {'LIMPO' if not sujo else chr(10) + sujo}")
if sujo:
    problemas.append(f"provas deixaram a arvore suja: {sujo[:200]}")

print("\n" + "=" * 62)
if problemas:
    print(f"{len(problemas)} problema(s):")
    for p in problemas:
        print("  -", p)
    sys.exit(1)
print("todo --check do repo recusa o estado que promete caçar")
