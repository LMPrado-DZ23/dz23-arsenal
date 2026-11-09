import { test as base, expect } from '@playwright/test';

// ── fixture global: console + pageerror + network 4xx/5xx ──────────────
export const test = base.extend({
  page: async ({ page }, use, testInfo) => {
    const consoleErrors: string[] = [];
    const failedRequests: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    page.on('pageerror', err => consoleErrors.push(`pageerror: ${err.message}`));
    page.on('response', res => {
      if (res.status() >= 400) failedRequests.push(`${res.status()} ${res.url()}`);
    });

    await use(page);

    await testInfo.attach('console-errors', {
      body: JSON.stringify(consoleErrors, null, 2),
      contentType: 'application/json',
    });
    await testInfo.attach('failed-requests', {
      body: JSON.stringify(failedRequests, null, 2),
      contentType: 'application/json',
    });

    // Tolerância zero a erro silencioso. Allowlist explícita só para ruído conhecido.
    expect(consoleErrors, 'erros de console/pageerror').toEqual([]);
    expect(failedRequests, 'respostas HTTP 4xx/5xx').toEqual([]);
  },
});

// ── fluxo de referência ────────────────────────────────────────────────
const FLUXO = 'login-e-dashboard';

test.describe(`[E2E] ${FLUXO}`, () => {
  // Sessão vem do storageState do projeto (auth.setup.ts) — não repita login visual.
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('abre o dashboard autenticado', async ({ page }) => {
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
    await page.screenshot({ path: `e2e/screenshots/${FLUXO}-sucesso.png`, fullPage: true });
  });

  test('rejeita credenciais inválidas', async ({ page, context }) => {
    // Cenário de login visual: contexto sem sessão.
    await context.clearCookies();
    await page.goto('/login');

    await page.getByLabel('E-mail').fill('naoexiste@example.com');
    await page.getByLabel('Senha').fill('errada');
    await page.getByRole('button', { name: /entrar/i }).click();

    await expect(page.getByRole('alert')).toBeVisible();
    await page.screenshot({ path: `e2e/screenshots/${FLUXO}-erro-credencial.png` });
  });
});
