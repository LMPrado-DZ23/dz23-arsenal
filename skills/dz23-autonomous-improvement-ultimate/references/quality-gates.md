# Matriz de Quality Gates

| Área | Evidência mínima para PASS | Casos de risco |
|---|---|---|
| Git/baseline | status, HEAD, diff inicial | alterações não commitadas |
| Lint/typecheck | comando + exit code + log | supressões artificiais |
| Unit/regression | testes específicos + suite | reproduzir falha anterior |
| Integration/API | endpoints reais em ambiente autorizado | timeout, retries, idempotência |
| E2E | fluxo completo + resultado | auth, erro de rede, estados vazios |
| Build/smoke | artefato compilado + execução | env, assets, rotas |
| Auth/security | testes de RBAC, IDOR, validação | escalada, sessão, XSS/CSRF/SSRF |
| Multitenancy | teste cruzado Tenant A/B | API, DB, cache, storage, jobs |
| Banco | migração testada + integridade | índices, rollback, concorrência |
| UI | screenshots/inspeção real | 320/375/768/1024/1440, dark mode se aplicável |
| A11y | axe + inspeção manual teclado | foco, labels, contraste, reduced motion |
| Performance | medições comparáveis | LCP, INP, CLS, regressões |
| Operação | health/logs e plano de rollback | TLS, backup, restore, deploy |

Use estados `PASS`, `FAIL`, `PARTIAL`, `NOT_RUN`, `BLOCKED` por gate. Só use PASS após execução ou inspeção observável; anote ferramenta, comando, resultado, ambiente e localização da evidência. Gate não aplicável deve ser justificado como `N/A`, nunca contado como PASS.

## Componentes e fluxos
- Botão: ação real, hover/focus/disabled/loading, teclado.
- Formulário: labels, validação, erro próximo, feedback, submit duplicado.
- Menu: rotas, item ativo, foco, Esc, mobile.
- Modal: foco inicial, contenção, fechamento, retorno do foco.
- Tabela: dados reais, filtros, paginação, vazio, loading, erro.
- API: autorização por recurso, schema, erros, retries e isolamento.

## Comparação com baseline
Anote falhas preexistentes separadamente das introduzidas; não declare regressão resolvida sem testar o fluxo que a expôs. Uma suíte verde com cobertura insuficiente não prova ausência de bugs.
