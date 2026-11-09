# Migração e zero-downtime

## Regra de ouro: expand → migrate → contract
Nunca altere em um passo o que quebra a versão em execução. Três fases:
1. **Expand**: adiciona o novo (coluna nulável, tabela, índice) sem quebrar o código atual.
2. **Migrate**: código escreve nos dois (dual write) ou backfill preenche o novo; leitura passa a usar o novo.
3. **Contract**: remove o antigo só quando nenhuma versão em produção o usa.

## Operações por custo (Postgres)
| Operação | Custo | Como fazer |
|---|---|---|
| `ADD COLUMN` nulável, sem default volátil | barato | direto |
| `ADD COLUMN ... DEFAULT <constante>` | barato (PG 11+) | direto |
| `ADD COLUMN ... DEFAULT <função>` | reescreve tabela | adicionar nulável + backfill + default depois |
| `CREATE INDEX` | lock de escrita | `CREATE INDEX CONCURRENTLY` fora de transação |
| `DROP INDEX` | barato | `DROP INDEX CONCURRENTLY` |
| `ALTER COLUMN TYPE` | reescreve tabela | nova coluna + backfill + troca + drop |
| `SET NOT NULL` | varredura + lock | validar antes (`CHECK ... NOT VALID` → `VALIDATE`) |
| `ADD CONSTRAINT` | lock | `NOT VALID` + `VALIDATE CONSTRAINT` |
| `RENAME COLUMN` | quebra código antigo | expand/contract, ou janela coordenada |
| `DROP COLUMN` | rápido, irreversível | só após contract + backup |

Sempre: `lock_timeout` e `statement_timeout` definidos na migração para não travar fila atrás de lock.

## Backfill
- Em lotes por cursor de PK (`WHERE id > :last ORDER BY id LIMIT 5000`), nunca `UPDATE` da tabela inteira.
- Idempotente e retomável; progresso persistido.
- Pausa entre lotes para não inundar WAL/replicação; monitore lag de réplica.
- Backfill roda como job separado da migração de schema.

## Ordem de deploy
1. Migração expand aplicada.
2. Deploy do código que escreve no novo, com a leitura ainda no antigo (ou tolerante).
3. Backfill.
4. Deploy do código que lê do novo.
5. Migração contract.

Com duas versões rodando (rolling/canary), o código precisa funcionar com os dois schemas simultaneamente — é isso que o dual write e a leitura tolerante garantem.

## Reversibilidade
Toda migração declara: **rollback** (script/DOWN) ou **roll-forward** (o que fazer se der errado). `DROP` e `TRUNCATE` exigem backup verificado e autorização explícita. Migração irreversível é decisão, não descuido.

## Dados e integridade
- Antes de alterar semântica de coluna existente, medir: quantas linhas, quantos nulos, qual distribuição.
- Validar depois: contagem antes/depois, soma de valores, amostragem de registros.
- Migração que muda dado de negócio (status, valor, data) precisa de relatório do que mudou e de quem autorizou.
- Nunca migre em produção sem ter rodado em cópia com volume representativo.

## Testes de migração
- Banco real (container) na CI: `up` → `down` → `up`; e `up` a partir de snapshot de produção anonimizado.
- Medir tempo e lock da migração em tabela com volume realista; documentar duração esperada.
- Teste de compatibilidade: versão N-1 do código contra schema N (expand) e versão N contra schema N-1 (rollback).

## Critério de saída da migração
(a) script up e down; (b) tempo e lock medidos; (c) backfill idempotente e retomável; (d) ordem de deploy escrita; (e) rollback ensaiado; (f) evidência de validação de dados.
