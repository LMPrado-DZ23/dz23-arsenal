# Revisão de contrato de API

Preencher para cada endpoint novo ou alterado. Um item vazio é um item reprovado.

## Identificação
- Método e caminho:
- Versão do contrato:
- Autenticação exigida:
- Autorização (recurso × permissão):
- Rate limit:

## Entrada
- Campos obrigatórios e tipos:
- Validações (formato, faixa, tamanho):
- Campos ignorados/desconhecidos: aceitar | rejeitar
- Tamanho máximo do payload:
- Idempotência (chave, TTL, comportamento em repetição):

## Saída de sucesso
- Status:
- Corpo (exemplo real):
- Campos estáveis × campos que podem mudar:
- Cabeçalhos relevantes (`Location`, `ETag`, `Cache-Control`):

## Erros
| Situação | Status | `code` | Mensagem ao usuário |
|---|---|---|---|
| Payload inválido | 400 | | |
| Não autenticado | 401 | | |
| Sem permissão | 403 | | |
| Inexistente / outro tenant | 404 | | |
| Conflito de estado | 409 | | |
| Regra de negócio | 422 | | |
| Limite de taxa | 429 | | |

## Listagem e paginação
- Estratégia (offset | keyset):
- Limite máximo:
- Ordenação padrão e tiebreaker:
- Filtros permitidos (allowlist):

## Compatibilidade
- Mudança breaking? sim | não
- Se sim: versão nova, janela de deprecação, instrumentação de uso da antiga.
- Campos removidos/renomeados: nenhum | lista
- Campo antigo pode ser reaproveitado? **não**

## Evidência
- [ ] OpenAPI/AsyncAPI atualizado
- [ ] Teste de contrato passando
- [ ] Teste de autorização por recurso
- [ ] Teste de tenant cruzado
- [ ] Exemplo de erro documentado
- [ ] `request_id` presente na resposta
