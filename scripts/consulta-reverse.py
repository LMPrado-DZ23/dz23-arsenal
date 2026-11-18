#!/usr/bin/env python3
"""consulta-postgres.py -- acervo de engenharia reversa (anti-padrões por fase, mapa de referências).

Conhecimento DENTRO da skill dz23-reverse-engineer-anything (dados/*.csv), consultável offline. Fonte:
references próprias da skill (ORIGINAL DZ23). Subcomando em português; responde
'sem correspondência' quando não há, nunca aproxima.

  python scripts/consulta-reverse.py listar
  python scripts/consulta-reverse.py anti firmware
  python scripts/consulta-reverse.py anti "simbolo"
  python scripts/consulta-reverse.py referencia emulacao
  python scripts/consulta-reverse.py busca entropia
"""
import argparse
import csv
import pathlib
import re
import unicodedata
import sys


def _acha_raiz() -> pathlib.Path:
    aqui = pathlib.Path(__file__).resolve()
    for alvo in (a.parent for a in [aqui.parent, aqui.parent.parent.parent]):
        if (alvo / "skills").is_dir():
            return alvo
    return aqui.parent.parent


RAIZ = _acha_raiz()
DADOS = RAIZ / "skills" / "dz23-reverse-engineer-anything" / "dados"

DATASETS = {
    "anti": {"arquivo": "anti-padroes.csv",
             "campos": ["fase", "anti_padrao", "por_que_doi", "correcao"],
             "titulo": "Anti-padrão de RE (sintoma, por que dói, correção)"},
    "referencia": {"arquivo": "selecao-de-referencia.csv", "campos": ["situacao", "referencia"],
                   "titulo": "Qual referência carregar para a situação"},
}
APELIDOS = {"antipadrao": "anti", "antipadroes": "anti", "erro": "anti", "fase": "anti",
            "ref": "referencia", "carregar": "referencia"}


def _palavras(s: str) -> set[str]:
    # normaliza acentos para que "producao" case "produção" (ç/á não quebram o match)
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return set(re.findall(r"[a-z0-9]+", s))


def _carrega(nome: str) -> list[dict]:
    p = DADOS / nome
    if not p.is_file():
        raise SystemExit(f"FALHA: {p} ausente. Rode install-all.ps1 -Force ou gere o acervo.")
    with p.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cmd_listar(_a) -> int:
    print(f"acervo em {DADOS.relative_to(RAIZ)}:")
    for chave, d in DATASETS.items():
        n = len(_carrega(d["arquivo"]))
        apel = ", ".join(k for k, v in APELIDOS.items() if v == chave)
        print(f"  {chave:<10} {d['arquivo']:<34} {n:>2} registros   {d['titulo']}  [PT: {apel}]")
    return 0


def _resolve(cmd: str) -> str | None:
    cmd = cmd.lower()
    if cmd in DATASETS:
        return cmd
    return APELIDOS.get(cmd)


def cmd_dataset(args) -> int:
    chave = _resolve(args.dataset)
    if chave is None:
        print(f"sem correspondencia para '{args.dataset}'. Veja 'listar'.")
        return 0
    d = DATASETS[chave]
    linhas = _carrega(d["arquivo"])
    termo = " ".join(args.termo).strip().lower() if args.termo else ""
    if termo:
        pals = _palavras(termo)
        linhas = [r for r in linhas if pals & _palavras(" ".join(r.get(c, "") for c in d["campos"]))]
        if not linhas:
            print(f"sem correspondencia para '{termo}' em {chave}.")
            return 0
    print(f"{d['titulo']} ({len(linhas)}) -- fonte: {linhas[0].get('origem_arquivo', 'ECC (MIT)')}:")
    for r in linhas:
        print("  - " + " | ".join(f"{c}: {r.get(c, '')}" for c in d["campos"]))
    return 0


def cmd_busca(args) -> int:
    termo = " ".join(args.termo).strip().lower()
    pals = _palavras(termo)
    if not pals:
        print("sem termo.")
        return 0
    achados = []
    for d in DATASETS.values():
        for r in _carrega(d["arquivo"]):
            texto = " ".join(r.get(c, "") for c in d["campos"])
            if pals & _palavras(texto):
                achados.append((d["titulo"], texto))
    if not achados:
        print(f"sem correspondencia para '{termo}'.")
        return 0
    print(f"{len(achados)} resultado(s) com '{termo}':")
    for t, texto in achados:
        print(f"  [{t}] {texto[:140]}")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Acervo de engenharia reversa (ORIGINAL DZ23).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar")
    for nome in ("anti", "referencia", "antipadrao", "antipadroes", "erro", "fase", "ref", "carregar"):
        p = sub.add_parser(nome)
        p.add_argument("termo", nargs="*")
        p.set_defaults(dataset=nome)
    pb = sub.add_parser("busca")
    pb.add_argument("termo", nargs="+")
    args = ap.parse_args(argv)
    if args.cmd == "listar":
        return cmd_listar(args)
    if args.cmd == "busca":
        return cmd_busca(args)
    return cmd_dataset(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
