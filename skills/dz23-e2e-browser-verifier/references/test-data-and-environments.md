# Dados de teste e ambientes

## Isolamento é a regra
Cada teste **cria** o que precisa e **limpa** o que criou. Nenhum teste depende de ordem, de "usuário padrão" compartilhado ou de banco com estado deixado por outro.

## Identificador único por execução
```ts
const runId = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
const email = `e2e+${runId}@exemplo.test`;
```
Isso elimina colisão em paralelo e permite limpar por prefixo no teardown.

## Como preparar estado
| Estado | Como |
|---|---|
| Usuário | API de seed/registro, nunca clicar no formulário se o teste não é sobre ele |
| Sessão | `storageState` gerado no setup |
| Dados de negócio | API de teste ou fixture; se não existir, é dívida do produto |
| Dinheiro/pagamento | sandbox do provedor ou mock no limite; nunca cartão real |
| Multi-tenant | um tenant por run, ou dois fixos e limpos por API |
| Tempo | relógio fixo quando o produto permitir; caso contrário, tolerância declarada |

## Seed e teardown
- Seed idempotente e por run; teardown remove por `runId`, não `truncate` no banco compartilhado.
- Nunca "delete tudo" em ambiente compartilhado — você apaga o dado de alguém em paralelo.
- Dado que falhou precisa **ficar** até o diagnóstico: marque `keepOnFailure`, limpe na execução seguinte.

## Ambientes
| Ambiente | Uso | Regra |
|---|---|---|
| local | desenvolvimento, debugging | dados descartáveis, browser headed permitido |
| CI/staging | gate de PR e smoke | banco próprio, credencial de teste, sem produção |
| preview por PR | validação de feature | efêmero, seed próprio |
| produção | **não** roda teste destrutivo | somente leitura/smoke sintético, com autorização explícita |

Produção: por padrão proibida para E2E. Exceção = smoke **read-only** (abrir home, login de conta de monitoramento, verificar health), nunca criar pedido, nunca pagar, nunca apagar. Autorização do dono registrada.

## Segredos
- Credencial por variável de ambiente/secret manager. Nunca no código, no fixture, no trace ou no screenshot.
- Usuário de teste com papel mínimo necessário.
- `storageState` contém cookie de sessão: não commitar, não colar em log, não anexar em artifact público sem checar.

## Dados sensíveis em evidência
Trace/vídeo capturam a tela: mascarar campo sensível (`fill` com máscara, `page.route` no dado pessoal, `locator.fill('***')` no screenshot) e não usar dado real de cliente no teste.

## Multi-tenant no E2E
Obrigatório quando o produto é multi-tenant:
1. tenant A cria recurso.
2. tenant B tenta acessar por URL direta → `404/403`.
3. listagem de B não contém o recurso de A.
Sem esse trio, "multi-tenant testado" é ficção.

## Banco de teste
- Banco próprio por pipeline (container efêmero é o padrão) ou schema por run.
- Migração aplicada antes do teste, na mesma versão do código.
- Jamais apontar `E2E_BASE_URL`/`DATABASE_URL` para produção "só para testar rápido".

## Critério de saída dos dados
(a) dado único por run; (b) seed e teardown idempotentes; (c) zero dependência de ordem; (d) ambiente declarado no relatório; (e) nenhum segredo em artifact.
