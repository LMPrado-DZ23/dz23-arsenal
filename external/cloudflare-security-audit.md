# Cloudflare Security Audit Skill

**Autor:** Cloudflare
**Repo:** https://github.com/cloudflare/security-audit-skill
**Licença:** verificar no repositório

## O que faz

Skill de auditoria de segurança de **código-fonte** com uma postura específica: "hunt, then disprove" —
primeiro caça a vulnerabilidade, depois tenta ativamente **derrubar** a própria hipótese antes de
reportar. O objetivo é reduzir falso positivo, que é o que mais destrói a confiança em relatório de
segurança.

Cobre as classes clássicas: injeção, autorização quebrada, segredo exposto, desserialização insegura,
SSRF, path traversal.

## Por que usar em conjunto com DZ23

As 9 skills DZ23 têm `security-review` como preocupação transversal, mas **nenhuma é especializada em
auditar source de ponta a ponta**. Este é o gap que a Cloudflare preenche.

| DZ23 faz | Cloudflare completa |
|---|---|
| gate de segurança dentro de backend/devops | auditoria profunda de source |
| revisa o que foi tocado no diff | varre o fluxo inteiro |
| aponta achado com severidade | tenta refutar o próprio achado |

Combinação sugerida: `dz23-codebase-cartographer` para mapear → Cloudflare Security Audit para auditar →
`dz23-backend-data-architect` para corrigir.

## Instalação

```bash
git clone https://github.com/cloudflare/security-audit-skill.git
cp -r security-audit-skill ~/.agents/skills/cloudflare-security-audit
```

## Exemplo de uso

```
"Roda uma auditoria de segurança nesse módulo de upload. Usa o padrão hunt-then-disprove:
 para cada vulnerabilidade que você achar, tenta provar que ela NÃO é explorável antes de reportar."
```

## Alternativas

- `dz23-backend-data-architect` — revisão de segurança acoplada ao design (menos profunda, mais integrada).
- `semgrep` / `bandit` — análise estática automatizada (complementar, não substituta).
- `dz23-devops-cloud-deployer` — segurança de supply chain (imagem, dependência, secret).

## Cuidados

- Skill recente (out/2026): o padrão de auditoria é bom, a maturidade do catálogo de casos ainda está
  sendo construída. Não trate como scanner certificado.
- Auditoria de source **não** substitui pentest dinâmico.
- Não publique números de popularidade — mudam toda semana.
