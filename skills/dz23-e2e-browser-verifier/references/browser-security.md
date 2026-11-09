# Segurança no E2E — autorização, tenant, IDOR e sessão

## A regra central
Autorização é decidida no servidor. Esconder botão, remover item de menu ou bloquear rota no cliente **não** protege nada. O teste de segurança em E2E prova o comportamento do servidor sob sessão real de um ator.

## IDOR — o defeito mais comum
Procedimento obrigatório (Tier 1):
1. Ator A cria o recurso (pedido, fatura, documento, perfil).
2. Ator B (ou A de outro tenant) tenta o **acesso direto** pela URL/API do recurso de A.
3. Esperado: `404` (não confirme existência) ou `403` — nunca `200` com dados.
4. Repita para escrita: `PATCH`/`DELETE` no recurso de A por B deve falhar.
5. Dados sintéticos e autorizados — nunca dado real de cliente.

## Multi-tenant
- Login no tenant A; `GET` de recurso do tenant B → `404/403`.
- Listagem de B não contém registro de A (sem vazamento por paginação/filtro).
- `tenant_id` nunca vem do body/query: derive da sessão. Teste envio explícito de `tenant_id` alheio no payload — deve ser ignorado ou rejeitado.
- Trocar de tenant na mesma sessão não deixa cache/storage do anterior.

## Sessão
- Sem sessão: rota protegida redireciona para login e preserva o destino (`?next=`), sem vazar dados.
- Sessão expirada/revogada: próxima ação volta ao login, sem erro 500 e sem dado antigo em tela.
- Logout limpa cookie, `localStorage`/`sessionStorage` e cache do usuário anterior; voltar (back) não reabre dado.
- Refresh de token não duplica efeito colateral (idempotência).

## CSRF / CORS (quando aplicável)
- Requisição `POST` de origem externa sem token CSRF é rejeitada.
- CORS não devolve `Access-Control-Allow-Origin: *` com credencial.
- Cookie de sessão com `HttpOnly`, `Secure`, `SameSite` coerente.

## Escopo e ética
- **Não** automatize brute force, fuzzing agressivo, enumeração de usuário ou exploração invasiva contra ambiente externo sem escopo autorizado por escrito.
- Produção: só checks `read-only` e não destrutivos, com autorização explícita. Nunca criar usuário real, pagar, disparar mensagem, apagar dado ou rodar carga.
- Achado de segurança grave: registre com evidência sanitizada e **pare** de explorar; não tente "provar até o fim".

## Segredos e artefatos
- Credencial por env/secret manager; usuário de teste com papel mínimo.
- `storageState` é credencial: não versionar, não anexar em artifact público.
- Trace/vídeo podem capturar dado pessoal — mascarar antes de compartilhar.

## Matriz mínima de segurança (tier 1)
| Caso | Esperado |
|---|---|
| A acessa recurso de B (GET) | `404/403` |
| A escreve recurso de B (PATCH/DELETE) | `403/404`, sem efeito |
| Usuário sem papel acessa rota admin | `403` ou redirect |
| Sessão expirada em rota protegida | redirect login |
| Logout e back | sem dado do usuário anterior |
| `tenant_id` forjado no payload | ignorado/rejeitado |
| Origem externa sem CSRF | rejeitado |

## Critério de saída
(a) IDOR testado em leitura e escrita; (b) tenant cruzado testado; (c) sessão expirada e logout cobertos; (d) `tenant_id` forjado testado; (e) nenhum segredo em artefato; (f) nenhuma exploração fora do escopo autorizado.
