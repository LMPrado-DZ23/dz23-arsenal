"""Confere o que os SKILL.md INSTRUEM a carregar, nao apenas o que existe na pasta.

check-structure e validate_skill verificam que references/*.md existem e que nenhuma referencia
citada esta morta. Falta o outro lado da moeda: cada skill tem um corpo de instrucao dizendo
"carregue references/x.md quando Y". Se esse x nao existe, o agente recebe uma ordem impossível;
se existe mas nunca e citado em nenhum gatilho, o arquivo e peso morto -- ocupa espaco no pacote,
custa manutengao e ninguem jamais le.

Mede os dois sentidos por skill: citacoes sem arquivo (ordem impossivel) e arquivos sem citacao
(material nao enderecado).
"""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SKILLS = RAIZ / "skills"
BT = chr(96)

sem_arquivo = []
sem_gatilho = []
por_skill = {}

for sk in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
    sm = sk / "SKILL.md"
    if not sm.is_file():
        continue
    # corpo inteiro da instrucao: SKILL.md + todos os references (um guia pode apontar o proximo)
    textos = {"SKILL.md": sm.read_text(encoding="utf-8", errors="replace")}
    rdir = sk / "references"
    refs_reais = set()
    if rdir.is_dir():
        for f in sorted(rdir.glob("*.md")):
            refs_reais.add(f.name)
            textos[f"references/{f.name}"] = f.read_text(encoding="utf-8", errors="replace")

    citados = set()
    for origem, t in textos.items():
        for m in re.finditer(BT + r"(?:references/)?([\w\-]+\.md)" + BT, t):
            nome = m.group(1)
            if nome in ("README.md",):
                continue
            if nome in refs_reais:
                citados.add(nome)
            elif "/" in m.group(0) or "references/" in t[max(0, m.start() - 20):m.start()]:
                # Antes de acusar, resolver como referencia a outra skill do arsenal. A frase
                # "`dz23-devops-cloud-deployer` (`references/supply-chain-security.md`)" existe em
                # backend-data-architect e e legitima: o autor nomeia a skill dona do arquivo. Um
                # medidor que so conhece a propria pasta transforma leitura correta em defeito.
                prefixo = t[max(0, m.start() - 260):m.start()]
                vizinhos = [n.name for n in SKILLS.iterdir()
                            if n.is_dir() and n.name != sk.name and f"`{n.name}`" in prefixo]
                if any((SKILLS / v / "references" / nome).exists() for v in vizinhos):
                    continue
                sem_arquivo.append((sk.name, nome, origem))

    nao_enderecados = sorted(refs_reais - citados)
    por_skill[sk.name] = (len(refs_reais), len(citados), nao_enderecados)
    for n in nao_enderecados:
        sem_gatilho.append((sk.name, n))

print("=== cobertura de endereco por skill ===")
for nome, (total_ref, citado, ruins) in por_skill.items():
    marca = "OK" if not ruins else f"{len(ruins)} nao enderecado(s)"
    print(f"  {nome:<44} refs={total_ref:<3} citados={citado:<3} {marca}")
    for r in ruins[:4]:
        print(f"      - {r}")

print(f"\nreferencias citadas sem arquivo correspondente: {len(sem_arquivo)}")
for s, r, o in sem_arquivo[:8]:
    print(f"   {s}: {r} (citado em {o})")

# Alcance direto vs indireto. Um arquivo citado apenas dentro de outro reference so e lido se o
# agente abrir aquele guia -- e as instrucoes de carregamento sob demanda estao no SKILL.md.
# Medir so "existe alguma citacao em algum lugar" aprova material que na pratica nao chega a ninguem.
alcance_indireto = []
for sk in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
    sm = sk / "SKILL.md"
    rdir = sk / "references"
    if not (sm.is_file() and rdir.is_dir()):
        continue
    corpo = sm.read_text(encoding="utf-8", errors="replace")
    nomes = {f.name for f in rdir.glob("*.md")}
    diretos = {n for n in nomes if n in corpo}
    todos = set(diretos)
    for f in rdir.glob("*.md"):
        t = f.read_text(encoding="utf-8", errors="replace")
        todos |= {n for n in nomes if n in t and n != f.name}
    for n in sorted(todos - diretos):
        alcance_indireto.append((sk.name, n))

print(f"\nreferencias alcancaveis apenas por cadeia (nenhuma nomeada no SKILL.md): "
      f"{len(alcance_indireto)}")
for s, n in alcance_indireto[:10]:
    print(f"   {s}: {n}")

totais = sum(v[0] for v in por_skill.values())
enderec = sum(v[1] for v in por_skill.values())
print(f"\ntotal de referencias: {totais} | alcancaveis por alguma instrucao: {enderec}")
problemas = len(sem_arquivo) + len(sem_gatilho) + len(alcance_indireto)
if problemas:
    print(f"PROBLEMAS: {problemas}"
          f" (sem arquivo {len(sem_arquivo)}, sem citacao {len(sem_gatilho)},"
          f" so por cadeia {len(alcance_indireto)})")
else:
    print("toda referencia e nomeada no SKILL.md e toda citacao aponta para arquivo real")
sys.exit(1 if problemas else 0)
