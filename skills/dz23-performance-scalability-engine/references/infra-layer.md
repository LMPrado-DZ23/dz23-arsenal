# Camada 4 — Infraestrutura & Deploy (DevOps e observabilidade)

Cada item: **problema que evita** · **como implementar** · **diretriz**.

## 4.1 CDN & distribuição de ativos
**Evita** latência de RTT para usuário distante e carga de banda no servidor de aplicação; evita cache miss de asset estático.
**Implementar** CDN para `assets`, imagens, fontes e build (Cloudflare/Fastly/CloudFront/Vercel Edge); `Cache-Control` correto por tipo (imutável com hash = 1 ano; HTML = `no-cache` ou `s-maxage` curto); `Vary: Accept-Encoding`; purge por tag/versão no deploy.
```nginx
location ~* \.(js|css|woff2|avif|webp)$ {
  add_header Cache-Control "public, max-age=31536000, immutable";
}
location = /index.html { add_header Cache-Control "no-cache"; }
```
**Diretriz** HTML nunca `immutable` (senão o usuário fica preso na versão antiga). Asset com hash + `immutable` é o par correto.

## 4.2 Compressão de tráfego
**Evita** transferir 3–5× mais bytes que o necessário em JS/CSS/JSON.
**Implementar** Brotli (q 4–6 dinâmico) com fallback GZIP; comprimir na borda (CDN) e/ou no proxy; **não** comprimir imagem/vídeo/zip (já comprimidos); `gzip_static`/`brotli_static` para servir variante pré-comprimida; mínimo de 1 KB para evitar overhead.
```nginx
brotli on; brotli_comp_level 5; brotli_types text/css application/javascript application/json image/svg+xml;
gzip on; gzip_comp_level 5; gzip_min_length 1024; gzip_types text/css application/javascript application/json;
```
```caddy
encode zstd br gzip
```
**Diretriz** Brotli ~15–20% menor que GZIP em JS. Sem `Vary: Accept-Encoding`, CDN entrega binário comprimido para cliente que não aceita.

## 4.3 Proximidade geográfica
**Evita** cada query pagando RTT cross-region (30–150 ms por round-trip, multiplicado por N queries e por N+1).
**Implementar** app na mesma região do banco primário; réplica de leitura na região do usuário só para leitura tolerante a lag; conexão persistente com pool (não abrir conexão por request); evitar chamada cross-region dentro de loop.
```
[usuário] → CDN (borda) → app (região A) → banco primário (região A)   ✅ 0.5 ms RTT
[usuário] → app (região B) → banco (região A)                          ❌ 80 ms × N queries
```
**Diretriz** co-localize app e primário. Se o app tem que ficar longe do banco, o custo é por round-trip: reduza **número** de idas (join, batch, cache), não só o tamanho da query.

## 4.4 Balanceamento de carga
**Evita** instância única como teto de throughput e ponto único de falha; evita conexão presa em instância saudável mas sobrecarregada.
**Implementar** ALB/Nginx/Ingress com health check real (`/readyz` com dependência), least-connections em vez de round-robin para requisição longa, sticky session só quando há estado local (prefira stateless), `keepalive` para upstream, limite de conexão por instância e autoscaling por métrica de fila/latência (não só CPU).
```nginx
upstream app { least_conn; server app1:3000 max_conns=200; server app2:3000 max_conns=200; keepalive 32; }
```
**Diretriz** autoscaling por CPU reage tarde para workload I/O-bound — escale por latência p95 ou profundidade de fila. Health check que não checa dependência mantém instância quebrada no pool.

## 4.5 Monitoramento & RUM
**Evita** descobrir lentidão pelo cliente; evita otimizar o que ninguém sente e não perceber a regressão do deploy.
**Implementar** OpenTelemetry (traces com span por query/HTTP/dependência, `service.name`, `deployment.environment`, `release`); exportar OTLP para collector (Tempo/Jaeger/Datadog); RUM com `web-vitals` (`onLCP`, `onINP`, `onCLS`, `onTTFB`) enviado com `navigator.sendBeacon`; amostragem explícita (head 10% + tail para erro/lento); alerta em SLO (p95 acima do budget por 10 min).
```ts
import { onLCP, onINP, onCLS } from 'web-vitals';
const send = (m) => navigator.sendBeacon('/rum', JSON.stringify({
  name: m.name, value: m.value, id: m.id, rating: m.rating, path: location.pathname }));
onLCP(send); onINP(send); onCLS(send);
```
```python
with tracer.start_as_current_span("db.query", attributes={"db.statement": sql_hash, "rows": n}):
    ...
```
**Diretriz** span por query é o que revela N+1 em produção. RUM é a única fonte de "velocidade do usuário"; sintético (Lighthouse) é proxy de laboratório. Sem `release` no span, você não sabe qual deploy degradou.

## Ordem de ataque nesta camada
1. compressão (uma linha de config) → 2. CDN de estáticos → 3. co-localização app↔banco → 4. balanceamento/autoscaling → 5. OTel + RUM (habilita todo o resto).

## Verificação
`curl -H 'Accept-Encoding: br' -sI https://host/app.js | grep -i content-encoding`; `curl -sI .../index.html | grep -i cache-control`; latência por região; p95 por instância no balanceador; trace com contagem de span de query; painel RUM com p75 de LCP/INP por rota.
