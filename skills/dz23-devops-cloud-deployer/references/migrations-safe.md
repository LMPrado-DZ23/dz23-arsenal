# Migração segura no deploy

## Expand → migrate → contract
1. **Expand**: adiciona o novo (coluna nulável, tabela, índice) sem quebrar o código em execução.
2. **Migrate**: código escreve nos dois; backfill preenche o novo em lotes.
3. **Contract**: remove o antigo só quando nenhuma versão em produção o usa.

## Forward-compatible
O código novo precisa funcionar com o schema antigo **e** com o novo (e o antigo com o novo schema,
durante o rollout). Se não funciona, não é deploy progressivo — é janela de manutenção disfarçada.

## Ordem no deploy
```
migração expand → deploy do código novo → backfill → validação → migração contract
```
Nunca rode migração destrutiva antes do código que parou de usá-la.

## Coordenação por ambiente
Staging primeiro, com volume parecido; produção depois. Registre: versão da migração, tempo, lock,
impacto em réplicas.

## Rollback de schema
Rollback de aplicação não desfaz migração. A política é **forward-fix**: corrigir com nova migração
compatível. `down` destrutivo só em ambiente descartável. Se a migração quebra N-1, o rollback de app
falha — o plano precisa cobrir o dado.

## Backup antes
Toda migração que altera/destrói dado exige backup verificado (ver `observability-backup-dr.md`) e
autorização. Sem restore ensaiado, não há garantia.

## Teste
- Rodar `up` → `down` → `up` em container.
- Rodar em cópia anonimizada de produção com volume realista e medir tempo/lock.
- Verificar contagem/soma antes e depois; amostra de registros.

## Quando não basta
Migração de dado de negócio (status, valor, data) exige relatório do que mudou e de quem autorizou.
Contrato de API e modelagem aprofundada ficam em `dz23-backend-data-architect`.

## Critério de saída
(a) expand/contract declarado; (b) compatível com N-1 testado; (c) backup verificado; (d) tempo e lock
medidos; (e) plano de forward-fix escrito.
