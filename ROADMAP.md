# Roadmap e estado honesto

Este documento existe para que ninguém precise acreditar em badge. O que está aqui é o que foi **verificado**;
o que não foi testado está marcado como `NOT_TESTED`, não como "funciona".

## Onde estamos (v1.3.0)

| Componente | Versão | Estado verificado |
|---|---|---|
| 9 skills DZ23 | ver [`INDEX.md`](INDEX.md) | estrutura ✅ · validadores ✅ · **evals `NOT_TESTED`** |
| `mcp/dz23-subagents-universal-mcp` | 4.4.1 | instalado e configurado no ambiente de origem; **não iniciado em CI** |
| `bundle/dz23-dsh-agency` | 1.0.0 | estrutura ✅; `build.py` não executado em CI |
| 9 skills externas | — | apenas documentadas (não redistribuídas) |
| 1 prompt de origem | — | copiado verbatim |

### O que roda em CI (a cada push/PR)

1. `validate_skill.py` de cada skill que tiver um
2. `check-structure.py` — arquivos obrigatórios, frontmatter, `VERSION` × frontmatter, schema dos evals
3. `check-links.py` — todo link relativo `.md` do repositório
4. `build-manifest.py --check` — `arsenal.json` e `INDEX.md` não podem estar desatualizados

Constantes do CI: [`.github/workflows/quality.yml`](.github/workflows/quality.yml).

## O buraco maior: evals não executados

As 9 skills declaram **~137 cenários** em `evals/evals.json`. Executados em harness real e julgados: **3**.

| Skill | Cenários | Executados |
|---|---|---|
| `dz23-performance-scalability-engine` | 16 | 3 (autoavaliados) |
| `dz23-autonomous-improvement-ultimate` | 12 | 1 (`pass-sem-teste`, PASS 6/6) |
| demais 7 | ~109 | 0 |

Isso significa: **o comportamento das skills em produção é não comprovado**, exceto pelos 4 casos acima. O
`evals.json` é especificação de comportamento, não certificado.

## Status de evals (atualizado 2026-11-09 · Rodada 2)

Fonte: `python scripts/run-evals.py --report`. Classificação completa em
[`evals-results/CLASSIFICATION.md`](evals-results/CLASSIFICATION.md); registros em [`evals-results/`](evals-results/).

### Por track

| Track | Total | Executados | % |
|---|---|---|---|
| **A — reasoning-only** | 78 | 25 | **32%** |
| **B — precisa de infra** (Docker/Postgres/Ghidra/browser/hardware) | 40 | 0 | 0% |
| **C — precisa de produto real** | 0 | 0 | — |
| **Total** | **128** | **25** | **19,5%** |

### Por skill

| Skill | Total | Executados | PASS | PARTIAL | FAIL | BLOCKED |
|---|---|---|---|---|---|---|
| `dz23-spec-to-system-engine` | 15 | **10** | 10 | 0 | 0 | 0 |
| `dz23-backend-data-architect` | 12 | **5** | 5 | 0 | 0 | 0 |
| `dz23-reverse-engineer-anything` | 15 | 3 | 3 | 0 | 0 | 0 |
| `dz23-devops-cloud-deployer` | 15 | 3 | 3 | 0 | 0 | 0 |
| `dz23-performance-scalability-engine` | 16 | 3 | 2 | 1 | 0 | 0 |
| `dz23-autonomous-improvement-ultimate` | 12 | 1 | 1 | 0 | 0 | 0 |
| `dz23-codebase-cartographer` | 15 | 0 | 0 | 0 | 0 | 0 |
| `dz23-e2e-browser-verifier` | 15 | 0 | 0 | 0 | 0 | 0 |
| `dz23-ultimate-pro-max` | 13 | 0 | 0 | 0 | 0 | 0 |
| **TOTAL** | **128** | **25** | **23** | **2** | **0** | **0** |

Não houve `FAIL`, então nenhuma regra precisou de correção nesta rodada. **Mas 15 desses 25 registros são
`method: auto`** — o mesmo agente respondeu e julgou. Auto-avaliação não homologa (a performance provou:
3/3 PASS na autoavaliação, 5 defeitos na reauditoria).

### Auditoria externa pendente

**5 dos 15 registros desta rodada** foram separados para revisão independente:
[`evals-results/AUDIT-SAMPLE.md`](evals-results/AUDIT-SAMPLE.md).

Releitura adversarial feita (mesmo autor — **não** é auditoria independente): [`evals-results/AUDIT-RESULT.md`](evals-results/AUDIT-RESULT.md). Resultado: **4 PASS · 1 PARTIAL**, com `float-for-money` rebaixado (o `expected` exige explicar o **erro de arredondamento fiscal** e a resposta só definiu a regra de arredondamento). Achado de infra corrigido: os registros não gravavam `fails_if` — template e backfill dos 25 ajustados.

Os 4 PASS seguem **não homologados** até um agente que nunca viu esta sessão revisar.

### Próximo passo

Rodada 3: os 53 evals reasoning-only restantes (Track A), priorizando categoria **A** — há 45 críticos no
total e apenas 12 executados. Depois, Track B (40 evals) quando houver infra.

### Harness de evals (implementado na v1.4.0)

`scripts/run-evals.py` existe e roda três coisas:

| Comando | O que faz |
|---|---|
| `--list` | lista os cenários por skill |
| `--check` | auditoria **determinística**: schema, ids duplicados, `expected` × `fails_if` contraditórios, cobertura (a regra do `expected` existe no `SKILL.md`/`references`?) e eval possivelmente impossível |
| `--record <skill> <arquivo>` | grava o veredito de quem executou, em `evals-results/<skill>.json` |
| `--report` | estado consolidado: quantos cenários têm resultado |

**O que ele não faz:** executar o comportamento. Isso exige uma sessão de agente real por cenário; o harness
prova que o eval é **coerente e executável** e guarda o veredito de quem executou.

Auditoria de 2026-11-09: **128 cenários, 0 erros de coerência, 3 avisos de cobertura**. Dois defeitos reais
foram encontrados e corrigidos nesse processo (evals de UI na skill de orquestração; `ultimate-pro-max` sem
nenhum eval).

## Dívidas conhecidas

| # | Dívida | Impacto | Esforço |
|---|---|---|---|
| 1 | Evals não executados (128 cenários) | alto — comportamento não comprovado | alto |
| 2 | `install-all.sh` nunca rodou em Linux/macOS | médio — caminho Linux não exercitado | baixo |
| 3 | **CI** — resolvido: rodando desde 2026-11-09 (2 runs verdes). Verificar: `gh run list --limit 5` | — | — |
| 4 | `mcp/` e `bundle/` não são testados em CI | médio | médio |
| 5 | Skills em português; sem tradução para inglês | baixo — alcance | alto |
| 6 | `external/` é só documentação; nenhuma skill externa é testada junto | baixo | — |
| 7 | Sem `evals/results/` versionado (histórico de execução) | médio — falta série temporal | médio |

## Não objetivos (para não prometer o que não vamos fazer)

- Substituir testes reais de produto: as skills organizam trabalho, não substituem QA.
- Instalar ferramenta sem autorização: toda dependência externa é declarada e `BLOCKED` quando falta.
- Ser framework universal: cobre engenharia de software; não é CRM, não é plataforma de agentes.
- Publicar popularidade (estrelas/downloads): número sem verificação é desinformação.

## Como acompanhar

- `INDEX.md` — inventário gerado dos arquivos (sempre atualizado por CI).
- `CHANGELOG.md` — histórico do arsenal; cada skill tem o seu.
- Issues abertas — o que está em andamento.

## Regra de honestidade deste documento

Quando algo passar de `NOT_TESTED` para `PASS`, este arquivo muda **com o comando e a saída** que provaram.
Enquanto isso, `NOT_TESTED` fica escrito — inclusive aqui.
