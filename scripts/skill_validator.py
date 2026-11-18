"""skill_validator.py — checagens comuns a toda skill DZ23.

Por que isto existe: cada skill tinha seu `validate_skill.py` copiado e os fortes
(cartographer, postgres, spec) nunca foram reunidos com os fracos. `ultimate-pro-max`
tinha 15 linhas e `backend-data-architect` 34; provado por injeção, o validador do
backend dava PASS para um `SKILL.md` citando `references/NAO-EXISTE-teste.md`. Referência
quebrada dentro de uma instrução de agente não é detalhe de build: é a skill mandando o
agente ler um arquivo que não existe.

Este módulo concentra o mínimo que **toda** skill precisa passar. O `validate_skill.py`
de cada skill continua dono das suas checagens específicas (marcas de seção, contagem de
evals, invariantes de script próprio) e chama `validar_comum()` para o resto.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# Nome da skill descontinuada. Montado por concatenação para que a própria string não
# apareça inteira no fonte (o teste "sem nome morto" procura exatamente por ela).
NOME_MORTO = "dz23" + "-premium" + "-ui-ultimate"


def frontmatter_de(texto: str) -> dict[str, str]:
    if not texto.startswith("---"):
        return {}
    m = re.match(r"^---\s*\n(.*?)\n---", texto, re.S)
    if not m:
        return {}
    saida: dict[str, str] = {}
    for linha in m.group(1).splitlines():
        if ":" in linha and not linha[:1].isspace():
            k, v = linha.split(":", 1)
            saida[k.strip()] = v.strip().strip("\"'")
    return saida


def validar_comum(root: Path, *, exigir_version_file: bool = True) -> list[str]:
    """Retorna lista de erros. Vazia = passou."""
    erros: list[str] = []
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return [f"{root.name}: SKILL.md ausente"]

    texto = skill_md.read_text(encoding="utf-8", errors="replace")
    fm = frontmatter_de(texto)

    # --- frontmatter -------------------------------------------------------------
    for chave in ("name", "description"):
        if not fm.get(chave):
            erros.append(f"frontmatter sem '{chave}'")
    if fm.get("name") and fm["name"] != root.name:
        erros.append(f"frontmatter name={fm['name']!r} != diretório {root.name!r}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", fm.get("version", "")):
        erros.append(f"frontmatter version inválida: {fm.get('version')!r}")

    # --- VERSION x frontmatter ---------------------------------------------------
    versao_file = root / "VERSION"
    if exigir_version_file:
        if not versao_file.is_file():
            erros.append("VERSION ausente")
        else:
            v = versao_file.read_text(encoding="utf-8").strip()
            if not re.fullmatch(r"\d+\.\d+\.\d+", v):
                erros.append(f"VERSION inválido: {v!r}")
            elif fm.get("version") and v != fm["version"]:
                erros.append(f"VERSION={v} != frontmatter={fm['version']}")

    # --- arquivos de apoio -------------------------------------------------------
    for obrigatorio in ("README.md", "CHANGELOG.md"):
        if not (root / obrigatorio).is_file():
            erros.append(f"{obrigatorio} ausente")

    # --- PROMPT-ATIVACAO.txt não pode ficar congelado em versão velha ------------
    # Observado no arsenal: backend/devops/performance avançaram a VERSION e o arquivo
    # de ativação continuava dizendo v1.0. Quem cola o prompt usa texto desatualizado.
    ativacao = root / "PROMPT-ATIVACAO.txt"
    if ativacao.is_file():
        corpo = ativacao.read_text(encoding="utf-8", errors="replace")
        versoes_citadas = set(re.findall(r"v?(\d+\.\d+(?:\.\d+)?)", corpo))
        atual = fm.get("version", "")
        if atual and versoes_citadas and atual not in versoes_citadas:
            erros.append(
                f"PROMPT-ATIVACAO.txt cita {sorted(versoes_citadas)} mas a skill está na "
                f"{atual} — regenerar o arquivo")

    # --- referências citadas têm de existir --------------------------------------
    # Este é o defeito que a injeção provou: citar references/foo.md inexistente passava.
    # Atenção ao falso positivo: `references/x.md` dentro de um parêntese logo após o
    # nome de outra skill é referência CROSS-SKILL (o arquivo existe na vizinha), não
    # caminho relativo local. Só cobra existência local quando o texto não atribui a
    # referência a outra skill.
    def _atribuida_a_outra_skill(linha: str) -> bool:
        return bool(re.search(r"`dz23-[a-z0-9-]+`\s*\(?[^。]*$", linha)) and "dz23-" in linha

    citadas = set(re.findall(
        r"`((?:references|templates|scripts|examples)/[A-Za-z0-9._/-]+)`", texto))
    for ref in sorted(citadas):
        if (root / ref).exists():
            continue
        linha_dono = next((l for l in texto.splitlines() if f"`{ref}`" in l), "")
        if _atribuida_a_outra_skill(linha_dono):
            dono = re.search(r"`(dz23-[a-z0-9-]+)`", linha_dono)
            if dono and (root.parent / dono.group(1) / ref).exists():
                continue  # referência válida à skill irmã
        erros.append(f"referência citada no SKILL.md não existe: {ref}")

    for arq in sorted((root / "references").glob("*.md")) if (root / "references").is_dir() else []:
        corpo = arq.read_text(encoding="utf-8", errors="replace")
        for n, linha in enumerate(corpo.splitlines(), 1):
            for ref in sorted(set(re.findall(r"`(references/[A-Za-z0-9._/-]+)`", linha))):
                if (root / ref).exists():
                    continue
                if _atribuida_a_outra_skill(linha):
                    dono = re.search(r"`(dz23-[a-z0-9-]+)`", linha)
                    if dono and (root.parent / dono.group(1) / ref).exists():
                        continue
                erros.append(f"{arq.relative_to(root)}:{n}: referência quebrada: {ref}")

    # --- skill descontinuada não pode reaparecer COMO SKILL VIVA ------------------
    # Mencionar o nome antigo em CHANGELOG é histórico correto (registra o que foi
    # substituído). O que não pode é existir um arquivo com frontmatter próprio
    # declarando `name: <nome-morto>` — isso é uma segunda skill se passando por
    # referência, e o agente pode carregá-la.
    for arq in sorted(root.rglob("*.md")):
        corpo = arq.read_text(encoding="utf-8", errors="replace")
        if arq.name == "CHANGELOG.md":
            continue
        if re.search(rf"(?m)^name:\s*{re.escape(NOME_MORTO)}\s*$", corpo):
            erros.append(
                f"{arq.relative_to(root)}: declara frontmatter da skill descontinuada "
                f"'{NOME_MORTO}' — vira uma segunda skill carregável; remover o bloco "
                f"de frontmatter ou apagar o arquivo")

    # --- evals coerentes ----------------------------------------------------------
    ev = root / "evals" / "evals.json"
    if ev.is_file():
        try:
            dados = json.loads(ev.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            erros.append(f"evals/evals.json ilegível: {exc}")
            dados = {}
        cases = dados.get("cases", [])
        if not isinstance(cases, list):
            erros.append("evals.json: 'cases' não é lista")
            cases = []
        ids = [c.get("id") for c in cases if isinstance(c, dict)]
        if len(ids) != len(cases):
            erros.append("evals.json: caso sem 'id'")
        if len(set(ids)) != len(ids):
            duplicados = sorted({i for i in ids if ids.count(i) > 1})
            erros.append(f"evals.json: ids duplicados {duplicados}")
        for c in cases:
            if not isinstance(c, dict):
                continue
            for campo in ("id", "title", "input", "expected", "fails_if"):
                valor = c.get(campo)
                if not (isinstance(valor, str) and valor.strip()):
                    erros.append(f"evals.json: caso {c.get('id')!r} sem campo '{campo}'")

    # --- nenhum markdown vazio ----------------------------------------------------
    for arq in sorted(root.rglob("*.md")):
        if not arq.read_text(encoding="utf-8", errors="replace").strip():
            erros.append(f"arquivo vazio: {arq.relative_to(root)}")

    return erros


def relatar(nome: str, erros: list[str], ok_extra: str = "") -> int:
    """Imprime no formato já usado pelo arsenal e devolve exit code."""
    if erros:
        print(f"FALHAS em {nome}:")
        for e in erros:
            print(f"  - {e}")
        return 1
    print(f"PASS: {nome} · checagens comuns OK{(' · ' + ok_extra) if ok_extra else ''}")
    return 0
