---
name: replica-diff
version: 1.0.0
description: >
  Compara um clone contra o app original: um score de paridade de features a partir da matriz (pesado
  por must/should/could) com a lista do que falta em ordem de construção, mais um diff de layout por
  screenshot que ignora cor — para que o rebrand não conte contra você. Duas ferramentas Python stdlib.
  Use ao pedir "quão perto está meu clone", "compara com o original", "o que falta", "parity check",
  "diff das telas", "está pronto", ou depois de replica-test. Paridade aqui é fazer o mesmo trabalho,
  não parecer igual: o score de features é o número que importa, o de layout confere estrutura (ignora
  cor de propósito). Dá números honestos — um clone a 62% está a 62%.
user-invocable: true
argument-hint: "<matriz de features>"
metadata:
  origin: Jakeschincariol/replica-skill (skill replica-diff), MIT lida no arquivo LICENSE da raiz (Copyright 2026 Jake Schincariol)
  license: MIT
  source-file: skills/replica-diff/SKILL.md
  method: internalizado em PT; os scripts parity.py e imgdiff.py entraram funcionais (MIT, stdlib)
---

# replica-diff

Duas ferramentas stdlib, sem instalar nada: `scripts/parity.py` (paridade de features + o que falta)
e `scripts/imgdiff.py` (diff de layout por screenshot, ignorando cor).

## O que paridade significa aqui

**Paridade é fazer o mesmo trabalho, não parecer igual.** O score de **features** é o número que
importa: o usuário consegue fazer tudo o que fazia no original. O de **layout** confere estrutura (a
informação está nos mesmos lugares, na mesma hierarquia) — é o que faz quem troca se sentir em casa.
Ele **ignora cor de propósito**, porque o replica-brand muda toda cor por decisão. Não persiga
paridade de pixel: o visual exato do original é trade dress dele e muda antes do lançamento.

## Como fazer (o detalhe mora nas referências)

Método completo em `references/metodo.md`; o que o score mede em `references/o-que-e-paridade.md`.

1. **Paridade de features:** mantenha atual a matriz a **gerar** no recon, `replica/features.csv` (coluna `clone` em cada linha:
   `yes`/`partial` com nota/`no`/`skip` com motivo) e rode
   **gere** o score: `python scripts/parity.py replica/features.csv`. Ele pesa must 3, should 2, could 1, conta partial
   meio, deixa `skip` e extras de fora, e imprime o score, must-haves feitos de total, cada área do
   pior para o melhor, e a lista do que falta em ordem de construção. Must-have não feito = não
   shippable, e ele diz isso.
2. **Diff de layout:** para cada tela-chave, dois screenshots no **mesmo viewport** (1440×900 desktop,
   390×844 mobile) e **mesmo estado**. Rode
   `python scripts/imgdiff.py replica/screens/S07.png replica/clone-screens/S07.png --out replica/diffs/S07.png`.
   Modo layout (default) vira edge map, corta em grade e compara onde as coisas estão (score: 90+
   match, 75+ perto, 50+ parcial, abaixo diferente). `--mode pixel` é só para suas próprias regressões.
3. **Diff de comportamento:** percorra cada fluxo nos dois apps e compare o que o score não vê: cliques
   para terminar o core loop, o que acontece em erro, o que é lembrado entre visitas, que e-mails
   chegam. Menos cliques que o original é vitória.
4. **O relatório:** **grave** `replica/parity.md` (score geral, features, layout por tela, o que falta
   em ordem, diferenças de comportamento) com o veredito.

## As ferramentas

- `scripts/parity.py` (stdlib): lê a matriz e dá o score; `--json`, `--markdown`, `--fail-under N`.
  Exemplo: `examples/features-exemplo.csv`.
- `scripts/imgdiff.py` (stdlib, decoder PNG próprio): lê PNG 8/16 bit (grey/RGB/paleta/alpha), recusa
  interlaçado com mensagem. Exemplo: `examples/orig.png` e `examples/clone.png`.

## Veredito

- **não shippable:** qualquer must-have faltando, ou qualquer bug S1 aberto.
- **shippable:** todos os must-haves feitos, score de features 80+, sem S1/S2 aberto.
- **melhor que o original:** shippable + as correções do replica-entrepreneur. É o objetivo — uma
  cópia reta não tem razão de existir.

Dê números honestos. Um clone a 62% está a 62%.

## Estados de evidência

| Estado | Critério |
|---|---|
| PASS | parity.md gerado do parity.py, veredito justificado, números honestos |
| PARTIAL | matriz incompleta (linhas `clone` em branco) ou telas sem diff |
| NOT_TESTED | veredito dado sem rodar parity.py (score de memória) |

## Roteamento com outras skills

- Preencher a matriz vem do mapa: `replica-recon`. Construir as lacunas: as skills de engenharia DZ23.
- Testar os fluxos antes do diff: `dz23-e2e-browser-verifier`.
- Se a paridade está lá, buscar o "melhor que o original": `replica-entrepreneur`.
