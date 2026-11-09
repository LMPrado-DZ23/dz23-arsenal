# Modelagem de dados

## Ordem de decisão
1. **Invariantes**: o que nunca pode acontecer (saldo negativo, dois documentos iguais, filho sem pai). Modele no banco quando o banco garante.
2. **Ciclo de vida**: nasce, muda, é arquivado, é apagado? Isso define soft delete, histórico e retenção.
3. **Volume e acesso**: quantas linhas em 1 ano, quais consultas dominam, qual o padrão de leitura. Modelo bom nasce da query.
4. **Tipos e chaves**: escolha consciente, não default do ORM.

## Chaves
- **PK**: `uuid` v7/ULID (padrão quando o id trafega em URL/API — ordenável e não previsível) ou `bigint identity` para tabela interna. UUIDv4 como PK em tabela grande fragmenta índice — aceite só com motivo.
- **Id público**: separado do PK quando o número é sensível (fatura, pedido, usuário). Nunca exponha `SERIAL`/sequencial em URL sem proteção.
- **Natural key**: use como `UNIQUE` adicional (CPF, e-mail, slug), nunca como PK mutável.
- Todo FK tem índice (no Postgres, FK não cria índice sozinho).

## Tipos
| Dado | Tipo correto | Proibido |
|---|---|---|
| Dinheiro | `bigint` em centavos ou `numeric(19,4)` + coluna de moeda | `float`/`real`/`double` |
| Data de negócio (vencimento) | `date` | `timestamp` com hora zerada |
| Instante | `timestamptz` em UTC | `timestamp` sem fuso, hora local |
| Percentual/taxa | `numeric` com escala declarada | `float` |
| Estado | `enum` do banco quando finito e estável, ou tabela de domínio + FK | string livre |
| Texto livre com estrutura | `jsonb` com validação de schema na aplicação e check quando possível | `json` sem validação |
| Telefone/documento | `text` normalizado + coluna de forma canônica | `int` |

## Constraints
- `NOT NULL` por padrão; nulo só quando "ausente" é estado de negócio legítimo e documentado.
- **Auditoria**: `created_at` e `updated_at` `NOT NULL DEFAULT now()` em toda tabela de negócio (`updated_at` mantido por trigger ou pela aplicação — escolha uma e mantenha).
- `UNIQUE` com índice parcial quando a unicidade vale só para parte (`WHERE deleted_at IS NULL`).
- `CHECK` para invariante barata (`amount_cents >= 0`, `ends_at > starts_at`) e para formato.
- `FOREIGN KEY` com `ON DELETE` escolhido conscientemente (`RESTRICT` é o padrão seguro; `CASCADE` só quando o filho não existe sem o pai).
- `EXCLUDE` (Postgres) para sobreposição de período (agenda, reserva).

## Soft delete e histórico
- Soft delete exige: coluna `deleted_at`, índice parcial para as queries vivas, política de retenção e filtro em **todo** acesso (ou view/RLS). Soft delete sem filtro global é vazamento de dado apagado.
- Histórico: tabela de auditoria (quem, quando, antes/depois) ou event sourcing quando o "como chegou aqui" for requisito. Auditoria nunca guarda segredo nem PII desnecessária.
- Imutabilidade: registro financeiro/contábil não é atualizado — é estornado com novo lançamento.

## Modelagem multi-tenant
- `tenant_id` em toda tabela de negócio, `NOT NULL`, FK para o tenant.
- PK composta `(tenant_id, id)` ou índice composto **começando por `tenant_id`** para toda query.
- `UNIQUE` sempre inclui `tenant_id` (`(tenant_id, email)`), nunca global sem intenção.
- RLS no Postgres como segunda barreira: política `USING (tenant_id = current_setting('app.tenant_id')::uuid)`; a aplicação define o setting por transação.
- Teste obrigatório: usuário do tenant A recebe `404/403` ao pedir id do tenant B em cada recurso.

## Particionamento e volume
- Particione por tempo quando a tabela passa de dezenas de milhões de linhas e o acesso é por período.
- Partição não substitui índice; `EXPLAIN` valida que o prune acontece.
- Arquivamento com política (mover para tabela histórica/object storage), não `DELETE` gigante em produção.

## Nomenclatura
`snake_case`, tabela no plural (`orders`, `order_items`), FK `<entidade>_id`, booleano com `is_`/`has_`, data com sufixo `_at`, dinheiro com `_cents` ou `_amount` + `currency`. Consistência vale mais que preferência.

## Critério de saída do modelo
ERD (ou lista de tabelas) + invariantes por tabela + índices propostos com a query que justifica + política de retenção + plano de migração.
