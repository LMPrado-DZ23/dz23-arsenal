#!/usr/bin/env python3
"""prova-consulta-web.py -- prova que o consulta-web responde certo e RECUSA quando deve.

Um consultor que aproxima ('aria' -> qualquer regra) e pior que ausente: o agente confia na linha
errada. Esta prova exige: categorias conhecidas respondem a categoria certa; termos inexistentes
recusam honestamente; todo sinonimo PT do mapa aponta para categoria que existe no acervo; o esquema
e a contagem batem com o CSV.
"""
import csv
import pathlib
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONS = RAIZ / "scripts" / "consulta-web.py"
ARQ = RAIZ / "skills" / "web-design-guidelines" / "dados" / "regras-por-categoria.csv"


def _run(args: list[str]) -> str:
    r = subprocess.run([sys.executable, str(CONS), *args], capture_output=True, text=True,
                       encoding="utf-8")
    return (r.stdout or "") + (r.stderr or "")


def main() -> int:
    erros: list[str] = []

    # 1. esquema do acervo
    if not ARQ.is_file():
        print(f"FALHA: {ARQ} ausente")
        return 1
    with ARQ.open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    for col in ("categoria", "regra", "origem_arquivo", "origem_secao"):
        if linhas and col not in linhas[0]:
            erros.append(f"coluna ausente no CSV: {col}")
    cats = {r["categoria"] for r in linhas}

    # 2. consultas legitimas: a categoria certa responde com regras
    positivos = {
        "acessibilidade": "aria-label",
        "formulario": "label",
        "antipadroes": None,   # so exige que responda alguma regra
        "performance": None,
        "dark": None,
    }
    for termo, esperado in positivos.items():
        out = _run(["categoria", termo])
        if "sem correspondencia" in out:
            erros.append(f"'{termo}' deveria casar uma categoria, recusou")
        elif esperado and esperado not in out:
            erros.append(f"'{termo}' nao trouxe regra esperada ({esperado!r})")

    # 3. controles negativos: termo inexistente RECUSA, nao aproxima
    for termo in ("xyz inexistente", "blockchain", "futebol"):
        out = _run(["categoria", termo])
        if "sem correspondencia" not in out:
            erros.append(f"controle negativo falhou: '{termo}' nao foi recusado")

    # 4. todo sinonimo do mapa aponta para categoria que existe (sem apelido morto)
    sys.path.insert(0, str(RAIZ / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("cw", CONS)
    cw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cw)
    vivos = 0
    for pt, canon in cw.SINONIMOS.items():
        if canon not in cats:
            erros.append(f"sinonimo '{pt}' aponta para categoria inexistente: {canon}")
        else:
            vivos += 1

    # 5. integridade: listar reporta a mesma contagem do CSV
    out = _run(["listar"])
    if f"{len(linhas)} regras" not in out:
        erros.append(f"listar nao reporta {len(linhas)} regras")

    if erros:
        for e in erros:
            print(f"FALHA: {e}")
        return 1
    print(f"OK: categorias certas, {len(positivos)} consultas corretas, 3 recusas honestas, "
          f"{vivos} sinonimos vivos, esquema valido, {len(linhas)} regras em {len(cats)} categorias")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
