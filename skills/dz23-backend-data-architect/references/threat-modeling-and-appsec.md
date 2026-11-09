# Modelagem de ameaças e AppSec

Segurança de aplicação começa **antes** do código: com um modelo de ameaças. O resto — scan, lint, pentest —
verifica o que o modelo previu. Sem modelo, você corrige o que o scanner achou, não o que o atacante faria.

## 1. Threat model em 6 passos (45 minutos, não 3 dias)

1. **Desenhe o fluxo de dados.** Quais entidades entram, onde são armazenadas, para onde vão. Uma página.
2. **Marque as fronteiras de confiança.** Onde o dado passa de "controlado por mim" para "controlado pelo
   atacante": request HTTP, upload, webhook, fila, integração de terceiro, job agendado.
3. **Aplique STRIDE por elemento**, não por aplicação inteira.
4. **Ranqueie** por impacto × probabilidade. Só os 5 primeiros viram controle obrigatório.
5. **Defina o controle** e **onde ele é testado**. Controle sem teste é intenção.
6. **Registre** em `adr/ADR-NNN-threat-model.md` e **reveja quando o fluxo mudar** — modelo velho é pior que
   nenhum, porque dá falsa segurança.

## 2. STRIDE — o que perguntar em cada fronteira

| Ameaça | Pergunta objetiva | Controle típico | Teste |
|---|---|---|---|
| **S**poofing | Quem pode se passar por outro usuário/serviço? | authN forte, verificação de assinatura, mTLS | login com credencial inválida; webhook sem assinatura |
| **T**ampering | O dado pode ser alterado em trânsito ou em repouso? | TLS, assinatura/HMAC, integridade no banco | payload alterado é rejeitado? |
| **R**epudiation | Dá para negar que fez a ação? | audit log imutável com ator, antes/depois, timestamp | log existe para ação crítica? |
| **I**nformation disclosure | Quem pode ler o que não deveria? | authz por recurso, cifra, redaction de log | IDOR: `GET /orders/<id de outro tenant>` |
| **D**enial of service | O que derruba com custo baixo? | rate limit, timeout, limite de payload, fila | 100 req/s na rota cara |
| **E**levation of privilege | Como virar admin/outro tenant? | authz server-side, negar por padrão | usuário comum chamando rota admin |

Regra: **negar por padrão**. Rota nova nasce fechada e abre com justificativa explícita.

## 3. OWASP Top 10 → controle verificável

| Risco | Controle mínimo | Como provar |
|---|---|---|
| A01 Broken Access Control | authz por recurso no servidor, tenant explícito | teste de IDOR e de troca de tenant |
| A02 Cryptographic Failures | TLS obrigatório, hash forte (argon2/bcrypt), sem MD5/SHA1 para senha | inspeção + teste de senha |
| A03 Injection | query parametrizada, ORM sem string concatenada, validação de entrada | teste com payload de injeção |
| A04 Insecure Design | threat model documentado | existe o ADR? |
| A05 Security Misconfiguration | CORS restrito, headers, debug off, sem default admin | checklist de config por ambiente |
| A06 Vulnerable Components | scan de dependência no CI (trivy/`npm audit`/`pip-audit`) | saída do scan sem CRITICAL/HIGH |
| A07 Auth Failures | lockout/rate limit no login, MFA onde cabe, sessão com rotação | teste de brute force |
| A08 Integrity Failures | verificação de assinatura em webhook/upload/update | payload sem assinatura é rejeitado |
| A09 Logging Failures | log de evento de segurança sem segredo/PII | inspeção do log |
| A10 SSRF | allowlist de destino, bloquear IP interno/link-local | URL para `169.254.169.254` falha |

**ASVS:** para SaaS que trata dado de cliente, mire **L2**. L1 é o mínimo (login, sessão, validação);
L3 (criptografia avançada, hardware) só se contrato/regulação exigir.

## 4. Segredos, dependências e upload

**Segredos**
- Nenhum segredo em código, log, teste ou histórico do git. Se vazou no commit, **rotacione** — remover do
  histórico não desfaz o vazamento.
- Detecção: `gitleaks detect --no-banner` e `trivy fs --scanners secret`.
- Variável de ambiente é o mínimo; ideal é secret manager com rotação e escopo por serviço.

**Dependências**
- Scan no CI, bloqueando `CRITICAL` e `HIGH` com correção disponível.
- Pin por versão exata + lockfile commitado. Atualização é rotina, não evento.

**Upload**
- Nunca confie em `Content-Type` nem em extensão: valide **magic bytes**.
- Renomeie o arquivo (não use o nome do cliente), grave fora do webroot, sirva por rota autenticada.
- Limite tamanho e quantidade; processamento de mídia em worker isolado.

## 5. Hardening mínimo antes de expor

```text
CORS: origin allowlist explícita; nunca * com credencial
Headers: HSTS, X-Content-Type-Options, X-Frame-Options/frame-ancestors, Referrer-Policy, CSP
Rate limit: por IP e por usuário, nas rotas caras (login, busca, export, IA)
Payload: limite de tamanho no proxy e no app
Timeout: toda dependência externa com timeout e limite de tentativa
Debug: desligado em produção; erro genérico para o cliente, detalhe só no log
Sessão: cookie HttpOnly + Secure + SameSite; rotação no login; invalidação no logout
```

## 6. Gates de AppSec (bloqueiam merge)

| Gate | BLOCKER quando | Evidência exigida |
|---|---|---|
| Authz por recurso | rota sem verificação de dono/tenant | teste de IDOR vermelho antes, verde depois |
| Injeção | query concatenada com entrada do usuário | teste com payload |
| Segredo | credencial em código/log | `gitleaks` limpo |
| Dependência | CRITICAL/HIGH com fix disponível | saída do scan |
| Webhook | sem verificação de assinatura | payload não assinado rejeitado |
| Upload | confia em `Content-Type`/extensão | magic byte validado |
| SSRF | URL de destino vem do usuário sem allowlist | teste com IP interno |

## 7. O que este documento não faz

- Não substitui pentest profissional nem auditoria independente.
- Não cobre segurança de infraestrutura (rede, IAM, cluster) — isso é
  `dz23-devops-cloud-deployer` (`references/supply-chain-security.md`).
- Não cobre auditoria profunda de source de terceiro — para isso existe
  [`external/cloudflare-security-audit.md`](../../external/cloudflare-security-audit.md), que usa a postura
  "hunt, then disprove".
