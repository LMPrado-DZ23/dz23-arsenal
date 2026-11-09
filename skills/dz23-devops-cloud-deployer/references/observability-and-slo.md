# Observabilidade e SLO

## O que todo serviço publica
- **Métrica**: requisição (taxa, erro, latência p50/p95/p99), saturação (CPU, memória, conexões, fila), dependências (erro/latência por downstream).
- **Log**: estruturado (JSON), com `timestamp`, `level`, `service`, `version`/`git_sha`, `request_id`, `status`, `duration_ms`. Sem PII/segredo.
- **Trace**: correlação ponta a ponta no caminho crítico (`trace_id` propagado).
- **Evento de release**: deploy iniciado/concluído/rollback, com digest e versão.

## SLO
- Defina por rota crítica: ex. disponibilidade 99,9% e p95 < 300 ms.
- Orçamento de erro: 0,1% de 30 dias ≈ 43 min. Alerta queima quando o orçamento queima, não a cada erro.
- Alerta **acionável**: o que fazer, quem, e onde está o runbook. Alerta sem ação vira ruído e é ignorado.

## Painel mínimo
1. Golden signals por serviço (latência, tráfego, erro, saturação).
2. Estado do rollout (réplicas prontas por versão).
3. Dependências externas.
4. Erro por versão (para detectar regressão pós-deploy).

## Health e smoke
- `/health` (liveness) sem dependência externa; `/ready` (readiness) com dependência essencial.
- Smoke pós-deploy: 3–5 chamadas reais (login, listagem, health) com assertiva de status e conteúdo mínimo.
- Health que sempre responde 200 esconde outage.

## Custo e capacidade
- Requests realistas; HPA com métrica correta; revisar custo por release.
- Log de debug desligado em produção; amostragem em alta volumetria.

## Critério de saída
(a) métrica de erro e latência por versão; (b) log estruturado com `git_sha`; (c) SLO declarado na rota crítica; (d) alerta acionável; (e) smoke pós-deploy executado.
