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

## Lock ≠ rewrite (o erro mais caro desta tabela)

`CREATE INDEX CONCURRENTLY` **não roda dentro de transação** — a maioria das ferramentas de migração
(Django, Prisma, golang-migrate com wrapper transacional) falha ou silencia o `CONCURRENTLY` se você
não desligar o wrapper explicitamente. Verificado nesta máquina em Postgres 17.11: as sete asserções
de `examples/postgres-add-column.sql` e `examples/postgres-column-rename.sql` passam com exit 0.

Adicionar coluna é barato **sem reescrita**, mas nunca é barato em lock:

| Operação | Reescreve tabela? | Lock |
|---|---|---|
| `ADD COLUMN x text` (nulável) | não | `ACCESS EXCLUSIVE`, segurado até fim da transação |
| `ADD COLUMN x bool NOT NULL DEFAULT true` (PG 11+) | não — default constante é materializado no metadata | idem |
| `ADD COLUMN x timestamptz DEFAULT clock_timestamp()` | **sim** — default volátil força rewrite | idem |
| `ADD COLUMN x text NOT NULL` em tabela populada | — | falha com `not_null_violation` (SQLSTATE 23502); **não** faz backfill |

Evitar reescrita não evita lock. Mantenha a transação curta; um `ALTER TABLE` que espera por lock atrás
de uma query longa bloqueia tudo que vem depois dele.

## Cinco regras que nenhuma linha acima cobre

1. **Migração aplicada é imutável.** Nunca edite um arquivo de migração que já rodou em produção —
   quem tem o schema antigo não vai reproduzir seu estado. Corrija com migração nova à frente.
2. **Produção é forward-only.** "Rollback" em produção é uma migração nova que desfaz; o `DOWN` serve
   para dev/staging. Depender de `migrate down` em produção é depender de algo que ninguém testou.
3. **DDL e DML nunca na mesma migração.** Schema muda primeiro, dado depois, em passos separados e
   retomáveis. Misturar os dois transforma um backfill que falhou na metade em migração quebrada.
4. **Teste contra volume representativo de produção.** Migração que roda em 100 linhas pode travar por
   horas em 10M. Meça tempo e lock antes, não depois.
5. **Nunca edite manualmente banco de produção.** Toda mudança entra como migração, inclusive a
   correção emergencial.

## Backfill que converge (não só que roda)

O padrão `WHERE id > :last ORDER BY id LIMIT n` avança, mas **não reconcilia**: se o valor antigo
mudou entre a leitura e a escrita, gravar a cópia obsoleta do app destrói o dado novo. Regras que
tornam o lote idempotente e convergente:

```sql
-- Copie o valor na própria linha-alvo, dentro do UPDATE. Nunca traga para a memória
-- do app e escreva depois: essa foto pode estar velha.
UPDATE users SET display_name = username
WHERE id > :de AND id <= :ate
  AND display_name IS DISTINCT FROM username;   -- != nao pega NULL de um lado so
```

- **`IS DISTINCT FROM`** trata par `(NULL, 'x')` e `(NULL, NULL)` corretamente; `<>` silenciosamente
  ignora linha com NULL dos dois lados e nunca conserta valor obsoleto não-nulo.
- Commit por faixa; checkpoint **só depois do commit**; lote que falhou se repete inteiro.
- `FOR UPDATE SKIP LOCKED` quando writers concorrentes existem — o lote pula a linha em vez de esperar
  e morrer no `lock_timeout`.
- Valide a paridade **depois** de todas as faixas, ainda com dual write ligado:
  `SELECT count(*) FROM t WHERE novo IS DISTINCT FROM antigo` precisa ser zero antes de trocar a leitura.

Escolha as bordas pelo espaço de chaves real (inclua id 0 e negativos, se existirem). Preencher
dual write não conserta drift anterior sozinho: drene os escritores antigos **antes** do backfill.

Depois que a escrita passa a ser só na coluna nova, a antiga congela e pode ficar obsoleta — não
reative este backfill nem volte a ler a coluna velha sem um plano de reconciliação explícito.

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

---

**Proveniência.** As seções "Lock ≠ rewrite", "Cinco regras" e "Backfill que converge", bem como os
executáveis `examples/postgres-add-column.sql` e `examples/postgres-column-rename.sql`, derivam do
skill `database-migrations` do [ECC](https://github.com/affaan-m/ECC) (affaan-m/everything-claude-code),
MIT — que por sua vez credita as Supabase Agent Skills, MIT. Destilado e vertido para português, com a
tabela de operações desta página reconciliada às asserções dos exemplos. Verificados em execução nesta
máquina contra Postgres 17.11 (Supabase local): 7 asserções PASS, exit 0, sem resíduo no banco. Registro
completo em `dados-design/VENDOR.md`.
