# prune-tests

Poda todo teste que não guarda comportamento. Diagnóstico por dependência — *este teste depende do
comportamento intencional?* — e remoção das três famílias que não dependem: o passado (afirma que
código removido continua removido), o nada (nenhuma mudança no código o faz falhar) e a implementação
(muda junto com o código mesmo sem mudança de comportamento).

Use antes de confiar numa suíte, ao herdar testes alheios, ou junto da `untangle-codebase` num
refactor profundo. Não é aumentar cobertura nem caçar flaky — é remover teste que não tem razão
própria de existir, preservando toda cobertura de comportamento real.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| [`SKILL.md`](SKILL.md) | As regras: três famílias, como podar, regras inegociáveis, estados de evidência, veredito |
| [`references/taxonomia-do-que-podar.md`](references/taxonomia-do-que-podar.md) | As três famílias (passado, nada, implementação) + duplicata, com exemplos |
| [`references/method.md`](references/method.md) | O passe completo: baseline, mapa, poda, verificação |
| [`references/verification.md`](references/verification.md) | Como provar que nenhum comportamento perdeu sua rede |
| [`references/git-as-evidence.md`](references/git-as-evidence.md) | Cada poda como commit rastreável à razão |
| [`templates/prune-log.md`](templates/prune-log.md) | Registro de poda (teste → família → ação → rede → commit) |
| [`evals/evals.json`](evals/evals.json) | 6 cenários de avaliação |

## Como usar com as outras skills

- Num refactor profundo que reorganiza dependências: `untangle-codebase` (escopo maior, mesma filosofia).
- Para criar os testes de comportamento que faltam: `tdd`.
- Verificar o comportamento preservado ponta a ponta: `dz23-e2e-browser-verifier`.

## Arsenal

Esta skill faz parte do [dz23-arsenal](../../README.md). **Origem:** incorporada de
[`caldoai/skills`](https://github.com/caldoai/skills) (`prune-tests`), licença **MIT** lida no arquivo
`LICENSE` da raiz do repositório (Copyright 2026 Maze). O conteúdo foi internalizado e adaptado ao rito
do arsenal (eval executável, referências, validador e gate), não copiado byte a byte — ver `metadata`
no [`SKILL.md`](SKILL.md) e o registro em [`dados-design/VENDOR.md`](../../dados-design/VENDOR.md).

Instalação, verificação e índice geral: [`README.md`](../../README.md) do repositório. Estado de evals
e o que é `NOT_TESTED`: [`ROADMAP.md`](../../ROADMAP.md).
