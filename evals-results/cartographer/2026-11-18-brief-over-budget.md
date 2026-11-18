# Eval: brief-over-budget

- **Skill:** dz23-codebase-cartographer v1.2.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Context brief com 600 linhas e trechos colados de código.

## Resposta

600 linhas com código colado é despejo, não brief. Reescrevo com ponteiros (arquivo:linha) e orçamento declarado (<=120 linhas). O brief aponta onde olhar, não cola o que já está no repo.

## Esperado

Reescreve com ponteiros e orçamento declarado (≤120 linhas), cortando despejo de código.

## Falhas (fails_if)

Entrega o brief gigante.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: orçamento declarado

## Notas

raciocínio puro; resposta atende expected e evita fails_if
