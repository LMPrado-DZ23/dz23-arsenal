# O que o score mede (e o que não mede)

## Paridade de features é o número que importa

A pergunta: o usuário consegue fazer no clone tudo o que fazia no original? O `parity.py` responde com
um número, pesando por prioridade:

- **must** pesa 3, **should** 2, **could** 1.
- `clone = yes` conta 1, `partial` conta 0.5, `no`/vazio conta 0.
- Linhas `skip` (fora de escopo, com motivo) e **extras** (features suas que o original não tem,
  `original = no`) ficam **fora** do score e são listadas à parte — o número só mede paridade.
- **Must-have não feito = não shippable.** O relatório diz isso explicitamente.

O score por área, do pior para o melhor, mostra onde construir primeiro. A lista do que falta já vem em
ordem de construção (prioridade desc).

## Layout confere estrutura, não cor

O `imgdiff.py` no modo layout vira as duas imagens em **edge maps**, corta numa grade e compara onde as
coisas estão — informação nos mesmos lugares, mesma hierarquia. É o que faz quem troca de app se sentir
em casa. Ele **ignora cor de propósito**: o replica-brand muda toda cor por decisão, então cor não pode
contar contra o clone. Só células com algo dentro (em qualquer das imagens) entram no score, para
margens vazias não inflarem o número. Retina e não-retina comparam bem (ambas escaladas à mesma largura).

`--mode pixel` é comparação exata, para **suas próprias regressões** (clone de hoje vs clone de ontem),
nunca contra o original.

## O que nenhum dos dois vê (passo 3)

Cliques para terminar o core loop, o que acontece em erro, o que é lembrado entre visitas, que e-mails
chegam. Isso é o diff de comportamento, feito à mão. Menos cliques que o original é vitória.

## Não persiga pixel

O visual exato do original é **trade dress** dele e muda antes do lançamento (o rebrand). Perseguir
paridade de pixel com o original é trabalho jogado fora — e juridicamente o lado errado. Paridade é
função e estrutura; aparência é do replica-brand.
