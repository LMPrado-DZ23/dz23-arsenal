# Máquinas de estado

## Quando exigir FSM
Toda entidade que **muda ao longo do tempo**: pedido, agendamento, assinatura, cobrança, job de agente,
convite, contrato. Se tem status, tem ciclo de vida — e ciclo de vida não escrito vira `status = "ativo"`
espalhado pelo código.

## Template
```
Estados: RASCUNHO → PENDENTE → ATIVO → SUSPENSO → ARQUIVADO

| De       | Para      | Trigger            | Guard (pré-condição)        | Side effect                  |
|----------|-----------|--------------------|-----------------------------|------------------------------|
| RASCUNHO | PENDENTE  | submeter()         | campos obrigatórios OK      | envia e-mail de recebido     |
| PENDENTE | ATIVO     | aprovar()          | papel = admin               | libera acesso, log de auditoria |
| ATIVO    | SUSPENSO  | suspender()        | motivo preenchido           | bloqueia login, notifica dono |
| SUSPENSO | ATIVO     | reativar()         | papel = admin               | libera login                 |
| *        | ARQUIVADO | arquivar()         | não ATIVO há > 90 dias      | soft delete                  |
```

## Regras
- **Estado inicial e finais explícitos.** Estado sem saída é "estado zumbi" — ou é final, ou tem transição.
- **Toda transição tem trigger nomeado** (evento/comando), não "editar status".
- **Guard é pré-condição verificável**: papel, invariante, limite.
- **Side effect é explícito**: e-mail, notificação, webhook, lançamento, log. Efeito invisível é bug.
- **Transições proibidas documentadas**: `ATIVO → RASCUNHO` nunca; `PAGO → PENDENTE` nunca.
- **Quem pode acionar** cada transição (ator/role) faz parte da tabela.

## Exemplo: pedido
```
PENDING_PAYMENT --(webhook payment.confirmed)--> CONFIRMED
PENDING_PAYMENT --(timeout 30m | user.cancel)--> EXPIRED | CANCELLED
CONFIRMED       --(staff.complete)-------------> COMPLETED
CONFIRMED       --(customer.no_show)-----------> NO_SHOW
CONFIRMED       --(refund.requested)-----------> REFUNDED (guard: prazo <= 7d)
```

## Da FSM para o banco
A FSM vira, na implementação (ver `dz23-backend-data-architect`):
- `enum` do banco (ou tabela de domínio) com todos os estados;
- `CHECK`/trigger que rejeita transição inválida quando possível;
- validação no domínio com mensagem clara (`409`/`422` no contrato);
- histórico de transição (`order_status_history`: de, para, ator, quando, motivo) para auditoria.

## Da FSM para a UI
- Cada estado pode ter tela/ação diferente (botão "Cancelar" só em `CONFIRMED`).
- Estado sem ação disponível é estado morto — reveja a FSM.
- A UI não inventa transição: só oferece as permitidas.

## Saída
Tabela de estados, tabela de transições com guard e side effect, transições proibidas, e a nota de como
cada FSM vira enum/constraint/teste.
