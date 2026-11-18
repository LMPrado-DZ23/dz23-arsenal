---
name: replica-entrepreneur
version: 1.0.0
description: >
  Pesquisa o app que está sendo clonado e lê o que os usuários reais dizem em avaliações públicas
  (App Store, Google Play, G2, Capterra, Trustpilot, Reddit, Hacker News, o board de feature-request
  dele), ranqueia o que odeiam, o que falta e o que fica sem solução, e vira um plano de correção para
  o clone e um ângulo de posicionamento para vender. Toda citação é real, verbatim e com link. Use ao
  pedir "o que as pessoas odeiam no X", "ler as avaliações", "como faço o meu melhor", "achar a lacuna",
  "como posiciono isto", "deixar vendável", ou depois de replica-diff. Uma cópia reta de um app não tem
  razão de existir; esta skill acha a razão: o que os usuários do original odeiam, nas palavras deles.
user-invocable: true
argument-hint: "<app sendo clonado>"
metadata:
  origin: Jakeschincariol/replica-skill (skill replica-entrepreneur), MIT lida no arquivo LICENSE da raiz (Copyright 2026 Jake Schincariol)
  license: MIT
  source-file: skills/replica-entrepreneur/SKILL.md
  method: internalizado em PT; o script reviews.py entrou funcional (MIT) com um endurecimento contra CSV malformado
---

# replica-entrepreneur

Uma cópia reta de um app não tem razão de existir. Esta skill acha a razão: o que os usuários do
original odeiam, nas palavras deles, e conserta no seu. Ferramenta: `python scripts/reviews.py`.

## Regras inegociáveis

- **Nunca fabricar.** Nenhuma avaliação, citação, nota, contagem, usuário ou fonte inventada. Se uma
  fonte não dá para alcançar, diga e siga. Se há 14 avaliações, diga 14.
- **Toda citação é verbatim e com link.** Copiada exatamente da página, com a URL da avaliação ou
  thread. O `reviews.py` descarta qualquer linha sem link.
- **Ler, não raspar.** Leia as páginas de avaliação como uma pessoa, no navegador, e copie as linhas
  para a planilha. Sem bibliotecas de scraping contra lojas/sites cujos termos proíbem. Feeds e APIs
  públicas oficiais, dentro dos termos, podem: RSS de avaliações da Apple, API Algolia do Hacker News,
  API oficial do Reddit sob os termos dela.
- **Nunca review falsa.** Nem a favor do seu app, nem contra o deles. É ilegal nos EUA (regra da FTC
  de 2024) e em muitos outros lugares.
- **Avaliadores não são seus depoimentos.** As palavras deles são pesquisa; não vão na sua landing.

## Como fazer (o detalhe mora nas referências)

Método completo em `references/metodo.md`; fontes e seus termos em `references/fontes-e-termos.md`.

1. **Colete** 100+ avaliações em pelo menos 3 fontes, recentes primeiro. **Crie** `replica/reviews.csv` (`source,url,date,rating,text`, texto copiado exato). Leia também as de 3 e 4
   estrelas — "amo, mas…" é onde moram as melhores correções.
2. **Ranqueie** e **grave** `replica/feedback.md`: `python scripts/reviews.py replica/reviews.csv --out replica/feedback.md`. Ele separa
   em temas (`scripts/themes.json`, editável por categoria), pesa notas baixas e recentes, marca temas
   com menos de 3 avaliações ou fonte única como **thin**, e lista as notas baixas sem tema — leia
   essa última à mão, costuma ser o melhor.
3. **Três listas** (de `feedback.md`): o que **odeiam**, o que **falta**, o que fica **sem solução**
   (vira posicionamento). Thin é marcado como thin; não apresente três comentários de Reddit como
   tendência.
4. **Plano de correção:** top 5–8 por evidência × quão barato conserta. Para cada, **grave** uma linha em `replica/features.csv` com `original` = `no`. Reclamação de preço vai para replica-launch.
5. **O ângulo:** 3 opções de posicionamento, cada uma ancorada num tema do topo, com a evidência
   (tema, nº de avaliações, nº de fontes). Recomende um. Nunca ponha o nome do original no seu nome,
   anúncio ou listagem.

## A ferramenta

`scripts/reviews.py` (stdlib, só reorganiza o que você dá — não escreve avaliação, não parafraseia;
toda citação impressa é substring de uma linha que você forneceu, com o link dela). Entrada mínima:
`source,url,date,rating,text`; linha sem URL ou sem texto é descartada e contada, nunca adivinhada.
Exemplo em `examples/reviews-exemplo.csv`. Temas em `scripts/themes.json`.

## Entregáveis

**Crie** `replica/reviews.csv`, `replica/feedback.md` e `replica/fixes.md` (as três listas + plano + ângulo), e novas linhas a **gravar** em `features.csv`, com um resumo que **declara o tamanho da amostra**. Próximo: replica-brand.

## Estados de evidência

| Estado | Critério |
|---|---|
| PASS | ≥3 fontes, amostra declarada, cada tema com citações verbatim+link, thin marcado |
| PARTIAL | coletou mas abaixo de 30 avaliações (direção, não ranking) ou faltam fontes |
| NOT_TESTED | listas escritas sem o CSV de evidência por trás (citação sem link) |

## Veredito

Pronto quando: o CSV existe com link em toda linha; o ranking saiu do `reviews.py`, não da memória;
toda citação é verbatim e linkada; thin está marcado; o tamanho da amostra está declarado; o ângulo
cita a evidência. Caso contrário, PARTIAL com o que falta.

## Roteamento com outras skills

- Mapear o produto antes de pesquisar: `replica-recon`.
- Transformar o ângulo em nome e marca: `replica-brand`.
- Preço e billing do lançamento: `replica-launch`.
- Cada correção escolhida vira trabalho de engenharia nas skills DZ23 (backend, ultimate-pro-max, …).
