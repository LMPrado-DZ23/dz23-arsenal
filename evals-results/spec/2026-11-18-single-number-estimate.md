# Eval: single-number-estimate

- **Skill:** dz23-spec-to-system-engine v1.3.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Cronograma com '3 dias' para cada uma das 8 fatias.

## Resposta

'3 dias' por fatia não é estimativa, é um palpite repetido. Troco cada um por intervalo com premissa:
p.ex. "SL-03: 2–4 dias, supondo o schema de pagamento já aprovado e o endpoint de terceiro no ar".
Depois somo pelo CAMINHO CRÍTICO, não pelo total. O buffer vai em quarentena no fim do caminho crítico
(um bloco único, ~20–30%), não diluído. Nunca 'multiplico por 2': é o mesmo palpite inflado.

## Esperado

Troca por intervalo com premissas, identifica caminho crítico e quarentena de buffer.

## Falhas (fails_if)

Aceita o cronograma ou só 'multiplica por 2'.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Troco cada um por intervalo com premissa

## Notas

raciocínio puro; resposta atende expected e evita fails_if
