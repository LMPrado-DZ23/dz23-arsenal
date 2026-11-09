# BENCHMARK — <mudança> — <data>

## Configuração (deve ser idêntica antes e depois)
| Item | Valor |
|---|---|
| Ambiente | <local/staging/prod> |
| Build/commit | `<sha>` antes · `<sha>` depois |
| Dado | <volume, distribuição, tenants> |
| Carga | <k6: vus, estágios, duração> |
| Cache | <frio | aquecido — declarar> |
| Máquina/instância | <tipo, CPU, RAM> |
| Região | <app> × <banco> |
| Janela | <n minutos / n requisições> |

## Antes
| Métrica | p50 | p95 | p99 | Observação |
|---|---|---|---|---|
| Latência da rota | | | | |
| Queries por request | | | | |
| TTFB | | | | |
| Payload (KB) | | | | |
| CPU / RAM | | | | |
| Erros | | | | |

## Depois
| Métrica | p50 | p95 | p99 | Δ vs antes |
|---|---|---|---|---|
| Latência da rota | | | | |
| Queries por request | | | | |
| TTFB | | | | |
| Payload (KB) | | | | |
| CPU / RAM | | | | |
| Erros | | | | |

## Evidência bruta
```
<saída do k6 / EXPLAIN / trace-id / Lighthouse>
```

## Veredito
- Budget cumprido? <sim/não — quais linhas>
- Regressão em métrica não-alvo? <nenhuma | qual>
- Custo da mudança: <memória/CPU/dinheiro/complexidade>

## O que este benchmark NÃO prova
- <tráfego real de produção | cenário fora do declarado | device real>
