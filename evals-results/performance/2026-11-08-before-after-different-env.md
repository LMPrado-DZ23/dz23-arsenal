# Eval: before-after-different-env

- **Skill:** dz23-performance-scalability-engine v1.3.0
- **Data:** 2026-11-08
- **Método:** autoavaliação + reauditoria (mesmo autor)
- **Veredito:** **PASS**

## Cenário

Antes medido em produção, depois em laptop com dado de 10 registros.

## Resposta

> Declara a comparação inválida e exige mesmo build, mesmo dado, mesmo ambiente, mesma carga e
> cache declarado; `GANHO: INVALIDADO`.

## Esperado

Recusa a comparação; exige mesmo build, dado, ambiente, carga e cache declarado.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: "Essa comparação é inválida — não existe ganho a declarar."

## Notas

Artefato: `projects/eval-performance/response-3.txt`.
