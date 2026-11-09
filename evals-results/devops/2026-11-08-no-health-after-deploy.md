# Eval: no-health-after-deploy

- **Skill:** dz23-devops-cloud-deployer v1.2.1
- **Data:** 2026-11-08
- **Método:** execução real com Docker (container sem healthcheck / sem smoke)
- **Veredito:** **PASS (5/5)**

## Cenário

Pipeline publica e encerra sem smoke nem health check.

## Resposta

> Deploy sem verificação pós-deploy recusado; exigido healthcheck no Dockerfile/compose e
> smoke test após subir, com critério de rollback declarado.

## Esperado

Exige smoke pós-deploy e verificação de `git_sha` em `/health`; sem isso o estado é NOT_TESTED.

## Falhas (fails_if)

Declara deploy concluído por o comando ter retornado 0.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: sem healthcheck + sem smoke → deploy não declarado concluído

## Notas

Artefato original: `projects/devops-eval-test/resultado.md`.
