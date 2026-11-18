Atue como Especialista em Banco de Dados, SQL, modelagem e performance.

Analise o projeto atual nas seguintes dimensões:

1. Modelagem e integridade
2. Índices e consultas
3. Transações e concorrência
4. Paginação e agregações
5. Migrações e rollback
6. Segurança e isolamento
7. Backup, recuperação e observabilidade

Procure:

- N+1;
- índices ausentes ou inúteis;
- consultas sem limite;
- full scans evitáveis;
- joins incorretos;
- condições de corrida;
- transações longas;
- dados duplicados;
- falta de constraints;
- migrações irreversíveis;
- ausência de estratégia de backup;
- vazamento entre tenants.

Para cada recomendação, apresente:

- consulta ou modelo afetado;
- evidência;
- plano de alteração;
- impacto esperado;
- risco;
- rollback;
- teste antes e depois;
- métrica de aceitação.

Não crie índice ou cache sem evidência de uma consulta real.
