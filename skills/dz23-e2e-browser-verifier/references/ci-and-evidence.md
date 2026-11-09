# Screenshot, vídeo, trace e sanitização

## Pipeline mínimo
```yaml
- run: npx playwright install --with-deps chromium
- run: npx playwright test --shard=${{ matrix.shard }}/4
  env:
    E2E_BASE_URL: ${{ secrets.E2E_BASE_URL }}
    E2E_USER: ${{ secrets.E2E_USER }}
    E2E_PASS: ${{ secrets.E2E_PASS }}
- uses: actions/upload-artifact@v4
  if: always()
  with: {name: playwright-report-${{ matrix.shard }}, path: 'playwright-report/,test-results/', retention-days: 14}
```

## Configuração de evidência
| Opção | Valor | Por quê |
|---|---|---|
| `trace` | `retain-on-failure` (ou `on-first-retry`) | permite reproduzir sem adivinhar |
| `screenshot` | `on` (ou `only-on-failure`) | estado visual no momento |
| `video` | `retain-on-failure` | defeito de interação/tempo |
| `reporter` | `html` + `junit` | humano e máquina |

## Console, pageerror e network (fixture global)
```ts
// e2e/fixtures.ts
import {test as base, expect} from '@playwright/test';
export const test = base.extend({
  page: async ({page}, use, testInfo) => {
    const erros: string[] = [];
    const falhas: string[] = [];
    page.on('console', m => { if (m.type() === 'error') erros.push(m.text()); });
    page.on('pageerror', e => erros.push(`pageerror: ${e.message}`));
    page.on('response', r => { if (r.status() >= 400) falhas.push(`${r.status()} ${r.url()}`); });
    await use(page);
    await testInfo.attach('console-errors', {body: JSON.stringify(erros, null, 2), contentType: 'application/json'});
    await testInfo.attach('failed-requests', {body: JSON.stringify(falhas, null, 2), contentType: 'application/json'});
    expect(erros, 'erros de console/pageerror').toEqual([]);
    expect(falhas, 'respostas 4xx/5xx').toEqual([]);
  },
});
```
Allowlist explícita só para ruído conhecido (ex.: analytics bloqueado), documentada no teste.

## Shard e workers
- **Shard** divide por arquivo/teste entre máquinas (`--shard=1/4`).
- **Workers** é paralelismo local: limitado por CPU, RAM e pool de banco. `workers = min(4, núcleos/2)` é ponto de partida.
- Banco com pool pequeno: 4 workers × pool 10 pode estourar `max_connections`.

## Tempo de suíte
Smoke ≤ 10 min; regressão ≤ 20 min com shard. Acima, ninguém espera e o gate vira teatro. Reporte duração total, top 5 mais lentos e tempo de setup.

## Retry e gate
`retries: 1` em CI como rede de segurança, com relatório marcando `flaky`. Retry global escondendo 20% de falha é dívida com issue. Falha bloqueia merge; quarentena não bloqueia mas aparece no relatório.

## Trace — o artefato que resolve
```bash
npx playwright show-trace test-results/.../trace.zip
```
Timeline, DOM snapshot por passo, network, console e o código do teste no instante da ação. Sem trace, investigar flake é adivinhação.

## Retenção
7–30 dias, conforme custo e política. Artifact de PR pode ter retenção curta; regressão de `main`/nightly, mais longa.

## Sanitização (obrigatório)
- Mascarar PII e credencial em screenshot/vídeo (`fill('***')`, dado sintético).
- Trace pode conter header de auth e corpo de request: revise antes de anexar em issue pública.
- **Nunca versionar** `storageState`, cookies, token ou `.env`.
- Não colar trace de produção com dado de cliente em repositório.

## Relatório
Use `templates/e2e-report.md`: ambiente, matriz de cobertura, comandos e resultados, bugs, evidências, limitações e veredito.

## Critério de saída
(a) CI roda com artifact; (b) trace/screenshot/vídeo configurados; (c) console e network capturados; (d) retenção declarada; (e) sanitização revisada; (f) nada sensível versionado.
