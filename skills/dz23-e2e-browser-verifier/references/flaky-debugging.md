# Flaky — protocolo de depuração e sincronização

## A regra
Espere **estado observável**, nunca tempo. `sleep(2000)` é uma aposta: falha em máquina lenta e desperdiça tempo em máquina rápida.

## Sincronização web-first
| Necessidade | Correto | Proibido |
|---|---|---|
| Elemento apareceu | `await expect(locator).toBeVisible()` | `waitForTimeout(1000)` |
| Elemento sumiu | `await expect(locator).toBeHidden()` | loop com sleep |
| Resposta da API | `await page.waitForResponse(r => … && r.status() === 201)` | esperar spinner sumir |
| Navegação | `await page.waitForURL('**/checkout/**')` | sleep pós-click |
| Texto mudou | `await expect(locator).toHaveText('Pago')` | `page.content()` em loop |

`click()`/`fill()` já esperam actionability (visível, estável, habilitado, recebe evento).

## Asserção síncrona — o erro silencioso
```ts
// ERRADO: avalia o estado no instante, sem aguardar o DOM atualizar
expect(await locator.isVisible()).toBe(true);
// CORRETO: auto-retentável
await expect(locator).toBeVisible();
```

## Protocolo de depuração (Trace Viewer)
1. **Reproduza**: `--repeat-each=5` no spec; anote taxa (ex.: 2/5).
2. **Abra o trace**: `npx playwright show-trace test-results/.../trace.zip`.
3. **Leia na ordem**: screenshot do passo anterior → snapshot do DOM no clique → log da aba Network → console.
4. **Formule hipótese** (uma por vez) e confirme no trace, não no palpite.
5. **Corrija a causa** (app ou teste) e rode `--repeat-each=5` de novo para comprovar.
6. Se não houver causa identificável: quarentena com issue e prazo — nunca "aumenta timeout".

## Hipóteses frequentes (Gemini)
- **Hidratação incompleta**: HTML do SSR renderizou, mas o listener ainda não estava ligado quando o clique chegou. Sinal: primeiro clique "se perde"; segundo funciona. Correção: desabilitar até hidratar ou esperar estado interativo.
- **Animação/transição**: modal ainda animando interceptou o ponteiro. Correção: esperar estado estável/final; `reducedMotion: 'reduce'` ajuda.
- **Colisão de dados**: dois workers paralelos mexeram no mesmo registro. Correção: dado único por worker.
- **Asserção síncrona sem await**: `expect(await x.isVisible())` avalia instantâneo.
- **Terceiro lento**: analytics/chat segurando a página. Correção: `route.abort()` no ruído.
- **Relógio/fuso**: fixar `timezoneId`, congelar data quando o produto permitir.
- **Recurso esgotado**: workers > CPU/banco.

## Retry: política honesta
`retries: 1` em CI é rede de segurança **se** o relatório marca `flaky` e há issue. Retry não pode ser o único mecanismo de verde. Retry com backoff só para integração externa.

## Quarentena
Teste instável vai para suíte `quarantine` com issue, dono, data e motivo. Roda fora do gate que bloqueia deploy, mas aparece no relatório. Quarentena sem prazo é exclusão disfarçada.

## Concorrência
Cada teste cria seu usuário/dado; ordem é requisito do produto, então vive dentro de **um** teste. `test.describe.serial` só com justificativa.

## Critério de saída
(a) zero `sleep` no diff; (b) `--repeat-each=5` sem flake; (c) timeout justificado; (d) retry com política; (e) quarentena com issue quando aplicável.
