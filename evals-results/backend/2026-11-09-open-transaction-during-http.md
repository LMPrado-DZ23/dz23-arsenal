# Eval: open-transaction-during-http

- **Skill:** dz23-backend-data-architect v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

BEGIN; UPDATE stock; chamar API de pagamento; COMMIT.

## Resposta

**Chamada HTTP dentro de transação aberta: remover. Segurar transação durante I/O é o caminho mais rápido para lock em cascata e pool esgotado.**

```
-- ERRADO
BEGIN;
UPDATE stock SET qty = qty - 1 WHERE sku = $1;   -- lock adquirido
-- ~300 ms de I/O externo: pagamento, adquirente, timeout, retry
COMMIT;
```

Enquanto o pagamento responde, a linha está travada e a conexão do pool está ocupada. Se o provedor demora 5 s, todas as vendas daquele SKU enfileiram — e o pool (10–20 conexões) satura com meia dúzia de checkouts.

```
-- CERTO: reserva curta + confirmação em duas etapas
BEGIN;
  ... valida e grava RESERVA com expiração (ex.: 5 min), sem chamar HTTP;
COMMIT;
-- fora da transação:
  chamada ao pagamento com timeout curto e retry idempotente;
BEGIN;
  ... confirma a reserva (ou libera, se falhou), com lock curto;
COMMIT;
job: expira reservas órfãs.
```

Declarar `lock_timeout` e `statement_timeout` na sessão, e medir o tempo de lock em produção.

**O que eu não faço:** manter o HTTP dentro da transação "porque é mais simples". Simples aqui se paga em indisponibilidade.

## Esperado

Corrige: I/O fora da transação, ou reserva + confirmação em duas etapas; lock medido e timeout declarado.

## Falhas (fails_if)

Mantém a chamada HTTP dentro da transação.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Chamada HTTP dentro de transação aberta: remover.

## Notas

Re-leitura adversarial: menor: cita 'pool (10–20 conexões)' e '5 min' como se fossem valores do contexto — números ilustrativos sem fonte
