#!/usr/bin/env python3
"""check-licenses.py — cada componente do arsenal precisa de licença declarada e compatível.

Contexto: o repo é MIT, mas incorpora técnica de terceiros (ECC MIT com uma exceção
CC-BY-SA-4.0, modern-web-guidance Apache-2.0, agent-desktop/playwright/open-code-review
Apache-2.0) e tem componentes próprios sem arquivo LICENSE (pentagi-mcp). Sem checagem
mecânica, "licença verificada" fica sendo memória de quem escreveu o documento.

O que este script exige:
  1. Todo diretório em mcp/ e bundle/ tem LICENSE próprio OU declara `license` no
     package.json. Ausência é falha, não aviso.
  2. Toda referência em external/*.md declara a licença do projeto de origem.
  3. Nenhuma skill própria redistribui texto CC-BY-SA / NC / ND (share-alike ou
     não-comercial contaminam um repo MIT).

Uso:
    python scripts/check-licenses.py          # exit 1 se houver problema
    python scripts/check-licenses.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def apontar_raiz(argv: list[str]) -> list[str]:
    """Consome `--raiz <pasta>` e reposiciona o global RAIZ (ver check-copies.py).

    Os derivados (`base`, `skills`, `ext`) são calculados dentro de main(), depois desta
    chamada, então reatribuir RAIZ basta aqui -- ao contrário de run-evals.py, que congela
    SKILLS/RESULTADOS no import.
    """
    global RAIZ
    restante = list(argv)
    for i, a in enumerate(restante):
        if a == "--raiz" and i + 1 < len(restante):
            RAIZ = Path(restante[i + 1]).resolve()
            del restante[i:i + 2]
            break
        if a.startswith("--raiz="):
            RAIZ = Path(a.split("=", 1)[1]).resolve()
            del restante[i]
            break
    return restante

# Licenças que impedem redistribuição num repo MIT sem separação explícita de obra.
# Precisam casar como token, não como substring: "ND" solto aparece dentro de
# "GRAND", "SECOND", "Kubernetes ND..." e gerava centenas de falsos positivos.
INCOMPATIVEIS: tuple[str, ...] = (
    r"CC[- ]BY[- ]SA",
    r"Attribution[\s-]ShareAlike",
    r"GNU\s+Affero",
    r"\bAGPL\b",
    r"\bGPL[- ]?\d",
    r"\bGPLv[23]",
    r"CC[- ]BY[- ]NC",
    r"NonCommercial",
    r"no\s+derivatives?",
    r"Sem\s+Derivados",
    r"\bLGPL\b",
)


def _ler(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


# Marcas de texto corrompido. Cuidado com falsos positivos: "Ã" ou "Â" sozinhos aparecem
# em português legítimo quando lidos por engano, mas num arquivo UTF-8 válido eles são
# raríssimos; as marcas abaixo são sequências que não existem em texto correto.
MARCAS_MOJIBAKE = ("Ã©", "Ã¡", "Ã£", "Ã§", "Ã­", "Ã´", "Ãµ", "â€", "Ã¶", "Ã¼")


def tem_mojibake(texto: str) -> bool:
    """Detecta texto corrompido, não menção a corrupção.

    U+FFFD isolado também aparece em quem documenta o próprio problema (um comentário
    dizendo 'evita mojibake'), então só se conta quando vem acompanhado de uma das
    sequências típicas de mojibake.
    """
    return any(m in texto for m in MARCAS_MOJIBAKE)


def licenca_de_pasta(pasta: Path) -> tuple[str | None, str | None]:
    """Retorna (fonte, valor): 'arquivo' + nome da licença lida, ou 'package.json' + campo."""
    for nome in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        arq = pasta / nome
        if arq.is_file():
            texto = _ler(arq)[:600]
            if "MIT License" in texto or "Permission is hereby granted, free of charge" in texto:
                return ("arquivo", "MIT")
            if "Apache License" in texto and "Version 2.0" in texto:
                return ("arquivo", "Apache-2.0")
            if "GNU AFFERO" in texto.upper() or "Affero General Public" in texto:
                return ("arquivo", "AGPL")
            if "Creative Commons" in texto:
                return ("arquivo", "Creative Commons")
            return ("arquivo", "desconhecida")
    pkg = pasta / "package.json"
    if pkg.is_file():
        try:
            v = json.loads(_ler(pkg)).get("license")
            if v:
                return ("package.json", str(v))
        except json.JSONDecodeError:
            return ("package.json", "ilegível")
    return (None, None)


EXT_TEXTO_CONHECIDOS = {".md", ".txt", ".json", ".py", ".yml", ".yaml", ".toml", ".cfg",
                        ".ini", ".csv", ".js", ".mjs", ".ts", ".sh", ".ps1", ".cmd"}


def _parece_texto(p: Path) -> bool:
    """Texto de verdade, decidido pelo conteúdo -- não pela extensão.

    Extensão conhecida resolve rápido; sem extensão (LICENSE, NOTICE, VERSION, Dockerfile) ou com
    extensão rara (.env.example, audit-public-file), testa UTF-8 decodificável sem byte nulo. Isso
    fecha o buraco em que 22 arquivos versionados eram invisíveis à checagem de encoding.
    """
    if p.suffix.lower() in EXT_TEXTO_CONHECIDOS or not p.suffix:
        try:
            dados = p.read_bytes()
        except OSError:
            return False
        if b"\x00" in dados[:8192]:
            return False
        return True
    return False


def _arquivos_para_encoding() -> list[Path]:
    """Só o conteúdo versionado. rglob puro varreria 3.639 arquivos de node_modules e qualquer
    artefato local, transformando a checagem em ruído; git ausente (tarball, snapshot) cai no
    rglob com exclusão explícita de dependências."""
    import subprocess

    r = subprocess.run(["git", "ls-files"], capture_output=True, cwd=str(RAIZ), timeout=60)
    if r.returncode == 0 and r.stdout.strip():
        nomes = r.stdout.decode("utf-8", "replace").splitlines()
        return [RAIZ.joinpath(*n.split("/")) for n in nomes]
    ign = ("node_modules", "__pycache__", ".git", "dist", "build")
    return [p for p in RAIZ.rglob("*")
            if p.is_file() and not any(x in p.parts for x in ign)]


def main(argv: list[str]) -> int:
    argv = apontar_raiz(argv)
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--raiz", default=None, help="conferir outra árvore (fixture de teste)")
    args = ap.parse_args(argv)

    problemas: list[str] = []
    inventario: list[dict] = []

    # Nada conferido não é nada aprovado. Cada laço abaixo usa `continue` quando a pasta não
    # existe, então uma árvore vazia -- ou um `--raiz` apontando para o lugar errado -- saía
    # com "licenças consistentes" e exit 0. É o mesmo gate-fantasma que motivou a v1.5.0,
    # reaparecendo aqui por outra porta: ausência de material tem que ser declarada, não
    # confundida com sucesso.
    conferidos = 0

    # 1. Componentes próprios precisam de licença.
    for subpasta in ("mcp", "bundle"):
        base = RAIZ / subpasta
        if not base.is_dir():
            continue
        for pasta in sorted(p for p in base.iterdir() if p.is_dir()):
            conferidos += 1
            fonte, valor = licenca_de_pasta(pasta)
            inventario.append({"componente": f"{subpasta}/{pasta.name}",
                               "fonte": fonte, "licenca": valor})
            if fonte is None:
                problemas.append(
                    f"{subpasta}/{pasta.name}: sem LICENSE e sem campo 'license' no package.json")
            elif valor in ("desconhecida", "Creative Commons", "AGPL"):
                problemas.append(f"{subpasta}/{pasta.name}: licença {valor} — conferir compatibilidade com MIT")

    # 2. Referências externas declaram a licença do origina?
    ext = RAIZ / "external"
    if ext.is_dir():
        for arq in sorted(ext.glob("*.md")):
            if arq.name == "README.md":
                continue
            conferidos += 1
            texto = _ler(arq)
            # Aceita tanto o formato de tabela (`| Licença | MIT |`) quanto o de linha
            # (`**Licença:** MIT`). O separador pode ser `:` ou `|`, e o valor pode vir
            # com `**` colado (markdown). Normalizar antes de casar é mais robusto do
            # que empilhar variações de regex.
            linha = next((l for l in texto.splitlines() if re.search(r"(?i)licen[çc]?a", l)), None)
            if linha is None:
                problemas.append(
                    f"external/{arq.name}: não declara a licença do projeto de origem")
                continue
            valor = re.sub(r"[`*|]", "", linha)
            valor = re.sub(r"(?i).*licen[çc]?a\s*[:|]?\s*", "", valor).strip()
            if not valor:
                problemas.append(f"external/{arq.name}: linha de licença sem valor")
            elif "verificar" in valor.lower():
                problemas.append(
                    f"external/{arq.name}: licença em aberto ('{valor[:48]}') — conferir no "
                    f"upstream antes de redistribuir qualquer trecho")

    # 3. Nenhuma skill própria embute texto incompatível.
    skills = RAIZ / "skills"
    if skills.is_dir():
        padroes = [re.compile(p, re.I) for p in INCOMPATIVEIS]
        for arq in sorted(skills.rglob("*.md")):
            texto = _ler(arq)
            atingido = next((p.pattern for p in padroes if p.search(texto)), None)
            if atingido:
                problemas.append(
                    f"{arq.relative_to(RAIZ)}: menciona licença incompatível ({atingido}) — "
                    f"obra derivada não pode ser redistribuída num repo MIT; manter só como "
                    f"referência em external/")

    # 4. Texto corrompido em qualquer arquivo versionado. O agente que carrega a skill
    #    lê exatamente esses bytes, então U+FFFD dentro de uma regra é bug funcional.
    mojibake: list[str] = []
    este_script = Path(__file__).resolve()
    for arq in _arquivos_para_encoding():
        if not arq.is_file() or ".git" in arq.parts:
            continue
        # Decidir por extensao deixava 22 arquivos versionados invisiveis a esta checagem: os tres
        # LICENSE, NOTICE, os onze VERSION, Dockerfile e os pontos de configuracao -- exatamente os
        # textos que mais importam para licenca. Reproduzido nesta sessao: gravando sequencia UTF-8
        # invalida em LICENSE na raiz, o check saia com 'licencas consistentes' e exit 0. Mesma
        # familia de audit-zips (rodada 51) e build-manifest (rodada 47): criterio por sufixo
        # silenciantdo arquivo sem sufixo. Agora decide-se pelo conteudo, dentro do escopo
        # versionado -- rglob puro varreria 3.639 arquivos de node_modules.
        if not _parece_texto(arq):
            continue
        if arq.resolve() == este_script:
            continue  # este arquivo contém as marcas de propósito, para detectá-las
        try:
            conteudo = arq.read_bytes().decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            problemas.append(f"{arq.relative_to(RAIZ)}: não é UTF-8 válido")
            continue
        if tem_mojibake(conteudo):
            mojibake.append(str(arq.relative_to(RAIZ)))

    if mojibake:
        problemas.append(
            f"{len(mojibake)} arquivo(s) com texto corrompido (U+FFFD ou sequências de "
            f"mojibake): {', '.join(mojibake[:5])}. Isso é lido pelo agente como está.")

    if conferidos == 0 and not problemas:
        # Sem mcp/, sem bundle/ e sem external/*.md não há o que aprovar. Sair 0 aqui faria um
        # `--raiz` errado parecer aprovação -- exatamente o gate-fantasma desta sessão.
        problemas.append(
            f"nenhum componente nem referência externa encontrado em {RAIZ} — "
            f"nada foi conferido, o que não é a mesma coisa que estar correto")

    if args.json:
        print(json.dumps({"ok": not problemas, "problemas": problemas,
                          "conferidos": conferidos,
                          "componentes": inventario, "mojibake": mojibake},
                         ensure_ascii=False, indent=2))
    else:
        for c in inventario:
            print(f"{'OK ' if c['licenca'] else '-- '}{c['componente']:<44} "
                  f"{c['licenca'] or 'SEM LICENÇA'} ({c['fonte'] or '-'})")
        print()
        if problemas:
            for p in problemas:
                print(f"PROBLEMA: {p}")
            print(f"\ntotal: {len(problemas)} problema(s) de licença")
        else:
            print("licenças consistentes")

    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
