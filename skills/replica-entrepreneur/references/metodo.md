# Método — da avaliação ao plano de correção

## Passo 1 — coletar

Mire 100+ avaliações em ≥3 fontes, recentes primeiro. **Crie** `replica/reviews.csv` com as colunas
`source,url,date,rating,text` — o texto copiado **exato**, a URL em toda linha. Leia também as de 3 e
4 estrelas: "amo, mas…" é onde moram as melhores correções. Linha sem URL ou sem texto é descartada
pelo `reviews.py` e contada, nunca adivinhada.

## Passo 2 — ranquear

```bash
python scripts/reviews.py replica/reviews.csv --out replica/feedback.md
```

Como ele pontua: cada avaliação que casa um tema soma um peso. 1 estrela soma 1.0, 5 estrelas 0.2,
sem nota 0.6. Avaliação mais velha que `--months` (18) conta metade. Tema com menos de 3 avaliações,
ou todas de uma fonte, é marcado **thin**. Ele lista também as notas baixas que não casaram tema —
leia à mão, costuma ser o melhor.

## Passo 3 — três listas

De `feedback.md`, escreva três listas ranqueadas. Cada item: o problema em uma linha, quantas
avaliações, quantas fontes, uma ou duas citações linkadas.

1. **O que odeiam** — reclamações sobre coisas que o app faz.
2. **O que falta** — features que pedem pelo nome.
3. **O que fica sem solução** — trabalhos ou grupos inteiros que o app ignora ("não serve para
   times", "inútil para terapeutas"). Isso vira posicionamento.

Thin é listado como thin. Não apresente três comentários raivosos de Reddit como tendência.

## Passo 4 — o plano de correção

Escolha os top 5–8 por **evidência × quão barato conserta**. Para cada: o que construir/mudar,
tamanho (S/M/L), qual skill faz, e a evidência. Adicione cada um como linha em `replica/features.csv`
com `original` = `no`. Reclamação de preço e billing vai para `replica-launch`.

## Passo 5 — o ângulo

Três opções de posicionamento, cada uma ancorada num tema do topo:

```
Para {{quem}} que {{odeia isto no original, em palavras simples}},
{{seu app}} {{faz isto em vez disso}}.
Evidência: {{tema}}, {{n}} avaliações em {{n}} fontes.
```

Recomende um. Ele guia o nome e a voz em `replica-brand` e o hero em `replica-launch`. **Nunca** ponha
o nome do original no nome do seu app, anúncio ou listagem; uma página de comparação factual é questão
jurídica para um advogado do seu país.
