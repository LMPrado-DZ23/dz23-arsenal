# Eval: matrix-stale

- **Skill:** dz23-spec-to-system-engine v1.3.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Matriz preenchida só no início; fatias entregues depois não atualizaram estado.

## Resposta

Matriz preenchida só no início é rastreabilidade falsa. Exijo atualização na MESMA entrega da fatia (a
linha REQ→fatia→critério→evidência→estado no mesmo PR) e reconciliação por fatia. Divergência vira
NOT_TESTED e bloqueia o 'pronto'. Não existe 'atualizo no fim'.

## Esperado

Exige atualização na mesma entrega e reconciliação por fatia; matriz divergente é rastreabilidade falsa.

## Falhas (fails_if)

Diz que a matriz 'será atualizada no fim'.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: atualização na MESMA entrega da fatia

## Notas

raciocínio puro; resposta atende expected e evita fails_if
