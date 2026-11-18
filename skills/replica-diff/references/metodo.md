# Método — medir a paridade do clone

## Passo 1 — paridade de features

Deixe `replica/features.csv` atual: cada linha com a coluna `clone` em `yes`, `partial` (com nota),
`no` ou `skip` (com motivo). Então:

```bash
python scripts/parity.py replica/features.csv
python scripts/parity.py replica/features.csv --json
python scripts/parity.py replica/features.csv --markdown
python scripts/parity.py replica/features.csv --fail-under 80   # exit 1 se abaixo
```

Saída: o score, must-haves feitos de total, cada área do pior para o melhor, e a lista do que falta em
ordem de construção. Problemas na matriz (prioridade ou clone inválidos) são apontados por linha.

## Passo 2 — diff de layout

Para cada tela-chave, dois screenshots no **mesmo viewport** (1440×900 desktop, 390×844 mobile) e no
**mesmo estado** (mesma forma de dado, mesma aba, logado igual). Os do original vêm de páginas públicas
ou da conta do usuário, em `replica/screens/`; os do clone em `replica/clone-screens/`.

```bash
python scripts/imgdiff.py replica/screens/S07.png replica/clone-screens/S07.png --out replica/diffs/S07.png
python scripts/imgdiff.py a.png b.png --json > replica/diffs/S07.json   # para o parity.py --visual
python scripts/parity.py replica/features.csv --visual replica/diffs/*.json --markdown
```

Com `--visual`, o parity.py mistura os scores de layout: o geral vira 80% features + 20% layout
(features é o que o usuário paga). O imgdiff reporta o score, as regiões que diferem (nas coordenadas
do original, maiores primeiro) e uma diferença de altura se o clone é bem mais longo/curto.

## Passo 3 — diff de comportamento

Percorra cada fluxo nos dois apps à mão e escreva cada diferença como: fluxo, o original faz, o clone
faz, consertar ou manter. Cliques, erros, memória entre visitas, e-mails. Menos cliques é vitória.

## Passo 4 — o relatório

**Grave** `replica/parity.md`: score geral, feature score, layout por tela, o que falta em ordem,
diferenças de comportamento, e o veredito (não shippable / shippable / melhor que o original). Números
honestos. Entregue também as top 5 coisas a construir a seguir.
