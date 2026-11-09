import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Auditoria de acessibilidade de referência.
 * Requer: npm i -D @axe-core/playwright
 * Regra: reportar violações sérias/críticas; allowlist exige issue e justificativa.
 * Axe NÃO substitui revisão manual (teclado, foco, leitor de tela).
 */

const PAGINAS = ['/', '/checkout', '/conta'];

for (const caminho of PAGINAS) {
  test(`axe: ${caminho} sem violações sérias`, async ({ page }) => {
    await page.goto(caminho);
    await page.waitForLoadState('domcontentloaded');

    const { violations } = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze();

    const graves = violations.filter(v => ['serious', 'critical'].includes(v.impact ?? ''));
    const resumo = graves.map(v => ({
      id: v.id,
      impact: v.impact,
      help: v.help,
      nodes: v.nodes.map(n => n.target.join(' ')).slice(0, 5),
    }));

    expect(graves, JSON.stringify(resumo, null, 2)).toEqual([]);
  });
}

test('teclado alcança o CTA principal sem armadilha de foco', async ({ page }) => {
  await page.goto('/checkout');
  const cta = page.getByRole('button', { name: /pagar|finalizar/i });

  for (let i = 0; i < 25; i++) {
    await page.keyboard.press('Tab');
    if (await cta.evaluate(el => el === document.activeElement).catch(() => false)) break;
  }

  await expect(cta).toBeFocused();
});

test('sem scroll horizontal no mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  );
  expect(overflow, 'overflow horizontal inesperado em 390px').toBe(false);
});
