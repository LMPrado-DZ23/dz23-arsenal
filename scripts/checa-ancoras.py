"""checa-ancoras.py -- toda âncora de edição deste repo ainda aponta para algo real?

Duas vezes nesta sessão eu "editei" um documento e a substituição não casou: o texto novo nunca
entrou no arquivo, e nada reclamou, porque editar por busca-e-substituição silenciosa tem exit 0
por construção. A primeira vez passou despercebida até alguém ler o ROADMAP e notar uma dívida que
nunca foi escrita lá.

Este script inverte a direção: em vez de confiar que a edição aconteceu, verifica se as alegações
estruturais dos documentos continuam presentes e coerentes. É barato, determinístico, e pega a
classe inteira (texto perdido, dívida duplicada, numeração furada, versão órfã).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def chave(v: str):
    return tuple(int(x) for x in v.split("."))


def problemas_roadmap() -> list[str]:
    t = (RAIZ / "ROADMAP.md").read_text(encoding="utf-8")
    out: list[str] = []
    i = t.find("| # | D")
    if i < 0:
        return ["ROADMAP sem tabela de dívidas"]
    seg = t[i:i + 9000]
    ids = re.findall(r"(?m)^\|\s*(\d+\w?)\s*\|", seg)
    if not ids:
        return ["tabela de dívidas sem linhas"]
    duplicados = sorted({n for n in ids if ids.count(n) > 1})
    if duplicados:
        out.append(f"dívidas com id repetido: {duplicados}")
    ints = sorted(int(n) for n in ids if n.isdigit())
    buracos = [k for k in range(1, max(ints) + 1) if k not in ints]
    if buracos:
        out.append(f"numeração de dívidas com buraco: {buracos}")
    # cada linha de dívida precisa das 4 colunas
    for m in re.finditer(r"(?m)^\|\s*(\d+\w?)\s*\|(.*)$", seg):
        corpo = m.group(2)
        if corpo.count("|") < 3:
            out.append(f"dívida {m.group(1)} sem colunas de impacto/esforço")
    return out


def problemas_changelog() -> list[str]:
    out: list[str] = []
    p = RAIZ / "CHANGELOG.md"
    if not p.is_file():
        return ["CHANGELOG.md ausente"]
    texto = p.read_text(encoding="utf-8")
    # Capturar o cabeçalho inteiro, não só \d+.\d+: uma linha `## [1.6.0-rc1]` ou um typo
    # `## [v1.5.14]` é uma entrada de versão que o leitor humano vê. Se o parser ignorar o
    # sufixo, a entrada some da checagem de ordem e do "topo é a maior" -- verificadores que
    # silenciosamente não enxergam parte do domínio são pior que cobertura menor declarada.
    brutas = re.findall(r"(?m)^## \[([^\]]+)\]", texto)
    vs = [v for v in brutas if re.fullmatch(r"\d+(?:\.\d+)+", v)]
    nao_lidas = sorted(set(brutas) - set(vs))
    if nao_lidas:
        out.append(f"entradas de versão que o parser não lê (ordem não garantida): "
                   f"{nao_lidas[:4]}")
    if not vs:
        return out or ["CHANGELOG sem entradas"]
    ruins = [(vs[i], vs[i + 1]) for i in range(len(vs) - 1) if chave(vs[i]) < chave(vs[i + 1])]
    if ruins:
        out.append(f"CHANGELOG fora de ordem descendente: {ruins[:3]}")
    # Comparação só entre vizinhos deixa passar um caso que já aconteceu aqui: uma entrada
    # nova registrada no lugar errado do arquivo, abaixo da mais antiga. Aquilo gera inversão
    # adjacente e é pego -- mas mover a [1.5.0] para o topo, ou qualquer versão para uma
    # posição onde continua menor que o vizinho de baixo, não gera. A propriedade que importa
    # é global: quem está no topo tem de ser a maior versão do arquivo.
    maior = max(vs, key=chave)
    if vs[0] != maior:
        out.append(f"CHANGELOG abre com [{vs[0]}] mas a maior versão do arquivo é [{maior}]")
    dups = sorted({v for v in brutas if brutas.count(v) > 1})
    if dups:
        out.append(f"CHANGELOG com versão repetida: {dups}")
    return out


def problemas_skills() -> list[str]:
    out: list[str] = []
    for sk in sorted(p for p in (RAIZ / "skills").iterdir() if p.is_dir()):
        ch = sk / "CHANGELOG.md"
        vf = sk / "VERSION"
        if not (ch.is_file() and vf.is_file()):
            continue
        atual = vf.read_text(encoding="utf-8").strip()
        texto = ch.read_text(encoding="utf-8")
        vs = re.findall(r"(?m)^#+\s*\[?(\d+\.\d+[\w.]*)\]?", texto)
        vs = [v for v in vs if re.match(r"^\d+\.\d+", v)]
        if not vs or vs[0] != atual:
            out.append(f"{sk.name}: topo do changelog é [{vs[0] if vs else 'nada'}], VERSION={atual}")
            continue
        ks = [chave(v) for v in vs if re.match(r"^\d+\.\d+$", v)]
        ruins = [(vs[i], vs[i + 1]) for i in range(len(ks) - 1) if ks[i] < ks[i + 1]]
        if ruins:
            out.append(f"{sk.name}: changelog fora de ordem {ruins[:2]}")
    return out


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    todos = problemas_roadmap() + problemas_changelog() + problemas_skills()
    print("âncoras estruturais conferidas: ROADMAP, CHANGELOG, 10 changelogs de skill")
    if todos:
        for p in todos:
            print(f"PROBLEMA: {p}")
        print(f"\ntotal: {len(todos)}")
        return 1
    print("todas coerentes (ordem, numeração, versão corrente no topo)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
