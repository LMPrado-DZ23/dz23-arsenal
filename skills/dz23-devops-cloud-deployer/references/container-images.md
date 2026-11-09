# Imagem e container

## Regra
Imagem é artefato imutável: mesmo digest = mesmo binário. Build que muda entre execuções não é artefato, é aposta.

## Dockerfile — estrutura
1. **multi-stage**: `builder` compila, `runtime` recebe só o necessário.
2. **base mínima**: `distroless`/`alpine`/`slim` — sem shell e sem gerenciador de pacote na imagem final, quando possível.
3. **pin por digest**: `FROM node:22-slim@sha256:…` — tag sozinha move.

O pin por digest vale para **todas** as bases:

```dockerfile
# ❌ flutuante
FROM node:22
FROM postgres:16

# ✅ imutável
FROM node:22@sha256:<digest>
FROM postgres:16@sha256:<digest>
```

Obter o digest: `docker pull node:22` + `docker inspect --format='{{index .RepoDigests 0}}' node:22`.
O `FROM` da base é onde o supply chain começa — não só a imagem final.

4. **non-root**: `USER 10001` (criar usuário/grupo explícito); sem `chown` amplo.
5. **camadas ordenadas** do que muda menos para o que muda mais (deps antes do código) — cache real.
6. **`.dockerignore`** com `node_modules`, `.git`, testes, segredos e artefatos locais.
7. **sem segredo em `ARG`/`ENV`** — build arg vaza no histórico da imagem.
8. **`HEALTHCHECK`** quando o orquestrador não tiver probe (k8s usa probe, não healthcheck).
9. **`tini`/`--init`** quando o processo não trata sinal; entrypoint exec-form (`["node","app.js"]`).

## Antes e depois (o que juda)
| Sintoma | Causa | Correção |
|---|---|---|
| Imagem 1,2 GB | base com toolchain | multi-stage + distroless |
| Build não reproduz | `latest` + `apt-get update` sem pin | pin por digest e versão |
| Roda como root | `USER` ausente | usuário numérico e `readOnlyRootFilesystem` |
| Segredo na imagem | `ARG TOKEN` + `ENV` | secret em runtime (env/secret manager) |
| Cache inútil | `COPY . .` antes de `npm ci` | copiar manifesto primeiro |

## Tamanho e superfície
- Remover build tools, cache de pacote e documentação do estágio final.
- Não instalar `curl`/`bash` "para debug" em produção — use `kubectl debug`/ephemeral container.
- Digital signature: ver `references/supply-chain-security.md`.

## Build reprodutível
- `SOURCE_DATE_EPOCH` quando a ferramenta suportar; evitar timestamp no binário.
- `npm ci`/`pip install --require-hashes` em vez de resolução livre.
- Build com `--no-cache` em release; com cache em PR, declarando a diferença.
- Provar: dois builds do mesmo commit → mesmo digest (ou declarar por que não).

## Teste local mínimo
```bash
docker build -t app:test --build-arg VERSION=$(git rev-parse --short HEAD) .
docker run --rm -p 8080:8080 --read-only --user 10001 app:test
curl -fsS localhost:8080/health || echo FAIL
docker history app:test | head -20
```

## Critério de saída
(a) multi-stage; (b) base pinada por digest; (c) non-root; (d) sem segredo no histórico; (e) tamanho medido e justificado; (f) dois builds do mesmo commit comparados.
