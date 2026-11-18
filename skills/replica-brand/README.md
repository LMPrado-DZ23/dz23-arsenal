# replica-brand

Nomeia e rebranda um clone para ser o do próprio usuário: candidatos a nome com as checagens de
trademark/domínio/loja/handle a rodar, uma paleta nova conferida para contraste, um brief de logo, um
guia de voz, e uma ferramenta de **sweep** que acha qualquer coisa do original que sobrou no código.
Nada lança sob a identidade do original — esta skill é a linha entre "um clone" e "o seu app".

## Estrutura

| Caminho | Conteúdo |
|---|---|
| [`SKILL.md`](SKILL.md) | Regras inegociáveis, método em 6 passos, a ferramenta de sweep, veredito |
| [`references/checagens-legais.md`](references/checagens-legais.md) | O teste "não confusamente similar" e as checagens (triagem, não liberação jurídica) |
| [`references/metodo.md`](references/metodo.md) | Nome → checagens → paleta → logo → voz → sweep |
| [`scripts/sweep.py`](scripts/sweep.py) | Acha nome/domínio/cor do original no código; exit 1 se achar (stdlib) |
| [`templates/brand.md`](templates/brand.md) · [`templates/brand.json`](templates/brand.json) | Modelo da marca e do config do sweep |
| [`examples/brand-exemplo.json`](examples/brand-exemplo.json) | Config de exemplo |
| [`evals/evals.json`](evals/evals.json) | 6 cenários de avaliação |

Rodar: `python scripts/sweep.py . --config replica/brand.json`.

## Como usar com as outras skills

- O ângulo vem de `replica-entrepreneur`. Contraste/acessibilidade da paleta: `web-design-guidelines`
  ou `dz23-ultimate-pro-max`. Roda **antes** de `replica-launch`.

## Arsenal

Esta skill faz parte do [dz23-arsenal](../../README.md). **Origem:** incorporada de
[`Jakeschincariol/replica-skill`](https://github.com/Jakeschincariol/replica-skill) (`replica-brand`),
licença **MIT** lida no arquivo `LICENSE` da raiz (Copyright 2026 Jake Schincariol). Orientação
internalizada em PT; `sweep.py` entrou funcional (MIT, stdlib). A checagem de contraste do original
dependia da skill `replica-design` (não incorporada — `dz23-ultimate-pro-max` cobre design); foi
**rerotada** para o acervo de acessibilidade do arsenal. Ver `metadata` no [`SKILL.md`](SKILL.md) e o
registro em [`dados-design/VENDOR.md`](../../dados-design/VENDOR.md).

Camada **produto-para-clone** (recon → entrepreneur → diff → brand → launch). Instalação e índice:
[`README.md`](../../README.md). Estado de evals: [`ROADMAP.md`](../../ROADMAP.md).
