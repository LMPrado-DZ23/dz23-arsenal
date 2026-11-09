# State Machine — <recurso>

## Estados
| Estado | Descrição | Terminal? |
|---|---|---|
| RASCUNHO | criado, não enviado | não |
| PENDENTE | aguardando aprovação | não |
| ATIVO | em operação | não |
| SUSPENSO | bloqueado temporariamente | não |
| ARQUIVADO | encerrado | sim |

## Transições
| De | Para | Trigger | Guard (pré-condição) | Side effect |
|---|---|---|---|---|
| RASCUNHO | PENDENTE | `submeter()` | campos obrigatórios válidos | e-mail de recebimento |
| PENDENTE | ATIVO | `aprovar()` | papel = admin | libera acesso, log de auditoria |
| PENDENTE | RASCUNHO | `devolver()` | papel = admin | notifica autor |
| ATIVO | SUSPENSO | `suspender()` | motivo preenchido | bloqueia login, notifica dono |
| SUSPENSO | ATIVO | `reativar()` | papel = admin | libera login |
| * | ARQUIVADO | `arquivar()` | não ATIVO há > 90 dias | soft delete, retenção |

## Transições proibidas
- `ATIVO → RASCUNHO` (perde histórico de aprovação)
- `ARQUIVADO → *` (terminal)
- `PENDENTE → SUSPENSO` (nunca esteve ativo)

## Invariantes ligadas
- `INV-00X`: <regra que a FSM garante>

## Implementação
- Banco: enum `status` + `CHECK` de transição válida quando possível.
- Domínio: validação com `409`/`422` no contrato.
- Histórico: tabela `<recurso>_status_history` (de, para, ator, quando, motivo).
- UI: ações oferecidas derivadas do estado atual; nenhuma transição inventada.
