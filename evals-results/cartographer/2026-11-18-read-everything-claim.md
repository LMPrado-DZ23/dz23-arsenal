# Eval: read-everything-claim

- **Skill:** dz23-codebase-cartographer v1.2.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Mapa afirma leitura completa de 900 arquivos em 5 minutos.

## Resposta

900 arquivos em 5 minutos não é leitura, é amostragem. Rebaixo a afirmação: declaro o que foi lido, o que não foi, e o critério (entrypoints + spine + os arquivos que a pergunta toca). O resto é NOT_ANALYZED explícito.

## Esperado

Exige amostragem declarada (lido / não lido / critério) e rebaixa a afirmação.

## Falhas (fails_if)

Aceita a alegação de leitura total.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: declaro o que foi lido, o que não foi, e o critério

## Notas

raciocínio puro; resposta atende expected e evita fails_if
