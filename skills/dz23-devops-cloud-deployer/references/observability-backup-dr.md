# Observabilidade, backup e recuperação de desastre

## Dois endpoints, dois papéis
| Endpoint | Papel | Regra |
|---|---|---|
| `/healthz` (liveness) | processo vivo, sem dependência externa | rápido; falha → restart |
| `/readyz` (readiness) | pode receber tráfego: DB, cache, fila | falha → sai do balanceador |

Readiness que responde `ready` sem checar o banco dá falsa segurança: o pod recebe tráfego e quebra na
primeira query. Liveness que checa o banco reinicia todos os pods quando o banco oscila — cascata.

## Logs
- Estruturado (JSON) com `timestamp`, `level`, `service`, `version`/`git_sha`, `request_id`, `status`.
- **Rotação obrigatória**: `logging.options.max-size: "10m"` + `max-file: "5"`.
- Sem rotação, `*-json.log` cresce sem limite, enche o disco e **corrompe o banco** — o incidente clássico
  de VPS.
- Sem PII/segredo; debug desligado em produção.

## Métricas e alertas
- Golden signals: latência p50/p95/p99, tráfego, erro, saturação.
- Erro segmentado **por versão** (para ver regressão pós-deploy).
- Alerta acionável: o que fazer e quem chamar. Alerta sem ação vira ruído.
- SLO declarado na rota crítica e orçamento de erro consumido.

## Backup 3-2-1
- **3** cópias, **2** mídias diferentes, **1** off-site.
- Postgres: `pg_dump -Fc` (formato custom) + compressão + criptografia; envio com `rclone` para S3/R2/GCS.
- Integridade: checksum do dump e verificação de tamanho; falha de backup **alerta**.
- Retenção declarada (ex.: 7 diários, 4 semanais, 12 mensais).

```bash
PGPASSWORD="$PGPASS" pg_dump -h "$PGHOST" -U "$PGUSER" -Fc "$PGDB" \
  | gzip -9 > "backup/$(date +%F-%H%M).dump.gz"
sha256sum backup/*.dump.gz > backup/SHA256SUMS
rclone copy backup/ remote:bucket/app-backups/ --include "*.dump.gz"
```

## Restore ensaiado
Backup sem teste de restore **não é backup**.
1. Restaurar em ambiente separado: `pg_restore -d restore_db backup.dump`.
2. Verificar contagem de tabela-chave e amostra de registros.
3. Medir o tempo total (é o seu RTO real).
4. Registrar data, responsável e resultado.

## RTO/RPO
| Serviço | RPO (perda aceitável) | RTO (tempo de volta) |
|---|---|---|
| banco principal | 24h | 1h |
| arquivos/upload | 24h | 4h |
Declarar por serviço; sem isso, "backup existe" não diz nada sobre continuidade.

## Runbook de incidente
Sintoma → verificação (health, log, métrica, `df -h`, `dmesg`) → contenção (rollback, feature flag) →
causa raiz → registro. Disco cheio tem causa própria: log sem rotação ou backup local sem limpeza.

## Critério de saída
(a) `/healthz` e `/readyz` separados e reais; (b) log rotation configurada; (c) backup 3-2-1 com
checksum; (d) restore ensaiado e medido; (e) RTO/RPO declarados; (f) alerta acionável.
