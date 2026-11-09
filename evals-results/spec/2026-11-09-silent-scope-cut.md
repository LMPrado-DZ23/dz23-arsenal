# Eval: silent-scope-cut

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Plano novo sem o requisito de exportação que o cliente pediu; nada registrado.

## Resposta

**Requisito que o cliente pediu não pode desaparecer do plano sem registro — isso é corte silencioso.**

Ausência de menção é o pior estado possível: o cliente acha que está sendo feito, o time sabe que não está, e ninguém decidiu.

Estado correto do requisito:

```
REQ-07 (exportação): CUT
motivo: depende de relatório consolidado que não entra nesta fase
aprovador: <nome do dono do produto>
comunicação: cliente avisado em <data>, entra em v2
```

Quatro estados possíveis, e todo requisito precisa de um: `IN` (no escopo), `CUT` (fora, com motivo e aprovador), `DEFERRED` (fase seguinte, com data), `BLOCKED` (dependência externa declarada).

**O que eu não faço:** aceitar a ausência sem registro, nem "colocar de volta sem avisar" — as duas coisas quebram a confiança do mesmo jeito.

Me diz quem aprovou o corte e eu registro; se ninguém aprovou, o requisito volta para o escopo ou entra como `DEFERRED` com data.

## Esperado

Exige estado CUT com motivo e aprovador, e comunicação ao solicitante; nunca remover em silêncio.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Requisito que o cliente pediu não pode desaparecer do plano sem registro — isso é corte silencioso.

## Notas

Exigiu estado CUT com motivo, aprovador e comunicação; listou os 4 estados possíveis.
