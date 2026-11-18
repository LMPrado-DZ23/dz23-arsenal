# Eval: spike-without-question

- **Skill:** dz23-spec-to-system-engine v1.3.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

'Spike de 5 dias para explorar a integração'.

## Resposta

'Spike de 5 dias para explorar a integração' é exploração aberta, não spike. Reescrevo: PERGUNTA
específica ("o webhook entrega idempotency-key?"), PRAZO curto de 1 dia, e SAÍDA esperada (resposta +
evidência + impacto no plano). Sem pergunta + prazo + saída, 'explorar' não fecha decisão.

## Esperado

Exige pergunta específica, prazo curto e saída esperada (resposta + evidência + impacto no plano).

## Falhas (fails_if)

Aceita exploração aberta como spike.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: PERGUNTA\n específica

## Notas

raciocínio puro; resposta atende expected e evita fails_if
