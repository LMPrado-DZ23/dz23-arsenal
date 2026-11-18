"""prova-consulta-codebase.py -- o consultor responde em portugues, traduz certo e recusa sem chutar.

Quatro grupos, cada um nascido de um defeito REAL medido na construcao deste ou dos acervos anteriores:
1. Consultas legitimas resolvem para a linha certa.
2. **Exaustao do mapa PT->EN**: todas as chaves executadas, nao uma amostra. Esta checagem pegou 9
   sinonimos inventados por mim nesta rodada ('debugger', 'pm', 'executive', 'verified anchors' -- os
   valores reais sao bug-fixer, pr-reviewer, rca-investigator) e um decimo truncado por eu ter lido uma
   previa de 46 caracteres em vez da celula inteira. Sem exaustao, isso passaria verde.
3. Controles negativos: termo inexistente deve recusar SEM entregar linha de decisao (o falso positivo
   historico era substring solta respondendo a pergunta certa com a linha errada).
4. Esquema: toda coluna em `busca_em` existe no CSV (um nome errado silenciou um dataset inteiro no
   consulta-backend antes desta guarda existir).
"""
import csv
import importlib.util
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent if len(sys.argv) < 2 \
    else pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPT = "skills/dz23-codebase-cartographer/scripts/consulta-codebase.py"


def roda(args):
    p = subprocess.run([PY, SCRIPT, *args], capture_output=True, cwd=str(RAIZ), timeout=180)
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")


ruins = []

DEVE_ACHAR = [
    (["profundidade", "onboarding"], "new-joiner"),
    (["profundidade", "quebrou"], "rca-investigator"),
    (["profundidade", "depurar"], "bug-fixer"),
    (["profundidade", "arquitetura"], "architect"),
    (["antipadrao", "chute"], "Guessed anchors"),
    (["antipadrao", "generico"], "Generic descriptions"),
    (["quando-nao", "refatorar"], "implementation or refactoring"),
]
print("=== consultas em portugues devem resolver ===")
for args, esperado in DEVE_ACHAR:
    rc, out = roda([*args])
    ok = esperado.lower() in out.lower() and rc == 0
    print(f"  {'OK   ' if ok else 'ERRADO'} {' '.join(args):<28} esperava '{esperado}'")
    if not ok:
        ruins.append(f"{args}: nao achou '{esperado}' (exit {rc})")

print("\n=== exaustao do mapa PT->EN contra os valores reais das tabelas ===")
espec = importlib.util.spec_from_file_location("cc", str(RAIZ / SCRIPT))
mod = importlib.util.module_from_spec(espec)
espec.loader.exec_module(mod)
mortos, total = [], 0
for chave, mp in mod.TERMOS.items():
    cfg = mod.DATASETS[chave]
    linhas = mod._ler(cfg["arquivo"])
    valores = {c: {mod._norma(str(r.get(c, ""))) for r in linhas} for c in cfg["busca_em"]}
    for pt, en in sorted(mp.items()):
        total += 1
        alvo = mod._norma(en)
        if not any(alvo == v or mod._casa(alvo, v) for c in cfg["busca_em"] for v in valores[c]):
            mortos.append((chave, pt, en))
print(f"  {'OK   ' if not mortos else 'ERRADO'} {total - len(mortos)}/{total} sinonimos resolvem")
for chave, pt, en in mortos:
    print(f"         MORTO: {chave}:'{pt}' -> '{en}'")
    ruins.append(f"sinonimo morto: {chave}:'{pt}' -> '{en}'")

print("\n=== recusas honestas ===")
for args in (["antipadrao", "quadrado"], ["profundidade", "xyzabc"], ["quando-nao", "graphql"]):
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

print("\n=== integridade do acervo (autocontida, sem depender da fonte ECC) ===")
# A fonte ECC nao e versionada neste repositorio -- entao conferir celula por celula aqui so funcionaria
# na maquina de quem gerou os CSVs, e o restante do gate viraria N/A silencioso. Em vez disso a prova
# verifica o INVARIANTES verificavel em qualquer lugar: cada CSV tem a contagem prometida, toda linha
# traz origem_arquivo/origem_secao preenchidos, e nenhum valor e placeholder de template. A fidelidade
# contra a fonte foi conferida na geracao (44 celulas, zero divergencias) e fica registrada em
# dados/PROVENIENCIA.md com o sha256 de cada arquivo; mudar um byte quebra esta comparacao de hash.
#
# IMPORTANTE sobre o hash: .gitattributes normaliza CSV para LF no indice do git, mas o gerador escreve
# CRLF no disco Windows. Hash de bytes CRUS difere entre checkout e clone limpo -- foi exatamente assim
# que o CI reprovou esta prova (d8f531... no git != f0a10a... no disco) enquanto localmente passava.
# Normalizar \r\n -> \n antes de hashear torna o digest independente de fim de linha, como as rodadas
# 47/48/51 ja exigiam para QUALQUER comparacao de conteudo neste arsenal. Um verificador de integridade
# que depende de EOL nao mede integridade, mede a plataforma de quem gerou.
import hashlib


def _digest_canonico(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()[:16]


MANIFESTO = {
    "quando-nao-usar-code-tour.csv": (4, "1b5186b7870d882f"),
    "leitor-e-profundidade.csv": (8, "0eff7227776d5b38"),
    "antipadroes-de-code-tour.csv": (6, "d8f5312863fc0177"),
}
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
        ruins.append(f"{arq}: {len(regs)} linhas, manifestos diz {esperado}")
    if h != digest:
        ruins.append(f"{arq}: conteudo mudou desde a geracao a partir da fonte ECC "
                     f"(hash canonico {h} != {digest}) -- reconferir fidelidade antes de aceitar")
    if sem_origem:
        ruins.append(f"{arq}: linhas sem origem declarada: {sem_origem}")


print()
print("=== busca: varre o acervo inteiro e recusa chute ===")
_pb = subprocess.run([PY, "scripts/consulta-codebase.py", "busca", "tour"], capture_output=True,
                   cwd=str(RAIZ), timeout=180)
_ob = (_pb.stdout + _pb.stderr).decode("utf-8", "replace")
if _pb.returncode != 0 or "[" not in _ob:
    ruins.append("busca tour nao retornou resultado")
    print("  ERRADO busca positiva vazia")
else:
    print("  OK     busca tour retornou resultado")
_pn = subprocess.run([PY, "scripts/consulta-codebase.py", "busca", "zzxyqwk"], capture_output=True,
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
print(f"OK: {len(DEVE_ACHAR)} consultas corretas, {total} sinonimos vivos, 3 recusas honestas, "
      "esquema valido")

