# Vertical Slice Plan — <projeto>

## DAG
```
Slice 1 (Fundação & Schema)
      │
      ▼
Slice 2 (Domínio & Contratos) ──┐
      │                          │ (após contrato fechado)
      ▼                          ▼
Slice 3 (Experiência Visual) ──► Slice 4 (Prova E2E & Hardening)
```

## Slice 1 — Fundação & Schema
- **Escopo**: migração, índices, constraints, seed mínimo, testes de repositório.
- **Arquivos alvo**: `migrations/`, `src/db/`, `tests/db/`.
- **Não faz**: regra de negócio, rota, tela.
- **Verificação**: `pnpm test:db`
- **DoD**: migração up/down; índice criado; teste de constraint; nenhum `SELECT *` sem índice justificado.

## Slice 2 — Domínio & Contratos
- **Escopo**: FSM, invariantes, schemas, serviço, proteção multi-tenant, contrato de rota.
- **Arquivos alvo**: `src/domain/`, `src/api/`, `contracts/`, `tests/integration/`.
- **Não faz**: UI, deploy.
- **Verificação**: `pnpm test:integration` + `curl` do contrato.
- **DoD**: 409/422/404 corretos; teste de tenant cruzado; contrato publicado.

## Slice 3 — Experiência Visual
- **Escopo**: UI com Loading, Empty, Success e Error; validação de formulário; integração com API.
- **Arquivos alvo**: `src/components/`, `src/pages/`, `tests/component/`.
- **Não faz**: mudar contrato (se precisar, volta para Slice 2).
- **Verificação**: `pnpm test:component`
- **DoD**: 4 estados implementados; erro de API exibido ao usuário; acessível por teclado.

## Slice 4 — Prova E2E & Hardening
- **Escopo**: testes em browser real (feliz + 4xx), observabilidade, deploy.
- **Arquivos alvo**: `e2e/`, `observability/`, `deploy/`.
- **Verificação**: `pnpm playwright test` + smoke pós-deploy.
- **DoD**: fluxo provado ponta a ponta; log/métrica do caminho novo; rollback pronto.

## Regras
- Nenhum slice termina sem comando de verificação executado.
- Contrato de interface fechado ao final do Slice 2 — só então Slice 3 pode paralelizar.
- Slice 4 não substitui teste de unidade/integração; ele prova a jornada.
