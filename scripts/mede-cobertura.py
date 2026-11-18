"""mede-cobertura.py -- que arquivos versionados cada verificador realmente abre.

Nao e um check do gate: e uma lente de diagnostico, usada a mao quando se quer saber se um
verificador cobre o dominio que anuncia. Foi ela que, na rodada 53, expôs a ausencia total de
guarda de credencial neste repositorio publico -- os verificadores liam 713 dos 714 arquivos
versionados, e o unico excluido era justamente mcp/.../.env.example, o arquivo onde um usuario
cola chave. Instrumentando open()/read_bytes()/read_text() via sitecustomize e contando por check.

LIMITACAO CONHECIDA E IMPORTANTE: o hook so vale para o processo em que roda. Verificadores que
abrem arquivos dentro de um subprocesso lancado por eles aparecem com contagem menor ou zero, o
que NAO significa que nao leem nada. Medido nesta sessao: executa-scripts-skills marcava 'lidos=0'
e gera-indice --check marcava 'exit=2 lidos=0' (PYTHONPATH do proprio harness), enquanto
check-secrets aparecia na lista de nunca-lidos apesar de ler e denunciar o .env.example -- provado
colando um ghp_ ali e vendo exit 1 com a linha exata. Antes de tratar qualquer 'nunca lido' como
defeito, confirme por comportamento: injete violacao no arquivo e veja se algum check reclama.
Um numero de cobertura e indício, nunca veredito.
"""
import os
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
PY = sys.executable
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

versionados = set(subprocess.run(["git", "ls-files"], capture_output=True, cwd=str(RAIZ))
                  .stdout.decode("utf-8", "replace").splitlines())

# rastreio de leitura via sitecustomize: registra todo open() em caminho dentro do repo
TRACE = r'''
import builtins, json, os, sys
_abertos = set()
_root = os.path.realpath(%(raiz)s)
_orig_open = builtins.open
def open(file, *a, **k):
    try:
        p = os.fsdecode(file)
        rp = os.path.realpath(p if os.path.isabs(p) else os.path.join(os.getcwd(), p))
        if rp.startswith(_root + os.sep):
            _abertos.add(os.path.relpath(rp, _root).replace(os.sep, "/"))
    except Exception:
        pass
    return _orig_open(file, *a, **k)
builtins.open = open
import io
_orig_rb = None
def _reg(path):
    try:
        rp = os.path.realpath(path if os.path.isabs(path) else os.path.join(os.getcwd(), path))
        if rp.startswith(_root + os.sep):
            _abertos.add(os.path.relpath(rp, _root).replace(os.sep, "/"))
    except Exception:
        pass
_orig_read_bytes = type(pathlib_path := __import__("pathlib").Path()).read_bytes
def read_bytes(self):
    _reg(str(self)); return _orig_read_bytes(self)
type(pathlib_path).read_bytes = read_bytes
_orig_read_text = type(pathlib_path).read_text
def read_text(self, *a, **k):
    _reg(str(self)); return _orig_read_text(self, *a, **k)
type(pathlib_path).read_text = read_text
def _dump():
    try:
        with _orig_open(os.environ.get("TRACE_OUT", ""), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(sorted(_abertos)))
    except Exception:
        pass
import atexit; atexit.register(_dump)
''' % {"raiz": repr(str(RAIZ))}

CHECKS = {
    "check-structure": ["scripts/check-structure.py"],
    "check-copies": ["scripts/check-copies.py"],
    "check-numbers": ["scripts/check-numbers.py"],
    "check-licenses": ["scripts/check-licenses.py"],
    "check-links": ["scripts/check-links.py", "."],
    "check-docs-runnable": ["scripts/check-docs-runnable.py"],
    "check-eval-results": ["scripts/check-eval-results.py"],
    "checa-ancoras": ["scripts/checa-ancoras.py"],
    "checa-enderecamento": ["scripts/checa-enderecamento.py"],
    "gera-indice (--check)": ["scripts/gera-indice-skills.py", "--check"],
    "audit-zips": ["scripts/audit-zips.py"],
    "executa-scripts-skills": ["scripts/executa-scripts-skills.py"],
}

tmp = RAIZ.parent / "sitecustomize.py"
tmp.write_text(TRACE, encoding="utf-8")

cobertura = {}
for nome, args in CHECKS.items():
    out_file = str(RAIZ.parent / f"_trace_{nome.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')}.json")
    env = dict(__import__("os").environ)
    # sitecustomize e importado automaticamente pelo CPython quando esta no PYTHONPATH
    env["PYTHONPATH"] = str(RAIZ.parent)
    env["TRACE_OUT"] = out_file
    cmd = [PY, *[str(RAIZ / a) for a in args]]
    p = subprocess.run(cmd, capture_output=True, cwd=str(RAIZ), env=env, timeout=900)
    lidos: set[str] = set()
    tp = pathlib.Path(out_file)
    if tp.is_file():
        lidos = set(__import__("json").loads(tp.read_text(encoding="utf-8")))
        tp.unlink(missing_ok=True)
    cobertura[nome] = (p.returncode, sorted(lidos))
    print(f"  {nome:<26} exit={p.returncode} arquivos lidos={len(lidos)}")

tmp.unlink(missing_ok=True)

print("\n=== arquivos versionados que NENHUM verificador abre ===")
todos_lidos = set()
for _, lidos in cobertura.values():
    todos_lidos |= set(lidos)
nunca = sorted(versionados - todos_lidos)
from collections import Counter
print(f"  versionados: {len(versionados)} | lidos por ao menos um: {len(versionados & todos_lidos)}"
      f" | nunca lidos: {len(nunca)}")
c = Counter(n.split("/")[0] if "/" in n else "(raiz)" for n in nunca)
print(f"  distribuicao dos nunca lidos: {dict(c.most_common(8))}")
for n in nunca[:18]:
    print("   ", n)
