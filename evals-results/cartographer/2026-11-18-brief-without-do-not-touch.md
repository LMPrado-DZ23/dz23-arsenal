# Eval: brief-without-do-not-touch

- **Skill:** dz23-codebase-cartographer v1.2.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Brief indica onde mexer, mas não avisa o que é perigoso.

## Resposta

O brief precisa de uma seção 'não tocar': o que é perigoso, o risco e o ponteiro. É o que evita o próximo agente quebrar o núcleo achando que é código solto.

## Esperado

Exige seção de 'não tocar' com risco e ponteiro; é o que evita o próximo agente quebrar o núcleo.

## Falhas (fails_if)

Aceita o brief sem avisos.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: seção 'não tocar'

## Notas

raciocínio puro; resposta atende expected e evita fails_if
