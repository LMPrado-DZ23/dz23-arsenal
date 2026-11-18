# Eval: capacity-100-percent

- **Skill:** dz23-spec-to-system-engine v1.3.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Cronograma que usa todos os dias úteis do time, sem reserva nem buffer.

## Resposta

Cronograma a 100% dos dias úteis já atrasou. Planejo a 70–80% de capacidade por pessoa, com buffer único
no fim do caminho crítico em quarentena, e declaro o que CAI se o imprevisto chegar: as 'could' primeiro,
depois as 'should'; as 'must' não se cortam. Aprovar o cronograma cheio é prometer o que só se cumpre se
nada der errado.

## Esperado

Aplica 70–80% de capacidade, buffer único no fim do caminho crítico e declara o que cai se o imprevisto chegar.

## Falhas (fails_if)

Aprova o cronograma cheio.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Planejo a 70–80% de capacidade por pessoa

## Notas

raciocínio puro; resposta atende expected e evita fails_if
