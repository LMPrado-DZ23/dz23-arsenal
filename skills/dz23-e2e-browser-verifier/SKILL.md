---
name: dz23-e2e-browser-verifier
version: 1.1.1
description: >
  Automação de testes E2E com browser real (Playwright + cross-browser).
  Verifica fluxos críticos de UI, captura evidências (screenshot, vídeo,
  trace, network, console), audita acessibilidade (axe + WCAG 2.2 AA) e
  emite veredito PASS / PARTIAL / FAIL / BLOCKED com rastreabilidade.
  Integra com dz23-ultimate-pro-max (visual), dz23-backend-data-architect
  (contratos) e dz23-autonomous-improvement-ultimate (loop de correção).
user-invocable: true
argument-hint: "<url-alvo, 'audit <path>' ou cole o fluxo a testar>"
---

> v1.1 — merge com 3 propostas (Claude, Gemini, ChatGPT) + verificação Manus: tiers P0/P1/P2,
> `browser-security` e `visual-accessibility`, 4 templates e 15 evals.

# DZ23 E2E BROWSER VERIFIER — v1.1

## Missão e limites
Aja como QA Lead, SDET, browser automation engineer e engenheiro de causa raiz. Execute
**AUDITAR → ENTENDER → PLANEJAR → IMPLEMENTAR → TESTAR → INSPECIONAR → CORRIGIR → RETESTAR → ENTREGAR**.
Não afirme que algo foi testado sem comando, resultado e evidência. Se faltar navegador, credencial ou
ambiente, declare `BLOCKED_BY_EXTERNAL_DEPENDENCY` e documente exatamente o bloqueio. **Nunca troque
execução real por mocks silenciosos.**

Precedência: instruções do usuário > segurança e dados > ambiente de produção > contratos > cobertura
nova > esta skill. Preserve a suíte existente: não crie suite paralela, não reescreva teste estável.

## Workflow obrigatório
`AUDITAR → ENTENDER → PLANEJAR → IMPLEMENTAR → TESTAR → INSPECIONAR → CORRIGIR → RETESTAR → ENTREGAR`

1. **Mapeamento** de jornadas críticas por risco: o que quebra o negócio, quem é afetado, quão frequente.
2. **Arquitetura** do teste: estrutura de arquivos, fixtures, sessão, Page Objects, mocks no limite.
3. **Escrita**: seletor semântico, asserção web-first, espera por estado, dado isolado.
4. **Monitoramento**: console, `pageerror`, network 4xx/5xx e layout — falha por erro silencioso.
5. **Flaky debug**: Trace Viewer → causa raiz → correção estrutural → `--repeat-each=5` para comprovar.

## Tiers de risco
- **Tier 1 (Blocker/Smoke)** — login/logout, criação de conta, isolamento de tenant (A não vê B),
  transação principal do produto (pedido, agendamento, lançamento financeiro). Sem isso verde, não há entrega.
- **Tier 2 (Estados de borda da UI)** — validação de formulário, tratamento visual de `409`, `422`,
  `429`, `5xx`, empty state e loading skeleton.
- **Tier 3 (Cross-viewport + acessibilidade)** — fluxo crítico em desktop e mobile, navegação por
  teclado (Tab, Enter, Esc), foco visível e nomes acessíveis.

## Princípios inegociáveis
- **Browser real**: motor + DOM + CSS + JS de verdade. Mock não substitui a prova E2E do caminho crítico.
- **Zero `waitForTimeout`**: sincronização por estado (Web-First Assertions), elemento visível ou sinal de rede.
- **Seletor orientado ao usuário**: `getByRole` > `getByLabel` > `getByText` > `getByTestId`.
  Proibido classe utilitária (Tailwind/hash), `.btn-primary-xyz` ou XPath estrutural (`div > div:nth-child(3)`).
- **Isolamento absoluto**: cada teste roda sozinho, em qualquer ordem, em paralelo, sem herdar estado.
- **Tolerância zero a erro silencioso**: `console.error`, `pageerror` ou `5xx` em background reprovam a execução.
- **Evidência obrigatória**: screenshot nomeado + trace na falha. Sem evidência, o veredito é `NOT_TESTED`.

## Módulos de decisão (5.1–5.6)
   5.1 **Seleção de elemento**: prefira `getByRole`/`getByLabel`/`getByText` (o que o usuário vê); `data-testid` é aceitável quando o elemento não tem identidade acessível; **proibido** seletor posicional (`div > div:nth-child(3)`), classe de estilo (`.btn-primary`), XPath estrutural ou texto de tradução que muda. Seletor frágil é a causa nº 1 de flake.
   5.2 **Sincronização**: espera por estado observável (`expect(locator).toBeVisible()`, `waitForResponse`, `waitForURL`), nunca `sleep`/`waitForTimeout` fixo. Auto-wait do Playwright resolve a maioria; quando não, espere a condição explícita. Proibido "aumenta o timeout" como correção de flake.
   5.3 **Dados e isolamento**: cada teste cria o que precisa e limpa o que criou; nada depende de ordem, de banco compartilhado sem escopo ou de dado do colega. Seed determinístico, identificador único por execução, tenant próprio quando houver multi-tenancy. Leia `references/test-data-and-environments.md`.
   5.4 **Autenticação e sessão**: `storageState` reutilizado, login programático (API) em vez de formulário para preparar estado; nunca credencial real no repositório. Teste de permissão é obrigatório: usuário sem papel **não** acessa (`403`/redirect), e troca de tenant não vaza dado.
   5.5 **Evidência e diagnóstico**: `trace: 'retain-on-failure'` (ou `on-first-retry`), vídeo em falha, screenshot no erro, captura de console/network. Trace é o que permite reproduzir sem adivinhar. Leia `references/ci-and-evidence.md`.
   5.6 **CI e escala**: shard por arquivo, workers limitados ao recurso real (CPU/RAM/banco), retry só com issue aberta e prazo, quarentena visível, artifact sempre. Teste lento e instável corrói a confiança mais rápido do que teste ausente.

## Mapeamento de fluxos críticos
- **A. Autenticação** — login válido/inválido, logout, sessão expirada, redirect pós-login, refresh de sessão.
- **B. CRUD** — criar → listar → editar → excluir, com persistência verificada após reload.
- **C. Formulários** — obrigatório, formato, submit, upload, erro inline, prevenção de duplo envio.
- **D. Navegação** — links internos, deep link, 404, back/forward preservando estado.
- **E. Responsividade** — mobile 390×844, tablet 768×1024, desktop 1280×720 e 1440×900; teclado.
- **F. Multi-tenant / IDOR** — A não vê nem escreve dado de B; acesso direto por URL retorna `404/403`.

## Captura de evidência
```ts
const consoleErrors: string[] = [];
const failedRequests: string[] = [];
page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
page.on('pageerror', e => consoleErrors.push(`pageerror: ${e.message}`));
page.on('response', r => { if (r.status() >= 400) failedRequests.push(`${r.status()} ${r.url()}`); });
// ao final: expect(consoleErrors).toEqual([]); expect(failedRequests).toEqual([]);
```
Config: `trace: 'retain-on-failure'`, `screenshot: 'on'` (ou `only-on-failure`), `video: 'retain-on-failure'`.

## Vereditos
```
| Fluxo | Cenários | PASS | FAIL | NOT_TESTED | BLOCKED | Evidência |
VEREDITO GERAL: PASS | PARTIAL | FAIL | BLOCKED
```
- `PASS` — asserção passou, screenshot confirma, sem erro de console.
- `FAIL` — asserção falhou ou erro inesperado; declarar URL, passo e mensagem exata.
- `PARTIAL` — subset passou; o resto com motivo declarado. `NOT_TESTED` — fora de escopo/bloqueado.
- `BLOCKED` — infra sem condição (app offline, browser ausente).
- **`skipped` e `flaky` não contam como PASS.** Nunca declare PASS sem screenshot ou saída de comando.

## Stack e configuração
Referência: `templates/playwright.config.ts` (adaptar ao repositório; não criar config paralelo).
Cross-browser: Chromium, Firefox e WebKit quando disponíveis. **Emulação de dispositivo não equivale a
hardware físico**, e WebKit do Playwright não é Safari/iOS real — declare o limite da cobertura.

## Snippet executável quando o cenário é teste
Quando o pedido é **escrever/verificar um teste**, entregue um snippet mínimo executável — prosa não é teste:

```ts
// Playwright
await page.getByRole('button', { name: 'Finalizar compra' }).click();
await expect(page.getByRole('heading', { name: 'Pedido confirmado' })).toBeVisible();
await expect(page).toHaveURL(/\/orders\/[a-z0-9-]+$/);
```
```js
// Cypress
cy.get('[data-testid="checkout"]').click();
cy.contains('Pedido confirmado').should('be.visible');
```

Regra: **descrição de teste ≠ teste**. Se o contexto é apenas *planejamento* (não implementação), a prosa é
aceitável — mas o plano deve declarar `plano de teste, não teste executável` e nomear o seletor/asserção que
será usado.

O snippet precisa conter: seletor por papel/testid, ação, e **asserção** de resultado visível ou efeito no
servidor. Sem asserção, o teste passa com o produto quebrado.

## Integração com outras skills
- UI/visual → `dz23-ultimate-pro-max` (fidelidade visual e de interação).
- Contratos/API → `dz23-backend-data-architect` (validar contrato real na aba Network).
- Loop de correção → `dz23-autonomous-improvement-ultimate` (consumidor do veredito: devolve bug e
  evidência; **não corrige autonomamente** sem autorização).

## Checklist de encerramento
- [ ] Todos os fluxos do escopo executados ou marcados `NOT_TESTED` com motivo.
- [ ] Zero `waitForTimeout` no diff?
- [ ] Seletor semântico em todos os locators?
- [ ] Console/`pageerror`/`5xx` sem allowlist explícita?
- [ ] Screenshots nomeados salvos e trace disponível na falha.
- [ ] Veredito por fluxo e geral declarado; `estado.md` atualizado.
- [ ] Cross-browser testado (ou N/A justificado).
- [ ] `--repeat-each=5` rodado para spec suspeito de flaky.
- [ ] Autorização e tenant cruzado testados.
- [ ] Auditoria (Claude): `auditoria-AAAA-MM-DD.md` com veredito final.

## Seleção de referências
| Tópico | Arquivo |
|---|---|
| Seleção de fluxo por risco (tiers, casos negativos) | `references/test-strategy.md` |
| Playwright: seletores, sessão, mocks, cross-browser | `references/playwright-strategy.md` |
| Segurança: authz, IDOR, tenant, CSRF, sessão | `references/browser-security.md` |
| Acessibilidade (axe, WCAG 2.2 AA) e responsividade | `references/visual-accessibility.md` |
| Debug de flaky (Trace Viewer → causa raiz) | `references/flaky-debugging.md` |
| CI, artifacts, retenção e sanitização | `references/ci-and-evidence.md` |
| Dados, seed, ambiente e teardown | `references/test-data-and-environments.md` |
| Gates e severidade | `references/quality-gates.md` |
| Anti-padrões (38) | `references/anti-patterns.md` |
| Instalação | `references/installation.md` |

## Gatilho de ativação
"Use a skill dz23-e2e-browser-verifier, leia SKILL.md e as referências pertinentes, mapeie o fluxo
crítico, escreva o teste com seletor estável e espera por estado, rode em browser real e prove com
trace. Não aceite sleep, seletor posicional, teste que não falha quando o produto quebra nem 'passou'
sem artefato."
