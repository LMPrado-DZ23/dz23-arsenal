# replica-entrepreneur

Pesquisa o app sendo clonado e lê o que os usuários reais dizem em avaliações públicas (App Store,
Google Play, G2, Capterra, Trustpilot, Reddit, Hacker News, o board dele), ranqueia o que odeiam, o
que falta e o que fica sem solução, e vira um plano de correção para o clone e um ângulo de
posicionamento. **Toda citação é real, verbatim e com link.** Uma cópia reta de um app não tem razão
de existir; esta skill acha a razão.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| [`SKILL.md`](SKILL.md) | Regras inegociáveis (ética), método em 5 passos, a ferramenta, veredito |
| [`references/metodo.md`](references/metodo.md) | Coletar → ranquear → três listas → plano → ângulo |
| [`references/fontes-e-termos.md`](references/fontes-e-termos.md) | Fontes públicas, feeds/APIs oficiais, e a lei (FTC, fabricação) |
| [`scripts/reviews.py`](scripts/reviews.py) | Ranqueia avaliações em temas (stdlib; só reorganiza, nunca escreve) |
| [`scripts/themes.json`](scripts/themes.json) | Taxonomia de temas (editável por categoria) |
| [`examples/reviews-exemplo.csv`](examples/reviews-exemplo.csv) | CSV de exemplo (dados fictícios) |
| [`templates/fixes.md`](templates/fixes.md) | Modelo das três listas + plano + ângulo |
| [`evals/evals.json`](evals/evals.json) | 6 cenários de avaliação |

Rodar: `python scripts/reviews.py replica/reviews.csv --out replica/feedback.md`.

## Como usar com as outras skills

- Mapear o produto antes: `replica-recon`. · Nome e marca do ângulo: `replica-brand`. · Preço/billing:
  `replica-launch`. Cada correção escolhida vira trabalho de engenharia nas skills DZ23.

## Arsenal

Esta skill faz parte do [dz23-arsenal](../../README.md). **Origem:** incorporada de
[`Jakeschincariol/replica-skill`](https://github.com/Jakeschincariol/replica-skill)
(`replica-entrepreneur`), licença **MIT** lida no arquivo `LICENSE` da raiz (Copyright 2026 Jake
Schincariol). Orientação internalizada em PT; o `reviews.py` entrou funcional (MIT) com um
endurecimento contra CSV malformado (não estourar traceback). Ver `metadata` no [`SKILL.md`](SKILL.md)
e o registro em [`dados-design/VENDOR.md`](../../dados-design/VENDOR.md).

Camada **produto-para-clone** (recon → entrepreneur → diff → brand → launch). Instalação e índice:
[`README.md`](../../README.md). Estado de evals: [`ROADMAP.md`](../../ROADMAP.md).
