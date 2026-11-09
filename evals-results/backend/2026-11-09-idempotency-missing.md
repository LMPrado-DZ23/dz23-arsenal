# Eval: idempotency-missing

- **Skill:** dz23-backend-data-architect v1.1.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

POST /payments cria cobrança; cliente faz retry em timeout.

## Resposta

**Retry em timeout não pode virar segunda cobrança. Sem chave de idempotência, `POST /payments` é uma bomba de dinheiro.**

O cliente não sabe se a requisição chegou; ele repete. O servidor recebe duas e cobra duas. Desabilitar botão no front não resolve: retry de rede, app reiniciado e gateway reenviam de qualquer jeito.

Implementação:

```
1. Cliente envia Idempotency-Key: <uuid> por operação (não por tentativa)
2. Servidor grava em idempotency_keys(key, request_hash, response, status, created_at)
   com UNIQUE(key) — a constraint é o que dá a garantia, não o SELECT
3. Mesma chave + mesmo payload → devolve a MESMA resposta gravada (não reprocessa)
4. Mesma chave + payload diferente → 409 conflict
5. TTL de 24–48h (janela de retry real)
6. Gravação da chave e do efeito na MESMA transação, ou outbox
```

Sem transação, existe a janela em que a cobrança foi criada e a chave não — e o retry duplica.

**O que eu não faço:** tratar retry como nova cobrança, nem "só desabilitar o botão". Botão não é garantia de rede.

## Esperado

Exige chave de idempotência persistida, mesma resposta na repetição e 409 para mesma chave com payload diferente.

## Falhas (fails_if)

Aceita o retry como nova cobrança ou sugere 'só desabilitar o botão'.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Retry em timeout não pode virar segunda cobrança.

## Notas

Pediu Idempotency-Key com UNIQUE, mesma resposta na repetição, 409 em payload diferente.
