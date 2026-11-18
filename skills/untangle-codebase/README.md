# untangle-codebase

Desembaraça um codebase inteiro num passe só, para que agentes leiam menos por mudança, quebrem
menos sem perceber e depurem mais rápido. Diagnóstico estrutural por uma pergunta única — *estas
peças deveriam mudar juntas?* — seguido de redesenho dos primeiros princípios: uma correção atrás
de vários problemas, não caso por caso, preservando o comportamento intencional.

Use quando um repo está difícil de mudar, espalhado por camadas, cheio de wrappers e flags
pontuais, ou antes de delegar trabalho pesado a agentes que gastam tokens procurando onde mexer.
Não é revisão de estilo nem caçada de bug isolado — é reorganização de dependência e coesão.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| [`SKILL.md`](SKILL.md) | As regras: fluxo em 5 passos, regras inegociáveis, estados de evidência, veredito |
| [`references/method.md`](references/method.md) | O método completo, passo a passo |
| [`references/defect-taxonomy.md`](references/defect-taxonomy.md) | As quatro famílias de defeito (elo oculto, elo desnecessário, sobra, caso especial) |
| [`references/git-as-evidence.md`](references/git-as-evidence.md) | Cada fix como commit rastreável ao problema que fechou |
| [`references/verification.md`](references/verification.md) | Como provar que o comportamento intencional não mudou |
| [`templates/decision-log.md`](templates/decision-log.md) | Registro de decisão (problemas + a correção que resolve vários) |
| [`evals/evals.json`](evals/evals.json) | 6 cenários de avaliação |

## Como usar com as outras skills

- Mapear o grafo de dependências antes de decidir por onde começar: `dz23-codebase-cartographer`.
- Podar apenas testes, sem tocar em produção: `prune-tests` (escopo menor, mesma filosofia).
- Registrar decisões estruturais como ADR: `dz23-spec-to-system-engine`.

## Arsenal

Esta skill faz parte do [dz23-arsenal](../../README.md). **Origem:** incorporada de
[`caldoai/skills`](https://github.com/caldoai/skills) (`untangle-codebase`), licença **MIT** lida no
arquivo `LICENSE` da raiz do repositório (Copyright 2026 Maze). O conteúdo foi internalizado e
adaptado ao rito do arsenal (eval executável, referências, validador e gate), não copiado byte a
byte — ver `metadata` no [`SKILL.md`](SKILL.md) e o registro em
[`dados-design/VENDOR.md`](../../dados-design/VENDOR.md).

Instalação, verificação e índice geral: [`README.md`](../../README.md) do repositório. Estado de
evals e o que é `NOT_TESTED`: [`ROADMAP.md`](../../ROADMAP.md).
