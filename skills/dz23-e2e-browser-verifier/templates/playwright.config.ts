import { defineConfig, devices } from '@playwright/test';

/**
 * Configuração de referência. Adapte baseURL, testDir e projetos ao repositório
 * existente — não crie uma config paralela para "não mexer" na atual.
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,            // sequencial para evidência clara; ligue em suites isoladas
  retries: process.env.CI ? 1 : 0, // 1 em CI como rede de segurança, nunca como solução
  workers: process.env.CI ? 2 : undefined,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'e2e/report', open: 'never' }],
    ['junit', { outputFile: 'e2e/report/junit.xml' }],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    headless: true,
    screenshot: 'on',               // sempre capturar
    video: 'retain-on-failure',     // vídeo só em falha
    trace: 'retain-on-failure',     // trace é o artefato que resolve flake
    locale: 'pt-BR',
    timezoneId: 'America/Sao_Paulo',
    reducedMotion: 'reduce',
  },
  projects: [
    { name: 'setup', testMatch: /auth\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 7'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
    },
    // Cross-browser: habilite quando o escopo exigir. Emulação != hardware real,
    // e WebKit do Playwright != Safari/iOS real.
    // { name: 'firefox', use: { ...devices['Desktop Firefox'] }, dependencies: ['setup'] },
    // { name: 'webkit', use: { ...devices['Desktop Safari'] }, dependencies: ['setup'] },
  ],
});
