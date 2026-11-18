# Changelog — dz23-e2e-browser-verifier

## [1.1.3] — 2026-11-18

### Corrigido
- Nota histórica do cabeçalho afirmava "4 templates e 15 evals", valores da v1.1. Hoje são 6 templates e 16 evals, e nenhum dos números batia nem com .ts (3) nem com .md (3): a frase era resíduo de versão, não contagem estrutural. Reescrita para não declarar contagens correntes em prosa -- cada bump as deixaria mentindo -- apontando ao CHANGELOG.

## [1.1.2] — 2026-11-17

### Corrigido
- `scripts/validate_skill.py` não usa mais `assert` para reportar falha das checagens comuns. Sob `python -O` a instrução é removida pelo interpretador e o validador imprimia OK com referência quebrada, saindo 0 — verificado nas dez skills desta data. Agora imprime cada erro em stderr e sai 1 nos dois modos.
- Reprodução: injetar ``Ver `references/quebrada-O-teste.md`.`` no SKILL.md e rodar `python -O scripts/validate_skill.py` → antes exit 0, agora exit 1. Coberto por caso permanente em `scripts/selftest-ferramentas.py` (grupo `rejeicao`).

## [1.1.1] — 2026-11-09

### Adicionado
- Regra de **snippet executável quando o cenário é teste**: exemplo Playwright e Cypress com seletor por
  papel/testid, ação e asserção. Prosa só é aceita em planejamento, declarada como `plano de teste, não teste
  executável`. Fecha OB-05 da auditoria externa de 2026-11-09.
- Novo eval `test-in-prose-not-code` (16 casos).

## [1.1.0] — 2026-11-08

Merge com 3 propostas externas (Claude, Gemini, ChatGPT) + relatório de verificação Manus.
Preserva a estrutura 5.1–5.6 existente e adiciona tiers de risco.

### Adicionado
- Seção "Tiers de risco" P0/P1/P2 no SKILL.md (Gemini)
- `references/playwright-strategy.md` (fusão de seletores + browser, com storage state auth)
- `references/browser-security.md` (novo — authz, IDOR, tenant, sessão, CSRF/CORS)
- `references/visual-accessibility.md` (novo — axe, WCAG 2.2 AA, responsividade)
- `references/ci-and-evidence.md` (fusão de CI + evidência, com sanitização e retenção)
- `references/flaky-debugging.md` (renomeado de synchronization; protocolo Trace Viewer)
- 4 templates: `playwright.config.ts`, `e2e-smoke.spec.ts`, `axe-audit.spec.ts`, `e2e-report.md`
- 3 novos evals: `click-before-hydration`, `sync-assertion-vs-async`, `tenant-cross-read-not-tested` (15 total)
- 4 anti-padrões do Gemini: asserção síncrona, clique antes da hidratação, usuário mutável
  compartilhado, testar implementação em vez de comportamento (38 total)
- Seções de workflow em 5 etapas, mapeamento A–F, vereditos e checklist de encerramento

### Corrigido
- Referência única à skill de UI: `dz23-ultimate-pro-max` (a skill anterior foi substituída)
- `templates/e2e-report.md` definido (era citado sem estrutura)

## [1.0.0] — 2026-11-08

Primeira versão.

- `SKILL.md`: missão, precedência, método em 9 etapas (risco → fluxo → nível → teste → browser →
  estabilização → evidência → CI → entrega) e módulo 5 com 6 decisões (seletor, sincronização,
  dados/isolamento, autenticação, evidência, CI/escala).
- 10 references: estratégia, seletores/Page Object, sincronização/flake, browser real, dados e
  ambientes, CI/paralelização, evidência/diagnóstico, quality gates, anti-padrões e instalação.
- 2 templates: plano de teste e triagem de flake.
- 12 cenários de avaliação em `evals/evals.json` (schema 1).
- Padrões inegociáveis: zero `sleep`, zero seletor posicional, isolamento de dado por run,
  autorização e tenant cruzado testados, evidência obrigatória (trace/screenshot/console),
  flake com quarentena e prazo.
- Quality gates com severidade BLOCKER/MAJOR/MINOR e matriz por fluxo (caminho feliz, erro,
  autorização, persistência, rede, idempotência, mobile, teclado).
