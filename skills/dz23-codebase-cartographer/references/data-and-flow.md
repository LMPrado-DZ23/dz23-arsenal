# Dados, estado e fluxo

## A pergunta central
Onde mora a verdade? Um sistema pode ter cinco cópias do mesmo dado — banco, cache, fila, arquivo, estado no front. O mapa aponta a fonte e as cópias.

## Inventário de estado
| Onde | O que guarda | Fonte ou cópia? | Evidência |
|---|---|---|---|
| Postgres | pedidos, usuários | **fonte** | `prisma/schema.prisma:12` |
| Redis | sessão, contador | cópia/efêmero | `src/redis.ts:8` |
| S3/local | uploads | **fonte** | `src/storage.ts:21` |
| Fila (SQS/Rabbit) | eventos | transporte | `src/queue.ts:5` |
| Front (store) | seleção de UI | cópia | `src/store/*.ts` |

## Schema e migrações
- Ferramenta (Prisma, Alembic, Knex, Flyway, SQL puro) e onde estão os arquivos.
- Última migração e se há migração pendente (`git log -- migrations/`).
- Convenção: nome, ordem, reversibilidade (`down` existe?).
- Armadilha: schema no ORM e schema real divergindo → conferir com `\d tabela` se houver banco acessível; se não, **marcar como não verificado**.

## Os 5 saltos (obrigatório mapear)
Da tela ao dado, cinco degraus — cada um com arquivo e função exatos:

| # | Salto | O que registrar |
|---|---|---|
| 1 | **UI / evento** | componente + evento (`onClick`, `submit`) → `arquivo:linha` |
| 2 | **API / client** | função do cliente HTTP + método e rota (`POST /orders`) |
| 3 | **Controller + schema** | handler + schema de validação (zod/pydantic/dto) |
| 4 | **Domain / service** | função de regra de negócio — é aqui que o negócio deveria estar |
| 5 | **Persistence / externo** | repositório + tabela + gateway/fila + efeito externo |

```
1. src/features/billing/CheckoutButton.tsx:41   onSubmit → createOrder()
2. src/lib/api/billing.ts:18                    POST /api/v1/orders
3. src/api/orders.controller.ts:22               + src/schemas/order.ts:9 (zod)
4. src/services/checkout.service.ts:57           calcula total, valida cupom
5. src/repositories/order.repo.ts:88             insert orders + order_items
   + gateway de pagamento src/clients/payment.ts:31
   + publica OrderCreated src/events/order.ts:14
```

**Expandir além dos 5**: authN/authZ em qual salto? evento/fila? webhook? resposta (status, shape)? Fronteira de tenant em qual salto é aplicada? Cada um recebe uma linha, no salto onde acontece.

Se algum salto não existir (CLI sem UI, job sem controller), registre `N/A` com motivo — buraco declarado, não inventado.

## Fluxo request → dado
Escreva o caminho com ponteiros, o mesmo do grafo:
```
POST /orders (src/routes/orders.ts:12)
  → valida (src/schemas/order.ts:5)
  → service (src/services/order.ts:40)
  → transação: cria order + itens (src/repositories/order.ts:60)
  → publica OrderCreated (src/events/order.ts:14)
  → worker consome e envia e-mail (src/workers/email.ts:22)
```
Cada seta precisa de arquivo:linha. Sem isso é conto, não mapa.

## Leitura e escrita
Para cada entidade importante: quem **escreve** (e se há mais de um escritor — risco de corrida), quem **lê**, e qual a regra de consistência (transação? eventual? cache com TTL?).

Dois escritores no mesmo dado, sem transação, é achado P1 — registre.

## Transações e fronteiras
- Onde a transação começa e termina.
- Se há efeito externo (e-mail, pagamento) dentro da transação — antipadrão clássico.
- Idempotência declarada em consumidor de fila.

## Dados sensíveis
Onde há PII/segredo, se está cifrado, se sai em log. Não copie valores — só a localização.

## O que declarar como não verificado
Se o banco não é acessível daqui: `schema real NÃO VERIFICADO — inferido de <arquivo>`. Isso muda o nível de confiança das conclusões sobre dado.

## Saída
Tabela de estado, fluxo com ponteiros, tabela escritor/leitor por entidade, e a lista de "não verificado".
