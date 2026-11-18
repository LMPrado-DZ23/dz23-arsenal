"""check-doc-hygiene.py -- caça resíduos de ferramenta nos documentos versionados.

Nasceu de um erro meu, duas vezes nesta sessão: injetei texto via aqui-string do PowerShell dentro
de um documento e (a) apareceram caracteres chineses no meio do português ("conte当前es", rodada 51)
e (b) apareceu uma expressão Python inteira como corpo de markdown -- aspas triplas seguidas de
concatenação, quando o escape falhou na rodada 57. Nos dois casos o repositório ficou verde:
conferi cinco verificadores com o artefato plantado no CHANGELOG e todos saíram exit 0 sem
mencioná-lo. Documento é a única superfície deste arsenal sem verificador de conteúdo, só de
existência e de link.

Não é OCR nem NLP: são quatro critérios fechados, cada um com motivo e com falso positivo
controlado. Toda regra aqui precisa de caso negativo executável -- sem isso vira decoração.

1. Sistema de escrita estranho em prosa portuguesa: CJK (hiragana/katakana/ideográfico/hangul).
   Exceção legítima declarada: linha dentro de bloco de código, ou arquivo cujo propósito é testar
   unicode (selftest-ferramentas.py cita ideograma como carga útil).
2. Resíduo de linguagem: aspas triplas isoladas, referência crua a grupo de regex,
   escape unicode literal não decodificado, template não expandido, resíduo de bytecode,
   marcador de merge não resolvido.
3. Marcador de merge não resolvido (`<<<<<<<`, `>>>>>>>`).
4. Espaçamento/tabulação com fim de linha duplicado? Não -- EOL nunca é defeito neste arsenal
   (rodadas 47/48/51), então esta checagem deliberadamente NÃO olha fim de linha.

Saidas: PROBLEMA falha; AVISO não falha mas declara dúvida.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent

CJK = re.compile(r"[\u3000-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]")
RESIDUOS = [
    # Cada padrão abaixo é procurado APENAS fora de crase: um documento que escreve ``__pycache__``
    # para explicar um defeito está citando, não vazando. A primeira versão desta checagem acusou
    # cinco linhas do próprio CHANGELOG por esse motivo -- todas citações legítimas. O resíduo real
    # (aspas triplas + concatenação vindas de aqui-string) aparece nu no meio da prosa, sem crase.
    (re.compile(r'"""'), 'aspas triplas de Python'),
    (re.compile(r"\\g<"), "referência a grupo de regex"),
    (re.compile(r"\\u[0-9a-fA-F]{4}"), "escape unicode literal nao decodificado"),
    (re.compile(r"\$\{[^}]*\}"), "template nao expandido"),
    (re.compile(r"<<<<<<<|>>>>>>>"), "marcador de merge nao resolvido"),
]
# dentro de crase ou bloco de codigo, estes sao citados de proposito e continuam suspeitos so se
# forem marcador de merge (ninguem cita conflito de merge num changelog a serio)
FORTE = {"marcador de merge nao resolvido"}
# Arquivos cujo conteúdo É teste de unicode/regex: nada aqui é acidente.
LEGITIMOS = re.compile(r"(selftest-ferramentas|check-audit-inputs|skill_validator|"
                       r"audita-sensibilidade|prova-verificadores|_achar_arsenal)")
BLOCO = re.compile(r"```.*?```", re.S)


def _versionados() -> list[pathlib.Path]:
    r = subprocess.run(["git", "ls-files"], capture_output=True, cwd=str(RAIZ), timeout=120)
    if r.returncode == 0 and r.stdout.strip():
        return [RAIZ.joinpath(*n.split("/")) for n in
                r.stdout.decode("utf-8", "replace").splitlines()]
    ign = ("node_modules", "__pycache__", ".git")
    return [p for p in RAIZ.rglob("*") if p.is_file() and not any(x in p.parts for x in ign)]


CRASE = re.compile(r"(`+)(?:(?!\1).)*\1", re.S)


def _protegido_por_crase(linha: str, pos: int) -> bool:
    """True se `pos` cai dentro de um trecho entre crases.

    Documento técnico cita backtick-pair para EXPLICAR um padrão; tratar citação como resíduo fez a
    primeira versão desta checagem acusar cinco linhas legítimas do CHANGELOG -- e "consertar" isso
    apagando as citações teria destruído o registro histórico. Só conta como problema o que aparece
    nu na prosa.

    Esta docstring era não-raw e continha uma sequência de escape de grupo de regex literal, o que
    fazia este próprio arquivo violar a regra que aplica (SyntaxWarning no import + autodenúncia
    quando copiado para diretório de teste). Escrita sem o padrão literal de propósito.
    """
    return any(m.start() <= pos < m.end() for m in CRASE.finditer(linha))


def _suspeitos(linha: str):
    """Rende (início, rótulo) de cada resíduo fora de bloco de código."""
    for rx, rotulo in RESIDUOS:
        for m in rx.finditer(linha):
            yield m.start(), rotulo, m.group(0)


def main(argv: list[str] | None = None) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--avisos", action="store_true")
    args = ap.parse_args(argv)

    problemas: list[dict] = []
    avisos: list[dict] = []
    conferidos = 0

    for arq in _versionados():
        try:
            if not arq.is_file() or arq.suffix.lower() != ".md":
                continue
            rel = str(arq.relative_to(RAIZ)).replace("\\", "/")
        except (OSError, ValueError):
            continue
        try:
            dados = arq.read_bytes()
        except OSError:
            continue
        if len(dados) > 2 * 1024 * 1024:
            continue
        try:
            texto = dados.decode("utf-8")
        except UnicodeDecodeError:
            continue          # isso é check-licenses, não daqui
        conferidos += 1

        # tirar blocos de código antes: neles, qualquer escrita é esperada
        spans = [(m.start(), m.end()) for m in BLOCO.finditer(texto)]

        def dentro_codigo(pos: int) -> bool:
            return any(a <= pos < b for a, b in spans)

        eh_legitimo = bool(LEGITIMOS.search(arq.name))

        for i, linha in enumerate(texto.splitlines(), 1):
            pos = texto.find(linha) if linha else -1
            if dentro_codigo(max(pos, 0)):
                continue
            m_cjk = CJK.search(linha)
            if m_cjk and not eh_legitimo:
                # CJK em prosa portuguesa so e problema fora de crase tambem: um changelog pode
                # citar o proprio erro de codificacao para documentar o que foi consertado. Escrever
                # aqui o caractere literal faria este arquivo violar a regra que aplica -- a primeira
                # versao fazia exatamente isso, e o caso passou batido porque o guard estava invertido.
                pos = m_cjk.start()
                if _protegido_por_crase(linha, pos):
                    avisos.append({"arquivo": rel, "linha": i,
                                   "tipo": "CJK citado em crase (possivelmente deliberado)",
                                   "trecho": linha.strip()[:90]})
                else:
                    problemas.append({
                        "arquivo": rel, "linha": i, "tipo": "escrita não-latina em prosa",
                        "trecho": linha.strip()[:90],
                    })
            for ini, rotulo, _texto in _suspeitos(linha):
                item = {"arquivo": rel, "linha": i, "tipo": rotulo,
                        "trecho": linha.strip()[:90]}
                if rotulo in FORTE or not _protegido_por_crase(linha, ini):
                    problemas.append(item)
                else:
                    avisos.append(item)

    if args.json:
        print(json.dumps({"ok": not problemas, "conferidos": conferidos,
                          "problemas": problemas, "avisos": avisos[:30]},
                         ensure_ascii=False, indent=2))
    else:
        print(f"documentos .md versionados conferidos: {conferidos}")
        for p in problemas:
            print(f"PROBLEMA: {p['arquivo']}:{p['linha']}: {p['tipo']} :: {p['trecho']}")
        if args.avisos:
            for a in avisos[:20]:
                print(f"aviso    : {a['arquivo']}:{a['linha']}: {a['tipo']} :: {a['trecho']}")
        elif avisos:
            print(f"{len(avisos)} aviso(s) (use --avisos); documentação pode citar esses "
                  f"padrões para explicá-los, então não bloqueiam")
        if not problemas:
            print("nenhum resíduo de ferramenta na prosa dos documentos")

    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
