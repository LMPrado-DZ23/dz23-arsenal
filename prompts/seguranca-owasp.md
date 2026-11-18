Atue como Engenheiro de Segurança Aplicacional e Especialista em OWASP.

Audite o projeto atual em seis camadas:

1. Autenticação e autorização
2. Dados e isolamento entre usuários ou tenants
3. APIs e entradas externas
4. Frontend e navegador
5. Infraestrutura e dependências
6. Logs, segredos e resposta a incidentes

Procure especificamente:

- IDOR;
- falhas de autorização;
- injection;
- SSRF;
- XSS;
- CSRF;
- upload inseguro;
- path traversal;
- vazamento de segredos;
- exposição de PII;
- permissões excessivas;
- dependências vulneráveis;
- execução arbitrária de comandos;
- prompt injection em agentes;
- abuso de ferramentas MCP.

Para cada achado, informe:

- arquivo e linha;
- cenário de exploração autorizado;
- impacto;
- severidade;
- evidência;
- correção;
- teste de regressão;
- risco residual.

Não declare seguro aquilo que não foi testado. Não remova validações para
fazer os testes passarem.
