# Avaliações (evals) — dz23-arsenal

Consolidação honesta do estado de avaliação. Harness de replay: [`eval-harness/README.md`](eval-harness/README.md).
Estado por eval: `python scripts/run-evals.py --audit`.

## Os números (os dois são verdadeiros)

- **Ledger DZ23:** 144 cenários nas 10 skills DZ23. **Registrados: 73/144 (50,7%)** — todos
  **Camada 1 (autoavaliação, viés do autor)**, não prova independente.
- **Total que o comando soma:** 192 avaliações (144 DZ23 + 48 das 8 incorporadas). As 48 são
  verificadas pela **prova do consultor/script no gate**, não pelo registro de eval → 73/192 (38%).

## A escada de camadas

| Camada | O que é | Estado |
|---|---|---|
| 1 — autoavaliação | mesma sessão, viés do autor | 73/144 registrados |
| 1-reproduzível | re-graduável por grader determinístico (replay) | **8 evals** em 6 skills |
| 2 — adversarial | releitura adversarial do mesmo autor | parcial (20/45) |
| 3 — independente | **juiz externo**, conjunto separado, controle de viés | **NOT_TESTED** |
| 4 — projeto real | uso em projeto de terceiro | 1 tarefa (no próprio repo) |
| 5 — conferência mecânica | scripts dentro do gate | ativa |

## Replay determinístico (dívida nº 1, primeiro passo)

O [`eval-harness/`](eval-harness/README.md) adapta o `grader-replay` do modern-web-guidance: a
resposta registrada é re-graduada por um grader mecânico que **também tem de reprovar** uma resposta
ruim sintética (prova de discriminação, não carimbo). Isso torna 8 vereditos **reproduzíveis** —
estritamente mais forte que uma asserção única, mas **não** é juízo independente.

Verificado no gate: `replay:executa` (reproduz + discrimina), `replay:verifica` (schema,
proveniência, cruzamento com `evals.json`), `replay:autoteste` (6 mutações reprovam).

## O que NÃO está provado

- ~71 de 144 evals nunca executados; 40 bloqueados por infra (Docker/Postgres/Ghidra/browser/hardware).
- **Camada 3 (juiz externo): NOT_TESTED** — exige outro modelo/pessoa, conjunto de casos separado,
  registro de modelo/ambiente/tempo/custo e controle contra viés.
- Uso em produto de outra pessoa: 0.

Rubrica subjetiva (qualidade de texto) **não** vira replay determinístico — fingir grader para ela
seria o "carimbo" que o verificador reprova. Ver [`ROADMAP.md`](ROADMAP.md) e [`LIMITATIONS.md`](LIMITATIONS.md).
