# Eval: latest-tag-in-prod

- **Skill:** dz23-devops-cloud-deployer v1.2.1
- **Data:** 2026-11-08
- **Método:** execução real com Docker (inspeção de tag e política de pin)
- **Veredito:** **PASS (5/5)**

## Cenário

Manifesto com `image: registry/app:latest` no ambiente de produção.

## Resposta

> `FROM node:latest` identificado como BLOCKER; exigência de pin por digest na imagem base e
> na final; `latest` recusado em produção; alternativa declarada (tag imutável + digest).

## Esperado

Exige digest (`image@sha256:…`), explica que a tag move e o rollout pode publicar outra coisa.

## Falhas (fails_if)

Aceita tag ou sugere `:v1` mutável.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: `FROM node:latest` → bloqueado; pin por digest exigido

## Notas

Artefato original: `projects/devops-eval-test/resultado.md`.
