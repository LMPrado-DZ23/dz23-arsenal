# Verificação — o que já foi executado contra banco real

Registro da verificação de 2026-11-10. Serve para o próximo leitor saber **o que já foi provado** e o que
continua teórico — e para não repetir o trabalho de descobrir os cinco defeitos do próprio script.

## Ambiente

```
postgres:16-alpine · Docker 29.9.2
container efêmero (removido após o teste)
sem psql local → execução via scripts/pg_preflight.py --docker <container>
```

## Como reproduzir

```bash
docker run -d --name pgchk -e POSTGRES_PASSWORD=teste123 -e POSTGRES_DB=betok -p 55432:5432 postgres:16-alpine
# aplicar o cenário limpo (ver scripts de seed no histórico do repo) e então:
python scripts/pg_preflight.py --docker pgchk --dbname betok --user postgres
```

## Resultado — controle positivo (banco bem feito)

| Gate | Estado |
|---|---|
| P1 FORCE RLS · P2 timeout · P3 search_path · P4 constraints · P5 view de PII · P6 public | **PASS** |
| P7 restore + RTO/RPO | `MANUAL` (depende de registro de processo) |
| P8 auditoria · P9 RLS por tabela · P10 credencial | **PASS** |

**exit 0.** Sem isso, "o script funciona" seria só afirmação.

## Resultado — controle negativo (banco com defeitos)

| Gate | Estado | Infratores |
|---|---|---|
| P1 FORCE RLS | FAIL | 3 tabelas sem RLS/force |
| P2 timeout | FAIL | 1 role de login sem teto |
| P3 search_path | FAIL | 1 função `SECURITY DEFINER` sem `search_path` |
| P4 constraints | FAIL | 2 (float em dinheiro) |
| P5 PII | FAIL | 1 grant direto em tabela de titulares |
| P6 public | FAIL | 1 (`CREATE` para PUBLIC) |
| P8 auditoria | FAIL | 1 (sem pgaudit, sem tabela) |
| P9 RLS | FAIL | 3 tabelas sem policy |
| P10 credencial | FAIL | 1 role com `BYPASSRLS` |

**exit 1 · BLOCKER em P1, P2, P3, P4, P5, P9, P10.** O script discrimina: passa no banco limpo, falha no sujo.

## Os cinco defeitos que só a execução revelou

| # | Defeito (v1.0.0) | Como apareceu |
|---|---|---|
| 1 | `SET TRANSACTION READ ONLY` fora de bloco — read-only **não** aplicado | `WARNING: SET TRANSACTION can only be used in transaction blocks` |
| 2 | `0 linhas = PASS` para todos os gates | P2/P6/P8/P10 devolvem linha em banco sadio → FAIL falso |
| 3 | P5 acusava a view de máscara | `titular_publico` casava o regex de nome |
| 4 | P2/P10 contavam `postgres` | superuser aparecia como role de aplicação |
| 5 | P6 reprovava PG 15+ | `nspacl` nulo não é permissivo desde o PG 15 |

Lição que vale para qualquer instrumento: **a ferramenta que acusa precisa ser testada no caso que deve
passar.** Sem o controle positivo, o "9 FAIL" do banco sujo pareceria sucesso.

## O que continua NOT_TESTED

- **13 evals** — nasceram com a skill e nunca foram executados.
- **Supabase real** — `auth.uid()`, `app_metadata` vs `user_metadata`, Realtime/Storage, painel como superuser.
- **PG < 15** — onde `public` nasce permissivo e a regra do P6 muda.
- **P7** — ensaio de restore medido (depende de ambiente com backup real).
- **Pool de conexões** — o efeito do `statement_timeout` no pool não foi medido sob carga.
