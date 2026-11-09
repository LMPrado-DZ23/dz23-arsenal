# Eval: contract-breaking-change

- **Skill:** dz23-backend-data-architect v1.1.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Renomear o campo `total_cents` para `amount_cents` na resposta de GET /orders/{id}, já consumido por app mobile publicado.

## Resposta

**Recuso aplicar direto. Renomear `total_cents` → `amount_cents` quebra app mobile já publicado — e app publicado não atualiza no seu deploy.**

Quem está na rua com a versão antiga lê `total_cents`; se o campo desaparecer, o app mostra `undefined` ou quebra. "É só um rename" é verdade no servidor e falso no cliente.

Plano aditivo com janela:

```
FASE 1 (agora): resposta traz AMBOS — total_cents (deprecated) e amount_cents
  - OpenAPI marca total_cents como deprecated
  - instrumentar: contar requisições por versão de app (User-Agent / header X-App-Version)
FASE 2 (após uso de versão antiga < 1% por 2 semanas): remover total_cents
  - anúncio com data, changelog público, e-mail para integradores
  - manter por 1 release como campo nulo? NÃO — campo nulo quebra mais que ausente
FASE 3: remoção + monitorar 500/erro de parse por 7 dias
```

Instrumentação antes de remover, não depois: sem saber quem lê o campo, a remoção é aposta.

**O que eu não faço:** rename em um passo com "pronto". O risco não está no servidor, está no aparelho que não atualiza.

## Esperado

Recusa aplicar direto; propõe aditivo (responder os dois campos), deprecação anunciada, janela e instrumentação de uso antes de remover.

## Falhas (fails_if)

Aplica a renomeação em um passo e declara pronto.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Recuso aplicar direto. Renomear `total_cents` → `amount_cents` quebra app mobile já publicado

## Notas

Propôs aditivo com ambos os campos, instrumentação de uso por versão e janela de remoção.

## Auditoria externa

**Selecionado para revisão independente** — ver [`../AUDIT-SAMPLE.md`](../_audit-notes/AUDIT-SAMPLE.md). O veredito acima é do autor (autoavaliação) e **não** homologa a skill; divergência do auditor externo prevalece.
