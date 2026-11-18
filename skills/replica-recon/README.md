# replica-recon

Engenharia reversa **black-box** de um app em um mapa de recon: inventário de telas, fluxos, lista de
componentes, modelo de dados inferido e matriz de features — de páginas públicas, screenshots,
listagem de loja, docs de ajuda e a conta do próprio usuário. É a primeira etapa de "clonar um app":
refaz o que o app **faz** e como o usuário se move, clean-room, nunca o que o app **possui**.

Não é engenharia reversa de binário (isso é `dz23-reverse-engineer-anything`) nem leitura de
código-fonte alheio — é recon de produto por fontes públicas, com regras de clean-room inegociáveis.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| [`SKILL.md`](SKILL.md) | Regras de clean-room, método em 9 passos, entregáveis, veredito |
| [`references/clean-room.md`](references/clean-room.md) | O que pode / não pode; termos de uso; por que importa |
| [`references/metodo.md`](references/metodo.md) | Os 9 passos em detalhe |
| [`references/fontes.md`](references/fontes.md) | Taxonomia de fontes públicas, em ordem de valor |
| [`templates/recon-map.md`](templates/recon-map.md) | Modelo do `replica/recon.md` |
| [`templates/features.csv`](templates/features.csv) | Modelo da matriz de features |
| [`evals/evals.json`](evals/evals.json) | 6 cenários de avaliação |

## Como usar com as outras skills

- Alvo **binário/firmware**, não produto: `dz23-reverse-engineer-anything` (Ghidra), não esta.
- Planejar stack/schema/API do mapa: `dz23-spec-to-system-engine` + `dz23-backend-data-architect`.
- O que os usuários do app odeiam (o clone corrige): `replica-entrepreneur`.
- Pontuar paridade do clone: `replica-diff`.

## Arsenal

Esta skill faz parte do [dz23-arsenal](../../README.md). **Origem:** incorporada de
[`Jakeschincariol/replica-skill`](https://github.com/Jakeschincariol/replica-skill) (`replica-recon`),
licença **MIT** lida no arquivo `LICENSE` da raiz (Copyright 2026 Jake Schincariol). Internalizada e
adaptada ao rito do arsenal (eval executável, referências, validador e gate), não copiada byte a byte —
ver `metadata` no [`SKILL.md`](SKILL.md) e o registro em
[`dados-design/VENDOR.md`](../../dados-design/VENDOR.md).

Primeira skill da **camada produto-para-clone** (recon → entrepreneur → diff → brand → launch), que
complementa as skills de engenharia DZ23 sem duplicá-las. Instalação e índice:
[`README.md`](../../README.md). Estado de evals: [`ROADMAP.md`](../../ROADMAP.md).
