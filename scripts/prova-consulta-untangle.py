#!/usr/bin/env python3
"""prova-consulta-untangle.py -- o consulta-untangle responde certo e RECUSA quando deve.

Molde das outras provas de consultor: casos legitimos que resolvem, controles negativos que
recusam sem aproximar, sinonimos vivos (todo PT do mapa aponta para familia que existe), e busca.
"""
import csv
import importlib.util
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONS = RAIZ / "scripts" / "consulta-untangle.py"
ARQ = RAIZ / "skills" / "untangle-codebase" / "dados" / "familias-de-defeito.csv"


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
    for col in ("familia", "sinal", "principio", "correcao", "origem_arquivo", "origem_secao"):
        if linhas and col not in linhas[0]:
            erros.append(f"coluna ausente no CSV: {col}")

    # 1. consultas legitimas: a familia certa com a correcao esperada
    positivos = {
        "caso-especial": "redesenhar",
        "oculto": "visivel",
        "sobra": "deletar",
        "desnecessario": "inverter",
    }
    for termo, esperado in positivos.items():
        out, rc = _run(["familia", termo])
        if rc != 0 or "sem correspondencia" in out:
            erros.append(f"'familia {termo}' deveria resolver, recusou")
        elif esperado not in out:
            erros.append(f"'familia {termo}' sem o esperado '{esperado}'")

    # 2. busca legitima e negativa
    out, rc = _run(["busca", "wrapper"])
    if rc != 0 or "Sobra" not in out:
        erros.append("busca 'wrapper' deveria achar a familia Sobra")
    out, rc = _run(["busca", "zzzqw"])
    if rc == 0 or "sem correspondencia" not in out.lower():
        erros.append("busca inexistente deveria recusar")

    # 3. controle negativo: familia inexistente RECUSA, nao aproxima
    for termo in ("xyzqw", "banana", "futebol"):
        out, rc = _run(["familia", termo])
        if rc == 0 or "sem correspondencia" not in out.lower():
            erros.append(f"controle negativo falhou: 'familia {termo}' nao foi recusado")

    # 4. sinonimos vivos: todo PT do mapa aponta para familia que existe
    spec = importlib.util.spec_from_file_location("cu", CONS)
    cu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cu)
    vivos = 0
    for pt, canon in cu.SINONIMOS.items():
        if canon not in familias:
            erros.append(f"sinonimo '{pt}' aponta para familia inexistente: {canon}")
        else:
            vivos += 1

    # 5. integridade: listar reporta as 4 familias
    out, _ = _run(["listar"])
    if f"{len(linhas)} familias" not in out:
        erros.append(f"listar nao reporta {len(linhas)} familias")

    if erros:
        for e in erros:
            print(f"FALHA: {e}")
        return 1
    print(f"OK: {len(positivos)} familias resolvem, 3 recusas honestas, busca + recusa, "
          f"{vivos} sinonimos vivos, {len(linhas)} familias em {len(familias)} chaves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
