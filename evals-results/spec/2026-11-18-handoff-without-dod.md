# Eval: handoff-without-dod

- **Skill:** dz23-spec-to-system-engine v1.3.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Handoff diz apenas 'implementar exportação'.

## Resposta

'Implementar exportação' não é handoff, é 'vira-se'. Devolvo pedindo: FATIA declarada, REQs, CONTRATO,
CRITÉRIO DE ACEITE, DoD (teste do caminho feliz + vazio + permissão negada) e o que está FORA DE ESCOPO.
Sem isso, cada pessoa implementa uma exportação diferente.

## Esperado

Exige fatia, REQs, contrato, critério de aceite, DoD e o que está fora — senão é 'vira-se'.

## Falhas (fails_if)

Aceita o handoff vago.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: o que está FORA DE ESCOPO

## Notas

raciocínio puro; resposta atende expected e evita fails_if
