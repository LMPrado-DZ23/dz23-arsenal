#!/usr/bin/env python3
"""prova-consulta-prune.py -- o consulta-prune responde certo e RECUSA quando deve."""
import csv
import importlib.util
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONS = RAIZ / "scripts" / "consulta-prune.py"
ARQ = RAIZ / "skills" / "prune-tests" / "dados" / "familias-de-poda.csv"


def _run(args):
    r = subprocess.run([sys.executable, str(CONS), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return (r.stdout or "") + (r.stderr or ""), r.returncode


def main() -> int:
    erros = []
    if not ARQ.is_file():
        print(f"FALHA: {ARQ} ausente")
        return 1
    with ARQ.open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    familias = {r["familia"] for r in linhas}
    for col in ("familia", "sinal", "por_que", "acao", "origem_arquivo", "origem_secao"):
        if linhas and col not in linhas[0]:
            erros.append(f"coluna ausente no CSV: {col}")

    positivos = {"implementacao": "reescrever", "passado": "deletar",
                 "snapshot": "framework", "duplicado": "manter"}
    for termo, esperado in positivos.items():
        out, rc = _run(["familia", termo])
        if rc != 0 or "sem correspondencia" in out:
            erros.append(f"'familia {termo}' deveria resolver, recusou")
        elif esperado not in out:
            erros.append(f"'familia {termo}' sem o esperado '{esperado}'")

    out, rc = _run(["busca", "snapshot"])
    if rc != 0 or "Depende do nada" not in out:
        erros.append("busca 'snapshot' deveria achar 'Depende do nada'")
    out, rc = _run(["busca", "zzzqw"])
    if rc == 0 or "sem correspondencia" not in out.lower():
        erros.append("busca inexistente deveria recusar")

    for termo in ("xyzqw", "banana", "futebol"):
        out, rc = _run(["familia", termo])
        if rc == 0 or "sem correspondencia" not in out.lower():
            erros.append(f"controle negativo falhou: 'familia {termo}' nao foi recusado")

    spec = importlib.util.spec_from_file_location("cp", CONS)
    cp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cp)
    vivos = 0
    for pt, canon in cp.SINONIMOS.items():
        if canon not in familias:
            erros.append(f"sinonimo '{pt}' aponta para familia inexistente: {canon}")
        else:
            vivos += 1

    out, _ = _run(["listar"])
    if f"{len(linhas)} familias" not in out:
        erros.append(f"listar nao reporta {len(linhas)} familias")

    if erros:
        for e in erros:
            print(f"FALHA: {e}")
        return 1
    print(f"OK: {len(positivos)} familias resolvem, 3 recusas honestas, busca + recusa, "
          f"{vivos} sinonimos vivos, {len(linhas)} familias")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
