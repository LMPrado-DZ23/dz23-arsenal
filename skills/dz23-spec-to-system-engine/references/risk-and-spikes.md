# Risco, spike e decisão

## Classificação de risco
| Risco | Sinal | Ação |
|---|---|---|
| Técnico desconhecido | "não sabemos se a API X suporta" | spike com prazo |
| Integração instável | terceiro sem SLA/teste | contrato + fallback |
| Dado inexistente/sujo | "precisa de histórico que não existe" | enquadrar escopo/backfill |
| Escopo ambíguo | duas interpretações plausíveis | decisão de produto registrada |
| Dependência externa | aprovação, contrato, credencial | `BLOCKED_BY_EXTERNAL_DEPENDENCY` |
| Prazo versus escopo | data fixa, escopo aberto | corte explícito, não silencioso |

## Spike — o que é e o que não é
Spike é investigação **com pergunta e prazo**, para reduzir incerteza antes de comprometer entrega.
```
SPIKE-03 · A API legada suporta consulta por período?
Pergunta: existe endpoint com filtro `from/to`? qual limite e latência?
Prazo: 4 horas · Dono: X
Saída esperada: resposta + evidência (curl/resposta) + impacto no plano
Regra: o código do spike é descartável; o conhecimento não
```
Não é spike: "explorar a tecnologia", "estudar a solução". Isso é escopo disfarçado.

## Decisão reversível × irreversível
- **Reversível** (nome de função, layout, biblioteca trivial): decida rápido, registre em uma linha.
- **Irreversível ou caro** (schema público, contrato de API, modelo de dados, provedor, autenticação):
  **ADR antes**, ver `templates/` do `dz23-backend-data-architect` (`adr.md`) se disponível.

## Estrutura do ADR curto
Contexto → opções (com prós/contras) → decisão → consequência → gatilho para revisitar. Uma página.

## Registro de risco vivo
`R-01 · Integração com gateway de pagamento pode não suportar estorno parcial · impacto alto · prob. média ·
mitigação: spike 4h + contrato de fallback · dono · prazo`

Revise a cada fatia entregue. Risco que fica no documento sem dono é decoração.

## Pre-mortem obrigatório (casos de borda)
Antes de implementar, imagine que o sistema já falhou em produção e responda. Preencha a matriz:

| Cenário | Pergunta | Comportamento esperado na spec |
|---|---|---|
| **Concorrência** | dois usuários clicam no mesmo ms no último slot | lock/transação; um recebe `409` |
| **Idempotência** | usuário clica 3× em pagar; gateway reenvia webhook | `Idempotency-Key`; dedupe por `event_id` |
| **Timezone** | "meia-noite" é UTC ou `America/Sao_Paulo`? | regra declarada; `timestamptz` + conversão na borda |
| **Tenant isolation** | tenant A abre URL com id de B | `404`; listagem filtrada; teste de vazamento |
| **Limites** | 0 / 1 / 50.000 itens na listagem | empty state, paginação com teto, performance declarada |
| **Rede** | gateway com timeout de 30 s; retry | timeout menor que o do cliente; backoff com jitter |
| **Cancelamento/reversão** | como cancelar, reagendar, estornar? | operação inversa especificada, com guard e efeito |

Tabela final: `cenário | entrada | comportamento esperado | teste que prova`.

**Regra:** todo fluxo que cria/altera dinheiro, agenda ou acesso precisa de pelo menos um cenário de
concorrência e um de reversão. Sem isso, a spec está incompleta — não "otimista".

## Saída
Lista de riscos com impacto/probabilidade/mitigação/dono, spikes com pergunta e prazo, e ADRs das decisões
irreversíveis.
