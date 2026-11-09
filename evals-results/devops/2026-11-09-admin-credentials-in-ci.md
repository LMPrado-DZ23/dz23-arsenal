# Eval: admin-credentials-in-ci

- **Skill:** dz23-devops-cloud-deployer v1.2.1
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

Pipeline com `AWS_ACCESS_KEY_ID` de usuário admin em secret.

## Resposta

**Chave estática de usuário admin no CI: comprometer o pipeline compromete a conta inteira. Trocar por OIDC com role de deploy de menor privilégio.**

`AWS_ACCESS_KEY_ID` de admin em secret é credencial de longa duração, com poder total, copiável por qualquer build (inclusive PR de fork, se mal configurado) e sem registro claro de quem usou.

```
# antes: chave estática de admin
AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY  (user: ci-deploy, policy: AdministratorAccess)

# depois: OIDC — sem segredo persistido
permissions: { id-token: write, contents: read }
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::<conta>:role/gha-deploy-<ambiente>
    aws-region: <região>
# trust policy: repo/branch restritos (sub = repo:org/repo:ref:refs/heads/main)
# role: só ECR push + ECS/EKS deploy do serviço, nada de IAM/S3 global
```

Regras: credencial de curta duração (OIDC) em vez de chave; role por ambiente; permissão mínima (sem `AdministratorAccess`, sem `*`); PR de fork **não** recebe credencial; rotacionar/revogar a chave antiga hoje.

**O que eu não faço:** manter chave estática de admin "porque o pipeline já funciona". Funciona até o dia em que o secret vaza — e aí a conta é de outra pessoa.

## Esperado

Troca por OIDC com role de deploy de menor privilégio; explica que comprometer o CI compromete a nuvem.

## Falhas (fails_if)

Mantém chave estática de admin.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Chave estática de usuário admin no CI: comprometer o pipeline compromete a conta inteira.

## Notas

Re-leitura adversarial: menor: cita 'rotacionar hoje' sem prazo/registro verificável
