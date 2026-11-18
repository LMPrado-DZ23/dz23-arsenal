# Eval: no-statement-timeout

- **Skill:** dz23-postgres-prod-preflight v1.1.2
- **Data:** 2026-11-18
- **Método:** docker exec psql no Postgres 17.11 vivo: pg_settings, consulta cara com e sem teto (cronometrada), duas roles criadas com overrides distintos, leitura de pg_db_role_setting
- **Veredito:** **PASS**

## Cenário

`SHOW statement_timeout` retornou `0`. Está tudo certo?

## Resposta

Resposta obtida por execucao em Postgres 17.11 vivo (container supabase_db_dsh-audit-v3 nesta maquina), nao por memoria do catalogo.

1) Estado medido no nivel do banco (`pg_settings`): statement_timeout = 0, idle_in_transaction_session_timeout = 0, lock_timeout = 0, todos com source = 'default'. Zero significa sem limite, nao 'padrao seguro'. Um `SHOW statement_timeout` devolvendo `0` nao esta tudo certo -- e exatamente o risco que o expected aponta.

2) Consequencia medida, nao alegada: a mesma consulta cara (`generate_series(1,200000000)`) ocupou a conexao por 18,5 s sem teto. Com `SET statement_timeout='1500'` foi cancelada aos 1,6 s com `ERROR: canceling statement due to statement timeout`. A diferenca de 18,5 s para 1,6 s em uma unica consulta e o que esgota o pool no pico: dez concorrencias lentas viram recusa de servico, e aumentar o pool so adia, porque as conexoes seguem presas pelo mesmo tempo.

3) Teto explicito POR ROLE funciona e foi verificado criando duas roles:
   - `app_web`: statement_timeout=3s, idle_in_transaction_session_timeout=10s, lock_timeout=2s. Na sessao dessa role os tres SHOW confirmam 3s/10s/2s, e a mesma consulta pesada foi cortada aos 3,2 s.
   - `batch_job`: statement_timeout=30min -- job longo existe e precisa existir separado, senao ou o app fica lento demais ou o batch morre no meio.
   Consulta de `pg_db_role_setting` mostra as duas linhas como evidencia da configuracao persistida (roloptions nao existe no catalogo desta versao; o lugar correto e pg_db_role_setting).

4) Achado que o cenario nao previu e muda a recomendacao: neste ambiente Supabase as roles de API JA vem com teto configurado pela plataforma -- anon 3s, authenticated 8s, authenticator 8s, service_role 15s, lock_timeout 5s em todas. O buraco real nao e 'falta statement_timeout no servidor', e sim que a role `postgres` (a que a migration e o consolo usam) nao recebe nenhum override de timeout: seu setconfig traz apenas search_path. Ou seja, o caminho critico desprotegido e justamente o administrativo, onde se roda DDL e query manual -- e verificar `pg_settings` global (que mostrava 0) teria sugerido o contrario para as roles de app. Conclusao operacional: declarar teto por role exige conferir role por role em pg_db_role_setting, nao o default do cluster; e ao `postgres` falta teto tanto de statement quanto de idle-in-transaction, que e o que segura lock indefinidamente depois de uma aplicacao quebrada no meio de uma transacao.

Veredito aplicado: o cenario pede teto explicito por role com os tres parametros e role separada para job longo -- os quatro itens foram executados e medidos acima, e a resposta recusa 'esta tudo certo' para `0`.

## Esperado

`0` significa sem limite: uma query cara ocupa conexão até terminar e esgota o pool no pico. Prescreve teto explícito por role (`statement_timeout`, `idle_in_transaction_session_timeout`, `lock_timeout`) e role separada para job longo.

## Falhas (fails_if)

Diz que está certo, ou que 'o Postgres já tem timeout padrão', ou sugere só aumentar o pool.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum na skill. Duas lacunas do proprio cenario: (a) nao distingue default do cluster de override por role, e neste ambiente as roles de API ja tem teto enquanto a role administrativa nao tem nenhuma; (b) o expected menciona os tres parametros mas nao diz onde conferir (pg_db_role_setting -- roloptions nao existe nesta versao)
- Trecho literal: pg_settings: statement_timeout=0 source=default | mesma query 18,5s sem teto vs cancelada em 1,6s com 1500ms | app_web cortada aos 3,2s com SHOW 3s/10s/2s | anon=3s authenticated=8s service_role=15s, postgres sem override de timeout

## Notas

Executado por sessao de agente real com banco vivo. Roles de teste criadas no container local e removidas em seguida.
