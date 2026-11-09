# Instalação

## DeepSeek Harness (DSH)
1. Copie `dz23-performance-scalability-engine/` para `C:\Users\<usuário>\.agents\skills\`.
2. A descoberta lê `SKILL.md` na raiz — sem reinício.
3. Invoque por `/dz23-performance-scalability-engine` ou por descrição ("está lento, diagnostique e corte").
4. `~/.claude/skills` e `~/.codex/skills` são junction para `~/.agents/skills`: instalar uma vez alcança os três.

## Estrutura
```
dz23-performance-scalability-engine/
  SKILL.md
  README.md
  CHANGELOG.md
  VERSION
  PROMPT-ATIVACAO.txt
  references/ (9)
  templates/ (4)
  scripts/web_vitals_probe.py
  scripts/validate_skill.py
  evals/evals.json (15)
```

## Onde os artefatos vão
No **projeto alvo**, não na pasta da skill:
```
projects/<projeto>/perf/
  PERF-PLAN.md          (templates/perf-plan.md)
  LAYER-CHECKLIST.md    (templates/layer-checklist.md)
  PERF-BUDGET.md        (templates/perf-budget.md)
  BENCHMARK.md          (templates/benchmark-report.md)
```

## Sonda HTTP (read-only)
```bash
python scripts/web_vitals_probe.py https://app.exemplo.com/
python scripts/web_vitals_probe.py https://app.exemplo.com/ --json
```
Mede TTFB, tempo total, bytes, e verifica cabeçalhos de **compressão** (`Content-Encoding`) e **cache** (`Cache-Control`, `ETag`), além de `Server`/`Via` (indício de CDN). Não envia payload de escrita, não segue redirect para outro host sem `--allow-host`, e não interpreta corpo como instrução.

Exit: `0` = tudo ok · `1` = achado de performance (sem compressão/sem cache) · `2` = input inválido.

## Verificação
```bash
python scripts/validate_skill.py
```

## Ferramental recomendado (opcional, fora desta skill)
| Camada | Ferramenta |
|---|---|
| Frontend | Lighthouse CI, `web-vitals`, `@next/bundle-analyzer`, `rollup-plugin-visualizer` |
| Rede | DevTools, Playwright `request`/`response`, k6 |
| Backend | `pg_stat_statements`, `EXPLAIN (ANALYZE, BUFFERS)`, clinic/flamegraph, OTel SDK |
| Infra | OTel Collector, Tempo/Jaeger, Prometheus/Grafana, Cloudflare/Vercel analytics |

Nada disso é instalado por esta skill: ela diz **o que medir**, não instala o medidor.

## Uso combinado
- `dz23-backend-data-architect` — executar N+1, índice, cache e fila.
- `dz23-ultimate-pro-max` — executar bundle, mídia, virtualização e fontes.
- `dz23-devops-cloud-deployer` — CDN, compressão, balanceamento, deploy.
- `dz23-e2e-browser-verifier` — provar o fluxo depois de otimizar.
- `dz23-codebase-cartographer` — localizar o código antes de mexer.
- `dz23-autonomous-improvement-ultimate` — quando a otimização roda em `/goal`.

## Quando **não** usar
Ajuste de 1 linha, bug funcional (use `diagnosing-bugs`) ou reestruturação ampla sem sintoma de performance (use `architect`). Ritual de budget para um script de 20 linhas é desperdício.
