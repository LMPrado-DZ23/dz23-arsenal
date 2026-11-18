# Skills DZ23 — índice

10 skills de engenharia, cada uma com uma responsabilidade clara. Todas seguem o mesmo padrão:
`SKILL.md` com as regras, `references/` para conhecimento sob demanda, `templates/` para artefatos,
`scripts/` quando há código executável e `evals/` com cenários de avaliação.

## Tabela comparativa

| Skill | Versão | Categoria | Complexidade | Refs | Templates | Scripts | Evals |
|---|---|---|---|---|---|---|---|
| [autonomous-improvement-ultimate](dz23-autonomous-improvement-ultimate/) | 2.1.6 | Orquestração | advanced | 5 | 2 | 3 | 13 |
| [backend-data-architect](dz23-backend-data-architect/) | 1.1.1 | Backend/DB | advanced | 10 | 2 | 3 | 12 |
| [codebase-cartographer](dz23-codebase-cartographer/) | 1.1.1 | Exploração | intermediate | 15 | 7 | 5 | 15 |
| [devops-cloud-deployer](dz23-devops-cloud-deployer/) | 1.2.3 | DevOps | advanced | 17 | 3 | 5 | 16 |
| [e2e-browser-verifier](dz23-e2e-browser-verifier/) | 1.1.2 | QA/E2E | advanced | 10 | 3 | 3 | 16 |
| [performance-scalability-engine](dz23-performance-scalability-engine/) | 1.3.3 | Performance | advanced | 10 | 6 | 6 | 16 |
| [postgres-prod-preflight](dz23-postgres-prod-preflight/) | 1.1.2 | Banco/Segurança | intermediate | 5 | 1 | 4 | 13 |
| [reverse-engineer-anything](dz23-reverse-engineer-anything/) | 1.1.4 | Eng. reversa | advanced | 12 | 4 | 5 | 15 |
| [spec-to-system-engine](dz23-spec-to-system-engine/) | 1.2.1 | Especificação | advanced | 17 | 9 | 5 | 15 |
| [ultimate-pro-max](dz23-ultimate-pro-max/) | 2.2.4 | UI/UX | advanced | 9 | 0 | 3 | 13 |

Totais do disco: **110 referências** e **144 cenários de eval** declarados.

> Esta tabela é gerada -- `python scripts/gera-indice-skills.py` -- e conferida pelo
> `check-numbers.py` a cada gate. Versões, contagens de refs/templates/scripts/evals vêm do
> filesystem. Categoria e complexidade são julgamento humano e ficam em
> `scripts/gera-indice-skills.py`; editar a tabela aqui não dura um commit.
