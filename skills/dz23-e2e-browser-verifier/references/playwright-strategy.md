# Playwright — seletores, sessão, mocks e cross-browser

## Hierarquia de seletor (do melhor para o pior)
1. `getByRole('button', {name: 'Salvar'})` — o que o usuário e o leitor de tela veem.
2. `getByLabel('E-mail')`, `getByPlaceholder`, `getByText` — rótulo e conteúdo.
3. `getByTestId('checkout-submit')` — identidade explícita de teste, quando não há papel/label.
4. `locator('input[name="email"]')` — atributo estável do produto (aceitável).
5. ❌ Classe CSS de estilo (`.btn-primary-xyz`, Tailwind hash), posição (`div > div:nth-child(3)`), XPath estrutural, texto traduzido.

Regra: se o elemento não tem nome acessível, isso já é um defeito de acessibilidade — prefira corrigir o componente a criar `testid`.

## Por que posicional quebra
Mudar a ordem de dois cards, adicionar um `<div>` de espaçamento ou trocar o grid muda `nth-child`. O teste falha sem o produto ter quebrado — e o time "conserta" o seletor até a suíte virar ruído.

## Page Object
Use quando o mesmo fluxo aparece em mais de um teste.
```ts
class CheckoutPage {
  constructor(page) { this.page = page; }
  get cep() { return this.page.getByLabel('CEP'); }
  get pagar() { return this.page.getByRole('button', {name: 'Pagar'}); }
  async preencher(dados) { await this.cep.fill(dados.cep); }
  async confirmar() { await this.pagar.click(); }
}
```
Regras: ações de página, não regra de negócio; asserção fica no teste (`await expect(locator)`), não escondida no helper; não criar um PO por div.

## Autenticação por storage state
Teste a tela de login **uma vez**, em spec dedicado. Para o resto, autentique por API e injete o estado — reduz até 80% do tempo.
```ts
// e2e/auth.setup.ts
import {test as setup, expect} from '@playwright/test';
setup('autenticar', async ({page, request}) => {
  const resp = await request.post('/api/login', {data: {email: process.env.E2E_USER!, password: process.env.E2E_PASS!}});
  expect(resp.ok()).toBeTruthy();
  await page.context().addCookies((await resp.json()).cookies);
  await page.context().storageState({path: 'e2e/.auth/user.json'});
});
```
```ts
// playwright.config.ts (trecho)
projects: [
  {name: 'setup', testMatch: /auth\.setup\.ts/},
  {name: 'chromium', use: {...devices['Desktop Chrome'], storageState: 'e2e/.auth/user.json'}, dependencies: ['setup']},
]
```
Nunca versionar `storageState`, cookies ou token.

## Dados únicos por worker
```ts
const email = `user_${testInfo.workerIndex}_${Date.now()}@test.local`;
```
Isso elimina colisão em paralelo e permite limpar por prefixo no teardown.

## Mocks: real vs controlado
- **Contra o próprio backend**: bata na API e no banco de teste reais. Mock aqui destrói a prova.
- **Contra terceiro** (gateway de pagamento, WhatsApp, LLM externa): `page.route()` com payload fiel ao contrato, cobrindo sucesso, timeout e `5xx`.

## Sincronização web-first
```ts
const resposta = page.waitForResponse(r => r.url().includes('/api/v1/appointments') && r.request().method() === 'POST');
await page.getByRole('button', {name: /confirmar agendamento/i}).click();
expect((await resposta).status()).toBe(201);
await expect(page.getByRole('status')).toContainText('Agendamento confirmado');
```
Nunca `page.waitForTimeout`. Nunca `expect(await locator.isVisible()).toBe(true)` — use `await expect(locator).toBeVisible()`.

## Hidratação (Next.js/React/SPA)
O HTML do SSR chega antes do JS ligar os eventos. Se o clique inicial "se perde", espere o estado interativo real (`toBeEnabled`, atributo de pronto, resposta de hidratação) — não um sleep.

## Cross-browser
Chromium + Firefox + WebKit quando disponíveis. Emulação de dispositivo **não** equivale a hardware físico, e WebKit do Playwright **não** é Safari/iOS real. Declare o limite da cobertura no relatório.

## Viewport e acessibilidade no E2E
Desktop 1440×900 e 1280×720; mobile 390×844; tablet 768×1024. `getByRole` já força nome acessível; teclado e foco cobrem o fluxo crítico. Detalhe em `references/visual-accessibility.md`.

## Modo headed
Para defeito visual/interação (arraste, hover, foco). Headless é o padrão em CI. Se só reproduz headed, registre — pode ser timing de render.

## Comandos
```bash
npx playwright test                      # suíte
npx playwright test e2e/login.spec.ts    # arquivo
npx playwright test --headed             # debug local
npx playwright test --grep @smoke        # tag
npx playwright test --repeat-each=5      # flaky
npx playwright show-report e2e/report
npx playwright show-trace test-results/<trace>.zip
```
