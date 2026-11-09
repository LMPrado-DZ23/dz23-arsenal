# Eval: circular-dependency

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

SL-02 depende de SL-03, que depende de SL-02.

## Resposta

**Ciclo detectado: SL-02 → SL-03 → SL-02. O plano atual é impossível, não é "questão de ordem".**

Dependência circular não se resolve ordenando melhor — não existe ordem que satisfaça as duas. Também não se resolve com paralelismo: paralelizar um ciclo produz dois trabalhos bloqueados em vez de um.

Três saídas, em ordem de preferência:

1. **Fundir as fatias** — se SL-02 e SL-03 só fazem sentido juntas, elas são uma fatia. `SL-02+03: contrato de pedido e persistência` com um critério de aceite único.
2. **Quebrar por contrato** — extrair a interface que ambas precisam (schema do evento, DTO) e implementá-la primeiro. Aí as duas passam a depender do contrato, não uma da outra.
3. **Inverter com stub** — uma implementa contra stub da outra, com contrato escrito e teste de contrato no CI.

**O que eu não faço:** "resolver com paralelismo" ou ignorar o ciclo deixando as duas em andamento. Ciclo em plano é sinal de fronteira mal desenhada — fundir ou contratar, não empurrar.

## Esperado

Detecta o ciclo, quebra a dependência ou funde as fatias; explica por que o plano atual é impossível.

## Falhas (fails_if)

Não percebe ou 'resolve' com paralelismo.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Ciclo detectado: SL-02 → SL-03 → SL-02. O plano atual é impossível

## Notas

Recusou 'resolver com paralelismo'; propôs fundir, contratar ou stub.

## Auditoria externa

**Selecionado para revisão independente** — ver [`../AUDIT-SAMPLE.md`](../_audit-notes/AUDIT-SAMPLE.md). O veredito acima é do autor (autoavaliação) e **não** homologa a skill; divergência do auditor externo prevalece.
