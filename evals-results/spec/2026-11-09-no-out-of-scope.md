# Eval: no-out-of-scope

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Spec com prazo de 3 semanas e nenhuma lista do que fica de fora.

## Resposta

**BLOCKER: prazo de 3 semanas sem fora de escopo declarado não é plano, é intenção.**

Qualquer escopo cabe em 3 semanas se ninguém definir o que não cabe. A lista de fora de escopo é o que protege o prazo.

Fora de escopo proposto (com motivo):

| Fica fora | Motivo |
|---|---|
| integração com o ERP legado | depende de terceiro sem SLA; risco de calendário |
| migração de dados históricos | volume exige janela própria; não cabe no prazo |
| relatórios exportáveis | valor secundário; entra em v2 |
| i18n | um idioma no lançamento |
| app mobile | escopo separado, time separado |

Regra: cada item fora precisa de **motivo** e **destino** (v2, outro time, decidir depois). "Fora" sem destino volta como surpresa na semana 3.

**O que eu não entrego:** plano com prazo e sem essa lista. Sem ela o compromisso é impossível de cumprir e impossível de provar que falhou.

## Esperado

Classifica como BLOCKER em entrega com prazo; produz lista explícita de fora de escopo com motivo.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: BLOCKER: prazo de 3 semanas sem fora de escopo declarado não é plano, é intenção.

## Notas

Produziu lista de fora de escopo com motivo e destino (v2).
