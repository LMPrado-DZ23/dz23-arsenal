# Eval: orm-leaked

- **Skill:** dz23-backend-data-architect v1.1.2
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Resposta do endpoint é a linha do ORM com senha_hash e internal_notes.

## Resposta

A resposta não pode ser a linha crua do ORM: vaza senha_hash e internal_notes. Crio um DTO/serializador com allowlist de saída (só os campos que o cliente vê) e um teste que falha se a resposta contiver 'senha_hash'. Remover 'na mão' em cada handler é frágil -- o próximo campo sensível vaza no handler que esqueceram.

## Esperado

Exige serializador/DTO com allowlist de saída e teste que garante ausência de campo sensível.

## Falhas (fails_if)

Retorna o modelo cru ou remove campos 'na mão' em cada handler.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: DTO/serializador com allowlist de saída

## Notas

raciocínio puro; resposta atende expected e evita fails_if
