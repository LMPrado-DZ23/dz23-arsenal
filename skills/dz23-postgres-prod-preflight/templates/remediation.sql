-- Correções dos 10 gates — aplicar em ordem de risco, com janela e rollback registrado.
-- Nada aqui é para rodar inteiro de uma vez. Cada bloco tem o rollback ao lado.
-- schema de exemplo: app. troque pelo seu.

-- ============================================================ P1 + P9  (BLOCKER)
-- Detecção primeiro:
--   SELECT n.nspname, c.relname, c.relrowsecurity, c.relforcerowsecurity
--   FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
--   WHERE c.relkind='r' AND n.nspname='app';
BEGIN;
ALTER TABLE app.wallet      ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.wallet      FORCE  ROW LEVEL SECURITY;
CREATE POLICY wallet_tenant ON app.wallet
  USING      (tenant_id = current_setting('app.tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
-- rollback: DROP POLICY wallet_tenant ON app.wallet;
COMMIT;

-- runtime separado do dono (não é owner, sem BYPASSRLS):
--   CREATE ROLE app_runtime NOLOGIN;
--   GRANT SELECT, INSERT, UPDATE ON app.wallet TO app_runtime;
--   ALTER ROLE app_runtime NOBYPASSRLS;

-- ============================================================ P2  (BLOCKER)
ALTER ROLE app_runtime SET statement_timeout = '5s';
ALTER ROLE app_runtime SET idle_in_transaction_session_timeout = '10s';
ALTER ROLE app_runtime SET lock_timeout = '2s';
-- rollback: ALTER ROLE app_runtime RESET statement_timeout; (idem para os outros)

-- ============================================================ P3  (BLOCKER)
ALTER FUNCTION app.fechar_aposta(uuid)          SET search_path = pg_catalog, app;
ALTER FUNCTION app.creditar_saldo(uuid, bigint) SET search_path = pg_catalog, app;
REVOKE EXECUTE ON FUNCTION app.fechar_aposta(uuid) FROM PUBLIC;
-- rollback: ALTER FUNCTION app.fechar_aposta(uuid) RESET search_path;

-- ============================================================ P4  (BLOCKER)
-- dinheiro: inteiro em centavos ou numeric com moeda
ALTER TABLE app.wallet ALTER COLUMN balance_cents SET NOT NULL;
ALTER TABLE app.wallet ADD CONSTRAINT wallet_balance_nao_negativo CHECK (balance_cents >= 0);
ALTER TABLE app.tx     ADD CONSTRAINT tx_idem_uk UNIQUE (tenant_id, idempotency_key);
-- rollback: ALTER TABLE app.wallet DROP CONSTRAINT wallet_balance_nao_negativo;
-- Cuidado: ADD CONSTRAINT CHECK valida a tabela inteira (lock). Em tabela grande:
--   ADD CONSTRAINT ... CHECK (...) NOT VALID;  depois  VALIDATE CONSTRAINT ...;  (lock fraco)

-- ============================================================ P5  (BLOCKER)
REVOKE ALL ON app.titular FROM app_runtime, anon;
CREATE OR REPLACE VIEW app.titular_publico
WITH (security_barrier = true) AS
SELECT id,
       regexp_replace(cpf,   '^(\d{3})\d{6}(\d{2})$',  '\1.***.***-\2') AS cpf_mascarado,
       regexp_replace(email, '(^.).*(@.*)$',            '\1***\2')       AS email_mascarado
FROM app.titular;
GRANT SELECT ON app.titular_publico TO app_runtime;
-- rollback: DROP VIEW app.titular_publico; GRANT SELECT ON app.titular TO app_runtime;

-- ============================================================ P6  (MAJOR)
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
-- rollback: GRANT CREATE ON SCHEMA public TO PUBLIC;
-- confira antes o que existe em public: ferramenta que cria objeto ali vai falhar.

-- ============================================================ P7  (BLOCKER · processo)
-- Alvos numéricos declarados (exemplo; confirme com o dono):
--   RTO < 30 min · RPO < 5 min
-- Ensaio (fora de produção):
--   pg_restore -d restore_test --clean --if-exists ultimo.dump
--   SELECT count(*) FROM app.wallet;        -- comparar com produção
--   SELECT max(created_at) FROM app.tx;     -- RPO atingido
-- Registrar: data, quem, tempo medido, verificação de conteúdo.

-- ============================================================ P8  (MAJOR)
CREATE TABLE IF NOT EXISTS app.audit_access (
  id          bigserial PRIMARY KEY,
  ts          timestamptz NOT NULL DEFAULT now(),
  actor_id    uuid,
  tenant_id   uuid,
  action      text NOT NULL,
  resource    text NOT NULL,
  resource_id text,
  request_id  text,
  outcome     text
);
REVOKE UPDATE, DELETE ON app.audit_access FROM app_runtime;
-- pgaudit: CREATE EXTENSION IF NOT EXISTS pgaudit;
--          ALTER ROLE app_runtime SET pgaudit.log = 'read';

-- ============================================================ P10  (BLOCKER)
-- 1) revogar a chave exposta no provedor e emitir nova (rotação imediata)
-- 2) remover do cliente/repo:  rg -n 'service_role|SERVICE_ROLE_KEY' .
-- 3) conferir roles com bypass:
--    SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolsuper OR rolbypassrls;
-- rollback: a rotação não é reversível por desenho; registre a data e o motivo.
