# Registro de poda — <projeto / caminho>

Data: <AAAA-MM-DD> · Baseline: <N testes, verde?, tempo> · Suíte final: <N testes, verde?, tempo>

## Lista (mapa antes da poda)

| Teste | De que depende | Família | Ação | Rede do comportamento (se aplica) | Commit |
|---|---|---|---|---|---|
| `pricing.test.ts: applies discount` | valor esperado derivado da lógica do código | implementação | reescrever | — (valor literal) | `<hash>` |
| `export.test.ts: legacy exporter is gone` | código já removido | passado | deletar | — | `<hash>` |
| `cart.test.ts: adds item` | estado privado `_items` | implementação | reescrever | `cart.total()` | `<hash>` |
| `checkout.test.ts: total includes tax` | — | duplicata | deletar | `cart.test.ts: total` | `<hash>` |
| `button.test.ts: renders` | o navegador | nada | deletar | — | `<hash>` |

## Código de produção removido (só existia para teste)

- `session.ts: _resetCacheForTests, _getCacheSize` — nenhum chamador de produção. Commit `<hash>`.

## Veredito

- [ ] Suíte verde antes e depois
- [ ] Toda deleção classificada por família
- [ ] Nenhum comportamento ficou sem rede (reescrito onde precisava)
- [ ] Nenhum par guarda o mesmo comportamento
- [ ] Nenhuma produção existe só para teste

Estado: **PASS / PARTIAL / NOT_TESTED** — <justificativa de uma linha>
