# Borda: proxy reverso e TLS

## Escolha
| Proxy | Quando usar | Prós | Contras |
|---|---|---|---|
| **Caddy** | padrão para VPS/self-hosted | TLS automático, config mínima | menos plugins |
| **Traefik** | Docker/K8s dinâmico, muitas rotas | service discovery, middlewares | config mais densa |
| **Nginx** | legado/sofisticado | maturidade, controle fino | TLS e config manual |
| **Nenhum** | Cloudflare Tunnel/Tailscale | sem porta pública, menos superfície | dependência de provedor |

## TLS
- TLS 1.2+ (1.3 preferido); renovação automática (ACME) e alerta de expiração.
- Redirect 80 → 443; HSTS com `max-age` ≥ 6 meses **só depois** de confirmar HTTPS em tudo.
- Certificado self-signed só em local; nunca em staging compartilhado.

## Headers de segurança
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY            # ou CSP frame-ancestors 'none'
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; ...
Permissions-Policy: geolocation=(), camera=(), microphone=()
```
`X-Frame-Options` sozinho não cobre todos os navegadores — use CSP `frame-ancestors` como principal.

## Limites e resiliência
- **Body size**: `client_max_body_size 10m` (Nginx) / `request_body max_size` (Caddy) — evita upload gigante.
- **Rate limit** por IP/rota em login e API pública; janela e burst declarados.
- **Timeouts** de leitura/escrita/header curtos (Slowloris); `keepalive_timeout` coerente.
- **Compressão** (zstd/gzip) com `Vary: Accept-Encoding`.
- **Retry/upstream**: no máximo 1 retry idempotente; não mascare erro do app.

## Alternativas sem porta pública
- **Cloudflare Tunnel**: liga o container ao edge da Cloudflare, sem abrir 80/443 no host.
- **Tailscale**: acesso privado via VPN mesh; bom para admin e ambiente interno.

## Verificação
```bash
curl -sSI https://app.exemplo.com | grep -Ei 'strict-transport|x-content-type|x-frame|referrer-policy'
openssl s_client -connect app.exemplo.com:443 -servername app.exemplo.com </dev/null 2>/dev/null | openssl x509 -noout -dates
curl -s -o /dev/null -w '%{http_code}\n' http://app.exemplo.com   # espera 301/308
```

## Critério de saída
(a) TLS automático e válido; (b) redirect 80→443; (c) headers presentes; (d) body/timeout/rate limit
definidos; (e) nenhuma porta de app exposta direto.
