# Eval: secret-in-log

- **Skill:** dz23-backend-data-architect v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

log.info({ headers, body }) em rota de login.

## Resposta

**`log.info({ headers, body })` em rota de login grava `Authorization`, senha e token em claro. Mascarar no dashboard é tarde — o dado já está no coletor, nos índices e nos backups.**

```
// errado
log.info({ headers: req.headers, body: req.body });
// certo: allowlist do que vai para o log
log.info({
  path: req.path, method: req.method, status,
  userId: req.user?.id, requestId: req.id, durationMs,
  // nunca: headers, body, query inteiros
});
// se precisar de header específico, redigir na origem
redact: { paths: ['req.headers.authorization', 'req.body.password', '*.token'], censor: '[REDACTED]' }
```

Regras: redaction **na origem** (logger/serializer), não no painel; PII não vai para o coletor de terceiro; `Authorization`, `Cookie`, `password`, `secret`, `token` são mascarados por padrão, não por escolha; varredura no diff (`rg "log\.(info|debug).*body"`) no PR.

**O que eu não faço:** sugerir mascarar no dashboard. Log de aplicação é fonte, painel é leitura — mascarar na leitura deixa o vazamento nos dados e em quem tem acesso ao coletor.

## Esperado

Identifica vazamento de Authorization/senha; mascara na origem, sem PII no coletor; varredura no diff.

## Falhas (fails_if)

Sugere mascarar no dashboard de log depois.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: `log.info({ headers, body })` em rota de login grava `Authorization`, senha e token em claro.

## Notas

Re-leitura adversarial: nenhum
