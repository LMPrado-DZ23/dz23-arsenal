#!/usr/bin/env python3
"""check-eval-results.py — valida o diretório evals-results/.

Checa:
  - existe pelo menos 1 registro (o piloto não basta para sempre, mas 0 é erro)
  - cada arquivo .md tem as seções exigidas e um veredito reconhecido
  - o eval-id do arquivo existe no evals.json da skill correspondente
  - veredito PASS traz trecho literal (Evidence não vazio)
  - BLOCKED traz a dependência
  - todo cenário NOT_TESTED está mencionado no ROADMAP.md

Exit: 0 ok · 1 problema
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RES = RAIZ / "evals-results"
SKILLS = RAIZ / "skills"
ROADMAP = RAIZ / "ROADMAP.md"

# Mapa apelido → skill vem de scripts/_tracks.py, derivado do disco. As três cópias
# manuais deste dicionário eram o motivo de dz23-postgres-prod-preflight não conseguir
# registrar eval: record-eval criava uma pasta e este script a rejeitava como "não
# mapeada".
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tracks import para_skill as _para_skill  # noqa: E402

CURTO = _para_skill()

VEREDITOS = ("PASS", "PARTIAL", "FAIL", "NOT_TESTED", "BLOCKED", "NOT_RECOVERED")
SECOES = ("## Cenário", "## Resposta", "## Esperado", "## Avaliação", "## Notas")


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    if not RES.is_dir():
        print("PROBLEMA: evals-results/ não existe")
        return 1

    arquivos = sorted(md for md in RES.glob("*/*.md") if md.parent.name != "_audit-notes")
    if not arquivos:
        print("PROBLEMA: nenhum registro em evals-results/")
        return 1

    problemas: list[str] = []
    for md in arquivos:
        pasta = md.parent.name
        skill = CURTO.get(pasta)
        if skill is None:
            problemas.append(f"{md.relative_to(RAIZ)}: pasta '{pasta}' não mapeada para skill")
            continue
        texto = md.read_text(encoding="utf-8", errors="replace")

        for secao in SECOES:
            if secao not in texto:
                problemas.append(f"{md.relative_to(RAIZ)}: falta seção '{secao}'")

        m = re.search(r"\*\*Veredito:\*\*\s*\*{0,2}([A-Z_]+)", texto)
        if not m:
            problemas.append(f"{md.relative_to(RAIZ)}: sem veredito")
            continue
        veredito = m.group(1)
        if veredito not in VEREDITOS:
            problemas.append(f"{md.relative_to(RAIZ)}: veredito inválido '{veredito}'")

        m_id = re.match(r"\d{4}-\d{2}-\d{2}-(.+)$", md.stem)
        eval_id = m_id.group(1) if m_id else md.stem
        evals_file = SKILLS / skill / "evals" / "evals.json"
        if evals_file.is_file():
            dados = json.loads(evals_file.read_text(encoding="utf-8"))
            ids = {c["id"] for c in dados["cases"]}
            if eval_id not in ids:
                problemas.append(f"{md.relative_to(RAIZ)}: eval '{eval_id}' não existe em {skill}")

        if veredito == "PASS":
            trecho = re.search(r"- Trecho literal:\s*(.+)", texto)
            if not trecho or "sem trecho literal" in trecho.group(1):
                problemas.append(f"{md.relative_to(RAIZ)}: PASS sem trecho literal")
        if veredito == "BLOCKED" and "BLOCKED_BY_EXTERNAL_DEPENDENCY" not in texto:
            problemas.append(f"{md.relative_to(RAIZ)}: BLOCKED sem dependência declarada")

    # Todo cenário sem registro precisa estar declarado no ROADMAP — não basta a seção
    # existir. Antes o teste era apenas `if "Status de evals" not in roadmap`, que passava
    # com a seção vazia e nunca cruzava nada: um NOT_TESTED fantasma dava PROBLEMAS: 0.
    roadmap = ROADMAP.read_text(encoding="utf-8", errors="replace") if ROADMAP.is_file() else ""
    if "Status de evals" not in roadmap:
        problemas.append("ROADMAP.md: falta a seção 'Status de evals'")
    else:
        # Identidade de um registro é (skill, id), não id solto. A pasta de destino já era lida acima
        # (`arquivos` vem do rglob), mas o set descartava a skill -- entao reexecutar o mesmo cenario
        # em datas diferentes produzia UM elemento para DOIS arquivos e a contagem de pendentes ficava
        # otimista por construcao. Medido nesta sessao: apos gravar 2026-11-18-migration-without-rollback
        # ao lado do de 2026-11-09, run-evals dizia 48 registrados e este check, 47 -- os dois "certos"
        # sob premissas diferentes. Ids hoje sao globais entre skills (verificado: zero colisoes), mas
        # isso e propriedade acidental do conteudo, nao contrato; codificar a premissa e o que quebra
        # quando alguem reaproveitar um nome de caso.
        registrados: set[tuple[str, str]] = set()
        for md in arquivos:
            m_id = re.match(r"\d{4}-\d{2}-\d{2}-(.+)$", md.stem)
            if not m_id:
                continue
            # resolver para o NOME da skill, nao o apelido da pasta: declarados monta a outra ponta
            # com nome completo, e comparar apelido contra nome nunca casaria nada (o que, por
            # silencio, contaria todos os cenarios como pendentes).
            skill = CURTO.get(md.parent.name)
            if skill:
                registrados.add((skill, m_id.group(1)))

        declarados: set[tuple[str, str]] = set()
        for pasta_skill in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
            # Ledger de cobertura é das skills DZ23. Skills incorporadas (ex.: untangle-codebase)
            # declaram os próprios evals na própria pasta, NOT_TESTED, mas fora deste total —
            # mesma regra de check-numbers.py, para não mover o denominador das DZ23.
            if not pasta_skill.name.startswith("dz23-"):
                continue
            ev = pasta_skill / "evals" / "evals.json"
            if not ev.is_file():
                continue
            try:
                dados_sk = json.loads(ev.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for case in dados_sk.get("cases", []):
                cid = case.get("id")
                if isinstance(cid, str) and cid:
                    declarados.add((pasta_skill.name, cid))

        pendentes = len(declarados - registrados)

        # O ROADMAP declara o total pendente em tabela ("**Total pendente** | **99**").
        # Exigir que esse número bata pega ROADMAP desatualizado sem obrigar o documento
        # a citar cada id individualmente.
        m_pend = re.search(r"Total pendente\*{0,2}\s*\|\s*\*{0,2}(\d+)", roadmap)
        if m_pend:
            declarado = int(m_pend.group(1))
            if declarado != pendentes:
                problemas.append(
                    f"ROADMAP.md: diz 'Total pendente {declarado}', mas há {pendentes} "
                    f"cenários sem registro em evals-results/")
        elif pendentes:
            problemas.append(
                f"ROADMAP.md: não declara quantos cenários estão pendentes ({pendentes})")

    print(f"registros verificados: {len(arquivos)}")
    if problemas:
        print(f"PROBLEMAS: {len(problemas)}")
        for p in problemas:
            print(f"  - {p}")
        return 1
    print("PROBLEMAS: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
