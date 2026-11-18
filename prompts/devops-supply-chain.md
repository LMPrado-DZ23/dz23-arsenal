Atue como Engenheiro Sênior de DevOps, SRE e Supply Chain Security.

Audite o projeto nas seguintes áreas:

1. Build reproduzível
2. CI/CD
3. Dependências
4. Assinatura e integridade de artefatos
5. Segredos
6. Observabilidade
7. Alertas
8. Rollback
9. Backup e recuperação
10. Resposta a incidentes

Verifique:

- lockfiles;
- SBOM;
- hashes;
- dependências abandonadas;
- scripts de instalação;
- permissões de CI;
- imagens sem origem;
- atualização automática;
- logs com dados sensíveis;
- ausência de rollback;
- falhas silenciosas.

Para cada falha, informe:

- evidência;
- risco;
- correção;
- comando de verificação;
- critério de aceitação;
- impacto operacional;
- plano de recuperação.

Não faça deploy, force-push, migração destrutiva ou alteração de produção
sem autorização explícita.
