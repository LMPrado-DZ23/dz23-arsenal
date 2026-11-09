# Relatório E2E — <projeto> — <data>

## Ambiente
- URL:
- Commit / branch:
- Browser(s): Chromium | Firefox | WebKit
- Viewport(s): 390×844 | 768×1024 | 1280×720 | 1440×900
- Dados: sintéticos | banco de teste (nunca produção)

## Matriz de cobertura
| Fluxo | Cenário | Estado | Evidência |
|---|---|---|---|
| login | credencial válida | PASS | `screenshots/login-sucesso.png` |
| login | credencial inválida | PASS | `screenshots/login-erro.png` |
| checkout | pagamento aprovado | PASS | `screenshots/checkout-pago.png`, `trace.zip` |
| checkout | cartão expirado | FAIL | `trace.zip`, bug #42 |

## Comandos e resultados
```
npx playwright test            → passed: __  failed: __  skipped: __  flaky: __
npx playwright test --repeat-each=5 <spec> → __/5 estável
exit code: __
```

## Bugs encontrados
| ID | Fluxo | Passo | Sintoma | Causa raiz | Correção | Regressão |
|---|---|---|---|---|---|---|
| #42 | checkout | pagar com cartão expirado | tela branca | erro 500 não tratado | tratar erro no handler | `checkout-erro.spec.ts` |

## Evidências
- Screenshots: `e2e/screenshots/*.png`
- Traces: `e2e/test-results/*.zip`
- Console/network: anexos `console-errors.json` / `failed-requests.json`
- Relatório HTML: `e2e/report/index.html`

## Limitações e riscos
- Cross-browser testado? (Chromium / Firefox / WebKit — declarar quais)
- Acessibilidade: axe em quais páginas + o que ficou manual
- Ambientes: staging / preview / produção (somente read-only, com autorização)
- O que NÃO foi testado:

## Veredito geral
**PASS | PARTIAL | FAIL | BLOCKED**

> `skipped` e `flaky` não contam como PASS. Sem screenshot e saída de comando, o estado é `NOT_TESTED`.
