# Changelog — dz23-autonomous-improvement-ultimate

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
