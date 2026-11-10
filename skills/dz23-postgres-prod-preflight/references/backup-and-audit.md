# Backup, restore e trilha de auditoria

## 1. Backup sem restore não é backup

A pergunta que importa não é "existe backup?", é: **quanto tempo para voltar a operar e quanto dado se perde?**
Sem ensaio, as duas respostas são desconhecidas — e se descobre no pior dia.

### RTO e RPO: número, não verbo

| Métrica | Definição | Exemplo aceitável | Exemplo reprovado |
|---|---|---|---|
| **RTO** | tempo máximo de indisponibilidade tolerado | `RTO < 30 min` | "medir o RTO" |
| **RPO** | perda máxima de dado tolerada | `RPO < 5 min` | "backup diário" sem dizer o que isso perde |

"Medir" é etapa. A resposta é o valor. Se o dono não declarou, proponha default explícito como *proposta
inicial* e diga que precisa de confirmação.

### Ensaio de restore — registro mínimo

```
data: 2026-11-09 14:20 BRT
quem: <nome>
origem: <snapshot/dump> / <local>
destino: ambiente isolado (nunca produção)
comando: pg_restore -d restore_test ...   (colar)
verificação de conteúdo:
  - app.wallet: 1.284.331 linhas (produção: 1.284.331) ✅
  - app.transaction: 9.102.884 linhas ✅
  - checksum de app.wallet (md5 de soma): igual ✅
  - dado mais recente presente: 2026-11-09 14:15 → RPO atingido = 5 min ✅
tempo medido: 12 min 40 s  → RTO real
```

Sem "verificação de conteúdo" e "tempo medido", o backup é `NOT_TESTED`.

### Detecção no Postgres

```sql
SHOW wal_level;              -- replica|logical para PITR
SHOW archive_mode;           -- on para arquivar WAL
SELECT * FROM pg_stat_archiver;  -- última arquivada e falhas
SELECT pg_size_pretty(pg_database_size(current_database()));
```

Backup lógico (`pg_dump`) só não garante RPO baixo: o RPO depende do WAL/PITR. Declare qual dos dois você tem.

## 2. Trilha de auditoria de leitura

### Por que log de erro não basta
Log de erro diz que algo quebrou. Log de **acesso** diz quem leu o quê — a única coisa que responde "qual foi o
escopo do vazamento" e "quem alterou saldo".

### Tabela mínima

```sql
CREATE TABLE app.audit_access (
  id           bigserial PRIMARY KEY,
  ts           timestamptz NOT NULL DEFAULT now(),
  actor_id     uuid,
  tenant_id    uuid,
  action       text NOT NULL,          -- 'read' | 'write' | 'export'
  resource     text NOT NULL,          -- 'wallet' | 'titular' | 'transaction'
  resource_id  text,
  request_id   text,
  ip           inet,
  outcome      text                    -- 'ok' | 'denied'
);
REVOKE UPDATE, DELETE ON app.audit_access FROM app_runtime;
-- INSERT na MESMA transação do efeito: fora dela, o efeito pode existir sem registro
```

### Custo e escolha
| Opção | Cobertura | Custo | Quando usar |
|---|---|---|---|
| Tabela da aplicação | o que o código instrumenta | baixo | sempre (mínimo) |
| `pgaudit` (`log_relation`, `log_statement='read'`) | tudo no banco | storage + I/O | tabela de PII e de dinheiro |
| Log de statement (`log_statement='all'`) | tudo, em texto | alto, e vaza valor em log | nunca em produção sem filtro |

`pgaudit` em `read` sobre `wallet`/`titular` é o padrão defensável para domínio financeiro.

### Teste que prova (não presuma)

```sql
-- 1. ler como usuário A
SET LOCAL app.tenant_id = '<A>'; SELECT * FROM app.wallet LIMIT 1;
-- 2. conferir a linha de auditoria
SELECT actor_id, tenant_id, action, resource, ts
FROM app.audit_access ORDER BY ts DESC LIMIT 3;
```

Colou a linha com `actor_id` de A e `resource='wallet'`? `PASS`. Não colou? `NOT_TESTED`.

## 3. Retenção e privacidade

- Auditoria guarda **quem/quando/o quê**, não o **valor** lido (não copie CPF para o log).
- Retenção mínima típica: 6 meses (LGPD/contrato) a 5 anos (financeiro) — declare o prazo.
- Log de auditoria é `append-only`: role da aplicação insere, não altera.
- Exportação de dados sensíveis (`action='export'`) merece alerta, não só registro.

## 4. Checklist P7 + P8

- [ ] RTO e RPO em número, com dono
- [ ] restore executado em ambiente isolado com data, tempo e verificação de conteúdo
- [ ] ensaio periódico (mensal/trimestral) — derivado do RTO, não escolhido ao acaso
- [ ] PITR/WAL conferido (`archive_mode`, `pg_stat_archiver`)
- [ ] tabela de auditoria com INSERT na mesma transação do efeito
- [ ] `REVOKE UPDATE, DELETE` na auditoria
- [ ] `pgaudit` (ou equivalente) nas tabelas de PII e dinheiro
- [ ] teste de leitura gerando linha de auditoria, com saída colada
- [ ] retenção declarada e purga automatizada (sem `DELETE` manual)
