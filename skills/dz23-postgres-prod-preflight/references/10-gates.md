# Os 10 gates — falha, detecção e correção

Cada gate tem: **o que a IA faz de errado**, **como detectar por consulta**, **como corrigir**, **critério de PASS**.
Consulta sem saída colada = `NOT_TESTED`.

---

## P1 — `FORCE ROW LEVEL SECURITY` (BLOCKER)

### A falha
`ALTER TABLE ... ENABLE ROW LEVEL SECURITY` **não** aplica a política ao **dono da tabela**. Aplicação que
conecta com a role dona (comum quando a IA usa a mesma credencial da migration) lê tudo, ignorando a policy.
Função `SECURITY DEFINER` também executa como o dono → mesmo furo, por outro caminho.

### Detecção
```sql
-- tabelas SEM force, mesmo com RLS habilitado
SELECT n.nspname AS schema, c.relname AS tabela, c.relrowsecurity AS rls, c.relforcerowsecurity AS force
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND (NOT c.relrowsecurity OR NOT c.relforcerowsecurity)
ORDER BY 1, 2;
```

E na conexão da aplicação:
```sql
SELECT current_user, session_user, current_setting('is_superuser') AS superuser;
-- se current_user = dono da tabela e force = false, o RLS é decorativo
```

### Correção
```sql
ALTER TABLE app.wallet ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.wallet FORCE ROW LEVEL SECURITY;
-- e a aplicação NÃO deve conectar como dono:
-- criar role de runtime sem BYPASSRLS e conceder apenas DML necessário
```

### PASS
Toda tabela de negócio com `relrowsecurity = true` **e** `relforcerowsecurity = true`, e a role de runtime
diferente do dono, sem `BYPASSRLS`.

---

## P2 — `statement_timeout` por conexão (BLOCKER)

### A falha
Sem teto, uma única query cara (agregação de odds ao vivo, relatório de afiliados, `ORDER BY` sem índice) ocupa
conexão até terminar. Com pool pequeno, poucas queries simultâneas esgotam o pool → site fora do ar no pico.

### Detecção
```sql
SHOW statement_timeout;                       -- '0' = sem limite
SHOW idle_in_transaction_session_timeout;     -- '0' = transação aberta para sempre
SHOW lock_timeout;
-- por role (o que realmente vale para a aplicação)
SELECT rolname, rolconfig FROM pg_roles WHERE rolname NOT LIKE 'pg\_%';
```

### Correção
```sql
ALTER ROLE app_runtime SET statement_timeout = '5s';
ALTER ROLE app_runtime SET idle_in_transaction_session_timeout = '10s';
ALTER ROLE app_runtime SET lock_timeout = '2s';
-- consultas longas (relatório/job) usam role própria, com teto maior e janela
ALTER ROLE app_batch SET statement_timeout = '120s';
```

### PASS
`statement_timeout` diferente de `0` na role que atende request; `idle_in_transaction_session_timeout` diferente
de `0`; role de job separada com teto maior. Valor medido, não "definido".

---

## P3 — `search_path` fixado nas funções (BLOCKER)

### A falha
Função sem `SET search_path` resolve nomes na hora da execução, na ordem do `search_path` do chamador. Se o
atacante consegue criar um schema/objeto antes, a função executa **o código dele** — com os privilégios do dono,
se `SECURITY DEFINER`. Cálculo de prêmio, fechamento de aposta e movimentação de saldo costumam ser funções.

### Detecção
```sql
SELECT n.nspname AS schema, p.proname AS funcao, p.prosecdef AS security_definer,
       array_to_string(p.proconfig, ', ') AS config
FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND (p.proconfig IS NULL OR NOT EXISTS (
        SELECT 1 FROM unnest(p.proconfig) c WHERE c LIKE 'search_path=%'))
ORDER BY p.prosecdef DESC, 1, 2;
```

### Correção
```sql
ALTER FUNCTION app.fechar_aposta(uuid) SET search_path = pg_catalog, app;
-- schema do chamador nunca no caminho; qualificar objetos no corpo também ajuda
```

### PASS
Toda função de negócio com `search_path` explícito (começando por `pg_catalog`), e `SECURITY DEFINER` só onde
necessário, com `REVOKE EXECUTE ... FROM PUBLIC`.

---

## P4 — Integridade na camada de persistência (BLOCKER)

### A falha
Validação só no frontend/API. Saldo negativo, valor nulo em coluna obrigatória, transação duplicada por retry —
tudo passa porque o banco não tem `CHECK`/`NOT NULL`/`UNIQUE`. Duas requisições simultâneas furam validação de
aplicação que não tem constraint para segurar.

### Detecção
```sql
-- colunas de dinheiro sem CHECK de não-negativo
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'app'
  AND (column_name ILIKE '%balance%' OR column_name ILIKE '%amount%' OR column_name ILIKE '%valor%')
  AND is_nullable = 'YES';

-- tabelas sem nenhuma constraint UNIQUE/PK que não seja a surrogate
SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'app' AND c.relkind = 'r'
  AND NOT EXISTS (SELECT 1 FROM pg_constraint k WHERE k.conrelid = c.oid AND k.contype IN ('u','p'));

-- dinheiro em ponto flutuante
SELECT table_name, column_name FROM information_schema.columns
WHERE table_schema = 'app' AND data_type IN ('real','double precision');
```

### Correção
```sql
ALTER TABLE app.wallet ALTER COLUMN balance_cents SET NOT NULL;
ALTER TABLE app.wallet ADD CONSTRAINT wallet_balance_nao_negativo CHECK (balance_cents >= 0);
ALTER TABLE app.transaction ADD CONSTRAINT transaction_idem_uk UNIQUE (tenant_id, idempotency_key);
-- dinheiro: BIGINT em centavos ou NUMERIC(18,2) com moeda explícita
```

### PASS
Dinheiro em inteiro/`numeric`; `CHECK (>= 0)` onde o domínio proíbe negativo; `NOT NULL` nas colunas que a
regra exige; `UNIQUE` em chave natural e em chave de idempotência.

---

## P5 — PII exposta por tabela, não por view (BLOCKER · LGPD)

### A falha
`GRANT SELECT` na tabela de titulares (CPF, e-mail, telefone, documento) para a role da aplicação ou, pior, para
`anon`. Qualquer consulta "geral" passa a devolver PII em claro — e um endpoint mal escrito vira vazamento.

### Detecção
```sql
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'app' AND privilege_type = 'SELECT'
  AND (table_name ILIKE '%user%' OR table_name ILIKE '%titular%' OR table_name ILIKE '%kyc%')
ORDER BY 1, 3;

-- views que devolvem a coluna sensível em claro
SELECT c.table_name, c.column_name FROM information_schema.columns c
WHERE c.table_schema = 'app'
  AND c.column_name ~* '(cpf|cnpj|email|phone|telefone|documento)'
  AND c.table_name IN (SELECT table_name FROM information_schema.views WHERE table_schema='app');
```

### Correção
```sql
REVOKE SELECT ON app.titular FROM app_runtime, anon;
-- view com ofuscação na própria expressão
CREATE OR REPLACE VIEW app.titular_publico AS
SELECT id,
       regexp_replace(cpf, '^(\d{3})\d{6}(\d{2})$', '\1.***.***-\2') AS cpf_mascarado,
       regexp_replace(email, '(^.).*(@.*$)', '\1***\2') AS email_mascarado
FROM app.titular;
GRANT SELECT ON app.titular_publico TO app_runtime;
```

### PASS
Role de aplicação **sem** `SELECT` na tabela de PII; acesso por view que ofusca; a view testada devolvendo valor
mascarado (colar a saída).

---

## P6 — `CREATE` no schema `public` (MAJOR)

### A falha
No Postgres 14 e anteriores, `PUBLIC` tem `CREATE` em `public` por padrão. Role de menor privilégio (ou acesso
anônimo, dependendo do setup) cria tabela/função no schema padrão — planta objeto que outra função resolve via
`search_path`, ou cria tabela homônima para confundir migração.

### Detecção
```sql
SELECT nspname, nspacl FROM pg_namespace WHERE nspname = 'public';
-- procurar '=UC/' ou '=C/' (CREATE para PUBLIC)
SHOW search_path;
```

### Correção
```sql
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM anon;      -- quando existir role anon
GRANT USAGE ON SCHEMA public TO app_runtime;
-- cada objeto com GRANT explícito; nada implícito
```

### PASS
`REVOKE CREATE ON SCHEMA public FROM PUBLIC` aplicado e conferido em `pg_namespace.nspacl`; objects criados em
schema próprio (`app`), não em `public`.

---

## P7 — Backup com restauração validada + RTO/RPO (BLOCKER)

### A falha
"Temos backup" sem restore testado. Na hora do incidente ninguém sabe se o dump abre, se o dado mais recente
está lá, nem quanto tempo leva — e a decisão de recuperação vira aposta.

### Detecção (registro, não promessa)
```sql
-- WAL/PITR e retenção
SHOW archive_mode; SHOW archive_command; SHOW wal_level;
SELECT * FROM pg_stat_archiver;
-- backup físico lógico recente: consultar a rotina real (cron/k8s/serviço),
-- e o registro de restore com data, responsável e tempo medido
```

### Correção / exigência
Registro de restore contendo: **data**, **quem executou**, **origem do backup**, **destino isolado**,
**verificação de conteúdo** (contagem de linhas de 2–3 tabelas críticas + checksum de uma delas),
**tempo medido** (define o RTO real) e **RPO atingido** (data do dado mais recente presente).

Alvos numéricos explícitos, nunca "medir RTO":
`RTO < 30 min` · `RPO < 5 min` (ou `RPO = última janela de backup`). Sem alvo, não existe critério de aprovação.

### PASS
Restore executado em ambiente separado com evidência anexada, tempo medido, RTO/RPO declarados em número.

---

## P8 — Trilha de auditoria de leitura (MAJOR · LGPD)

### A falha
A IA implementa log de **erro** e esquece log de **acesso**. Sem trilha de leitura não se responde "quem viu o
saldo/CPF do titular X" — e sem isso não há como medir o escopo de um vazamento.

### Detecção
```sql
SHOW log_statement;              -- 'none' = nada de DML logado
SHOW pgaudit.log;                -- extensão ausente ou 'none'
SELECT * FROM pg_extension WHERE extname = 'pgaudit';

-- existe tabela de auditoria da aplicação?
SELECT n.nspname, c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND (c.relname ILIKE '%audit%' OR c.relname ILIKE '%access_log%');
```

### Correção
Mínimo aceitável: tabela de auditoria `append-only` com `tenant_id`, `actor`, `action`, `resource`, `ts`,
`request_id`; escrita na mesma transação do efeito; `INSERT` sem `UPDATE`/`DELETE` para a role da aplicação.
Complemento no banco: `pgaudit` para `read` nas tabelas sensíveis (custo de storage).

### PASS
Log de leitura existindo para as tabelas sensíveis, com teste: consultar como usuário A e provar que a linha de
auditoria foi gravada (colar a consulta e a saída).

---

## P9 — RLS verificado tabela por tabela (BLOCKER)

### A falha
Tabela nova nasce **sem RLS**. O schema cresce (bônus, afiliados, transações, histórico) e uma tabela esquecida
expõe tudo daquela tabela para qualquer sessão.

### Detecção
```sql
-- tabelas SEM policy nenhuma
SELECT n.nspname, c.relname
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname = 'app'
  AND NOT EXISTS (SELECT 1 FROM pg_policies p
                  WHERE p.schemaname = n.nspname AND p.tablename = c.relname)
ORDER BY 2;

-- policy permissiva demais
SELECT schemaname, tablename, policyname, cmd, qual, with_check
FROM pg_policies WHERE schemaname = 'app' AND (qual IS NULL OR qual = 'true');
```

E o teste que importa — **tentar contornar**: conectado como role de runtime, com o `tenant_id` de outro cliente
no `SET request.jwt.claims`/`app.tenant_id`, a consulta tem que voltar **zero linhas**.

### Correção
```sql
ALTER TABLE app.bonus ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.bonus FORCE ROW LEVEL SECURITY;
CREATE POLICY bonus_tenant ON app.bonus
  USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
```

### PASS
Toda tabela de negócio com RLS habilitado + forçado + policy por tenant, e o teste de leitura cruzada devolvendo
zero linhas (colar as duas saídas).

---

## P10 — Segregação de credencial (BLOCKER)

### A falha
`service_role`/master key **ignora RLS** e tem poder total de escrita. No Supabase, `anon` é pública por desenho.
Chave de serviço no bundle do cliente, no repositório, em print de tela ou no contexto entregue a uma IA =
qualquer um altera saldo.

### Detecção
```bash
# no código e no bundle (não no histórico do git — este é o segundo passo)
rg -n --hidden -g '!node_modules' -g '!.git' \
   'service_role|SUPABASE_SERVICE|SERVICE_ROLE_KEY|eyJhbGciOi' .
# procurar chave em variável exposta ao cliente
rg -n 'NEXT_PUBLIC_.*SERVICE|VITE_.*SERVICE|REACT_APP_.*SERVICE' .
```
```sql
-- quem tem BYPASSRLS ou é superuser
SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolsuper OR rolbypassrls;
```

### Correção
Rotação imediata da chave exposta. Role dedicada por serviço, com `BYPASSRLS` desligado quando possível;
`service_role` só em runtime de servidor, em secret manager, nunca em `NEXT_PUBLIC_*`/`VITE_*`. A IA recebe
DSN de **leitura** ou snapshot, não a master key.

### PASS
Nenhuma ocorrência de chave de serviço no cliente/repo (saída do `rg` vazia), rotação registrada quando houve
exposição, e `pg_roles` mostrando que a role de runtime não tem `BYPASSRLS`.

---

## Ordem de correção sugerida

1. **P10** (credencial) — se a chave vazou, nada mais importa até rotacionar.
2. **P1 + P9** (RLS forçado + policy por tabela) — o isolamento é o que vaza dado de cliente.
3. **P4** (constraints) — impede estado impossível enquanto o resto é corrigido.
4. **P2** (timeout) — barato e evita queda no pico.
5. **P5** (view de PII) — exige revogar grant e ajustar endpoint.
6. **P3** (search_path) — `ALTER FUNCTION`, sem downtime.
7. **P6** (public) — rápido, mas confira o que já existe em `public`.
8. **P7 + P8** (restore e auditoria) — projeto, não comando.
