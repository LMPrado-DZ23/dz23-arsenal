# Plano de teste E2E

## Fluxo
- Nome (comportamento do usuário):
- Risco de negócio (por que este fluxo importa):
- Severidade se quebrar: crítica | alta | média
- Dono:

## Escopo
- Incluído:
- Fora de escopo (e por quê):
- Camada escolhida: E2E | integração | unidade — justificativa:

## Pré-condição
- Ambiente: local | CI | staging | preview
- Papel/tenant do usuário:
- Dados necessários e como são criados (API/seed):
- Sessão: storageState | login programático | formulário (só se o fluxo for login)

## Passos (ações do usuário)
1.
2.
3.

## Critério de aceite (observável)
- UI:
- Efeito no servidor:
- Estado após reload:
- Autorização negativa (usuário sem papel / outro tenant):

## Seletores usados
| Elemento | Seletor | Tipo (role/label/testid) |
|---|---|---|

## Sincronização
| Espera | Condição observada |
|---|---|

## Evidência exigida
- [ ] Trace
- [ ] Screenshot na falha
- [ ] Console/network capturados
- [ ] Relatório com resultado por asserção

## Estabilidade
- Execuções de verificação: __ (mínimo 10)
- Flake observado: sim | não
- Ação se flake: correção da causa | quarentena + issue nº

## CI
- Shard/worker:
- Retry policy:
- Gate: bloqueia merge? sim | não
