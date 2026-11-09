# Modelo de dados na especificação

## Papel aqui
A spec descreve o dado **essencial** — tabela, campo, tipo, constraint, índice e regra. O detalhe de
migração, tuning e RLS fica em `dz23-backend-data-architect`; aqui o objetivo é não deixar o implementador
adivinhar.

## Tipos (consistentes com backend-data)
| Dado | Tipo | Proibido |
|---|---|---|
| id | `UUIDv7` (default quando exposto) ou `BIGINT` interno | sequencial exposto em URL |
| dinheiro | `BIGINT` centavos ou `NUMERIC(19,4)` + moeda | `float`/`real` |
| instante | `TIMESTAMPTZ` (UTC) | timestamp sem fuso |
| data de negócio | `DATE` | datetime com hora zerada |
| status | `ENUM`/tabela de domínio | string livre |
| json estruturado | `JSONB` com schema validado | json sem contrato |

## Tabela de entidade
```
## Entidade: Pedido (orders)

| Campo | Tipo | Nulo | Único | Default | Regra |
|---|---|---|---|---|---|
| id | UUID | não | sim | gen() | PK |
| tenant_id | UUID | não | não | — | FK tenants, índice |
| status | ENUM | não | não | 'pending_payment' | FSM |
| total_cents | BIGINT | não | não | 0 | >= 0 (INV-005) |
| currency | CHAR(3) | não | não | 'BRL' | ISO 4217 |
| created_at | TIMESTAMPTZ | não | não | now() | imutável |
| updated_at | TIMESTAMPTZ | não | não | now() | trigger |
| created_by | UUID | não | não | — | FK users |
| deleted_at | TIMESTAMPTZ | sim | não | null | soft delete |
```

## Constraints que a spec exige
- `NOT NULL` por padrão; nulo só quando é estado de negócio documentado.
- `UNIQUE` composto com `tenant_id` (`(tenant_id, slug)`), nunca global sem intenção.
- `CHECK` para invariante barata (valor >= 0, fim > início).
- FK com `ON DELETE` decidido: `RESTRICT` (padrão), `CASCADE` só quando o filho não existe sem o pai,
  `SET NULL` quando a referência é opcional.

## Índices que a spec exige
Índice nasce da query declarada na spec, não da intuição:
- composto começando por `tenant_id` (`(tenant_id, status, created_at)`);
- parcial quando a consulta é seletiva (`WHERE deleted_at IS NULL`);
- FK sempre indexada (o banco não cria sozinho);
- `EXPLAIN` antes/depois é evidência da implementação, não da spec — mas a spec declara a query alvo.

## Auditoria e histórico
Toda tabela de negócio: `created_at`, `updated_at`, `created_by` (e `updated_by` quando relevante).
Entidade com FSM ganha tabela de histórico de transição (de, para, ator, quando, motivo).

## Multi-tenant no dado
`tenant_id NOT NULL` em toda tabela de negócio; PK composta `(tenant_id, id)` ou índice composto. RLS é
decisão de implementação (`dz23-backend-data-architect`), mas a spec exige que **toda** query filtre tenant.

## Saída
Entidades com tabela de campos, constraints, índices com a query que justifica, FKs com `ON DELETE`,
campos de auditoria e a nota de onde a FSM vira enum/check.
