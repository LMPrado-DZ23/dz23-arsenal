# Supabase — o que muda na prática

## 1. As duas chaves

| Chave | Onde pode estar | O que faz | Risco |
|---|---|---|---|
| `anon` (pública) | cliente/browser | respeita RLS | nenhum por si — só se a policy estiver frouxa |
| `service_role` (secret) | **só** servidor/secret manager | **ignora RLS**, poder total | controle do banco se vazar |

Regra dura: `service_role` **nunca** em `NEXT_PUBLIC_*`, `VITE_*`, `REACT_APP_*`, bundle, issue, print ou contexto
de IA. Se apareceu, o passo é **rotacionar**, não "mover de lugar".

```bash
rg -n --hidden -g '!node_modules' -g '!.git' 'service_role|SERVICE_ROLE_KEY|SUPABASE_SERVICE' .
rg -n 'NEXT_PUBLIC_.*SUPABASE|VITE_.*SUPABASE' .   # chave anon no cliente é esperado; service não é
```

## 2. RLS no Supabase: `auth.uid()` e o JWT

A policy típica usa o claim do JWT:

```sql
CREATE POLICY wallet_tenant ON public.wallet
  FOR ALL
  USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid)
  WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);
```

Três armadilhas que a IA comete:

1. **Confiar em `user_metadata`** — o usuário pode editar `user_metadata` em alguns fluxos. Use
   `app_metadata`/claim customizado no token, nunca metadata editável, para autorização.
2. **Policy só em `SELECT`** — `INSERT/UPDATE/DELETE` sem `WITH CHECK` permite escrever linha de outro tenant.
3. **Esquecer `FORCE`** — o painel do Supabase não liga `FORCE` por você. E se a aplicação usar a conexão do
   dono (pooler com `postgres`), o RLS não vale.

## 3. `public` e o Supabase

Objetos criados pelo editor SQL nascem em `public`. Duas consequências:

- `REVOKE CREATE ON SCHEMA public FROM PUBLIC` pode quebrar ferramenta que cria objeto ali — confira antes.
- Schema próprio (`app`) reduz a superfície e deixa os grants explícitos. Se for usar `app`, dê
  `GRANT USAGE ON SCHEMA app TO anon, authenticated` e os grants por objeto.

## 4. Realtime e PII

Realtime respeita RLS na assinatura — mas payload de `postgres_changes` carrega a **linha inteira** (salvo
quando você usa `realtime.messages` ou réplica limitada). Antes de ligar Realtime em tabela com PII: confirme
que a policy filtra por tenant **e** que a coluna sensível não vai no payload.

## 5. Storage e service key

Bucket público não é "só leitura" — é leitura por qualquer um com a URL. CPF/documento enviado em bucket público
é vazamento sem SQL nenhum. Policies de `storage.objects` são RLS como qualquer outra: verifique
`auth.uid()`/tenant no path.

## 6. Migrações

- Migração pelo painel/MCP roda como `postgres` (superuser) → **não testa RLS** de verdade.
- Por isso o teste de contorno precisa rodar com a role da aplicação (`authenticated`), não com o editor SQL.
- `ALTER TABLE ... ADD COLUMN ... NOT NULL` sem default em tabela grande trava; use default barato, depois
  backfill, depois `SET NOT NULL`.

## 7. Checklist Supabase

- [ ] `service_role` ausente do cliente e do repo (saída de `rg` vazia)
- [ ] rotação feita se houve exposição, com data registrada
- [ ] policies com `WITH CHECK` nas escritas, usando claim do token (não `user_metadata`)
- [ ] `FORCE ROW LEVEL SECURITY` conferido (o painel não faz)
- [ ] teste de contorno rodando como `authenticated`, com saída colada
- [ ] Realtime/Storage revisados para PII
- [ ] `REVOKE CREATE ON SCHEMA public FROM PUBLIC` com plano de impacto nas ferramentas
