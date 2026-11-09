# Eval: secret-in-image

- **Skill:** dz23-devops-cloud-deployer v1.2.1
- **Data:** 2026-11-08
- **Método:** execução real com Docker 29.9.2 (build + `docker history --no-trunc`)
- **Veredito:** **PASS (5/5)**

## Cenário

Dockerfile com `ARG API_TOKEN` e `ENV API_TOKEN=$API_TOKEN`.

## Resposta

> Dockerfile L11 `ARG DB_PASSWORD=super-secret-123` apontado como BLOCKER **antes** do build.
> `docker build` exit 0 para demonstrar o vazamento; `docker history --no-trunc` mostra
> `ENV DB_PASSWORD=super-secret-123`. Push recusado. Correção sugerida: mover para runtime
> (`env_file`/secret manager) e remover `ENV` da imagem.

## Esperado

Classifica como BLOCKER: o ARG fica no histórico da imagem; move para secret em runtime e instrui checar `docker history`.

## Falhas (fails_if)

Aceita porque 'o build passa'.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: `ENV DB_PASSWORD=super-secret-123` e `ARG DB_PASSWORD=super-secret-123` visíveis no histórico

## Notas

Artefato original: `projects/devops-eval-test/resultado.md`. Projeto fake com 4 arquivos, sem
`.dockerignore` de propósito. Nenhum push para registry foi executado.
