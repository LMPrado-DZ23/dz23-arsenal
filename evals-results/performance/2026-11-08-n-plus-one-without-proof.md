# Eval: n-plus-one-without-proof

- **Skill:** dz23-performance-scalability-engine v1.3.0
- **Data:** 2026-11-08
- **Método:** autoavaliação + reauditoria (mesmo autor)
- **Veredito:** **PASS**

## Cenário

'Troquei o loop por include, resolvido.'

## Resposta

> Exige contador de queries por request com o critério "o número de queries não cresce com o
> número de linhas" (`limit=50` e `limit=200` com a mesma contagem) e `EXPLAIN` antes/depois.

## Esperado

Exige contador de queries por request (não cresce com linhas) ou EXPLAIN antes/depois.

## Falhas (fails_if)

Aceita a afirmação sem medição.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum bloqueante (D-3/D-4 registrados: 'presumo a listagem citada' e threshold sem rótulo
de proposta)
- Trecho literal: "Critério de aceite: o número de queries não cresce com o número de linhas"

## Notas

Artefato: `projects/eval-performance/response-2.txt`.
