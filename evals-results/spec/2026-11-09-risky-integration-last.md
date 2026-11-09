# Eval: risky-integration-last

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Plano deixa a integração externa desconhecida para a última fatia.

## Resposta

**Inverter a ordem: a integração desconhecida tem que ser a primeira fatia, não a última.**

Deixar o risco no fim transforma descoberta técnica em crise de cronograma. Se a integração não funciona como o plano supõe, você descobre na semana 3 — quando não há tempo de mudar de estratégia, só de pedir desculpa.

Reordenação:

```
SL-01: spike da integração (2 dias) → pergunta específica: o gateway aceita
       idempotência por header? qual o rate limit real? o sandbox espelha produção?
SL-02: contrato + mock a partir da resposta do spike
SL-03+: fatias de valor com o risco já resolvido
última: polimento, não descoberta
```

Critério do spike: **resposta + evidência** (documento, captura de request, saída de sandbox), não "explorei bastante". Se o spike mostrar que a integração é inviável, o plano muda na semana 1 — que é exatamente o ponto.

**O que eu não aceito:** manter o risco no fim, nem trocar por "vamos torcer". Risco não se agenda para depois; ele se compra cedo, com juros menores.

## Esperado

Reordena: a primeira fatia ataca a integração mais arriscada (descobrir caro cedo), ou exige spike antes.

## Falhas (fails_if)

Mantém o risco no fim do cronograma.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Inverter a ordem: a integração desconhecida tem que ser a primeira fatia, não a última.

## Notas

Reordenou com spike na SL-01 e exigiu evidência (não 'explorei bastante').

## Auditoria externa

**Selecionado para revisão independente** — ver [`../AUDIT-SAMPLE.md`](../AUDIT-SAMPLE.md). O veredito acima é do autor (autoavaliação) e **não** homologa a skill; divergência do auditor externo prevalece.
