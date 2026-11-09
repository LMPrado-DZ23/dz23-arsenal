# Revisão adversarial por camada

## Frontend
Quebra em 320px, zoom 200%, foco perdido, formulário duplo, loading infinito, rota direta, estado vazio, erro 401/403/500, assets faltantes, dark mode e reduced motion quando aplicáveis. Inspecione console e network no navegador real quando disponível.

## Backend e autenticação
IDOR por troca de IDs, autorização apenas no frontend, escalada de role, validação de payload, rate limiting, idempotência, retry/timeouts, CSRF e tokens/sessões, webhooks com assinatura e replay.

## Banco e multitenancy
Constraints, índices, transações, concorrência, N+1, migração e rollback, isolamento A/B em query, API, cache, storage, fila e worker. Não usar dados de produção sem autorização.

## Infra e supply chain
Healthcheck, restart, TLS, secrets, logs sem PII, backup/restore, dependências, lockfiles, artefatos de build e plano de rollback. Não fazer deploy sem autorização quando houver risco relevante.

## Estratégia de teste
Priorize riscos plausíveis e evidências reais. Use teste focado, suíte relacionada, smoke e exploração manual conforme impacto. Registre o que não foi testado e o motivo; não gere relatório “seguro” sem verificação.
