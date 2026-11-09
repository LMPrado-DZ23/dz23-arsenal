# Eval: requirement-without-criterion

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Pedido: 'fazer a tela ser mais rápida e intuitiva'.

## Resposta

**Isso não é requisito — é adjetivo. Não entra no plano executável.**

`mais rápida` e `mais intuitiva` não têm critério verificável, então não têm como ser aceitos nem rejeitados. Sem isso o item fica **fora** do plano de execução, registrado como `NOT_READY`.

Reescrevo em critério observável:

| Adjetivo | Critério proposto | Como medir |
|---|---|---|
| mais rápida | p95 da listagem ≤ 300 ms com 1.000 registros | medição de APM ou `curl -w`, antes/depois |
| mais intuitiva | concluir o fluxo principal em ≤ 3 cliques, sem erro em teste com 5 usuários | teste de usabilidade ou métrica de funil |

Sem o número, o critério de aceite fica "achismo com carimbo" — e todo mundo discorda no fim.

**O que eu não vou fazer:** quebrar "mais rápida e intuitiva" em tarefas (`otimizar bundle`, `melhorar layout`). Decompor requisito indefinido só distribui a indefinição entre várias pessoas.

Me confirma os limiares (300 ms? 3 cliques?) e eu devolvo a fatia com DoD.

## Esperado

Reescreve em critério observável (p95 ≤ X ms; concluir em ≤ 3 cliques) e declara que sem isso o item fica fora do plano executável.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Isso não é requisito — é adjetivo. Não entra no plano executável.

## Notas

Reescreveu em p95 ≤ 300 ms e ≤ 3 cliques, e declarou o item NOT_READY.
