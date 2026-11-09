# Supabase Postgres Best Practices

**Autor:** Supabase
**Repo:** https://github.com/supabase/agent-skills
**Licença:** verificar no repositório

## O que faz

Regras de modelagem e operação para Postgres/Supabase: índices apropriados por padrão de consulta, RLS
(Row Level Security) bem construída, políticas de acesso, uso de funções, conexão com pooler e as
armadilhas de performance em queries sobre tabelas com RLS.

O valor maior não é "boas práticas de SQL" — é RLS: é onde projeto Supabase tipicamente vaza dado ou
perde performance.

## Por que usar em conjunto com DZ23

| Skill DZ23 | Papel |
|---|---|
| `dz23-backend-data-architect` | modelo de dados, contrato, migração reversível, multi-tenancy |
| `dz23-performance-scalability-engine` | mede query, localiza N+1, define budget |
| **Supabase Postgres Best Practices** | **como** escrever o índice, a policy e a query certos |

Sobreposição de conceito: as duas falam de índice e multi-tenancy. A diferença é que DZ23 é agnóstico de
banco e esta é específica de Postgres/Supabase — quando as duas apontam coisas diferentes, vale a
específica **para detalhe de sintaxe**, e a DZ23 **para decisão de arquitetura**.

## Instalação

```bash
git clone https://github.com/supabase/agent-skills.git
cp -r agent-skills/skills/postgres-best-practices ~/.agents/skills/supabase-postgres-best-practices
```

## Exemplo de uso

```
"Essa tabela tem RLS ativa e a listagem está lenta. Aplicando as regras do Supabase:
 me mostra o plano de execução, o índice adequado e como a policy está sendo avaliada."
```

## Alternativas

- `dz23-backend-data-architect` — agnóstico, cobre migração e contrato.
- Documentação do Postgres sobre RLS e índices parciais.

## Cuidados

- **Só útil se o banco for Postgres/Supabase.** Regra de RLS não se aplica a MySQL.
- RLS mal escrita pode **piorar** performance (predicado não indexável) — sempre medir com `EXPLAIN`.
- Segurança de RLS não é opcional: policy desligada é vazamento entre tenants.
