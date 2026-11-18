# Limites das lojas e a regra de copycat

O `listing.py` confere tudo isto. Esta referência é o porquê.

## Limites de campo (caracteres, contados como uma pessoa conta)

| App Store | limite | Google Play | limite |
|---|---|---|---|
| name | 30 | title | 30 |
| subtitle | 30 | short_description | 80 |
| promotional_text | 170 | full_description | 4000 |
| keywords | 100 | | |
| description | 4000 | | |
| whats_new | 4000 | | |

Um emoji feito de partes conta como um caractere. Deixe de fora a loja para a qual não vai publicar.

## O que faz uma listagem ser rejeitada

- **O nome do original em qualquer campo** (nome, subtitle, descrição, keywords): outro app/marca na
  sua metadata faz a listagem ser rejeitada e convida um takedown. Descreva o que o **seu** faz.
- **Claims de ranking/preço em campos curtos** ("#1", "best", "free", "50% off"): o Google Play bane no
  título e short description; a Apple rejeita claim que você não comprova.
- **Emoji em campo curto:** o Play rejeita em títulos; revisores da App Store também, com frequência.
- **Keywords desperdiçadas:** palavra já no nome/subtitle, espaço depois de vírgula, repetição, vírgula
  dupla. Use `palavra1,palavra2,palavra3`.

## Apple Guideline 4.1 — Copycats

A revisão da Apple rejeita app que **simplesmente copia** um app popular ou faz **mudança mínima** no
nome ou UI de outro app. Suas **correções** (do replica-entrepreneur) e sua **marca própria** (do
replica-brand) são o que passa na revisão — então deixe-as **visíveis** nos screenshots e nas primeiras
linhas da descrição. Uma cópia reta é rejeitada; uma versão própria que resolve o que os usuários
odiavam, não.

## Sem prova falsa

Nenhum depoimento, contagem de usuários, nota, logo de imprensa inventados. Avaliações do original são
pesquisa, não depoimento seu. Uma seção de prova vazia é melhor que uma falsa — e review falsa é ilegal
(FTC). Beta users reais, com permissão, podem.
