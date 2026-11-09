# Changelog — dz23-autonomous-improvement-ultimate

## [2.1.3] — 2026-11-09

### Corrigido
- `evals/evals.json`: os casos não tinham `title`, exigido pelo `evals.schema.json` do arsenal (25 casos em 2 skills). Título derivado do id — mecânico, sem inventar conteúdo.

## [2.1.2] — 2026-11-09

### Corrigido
- **Evals fora do domínio da skill**: `tailwind3` e `tailwind4` testavam regra de UI numa skill de
  orquestração. Foram para `dz23-ultimate-pro-max` (que tem a reference de stack) e a regra não existia aqui —
  o `run-evals.py --check` acusou cobertura de 1/5 termos.
- **`streaming-chat`** também era de domínio de UI: movido para `dz23-ultimate-pro-max`.
- No lugar, entraram três cenários de orquestração: `checkpoint-ausente`, `escopo-inflado` e
  `delegacao-sem-skill`. Total permanece 12.

### Adicionado
- Regra no `SKILL.md`: **falha repetida exige mudança de estratégia diagnóstica** — três tentativas com a
  mesma hipótese produzem a mesma falha; na quarta, mudar o instrumento e preservar as evidências anteriores.

## [2.1.1] — 2026-11-09

### Corrigido
- `evals/evals.json` estava no **schema antigo** (`prompt` + `expectations[]`), enquanto as outras 8 skills do
  arsenal usam `input` / `expected` / `fails_if`. Consequência: o `check-structure.py` acusava **36 problemas**
  e qualquer harness que lesse os evals só desta skill quebrava.
- Os 12 casos foram migrados preservando o conteúdo: `prompt` → `input`, `expectations[0]` → `expected`, e
  cada caso ganhou um `fails_if` explícito (o comportamento que reprova), que antes não existia.

### Nota
Padronizar não é cosmético: sem `fails_if`, o eval descreve o que se espera mas não o que constitui falha — e
ficava impossível reprovar objetivamente.

## [2.1.0] — 2026-11-08

Versão atual. Este changelog foi criado retroativamente para fechar uma inconsistência: a skill era a única
do arsenal **sem** `VERSION` e **sem** `CHANGELOG.md`, o que quebrava empacotamento e a comparação
`zip × instalado` (a versão saía como `?`).

### Conteúdo
- loop autônomo verificável: auditoria → causa raiz → implementação → teste → revisão adversarial →
  correção → reteste
- matriz de requisitos com critério verificável, evidência e estado
- checkpoint retomável a cada rodada
- veredito explícito: `PASS` / `PARTIAL` / `FAIL` / `NOT_TESTED` / `BLOCKED_BY_EXTERNAL_DEPENDENCY`
- `references/` (5) e `templates/` (2); 12 cenários em `evals/evals.json`

### Estado de verificação
- 1 dos 12 evals executado em harness real (cenário `pass-sem-teste`) — **PASS 6/6**
- os outros 11 seguem `NOT_TESTED`
