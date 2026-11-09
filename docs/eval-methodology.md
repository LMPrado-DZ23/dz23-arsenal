# Metodologia de evals

## O que um eval prova

Um eval testa **um** comportamento. Passar significa que a resposta satisfez o `expected` e não caiu no
`fails_if` — nada além disso.

## O que um eval NÃO prova

| Não prova | Exemplo real deste repositório |
|---|---|
| Que a resposta está livre de violar **outras** regras da skill | `risky-integration-last` passou no eval e escreveu *"spike (2 dias)"* — violando a regra "estimativa é intervalo com premissas" que está no mesmo `SKILL.md` (L55) |
| Que a skill funciona em projeto real | nenhum eval roda contra produto de verdade |
| Que 128/128 executados = cobertura de comportamento | eval é amostra de regra, não matriz exaustiva |

## Camadas de verificação

| Camada | O que prova | Custo | Quem faz |
|---|---|---|---|
| 1. Autoavaliação | a resposta atende o `expected` literal | ~20 min/eval | autor |
| 2. Re-leitura adversarial | o autor relê como auditor e procura defeito em regra vizinha | +5 min/eval | autor |
| 3. Auditoria externa (amostra) | um terceiro valida método e veredito | ~20 min/amostra | outro agente |
| 4. Uso em projeto real | funciona no mundo real | semanas | usuário |

Cada camada é evidência mais forte que a anterior. **Nenhuma substitui a próxima.**

## Estado atual (2026-11-09)

| Camada | Cobertura |
|---|---|
| 1 — autoavaliação | **45/128 (35,2%)** |
| 2 — re-leitura adversarial | **20/45** (aplicada só na Rodada 3) |
| 3 — auditoria externa | **11/16 com veredito aproveitável** · 5 `NOT_AUDITED` (laudo julgou cenário parafraseado) |
| 4 — projeto real | **0** |

## Camada 5 — conferência do método

A auditoria de 2026-11-09 deu 16 PASS — mas julgou **cenários parafraseados**. Em 5 deles a paráfrase removeu
a armadilha, e o `fails_if` ficou inalcançável. Só um script comparando o `input` citado com o do pacote
(`scripts/check-audit-inputs.py`) revelou isso.

Conclusão: a camada que confere a auditoria **também erra** — a primeira conferência reportou "2 de 16" porque
olhou os dois casos mais evidentes. Virou 16 de 16 quando deixou de ser olho e virou script.

| Camada | Quem | Erro típico que ela corrige |
|---|---|---|
| 1 autoavaliação | autor | viés de confirmação |
| 2 re-leitura adversarial | autor | regra vizinha violada |
| 3 auditoria externa | terceiro | veredito do autor errado |
| 4 uso em projeto real | usuário | tudo acima, na prática |
| 5 conferência do método | script | **a auditoria não julgou o que disse julgar** |

## Por que não perseguir 128/128

Duas razões medidas:

1. **40 dos 128 exigem infraestrutura que não existe aqui** — Postgres, Playwright com app rodando, Ghidra,
   hardware. Simular esses evals produziria `PASS` falso. Ver
   [`evals-results/_audit-notes/BLOCKED-TRACK-B.md`](../evals-results/_audit-notes/BLOCKED-TRACK-B.md).
2. **13 dos 45 críticos estão nesse grupo**: 100% de críticos não é atingível neste ambiente. O teto real é
   **32/45 (71%)**.

Cobertura por número bruto incentiva eval trivial; cobertura por criticidade incentiva eval que dói.

## Regras de honestidade embutidas na ferramenta

- `record-eval.py` **recusa** `PASS` sem `--response` e sem `--evidence` (trecho literal).
- `PASS` sem trecho literal aparece como defeito em `check-eval-results.py`.
- `BLOCKED` exige `--blocked-by` (a dependência nomeada).
- `NOT_RECOVERED` é aceito para execução antiga sem artefato — e nunca é reconstruído de memória.
- O registro grava `## Falhas (fails_if)`, para que o auditor julgue sem abrir o `evals.json`.

## O erro que este documento existe para evitar

Na Rodada 2, a autoavaliação deu 15 PASS em 15. A releitura adversarial do mesmo autor rebaixou **1 para
PARTIAL** e achou 3 defeitos menores. Na Rodada 1 da skill de performance, 3/3 PASS viraram 5 defeitos na
reauditoria.

Conclusão: **quem produz não homologa.** Uma segunda leitura do mesmo autor reduz o erro; não o elimina.

## Recomendação de sequência

1. ✅ 100% do que é executável entre os críticos (Rodada 3 → 32/45)
2. Auditoria externa dos 16 selecionados (Rodada 4)
3. 1 projeto real usando 3 skills, com evidência de uso (Rodada 5)
4. Track B quando houver Postgres/Playwright (Rodada 6)
