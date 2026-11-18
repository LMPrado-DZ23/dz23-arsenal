"""prova-consulta-espec.py -- o consultor de ADR responde em portugues, traduz certo e recusa sem chutar.

Cinco grupos, cada um nascido de um defeito REAL medido nos itens anteriores desta consolidacao:
1. Consultas legitimas resolvem para a linha certa.
2. **Exaustao do mapa PT->EN**: todas as 40 chaves executadas contra os valores reais da tabela, nao uma
   amostra. Foi assim que apareceram os sinonimos no radical ('waterfall' vs 'Waterfalls') e os apontando
   para personas inexistentes ('debugger', 'pm'). Sinonimo morto faz o usuario acreditar na ponte.
3. Controles negativos: termo fora do mapa deve recusar SEM entregar linha de decisao.
4. Esquema: toda coluna em `busca_em` existe no CSV (um nome errado silenciou um dataset inteiro).
5. Integridade por hash **CANONICO** (EOL-independente): .gitattributes normaliza CSV para LF no indice,
   o gerador escreve CRLF no disco Windows; hashear bytes crus fez o CI reprovar o item 4 enquanto local
   passava. Normalizar \\r\\n -> \\n antes do sha256 e o que torna a prova valer igual no checkout e no clone.
"""
import csv
import hashlib
import importlib.util
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent if len(sys.argv) < 2 \
    else pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPT = "skills/dz23-spec-to-system-engine/scripts/consulta-espec.py"


def roda(args):
    p = subprocess.run([PY, SCRIPT, *args], capture_output=True, cwd=str(RAIZ), timeout=180)
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")


ruins = []

DEVE_ACHAR = [
    (["categoria", "seguranca"], "Security"),
    (["categoria", "microsservico"], "Architecture patterns"),
    (["categoria", "teste"], "Testing"),
    (["vale", "graphql"], "API design"),
    (["categoria", "infraestrutura"], "Infrastructure"),
]
print("=== consultas em portugues devem resolver ===")
for args, esperado in DEVE_ACHAR:
    rc, out = roda([*args])
    ok = esperado.lower() in out.lower() and rc == 0
    print(f"  {'OK   ' if ok else 'ERRADO'} {' '.join(args):<28} esperava '{esperado}'")
    if not ok:
        ruins.append(f"{args}: nao achou '{esperado}' (exit {rc})")

print("\n=== exaustao do mapa PT->EN contra os valores reais da tabela ===")
espec = importlib.util.spec_from_file_location("ce", str(RAIZ / SCRIPT))
mod = importlib.util.module_from_spec(espec)
espec.loader.exec_module(mod)
mortos, total = [], 0
for chave, mp in mod.TERMOS.items():
    cfg = mod.DATASETS[chave]
    linhas = mod._ler(cfg["arquivo"])
    for pt, en in sorted(mp.items()):
        total += 1
        alvo = mod._norma(en)
        casa = any(alvo == mod._norma(str(r.get(c, ""))) or mod._casa(alvo, str(r.get(c, "")))
                   for c in cfg["busca_em"] for r in linhas)
        if not casa:
            mortos.append((chave, pt, en))
print(f"  {'OK   ' if not mortos else 'ERRADO'} {total - len(mortos)}/{total} sinonimos resolvem")
for chave, pt, en in mortos:
    print(f"         MORTO: {chave}:'{pt}' -> '{en}'")
    ruins.append(f"sinonimo morto: {chave}:'{pt}' -> '{en}'")

print("\n=== recusas honestas ===")
for args in (["categoria", "quadrado"], ["vale", "xyzabc"]):
    rc, out = roda(args)
    recusou = rc != 0 and "sem correspondencia" in out.lower()
    entregou = any(l.strip().startswith("[") for l in out.splitlines())
    ok = recusou and not entregou
    print(f"  {'OK   ' if ok else 'ERRADO'} {' '.join(args):<28} recusou={recusou} "
          f"entregou_decisao={entregou}")
    if not ok:
        ruins.append(f"{args}: deveria recusar sem aproximar (exit {rc})")

print("\n=== esquema: colunas buscadas existem nos CSVs ===")
quebradas = mod._colunas_validas()
if quebradas:
    for q in quebradas:
        print("    ERRADO:", q)
        ruins.append(f"esquema: {q}")
else:
    print("    OK     todas as colunas existem")

print("\n=== integridade do acervo por hash CANONICO (EOL-independente) ===")
# Ver nota no cabecalho: este e o ponto exato que o CI pegou no item 4. Hashear bytes crus reprova um
# checkout Linux cujo conteudo e identico ao disco Windows so porque o git normalizou CRLF->LF.
MANIFESTO = {"categorias-de-decisao-adr.csv": (8, "21226a0132c4c7bb")}


def _digest_canonico(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]


for arq, (esperado, digest) in MANIFESTO.items():
    p = mod.DADOS / arq
    if not p.is_file():
        ruins.append(f"{arq}: ausente")
        continue
    h = _digest_canonico(p)
    with p.open(encoding="utf-8-sig", newline="") as fh:
        regs = list(csv.DictReader(fh))
    sem_origem = [r["No"] for r in regs
                  if not str(r.get("origem_arquivo", "")).strip()
                  or not str(r.get("origem_secao", "")).strip()]
    ok = len(regs) == esperado and h == digest and not sem_origem
    print(f"  {'OK   ' if ok else 'ERRADO'} {arq:<34}{len(regs)} linhas (esperava {esperado}), "
          f"hash={'igual' if h == digest else h}, origem_preenchida={not sem_origem}")
    if len(regs) != esperado:
        ruins.append(f"{arq}: {len(regs)} linhas, manifesto diz {esperado}")
    if h != digest:
        ruins.append(f"{arq}: conteudo mudou desde a geracao (hash canonico {h} != {digest}) "
                     "-- reconferir fidelidade antes de aceitar")
    if sem_origem:
        ruins.append(f"{arq}: linhas sem origem declarada: {sem_origem}")

print()
print("=== busca: varre o acervo inteiro e recusa chute ===")
_pb = subprocess.run([PY, "scripts/consulta-espec.py", "busca", "schema"], capture_output=True,
                   cwd=str(RAIZ), timeout=180)
_ob = (_pb.stdout + _pb.stderr).decode("utf-8", "replace")
if _pb.returncode != 0 or "[" not in _ob:
    ruins.append("busca schema nao retornou resultado")
    print("  ERRADO busca positiva vazia")
else:
    print("  OK     busca schema retornou resultado")
_pn = subprocess.run([PY, "scripts/consulta-espec.py", "busca", "zzxyqwk"], capture_output=True,
                   cwd=str(RAIZ), timeout=180)
_on = (_pn.stdout + _pn.stderr).decode("utf-8", "replace")
if _pn.returncode == 0 or "sem correspondencia" not in _on.lower():
    ruins.append("busca inexistente deveria recusar")
    print("  ERRADO busca negativa nao recusou")
else:
    print("  OK     busca inexistente recusou honestamente")

print()
if ruins:
    print("PROBLEMAS:")
    for r in ruins:
        print("  -", r)
    sys.exit(1)
print(f"OK: {len(DEVE_ACHAR)} consultas corretas, {total} sinonimos vivos, 2 recusas honestas, "
      "esquema valido, integridade canonica conferida")
