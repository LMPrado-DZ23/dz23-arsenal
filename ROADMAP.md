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

## Status de evals (atualizado 2026-11-09 · pós-Camada 4)

Fonte: `python scripts/run-evals.py --report` · estado de auditoria: `--audit` · método:
[`docs/eval-methodology.md`](docs/eval-methodology.md) · Camada 4:
[`docs/camada-4-2026-11-09.md`](docs/camada-4-2026-11-09.md).

### Por track

| Track | Pendentes | Executados | Observação |
|---|---|---|---|
| **A — reasoning-only** | 43 | 45 | executável sem infra |
| **B — exige infra** | 40 | 0 | `BLOCKED` por Docker/Postgres/Ghidra/browser/hardware |
| **Novos (v1.4.5)** | 3 | 0 | OB-03/04/05 — nasceram depois da classificação |
| **Total pendente** | **86** | — | de 131 declarados |

### Cobertura

| Métrica | Valor |
|---|---|
| Declarados | **131** |
| Executados | **45 (34,4%)** |
| Criticidade A (crítico) identificada | 45 |
| Críticos executados | **32 (71%)** — os 13 restantes exigem infra |
| Auditados em literais | **16/16 da amostra** |
| Camada 4 | 1 tarefa (CI verde) — **não é eval**, não entra em cobertura |

### Por skill

| Skill | Total | Executados | PASS | PARTIAL | FAIL |
|---|---|---|---|---|---|
| `dz23-spec-to-system-engine` | 15 | 10 | 10 | 0 | 0 |
| `dz23-backend-data-architect` | 12 | 10 | 9 | 1 | 0 |
| `dz23-devops-cloud-deployer` | 16 | 7 | 7 | 0 | 0 |
| `dz23-autonomous-improvement-ultimate` | 13 | 5 | 5 | 0 | 0 |
| `dz23-codebase-cartographer` | 15 | 5 | 5 | 0 | 0 |
| `dz23-performance-scalability-engine` | 16 | 3 | 2 | 1 | 0 |
| `dz23-reverse-engineer-anything` | 15 | 3 | 3 | 0 | 0 |
| `dz23-e2e-browser-verifier` | 16 | 1 | 1 | 0 | 0 |
| `dz23-ultimate-pro-max` | 13 | 1 | 1 | 0 | 0 |
| **TOTAL** | **131** | **45** | **43** | **2** | **0** |

### Auditoria (camada 3)

- **Válido:** `reaudit-5-2026-11-09.md` (5/5 PASS) e `reaudit-11-2026-11-09.md` (11/11 PASS), ambos com
  `input` literal.
- **Inválido como evidência:** `audit-2026-11-09.md` — parafraseou 13 de 16 inputs (em 5 removeu a
  armadilha) e citou fora do texto em 16 de 16 (54 de 68 citações não existem na resposta).
- Verificação automatizada no gate: `evals:citacoes` (`run-evals.py --verify-quotes`).

### Próximo passo

Rodada 4 dos 43 do Track A + os 3 novos. E, acima disso: **Camada 4 fora do próprio repo** — uso em projeto
de outra pessoa, onde o erro custa retrabalho e não parágrafo.

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
