# Compose, redes e o bypass de UFW

## Segmentação de rede
```
internet
   │ 80/443
┌──▼──────────┐        edge_net  (não-internal)
│   proxy     │──────────────────┐
│ Caddy/Traefik│                 │
└─────────────┘                 │
                         ┌──────▼──────┐
                         │    api      │  também em internal_net
                         └──────┬──────┘
                                │ internal_net  (internal: true)
                    ┌───────────┼───────────┐
              ┌─────▼────┐ ┌────▼─────┐ ┌───▼────┐
              │ postgres │ │  redis   │ │ broker │
              └──────────┘ └──────────┘ └────────┘
```
- `edge_net`: proxy + serviço que recebe HTTP externo.
- `internal_net` com `internal: true`: banco, cache, broker. Sem rota para a internet, sem exposição direta.

## Bind de porta — o detalhe que vaza banco
```yaml
ports:
  - "5432:5432"            # ❌ expõe em 0.0.0.0 — internet inteira
  - "127.0.0.1:5432:5432"  # ✅ só loopback (túnel SSH/tailscale)
```
O Compose 3+ faz bind em `0.0.0.0` por padrão. Só o loopback é seguro fora do proxy.

## Gotcha crítico: Docker ignora UFW
Docker escreve direto nas chains `PREROUTING`/`DOCKER` do `iptables`. Consequência: `ufw deny 5432` **não
protege** container publicado em `0.0.0.0:5432` — o pacote desvia antes da regra do UFW.
Correções válidas: (a) não publicar a porta (rede interna); (b) bind em `127.0.0.1`; (c) regra em
`DOCKER-USER`; (d) firewall do provedor cloud. Verifique com
`iptables -t nat -L DOCKER -n --line-numbers` e `nmap` de fora.

## Hardening do serviço
```yaml
    user: "1001:1001"
    read_only: true
    tmpfs: [/tmp]
    security_opt: [no-new-privileges:true]
    restart: unless-stopped
    init: true
    deploy:
      resources:
        limits: {cpus: "1.50", memory: 1024M}
    logging:
      driver: json-file
      options: {max-size: "10m", max-file: "5"}
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://127.0.0.1:3000/healthz"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 20s
    depends_on:
      postgres: {condition: service_healthy}
```

## Limites de recurso
Sem `deploy.resources.limits`, um memory leak derruba o host inteiro (OOM kill global), levando o banco
junto. Limite de CPU evita que um serviço faminto degrade os vizinhos.

## Log rotation
Sem `logging.options.max-size`, `/var/lib/docker/containers/*/*-json.log` cresce até encher o disco — e
disco cheio corrompe banco e derruba o host. `max-size: 10m` + `max-file: 5` = teto de 50 MB por serviço.

## Checklist de compose
- [ ] DB/cache em `internal_net` (`internal: true`).
- [ ] Nenhuma porta sensível em `0.0.0.0`.
- [ ] `no-new-privileges`, `read_only`, `tmpfs` onde possível.
- [ ] `limits` de CPU/memória.
- [ ] `restart: unless-stopped` e `init: true`.
- [ ] healthcheck real (não `true`).
- [ ] log rotation configurada.
