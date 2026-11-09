# DZ23 Backend & Data Architect v1.0

Skill de engenharia de backend, banco de dados, contratos de API, migrações seguras, multi-tenancy e observabilidade para DeepSeek Harness e agentes compatíveis com `SKILL.md`.

Cobre o caminho completo de uma entrega de servidor: **modelar o dado → desenhar o contrato → planejar a migração → implementar → testar com banco real → medir → revisar adversarialmente → entregar com evidência**.

## Conteúdo

| Arquivo | Para quê |
|---|---|
| `SKILL.md` | Skill principal: método, módulo 5 (fronteiras, persistência, multi-tenancy, migração, segurança, performance) e padrões inegociáveis |
| `references/service-architecture.md` | Fronteiras, eventos, outbox, idempotência, timeouts e falha parcial |
| `references/data-modeling.md` | Chaves, tipos, constraints, soft delete, multi-tenant e particionamento |
| `references/api-contracts.md` | REST/GraphQL/gRPC, status, erros, paginação, versionamento e eventos |
| `references/migrations-and-zero-downtime.md` | Expand/contract, custo de cada `ALTER`, backfill em lotes e rollback |
| `references/security-and-tenancy.md` | IDOR, injeção, segredos, LGPD, RLS e teste de isolamento |
| `references/performance-and-observability.md` | Índice por query, N+1, cache, pool, SLO e telemetria |
| `references/quality-gates.md` | Gates, severidade (BLOCKER/MAJOR/MINOR) e matriz de teste |
| `references/anti-patterns.md` | 36 erros recorrentes com sintoma, dano e correção |
| `templates/adr.md` | Registro de decisão de arquitetura |
| `templates/contract-review.md` | Checklist de revisão de endpoint |
| `scripts/validate_skill.py` | Validador documental |

## Escopo

Instruções e metodologia. Não é framework, não gera código pronto e não substitui o julgamento sobre o projeto real. A skill exige evidência: plano de query medido, teste com banco real, migração reversível e isolamento de tenant comprovado.

## Uso

1. Instalar a pasta no diretório de skills (`references/installation.md`).
2. Invocar por `/dz23-backend-data-architect` ou por descrição ("modele o schema e escreva a migração reversível").
3. Combinar com `security-review`, `data-migrations`, `api-and-contracts`, `delivery-pipeline` e `dz23-ultimate-pro-max` conforme o roteamento da skill.

**Prompt de ativação:** cole o conteúdo de [`PROMPT-ATIVACAO.txt`](PROMPT-ATIVACAO.txt) no agente.

**Avaliação:** `evals/evals.json` tem 12 cenários de contrato (schema 1). Cenários não são testes executados — rode em harness real e registre o resultado por caso.

**Versão:** `VERSION` (1.0.0) · histórico em [`CHANGELOG.md`](CHANGELOG.md).

## Princípio

Quem constrói não homologa: a entrega declara o que passou, o que **não** foi testado, os riscos e o rollback. `NOT_TESTED` nunca vira `PASS`.

---

## Arsenal — resumo operacional

**Versão real (VERSION/frontmatter):** 1.0.1 · **Categoria:** backend · **Complexidade:** advanced

### Quando usar

- Criar ou alterar serviço, endpoint, schema, tabela, índice ou migração.
- Definir contrato de API entre times.
- Diagnosticar N+1, query lenta ou escrita travada por índice.
- Garantir isolamento de tenant em dado multi-tenant.

### Quando NÃO usar

- Ajuste de UI sem impacto em dados (use `dz23-ultimate-pro-max`).
- Deploy, container ou IaC (use `dz23-devops-cloud-deployer`).
- Migração em produção sem possibilidade de teste: declare `BLOCKED` antes de improvisar.

### Instalação

```bash
# Já incluída no install-all. Manual:
cp -r skills/dz23-backend-data-architect ~/.agents/skills/dz23-backend-data-architect
```

### Uso

```bash
/dz23-backend-data-architect

# ou por descrição — o agente carrega sozinho (ver SKILL.md)
```

### Pré-requisitos de CLI

`git`, `python` (obrigatórias) · `docker`, `sqlite3`, `psql` (recomendadas — sem `psql`, o `EXPLAIN` fica `BLOCKED`).

### Evidência / Quality gates

- Contrato documentado antes da implementação (formato, erros, paginação, idempotência).
- Migração com caminho de reversão declarado.
- Índice justificado por `EXPLAIN` — índice por precaução é bloqueio.
- Prova de isolamento de tenant em toda query multi-tenant.

### Integração com outras skills

Recebe spec de `dz23-spec-to-system-engine` e mapa de `dz23-codebase-cartographer`; entrega imagem/pipeline para `dz23-devops-cloud-deployer`; recebe gargalo de `dz23-performance-scalability-engine`.

### Versão e changelog

Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em [`../../CHANGELOG.md`](../../CHANGELOG.md).
