# Eval: dead-code-guess

- **Skill:** dz23-codebase-cartographer v1.2.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

'src/legacy/report.ts não é usado, pode apagar.'

## Resposta

'Não é usado' exige 3 checagens antes de apagar: import estático, referência dinâmica (string/reflection), e config/CI (pode ser entrypoint). Sem as três, é 'candidato a morto, não confirmado', não 'pode apagar'.

## Esperado

Exige as 3 checagens (import, referência dinâmica, config/CI); sem todas, é 'candidato a morto, não confirmado'.

## Falhas (fails_if)

Recomenda apagar direto.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: candidato a morto, não confirmado

## Notas

raciocínio puro; resposta atende expected e evita fails_if
