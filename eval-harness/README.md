# Eval harness — replay determinístico (layer eval-harness/)

Dívida nº 1 do arsenal: os vereditos de eval eram **afirmações de uma vez** (Camada 1,
autoavaliação). Este harness os torna **reproduzíveis** — adaptando o padrão `grader-replay` do
`modern-web-guidance` (Apache-2.0): a resposta registrada é re-graduada por um grader
**determinístico** e o veredito derivado é comparado ao registrado.

## O que o replay prova — e o que NÃO prova

- **PROVA:** reprodutibilidade (mesma entrada → mesmo veredito, mecanicamente) e que o grader
  **discrimina** — a resposta boa dá `PASS`, uma resposta ruim sintética dá `FAIL`. Isso é
  estritamente mais forte que uma asserção única.
- **NÃO PROVA:** juízo independente. A resposta é do próprio autor; o replay a torna reproduzível,
  **não** remove o viés do autor.

## A escada de camadas (honesta)

| Camada | O que é | Estado neste repo |
|---|---|---|
| `1-reproduzivel` | autoavaliação do autor, agora **re-graduável por grader determinístico** | **3 evals** (este harness) |
| `2-adversarial` | releitura adversarial pelo mesmo autor | parcial (alguns registros) |
| `3-independente` | **juiz externo** (outro modelo/pessoa), conjunto de casos separado, evidência reproduzível | **NOT_TESTED** — fora do alcance desta sessão |
| `4-uso-real` | uso em projeto de terceiro, resultado observado | **NOT_TESTED** |

Só evals com rubrica **genuinamente mecânica** entram no replay. Rubrica subjetiva (qualidade de
texto em português) não é graduável de forma determinística e **não** recebe fixture aqui — fingir o
contrário seria o "carimbo" que o verificador reprova.

## Fixtures

Cada `replays/*.json` traz: `skill`, `eval_id`, `camada`, `provenance` (model, environment,
timestamp, method), `fonte_resposta` (o `.md` real em `evals-results/`), `response` (trecho real,
→ `expected_verdict`), `response_negativo` (resposta ruim sintética, → `FAIL`) e `grader`
(`contains`/`not_contains`/`regex`). As 3 atuais são ancoradas em respostas **reais** registradas.

## Verificação no gate

- `replay:executa` (`replay-eval.py`): re-gradua tudo; exige que cada fixture **reproduza** e
  **discrimine**.
- `replay:verifica` (`check-replay.py`): schema, proveniência completa, grader não-vazio,
  cruzamento com o `evals.json` da skill (sem replay para eval inexistente), `fonte_resposta` existe.
- `replay:autoteste` (`check-replay.py --selftest`): controle negativo — 6 mutações têm de reprovar.

## Próximo (Camada 3, quando houver)

Prova independente exige: juiz externo, conjunto de casos separado do autor, registro de
modelo/ambiente/tempo/custo e controle contra viés. O replay é o alicerce reproduzível sobre o qual
a Camada 3 se apoia — não a substitui.
