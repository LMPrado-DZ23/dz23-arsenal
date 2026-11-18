"""prova-consulta-backend.py -- o consultor resolve em portugues e recusa chutar.

Molde obrigatoriao do plano (Trilha A, item 3): toda skill com acervo ganha prova do consultor no
gate, com casos legitimos E controles negativos. O consulta-design tem 11 casos; este segue a mesma
forma, pelas mesmas duas razoes medidas naquela rodada:
  - substring solta fazia 'ux formulario' responder 'Animation :: Duration Timing';
  - um fallback 'nao sei -> devolvo tudo' respondia qualquer pergunta com a tabela inteira.
Ambos passaram no gate antes da prova existir. Sem controle negativo, 'tudo verde' so significa que
ninguem tentou quebrar.
"""
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent if len(sys.argv) < 2 \
    else pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# (args, string que DEVE aparecer na saida)
DEVE_ACHAR = [
    (["tipo", "dinheiro"], "numeric(10,2)"),
    (["tipo", "identificador"], "bigint"),
    (["indice", "tempo de serie"], "BRIN"),
    (["indice", "busca textual"], "GIN"),
    (["migracao", "editar migracao"], "Create new migration instead"),
    (["migracao", "apagar coluna"], "Remove code first"),
    (["http", "parcial"], "PATCH"),
    (["http", "substituir"], "PUT"),
    (["api", "scroll infinito"], "Cursor"),
    (["api", "pagina numerada"], "Offset"),
    (["limite", "interno"], "10000/min"),
    (["limite", "anonimo"], "30/min"),
    (["rest", "criar recurso"], "201"),
    (["rest", "versionamento"], "410"),
    (["rest", "nome"], "kebab-case"),
]

# (args, string que NAO pode aparecer) -- o falso positivo historico era outro dataset responder
DEVE_NEGAR = [
    (["tipo", "quadrado"], "numeric"),          # termo inexistente nao pode despejar a tabela
    (["indice", "xyzabc"], "B-tree"),
    # graphql pertence a OUTRO dominio (estilo de API), que este acervo nao tem. A recusa deve dizer
    # 'sem correspondencia' sem entregar uma linha de decisao como resposta. Cuidado com o criterio:
    # a mensagem de recusa LISTA os valores da tabela para orientar o usuario -- isso e util, nao e
    # aproximar. Exigir que nenhuma palavra apareca na saida cobria a ajuda com suspeita de vazamento
    # e quase me levou a remover uma funcionalidade boa para deixar o teste verde. O que importa e:
    # exit != 0 e nenhuma celula de DECISAO apresentada como resultado (prefixo '[' dos itens).
    (["api", "graphql"], None),
    (["rest", "quasarxyz"], None),          # termo inexistente no dataset rest recusa
]

ruins = []
print("=== casos que devem resolver (portugues -> linha certa) ===")
for args, esperado in DEVE_ACHAR:
    p = subprocess.run([PY, "scripts/consulta-backend.py", *args], capture_output=True,
                       cwd=str(RAIZ), timeout=180)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    ok = esperado.lower() in out.lower() and p.returncode == 0
    print(f"  {'OK   ' if ok else 'ERRADO'} {' '.join(args):<28} esperava '{esperado}'")
    if not ok:
        ruins.append(f"{args}: nao achou '{esperado}' (exit {p.returncode})")

print("\n=== controles negativos: sem correspondencia, nao chute ===")
for args, vedado in DEVE_NEGAR:
    p = subprocess.run([PY, "scripts/consulta-backend.py", *args], capture_output=True,
                       cwd=str(RAIZ), timeout=180)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    recusou = p.returncode != 0 and "sem correspondencia" in out.lower()
    # nenhuma linha de decisao deve ser apresentada como resposta. Itens comecam com '['; a lista
    # orientadora de valores da recusa comeca com 'valores desta tabela:', entao nao confunde.
    entregou_decisao = any(l.strip().startswith("[") for l in out.splitlines())
    limpo = (vedado is None or vedado.lower() not in out.lower()) and not entregou_decisao
    ok = recusou and limpo
    print(f"  {'OK   ' if ok else 'ERRADO'} {' '.join(args):<28} recusou={recusou} "
          f"nao_entregou_decisao={not entregou_decisao}")
    if not ok:
        ruins.append(f"{args}: deveria recusar sem aproximar (exit {p.returncode})")

print("\n=== esquema: colunas declaradas existem nos CSVs? ===")
p = subprocess.run([PY, "scripts/consulta-backend.py", "listar"], capture_output=True,
                   cwd=str(RAIZ), timeout=180)
out = (p.stdout + p.stderr).decode("utf-8", "replace")
if "FALHA de esquema" in out or p.returncode != 0:
    ruins.append("esquema do consultor aponta para colunas inexistentes")
    print("  ERRADO:", out.strip().splitlines()[0][:110])
else:
    print("  OK     todas as colunas buscadas existem nos CSVs")

print()
print("=== busca: varre o acervo inteiro e recusa chute ===")
_pb = subprocess.run([PY, "scripts/consulta-backend.py", "busca", "rollback"], capture_output=True,
                   cwd=str(RAIZ), timeout=180)
_ob = (_pb.stdout + _pb.stderr).decode("utf-8", "replace")
if _pb.returncode != 0 or "[" not in _ob:
    ruins.append("busca rollback nao retornou resultado")
    print("  ERRADO busca positiva vazia")
else:
    print("  OK     busca rollback retornou resultado")
_pn = subprocess.run([PY, "scripts/consulta-backend.py", "busca", "zzxyqwk"], capture_output=True,
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
print(f"OK: {len(DEVE_ACHAR)} termos em portugues resolvem, {len(DEVE_NEGAR)} recusas honestas, "
      "esquema valido")
