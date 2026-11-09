# Segurança de aplicação e multi-tenancy

## Autorização (o defeito nº 1)
- **Deny by default**: rota nova nasce fechada; permissão é concedida explicitamente.
- **Autorização por recurso**, não só por rota: além de "pode acessar `GET /orders/{id}`", verifique "este usuário/tenant é dono deste `order`". Sem isso é IDOR.
- Toda consulta que serve dado de usuário carrega o escopo (`WHERE tenant_id = :tenant AND (owner_id = :user OR :is_admin)`), nunca filtra depois de buscar.
- Admin não é curinga silencioso: ação de admin é auditada e, quando sensível, exige reautenticação (step-up).
- Retorne `404` para recurso de outro tenant (não confirme existência).

## Autenticação e sessão
- Senha com argon2id/bcrypt (custo calibrado), nunca hash rápido sem sal.
- Sessão com cookie `HttpOnly; Secure; SameSite=Lax/Strict`, rotação no login, expiração absoluta e por inatividade, revogação no logout/senha trocada.
- Token de serviço com escopo mínimo, expiração curta e rotação; nunca token de longa duração em cliente público.
- MFA para conta privilegiada; recuperação de senha com token de uso único e curto.
- Rate limit e lockout progressivo em login, recuperação e OTP.

## Injeção
- Consulta **sempre** parametrizada. Concatenação de string com entrada do usuário é proibida, inclusive em `ORDER BY`, nome de coluna e `LIKE` — resolva por allowlist.
- SQL dinâmico com identificador: mapeie para lista fechada (`allowedSort = {'created_at','total'}`), nunca `quoteIdentifier` de entrada crua.
- NoSQL: operadores injetáveis (`$ne`, `$gt`) e `$where` bloqueados; valide tipo do valor antes de usar em filtro.
- Comando/SO: nunca `exec` com string; argumentos em array e allowlist de binário.
- Template/HTML: escape por padrão; conteúdo rico passa por sanitização.

## Segredos
- Fora do código, do repositório, do log e da mensagem de erro. `.env` não versionado; secret manager ou variável injetada pelo runtime.
- Nunca logar header `Authorization`, cookie, corpo com senha/token/cartão; mascarar PII em log.
- Rotação documentada e testada; segredo vazado é revogado, não "monitorado".
- Chave de criptografia separada do dado e com plano de rotação (`kid`).

## Dados sensíveis e LGPD
- Base legal, finalidade e retenção por campo. Minimize: não colete o que não usa.
- PII criptografada em repouso quando o risco justifica; em trânsito sempre TLS.
- Direito ao esquecimento: procedimento real de anonimização/remoção, incluindo backups e derivados (relatórios, cache, fila).
- Log e telemetria sem PII; quando inevitável, hash com sal ou tokenização.
- Acesso a dado sensível é auditado (quem, quando, qual recurso).

## Upload
Tipo real por magic bytes (não extensão/`Content-Type` declarado), limite de tamanho, nome gerado, armazenamento fora do webroot, varredura quando houver, e nunca servir com `Content-Type` vindo do usuário.

## SSRF e saída de rede
URL fornecida pelo usuário: allowlist de host/protocolo, bloqueio de IP privado/link-local/metadata (`169.254.169.254`), resolução validada e sem redirect para interno.

## Multi-tenancy
Níveis: coluna `tenant_id` (padrão), schema por tenant, banco por tenant. A escolha depende de isolamento exigido e custo operacional.
- `tenant_id` derivado da sessão/token, **nunca** do payload do cliente.
- RLS no Postgres como defesa em profundidade; a aplicação define `app.tenant_id` por transação.
- Teste de isolamento obrigatório no CI: para cada recurso, tenant A tentando id de B → `404/403`; e listagem sem filtro não retorna linha de outro tenant.
- Operação de plataforma (suporte, admin global) é rota separada, auditada e com escopo explícito.

## Configuração e dependências
- Cabeçalhos de segurança (`HSTS`, `X-Content-Type-Options`, `CSP` quando houver HTML), CORS restrito por origem, método e header.
- Dependência com versão fixada e auditoria (`npm audit`/`pip-audit`/Dependabot); revisão de licença e manutenção antes de adotar.
- Debug e endpoint de diagnóstico desligados em produção.

## OWASP API Security Top 10 (2023) — checklist de exposição
| # | Categoria | O que verificar neste serviço |
|---|---|---|
| API1 | Broken Object Level Authorization (BOLA/IDOR) | toda consulta por id valida dono/tenant antes de retornar |
| API2 | Broken Authentication | sessão/token revogável, expiração, MFA em conta privilegiada |
| API3 | Broken Object Property Level Authorization | resposta sem campo sensível; escrita sem mass assignment |
| API4 | Unrestricted Resource Consumption | limite de payload, de páginas, de concorrência e rate limit |
| API5 | Broken Function Level Authorization | papel/escopo checado por operação, não só por rota |
| API6 | Unrestricted Access to Sensitive Business Flows | fluxo abusável (cupom, cadastro em massa, scraping) tem limite |
| API7 | Server Side Request Forgery | URL do usuário com allowlist e bloqueio de rede interna |
| API8 | Security Misconfiguration | CORS, headers, debug e endpoint de diagnóstico desligados |
| API9 | Improper Inventory Management | versão antiga/documentação esquecida desligada, não "esquecida" |
| API10 | Unsafe Consumption of APIs | resposta de terceiro validada e tratada como não confiável |
Marque cada linha como **coberto (com teste)**, **coberto (sem teste)** ou **aberto** — e nunca deixe `aberto` em rota exposta.

## Supabase / Postgres gerenciado
Quando o projeto usa Supabase, a autorização vira SQL — e erro de RLS é vazamento silencioso.
- **`auth.uid()`**: é o usuário autenticado; nunca confie em `user_id` vindo do cliente. Política típica: `USING (tenant_id = (select tenant_id from profiles where id = auth.uid()))`.
- **RLS obrigatório** em toda tabela exposta: sem `ENABLE ROW LEVEL SECURITY`, a tabela é pública via API REST do Supabase. Audite cobertura: tabela sem policy é tabela aberta.
- **Roles**: `anon` (não autenticado), `authenticated` (logado) e `service_role` (bypassa RLS). `service_role` **nunca** no cliente, no navegador, em app mobile ou em variável pública — só no servidor.
- **Views**: view padrão roda com permissão do dono e pode furar RLS. Use `security_invoker = true` (PG 15+) ou view com filtro explícito.
- **`search_path`**: função `SECURITY DEFINER` sem `SET search_path = public, pg_temp` é sequestrável por schema criado pelo usuário — sempre fixe o `search_path` nessas funções.
- **Função `SECURITY DEFINER`**: concede poder de dono; trate como código privilegiado (valide entrada, não use SQL dinâmico).
- **Storage e buckets**: policy por pasta/tenant; URL assinada com expiração; nunca bucket público para dado de cliente.
- Teste de isolamento: para cada tabela exposta, usuário A não lê nem escreve linha de B — no cliente real, não só no SQL.

## Critério de saída de segurança
(a) matriz recurso × permissão escrita; (b) teste de IDOR e de isolamento de tenant; (c) varredura de segredo no diff; (d) consulta parametrizada verificada; (e) log sem PII; (f) `security-review` executado quando o alvo é exposto.
