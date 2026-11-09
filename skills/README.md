# Skills DZ23 — índice

Nove skills de engenharia, cada uma com uma responsabilidade clara. Todas seguem o mesmo padrão:
`SKILL.md` com as regras, `references/` para conhecimento sob demanda, `templates/` para artefatos,
`scripts/` quando há código executável e `evals/` com cenários de avaliação.

## Tabela comparativa

| Skill | Versão | Categoria | Complexidade | Refs | Templates | Scripts | Evals |
|---|---|---|---|---|---|---|---|
| [autonomous-improvement-ultimate](dz23-autonomous-improvement-ultimate/) | 2.1 | Orquestração | advanced | 5 | 2 | 0 | 12 |
| [backend-data-architect](dz23-backend-data-architect/) | 1.1.0 | Backend/DB | advanced | 10 | 2 | 1 | 12 |
| [codebase-cartographer](dz23-codebase-cartographer/) | 1.1.0 | Exploração | intermediate | 15 | 7 | 3 | 15 |
| [devops-cloud-deployer](dz23-devops-cloud-deployer/) | 1.2.1 | DevOps | advanced | 17 | 7 | 3 | 15 |
| [e2e-browser-verifier](dz23-e2e-browser-verifier/) | 1.1.0 | Testes | intermediate | 10 | 6 | 1 | 15 |
| [performance-scalability-engine](dz23-performance-scalability-engine/) | 1.3.0 | Performance | advanced | 10 | 6 | 4 | 16 |
| [reverse-engineer-anything](dz23-reverse-engineer-anything/) | 1.1.1 | Exploração/RE | advanced | 12 | 4 | 3 | 15 |
| [spec-to-system-engine](dz23-spec-to-system-engine/) | 1.2.0 | Orquestração | intermediate | 17 | 11 | 3 | 15 |
| [ultimate-pro-max](dz23-ultimate-pro-max/) | 2.2.0 | Frontend | advanced | 9 | 0 | 1 | 0 |

## Por onde começar

| Se você quer… | Use |
|---|---|
| entender um código que não escreveu | `codebase-cartographer` |
| transformar ideia em plano executável | `spec-to-system-engine` |
| construir API/schema/migração | `backend-data-architect` |
| construir ou revisar interface | `ultimate-pro-max` |
| colocar em produção com segurança | `devops-cloud-deployer` |
| provar que a UI funciona | `e2e-browser-verifier` |
| descobrir por que está lento | `performance-scalability-engine` |
| analisar um binário ou firmware | `reverse-engineer-anything` |
| rodar tudo num ciclo autônomo | `autonomous-improvement-ultimate` |

## Regras comuns a todas

1. **Evidência ou silêncio** — `PASS` exige comando e saída; o resto é `NOT_TESTED`.
2. **Baseline antes de mudança** — vale para performance, codebase e refactor.
3. **Escopo declarado** — o que está fora do escopo é tão importante quanto o que está dentro.
4. **Sem segundo orquestrador** — cada skill sabe qual outra chamar, e não reimplementa.
5. **Autorização antes de ação destrutiva** — produção, custo, exclusão: perguntar antes.

## O que as skills NÃO fazem

- Não substituem teste em harness real. Eval declarado ≠ eval executado.
- Não adivinham stack: se o projeto não foi inspecionado, a resposta é `NOT_TESTED`.
- Não cobrem, por si, auditoria de segurança de source (ver `external/cloudflare-security-audit.md`).
- Não instalam ferramentas sem autorização explícita.
