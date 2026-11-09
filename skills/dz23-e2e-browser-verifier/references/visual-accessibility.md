# Acessibilidade e responsividade no browser

## Duas camadas
1. **Automatizada** — axe-core pega parte: nome acessível, contraste, estrutura, atributos ARIA inválidos.
2. **Manual** — teclado, foco, ordem de leitura, compreensão de erro. **Axe não substitui revisão manual**, e passar no axe não é conformidade WCAG.

## axe-core no Playwright
```ts
import {test, expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('sem violações sérias em /checkout', async ({page}) => {
  await page.goto('/checkout');
  const {violations} = await new AxeBuilder({page})
    .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
    .analyze();
  const graves = violations.filter(v => ['serious', 'critical'].includes(v.impact));
  expect(graves, JSON.stringify(graves, null, 2)).toEqual([]);
});
```
Allowlist explícita só com justificativa e issue — nunca silenciar tudo com `disableRules`.

## WCAG 2.2 AA — o que o E2E cobre
| Critério | Como verificar |
|---|---|
| Nome acessível | `getByRole` encontra o elemento pelo nome; teste de leitor de tela não é automatizável aqui |
| Teclado | Tab percorre o fluxo; Enter ativa; Esc fecha modal |
| Foco visível | elemento focado tem `outline`/indicador; foco não preso atrás de modal |
| Contraste | axe pega grande parte; conferir texto sobre imagem |
| Erro compreensível | mensagem junto do campo, não só toast genérico |
| Alvo de toque | ≥ 24×24 px (44×44 recomendado) no mobile |
| Reflow | sem scroll horizontal em 320 px de largura |

## Foco e modal
- Abrir modal: foco vai para dentro; Esc fecha; foco volta ao gatilho.
- Nunca `outline: none` sem substituto visível.
- Ordem de tabulação segue a ordem visual (sem `tabindex` positivo).

## Responsividade
| Largura | Uso |
|---|---|
| 320–390 px | mobile mínimo; sem overflow horizontal |
| 768 px | tablet |
| 1280 px | desktop comum |
| 1440 px | desktop largo |

Verificação de overflow:
```ts
const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
expect(overflow, 'scroll horizontal inesperado').toBe(false);
```

## Conteúdo dinâmico
- Mudança de estado anunciada (`role="status"`/`aria-live`) para leitor de tela.
- Loading tem estado textual, não só spinner; erro tem ação.
- Imagem com `alt` significativo (ou vazio quando decorativa).

## O que declarar no relatório
- axe rodado em quais páginas, com quais tags e allowlist.
- Navegação por teclado testada em quais fluxos.
- Viewports testados.
- O que **não** foi verificado (leitor de tela real, contraste manual de imagem, zoom 400%).

## Critério de saída
(a) axe sem `serious/critical` nas páginas-chave; (b) teclado e foco no fluxo crítico; (c) zero overflow horizontal no mobile; (d) limites da verificação declarados.
