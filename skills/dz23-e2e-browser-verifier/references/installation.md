# Instalação

## DeepSeek Harness (DSH)
1. Copie a pasta `dz23-e2e-browser-verifier/` para `C:\Users\<usuário>\.agents\skills\`.
2. Não é preciso reiniciar: a descoberta lê `SKILL.md` na raiz.
3. Invoque por `/dz23-e2e-browser-verifier` ou por descrição ("escreva o E2E do checkout e prove com trace").
4. `~/.claude/skills` e `~/.codex/skills` apontam para `~/.agents/skills` (junction): instalar uma vez alcança os três.

## Requisitos do projeto
```bash
npm i -D @playwright/test
npx playwright install --with-deps chromium
```
Node ≥ 18 no projeto (o ambiente DSH já tem Node 22+).

## MCP Playwright (verificação ad-hoc)
Configurado no perfil DSH. Para sessão persistente entre execuções, use `--user-data-dir`; sem isso, login se perde a cada run. Site local precisa de servidor HTTP (`python -m http.server`), pois `file://` é bloqueado.

## Variáveis de ambiente
```bash
E2E_BASE_URL=https://staging.exemplo.com
E2E_USER=e2e@exemplo.test
E2E_PASS=<secret>
```
Nunca commitar valores. Em CI, usar secrets do provedor.

## Estrutura
```
dz23-e2e-browser-verifier/
  SKILL.md
  README.md
  CHANGELOG.md
  VERSION
  PROMPT-ATIVACAO.txt
  references/
    test-strategy.md
    selectors-and-page-objects.md
    synchronization-and-flakiness.md
    browser-verification.md
    test-data-and-environments.md
    ci-and-parallelization.md
    evidence-and-debugging.md
    quality-gates.md
    anti-patterns.md
    installation.md
  templates/
    test-plan.md
    flaky-triage.md
  scripts/
    validate_skill.py
  evals/
    evals.json
```

## Verificação
```bash
python scripts/validate_skill.py
```

## Uso combinado
- `dz23-ultimate-pro-max` — quando o E2E cobre UI/regressão visual.
- `dz23-backend-data-architect` — contrato e dado que o fluxo consome.
- `security-review` — fluxo autenticado antes de expor.
- `delivery-pipeline` — pipeline, artifact e gate de deploy.
- `dz23-autonomous-improvement-ultimate` — quando roda dentro de `/goal`.
- `mobile-automation` — quando o alvo é app nativo, não browser.
