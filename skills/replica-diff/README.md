# replica-diff

Compara um clone contra o original: um score de paridade de **features** da matriz (pesado por
must/should/could) com a lista do que falta em ordem de construção, mais um diff de **layout** por
screenshot que **ignora cor** (para o rebrand não contar contra você). Duas ferramentas Python stdlib.
Paridade aqui é fazer o mesmo trabalho, não parecer igual. Números honestos — 62% é 62%.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| [`SKILL.md`](SKILL.md) | O que paridade significa, método, as ferramentas, veredito |
| [`references/o-que-e-paridade.md`](references/o-que-e-paridade.md) | O que o score mede e o que não mede |
| [`references/metodo.md`](references/metodo.md) | Features → layout → comportamento → relatório |
| [`scripts/parity.py`](scripts/parity.py) | Score de paridade de features da matriz (stdlib) |
| [`scripts/imgdiff.py`](scripts/imgdiff.py) | Diff de layout por screenshot, decoder PNG próprio (stdlib) |
| [`templates/parity.md`](templates/parity.md) | Modelo do relatório de paridade |
| [`examples/`](examples/) | `features-exemplo.csv`, `orig.png`, `clone.png` |
| [`evals/evals.json`](evals/evals.json) | 6 cenários de avaliação |

Rodar: `python scripts/parity.py replica/features.csv` ·
`python scripts/imgdiff.py orig.png clone.png --json`.

## Como usar com as outras skills

- A matriz vem do mapa: `replica-recon`. Construir as lacunas: skills de engenharia DZ23. Testar
  fluxos antes: `dz23-e2e-browser-verifier`. "Melhor que o original": `replica-entrepreneur`.

## Arsenal

Esta skill faz parte do [dz23-arsenal](../../README.md). **Origem:** incorporada de
[`Jakeschincariol/replica-skill`](https://github.com/Jakeschincariol/replica-skill) (`replica-diff`),
licença **MIT** lida no arquivo `LICENSE` da raiz (Copyright 2026 Jake Schincariol). Orientação
internalizada em PT; `parity.py` e `imgdiff.py` entraram funcionais (MIT, stdlib). Ver `metadata` no
[`SKILL.md`](SKILL.md) e o registro em [`dados-design/VENDOR.md`](../../dados-design/VENDOR.md).

Camada **produto-para-clone** (recon → entrepreneur → diff → brand → launch). Instalação e índice:
[`README.md`](../../README.md). Estado de evals: [`ROADMAP.md`](../../ROADMAP.md).
