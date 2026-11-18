# replica-launch

Escreve o lançamento de um clone: a landing page sobre o ângulo de posicionamento, o preço fixado
contra o preço público do original e as reclamações dos usuários, e a listagem de App Store e Google
Play conferida contra os limites das lojas e as regras anti-cópia. É a última etapa de clonar um app.
Sem prova falsa, sem avaliações como depoimento, nome do original fora da listagem.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| [`SKILL.md`](SKILL.md) | As regras, método em 4 passos, a ferramenta de listing, veredito |
| [`references/metodo.md`](references/metodo.md) | Landing → preço → listagem → plano |
| [`references/lojas.md`](references/lojas.md) | Limites de campo e a Guideline 4.1 (Copycats) da Apple |
| [`scripts/listing.py`](scripts/listing.py) | Lint da listagem contra limites e regras anti-cópia (stdlib) |
| [`templates/landing.md`](templates/landing.md) · [`pricing.md`](templates/pricing.md) · [`launch-plan.md`](templates/launch-plan.md) | Modelos |
| [`examples/listing-exemplo.json`](examples/listing-exemplo.json) | Listagem de exemplo |
| [`evals/evals.json`](evals/evals.json) | 6 cenários de avaliação |

Rodar: `python scripts/listing.py replica/launch/listing.json`.

## Como usar com as outras skills

- Ângulo e evidência de `replica-entrepreneur`; nome/marca de `replica-brand` (roda antes). Contraste:
  `web-design-guidelines`/`dz23-ultimate-pro-max`. Deploy: `dz23-devops-cloud-deployer`.

## Arsenal

Esta skill faz parte do [dz23-arsenal](../../README.md). **Origem:** incorporada de
[`Jakeschincariol/replica-skill`](https://github.com/Jakeschincariol/replica-skill) (`replica-launch`),
licença **MIT** lida no arquivo `LICENSE` da raiz (Copyright 2026 Jake Schincariol). Orientação
internalizada em PT; `listing.py` entrou funcional (MIT, stdlib). O contraste da landing dependia de
`replica-design` (não incorporada — `dz23-ultimate-pro-max` cobre); foi **rerotado** para o acervo de
acessibilidade. Ver `metadata` no [`SKILL.md`](SKILL.md) e [`dados-design/VENDOR.md`](../../dados-design/VENDOR.md).

Última skill da camada **produto-para-clone** (recon → entrepreneur → diff → brand → launch).
Instalação e índice: [`README.md`](../../README.md). Estado de evals: [`ROADMAP.md`](../../ROADMAP.md).
