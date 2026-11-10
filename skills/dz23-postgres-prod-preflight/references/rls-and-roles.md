# RLS, roles e search_path — o que realmente fecha o isolamento

## 1. As três portas do RLS

`ENABLE ROW LEVEL SECURITY` fecha **uma** porta. Continuam abertas:

| Porta | Por que abre | Fecha com |
|---|---|---|
| **Dono da tabela** | policy não se aplica ao owner por padrão | `FORCE ROW LEVEL SECURITY` + runtime com role que não é owner |
| **`SECURITY DEFINER`** | executa como o dono → cai na porta anterior | `FORCE` + `search_path` fixo + `REVOKE EXECUTE ... FROM PUBLIC` |
| **`BYPASSRLS` / superuser** | ignora policy por atributo de role | role de runtime sem esse atributo; superuser só em operação |

```sql
-- as três, numa consulta
SELECT c.relname AS tabela,
       c.relrowsecurity AS rls,
       c.relforcerowsecurity AS force,
       pg_get_userbyid(c.relowner) AS dono
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname = 'app'
ORDER BY c.relname;

SELECT rolname, rolsuper, rolbypassrls, rolcanlogin FROM pg_roles WHERE rolcanlogin;
```

## 2. A role certa por função

| Role | Para que serve | Atributos |
|---|---|---|
| `app_migrator` | DDL/migração, dono dos objetos | `CREATE`, sem `LOGIN` de runtime |
| `app_runtime` | request da aplicação | `LOGIN`, **sem** `BYPASSRLS`, **não** é owner |
| `app_batch` | job/relatório | `statement_timeout` maior, janela própria |
| `anon` (Supabase) | visitante | nenhum `SELECT` em tabela de PII |

Erro clássico: a IA usa **uma** credencial para tudo. Aí o `FORCE` não protege, porque a aplicação é o dono.

## 3. Policy por tenant que funciona

```sql
-- tenant vem da sessão, NUNCA do corpo da request
SET LOCAL app.tenant_id = '<uuid-do-token>';

CREATE POLICY wallet_tenant ON app.wallet
  USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
```

`current_setting(..., true)` devolve `NULL` quando não definido — e `NULL` em `USING` **nega**. É o
comportamento desejado: sem contexto, sem linha.

### Teste de contorno (o que decide PASS/FAIL)

```sql
-- conectado como app_runtime, com o tenant do cliente A
SET LOCAL app.tenant_id = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
SELECT count(*) FROM app.wallet;                 -- esperado: só linhas de A

SET LOCAL app.tenant_id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';
SELECT count(*) FROM app.wallet WHERE id = '<id-de-A>';   -- esperado: 0

RESET app.tenant_id;
SELECT count(*) FROM app.wallet;                 -- esperado: 0 (contexto ausente nega)
```

Colou as três saídas? Então P1+P9 são `PASS`. Só leu a policy no código? `NOT_TESTED`.

## 4. `search_path`: o sequestro em três linhas

```sql
-- atacante com CREATE em algum schema do path
CREATE SCHEMA evil;
CREATE FUNCTION evil.now() RETURNS timestamptz AS $$ SELECT '2000-01-01'::timestamptz $$ LANGUAGE sql;
-- função da aplicação sem search_path resolve evil.now() se evil vier antes de pg_catalog
```

Correção fixa o caminho **e** qualifica o corpo:

```sql
ALTER FUNCTION app.fechar_aposta(uuid) SET search_path = pg_catalog, app;
-- no corpo: agora(), app.wallet, public.x  (nunca nome nu)
```

`SECURITY DEFINER` sem `search_path` fixo + `EXECUTE` para `PUBLIC` = execução de código do atacante com
privilégio do dono. É o caminho mais curto para escrita arbitrária em banco de produção.

## 5. Views de PII — o padrão que passa em auditoria

```sql
CREATE OR REPLACE VIEW app.titular_publico
WITH (security_barrier = true, security_invoker = false) AS
SELECT id,
       regexp_replace(cpf,   '^(\d{3})\d{6}(\d{2})$',  '\1.***.***-\2') AS cpf_mascarado,
       regexp_replace(email, '(^.).*(@.*)$',            '\1***\2')       AS email_mascarado,
       created_at
FROM app.titular;

REVOKE ALL ON app.titular FROM app_runtime, anon;
GRANT SELECT ON app.titular_publico TO app_runtime;
```

`security_barrier` impede que função do chamador seja empurrada para dentro da view e veja o valor antes da
máscara. Sem isso, `WHERE` malicioso pode inferir o valor por comparação.

## 6. Checklist de fechamento do isolamento

- [ ] `relrowsecurity` **e** `relforcerowsecurity` = true em toda tabela de negócio
- [ ] runtime ≠ owner; `BYPASSRLS` desligado na runtime
- [ ] policy cobre `SELECT/INSERT/UPDATE/DELETE` (ou `FOR ALL`), com `WITH CHECK` nas escritas
- [ ] `tenant_id` vem da sessão, nunca do body
- [ ] teste de leitura cruzada com saída colada (3 consultas acima)
- [ ] funções com `search_path` fixo e `EXECUTE` revogado de `PUBLIC`
- [ ] view de PII com máscara na expressão + `security_barrier`
- [ ] `REVOKE CREATE ON SCHEMA public FROM PUBLIC` conferido em `nspacl`
