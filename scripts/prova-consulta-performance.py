"""prova-consulta-performance.py -- o consultor prioriza certo, traduz certo e recusa sem chutar.

Quatro grupos, cada um nascido de um defeito real medido nesta sessao (nao de checklist inventado):

1. Termos em portugues resolvem para a linha certa do acervo.
2. TODOS os termos do mapa PT->EN, exercitados um a um -- nao uma amostra escolhida a dedo. A primeira
   versao do mapa tinha quatro entradas apontando para o radical ('waterfall' contra 'Waterfalls'), que
   nunca casavam nada, e passaram batidas porque a prova testava justamente os termos que eu havia
   escolhido para ela. Um mapa fechado so e confiavel se cada chave for executada.
3. Controles negativos: termo inexistente deve dar 'sem correspondencia' e exit != 0, SEM entregar linha
   de decisao como resposta. O falso positivo historico do arsenal foi substring solta respondendo a
   pergunta certa com a linha errada ('ux formulario' -> 'Animation :: Duration Timing').
4. Esquema: toda coluna listada em `busca_em` existe no CSV. Ja silenciou um dataset inteiro aqui.
"""
import importlib.util
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent if len(sys.argv) < 2 \
    else pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def roda(args):
    p = subprocess.run([PY, "scripts/consulta-performance.py", *args], capture_output=True,
                       cwd=str(RAIZ), timeout=180)
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")


ruins = []

# --- 1) termos legítimos -----------------------------------------------------------------------
DEVE_ACHAR = [
    (["prioridade", "cascata"], "Eliminating Waterfalls"),
    (["prioridade", "peso"], "Bundle Size Optimization"),
    (["prioridade", "ssr"], "Server-Side Performance"),
    (["prioridade", "animacao"], "Rendering Performance"),
    (["metrica", "lcp"], "Waterfalls"),
    (["metrica", "pulo de layout"], "CLS"),
    (["metrica", "travamento"], "TBT"),
    (["categoria", "bundle"], "bundle-"),
    (["categoria", "renderizacao"], "Rendering Performance"),
]
print("=== termos em portugues devem resolver ===")
for args, esperado in DEVE_ACHAR:
    rc, out = roda([*args])
    ok = esperado.lower() in out.lower() and rc == 0
    print(f"  {'OK   ' if ok else 'ERRADO'} {' '.join(args):<28} esperava '{esperado}'")
    if not ok:
        ruins.append(f"{args}: nao achou '{esperado}' (exit {rc})")

# --- 2) exaustao do mapa -----------------------------------------------------------------------
print("\n=== cada termo do mapa PT->EN resolve? (exaustao, nao amostra) ===")
espec = importlib.util.spec_from_file_location(
    "cp", str(RAIZ / "scripts/consulta-performance.py"))
mod = importlib.util.module_from_spec(espec)
espec.loader.exec_module(mod)
mortos = []
total_termos = 0
for chave, mapa in mod.TERMOS.items():
    cfg = mod.DATASETS[chave]
    linhas = mod._ler(cfg["arquivo"])
    for pt, en in sorted(mapa.items()):
        total_termos += 1
        casa = any(any(mod._casa(alvo, str(r.get(c, ""))) for c in cfg["busca_em"])
                   for r in linhas for alvo in (en, pt))
        if not casa:
            mortos.append(f"{chave}: '{pt}' -> '{en}'")
print(f"  {total_termos - len(mortos)}/{total_termos} termos vivos")
for m in mortos:
    print("    MORTO:", m)
    ruins.append(f"sinonimo morto no mapa: {m}")

# --- 3) controles negativos --------------------------------------------------------------------
print("\n=== recusas honestas (sem aproximar, sem despejar tabela) ===")
DEVE_NEGAR = [
    ["metrica", "quadrado"],
    ["prioridade", "xyzabc"],
    ["categoria", "graphql"],      # outro dominio; nao deve virar linha de prioridade
]
for args in DEVE_NEGAR:
    rc, out = roda(args)
    recusou = rc != 0 and "sem correspondencia" in out.lower()
    entregou = any(l.strip().startswith("[") for l in out.splitlines())
    ok = recusou and not entregou
    print(f"  {'OK   ' if ok else 'ERRADO'} {' '.join(args):<28} recusou={recusou} "
          f"entregou_decisao={entregou}")
    if not ok:
        ruins.append(f"{args}: deveria recusar sem aproximar (exit {rc})")

# --- 4) esquema ---------------------------------------------------------------------------------
print("\n=== colunas declaradas existem nos CSVs ===")
quebradas = mod._colunas_validas()
if quebradas:
    for q in quebradas:
        print("    ERRADO:", q)
        ruins.append(f"esquema: {q}")
else:
    print("    OK     todas as colunas buscadas existem")

print()
if ruins:
    print("PROBLEMAS:")
    for r in ruins:
        print("  -", r)
    sys.exit(1)
print(f"OK: {len(DEVE_ACHAR)} consultas corretas, {total_termos} sinonimos vivos, "
      f"{len(DEVE_NEGAR)} recusas honestas, esquema valido")
