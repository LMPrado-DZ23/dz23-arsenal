# DSH — Registro de decisões do Diretor

Uma linha por decisão que o Diretor toma ou escala: qual pod montou, o que foi
escalado, o que foi aprovado. É a prova de que a divergência não foi apagada e
de que ações de impacto tiveram dono e autorização. Preencha ao vivo; não
reconstrua de memória.

## Como usar

- Registre toda decisão de **T2/T3**, todo **conflito escalado** e toda **aprovação** pedida ao usuário.
- `Impacto` é T0–T3. `Dono` é quem decide (especialista, Diretor ou usuário).
- `Alvo/ambiente`, `Janela da aprovação` e `Rollback` capturam a autorização que o núcleo exige: uma confirmação vale só para o alvo, o ambiente, a ação e a janela informados.
- `Evidência` aponta o que sustenta a decisão (log, teste, documento) — não "achei".
- `Status`: proposto · aprovado · executado · revertido · bloqueado.

## Tabela

| Data (ISO) | Demanda | Impacto | Pod | Decisão | Alvo/ambiente | Janela da aprovação | Rollback | Alternativas | Evidência | Dono | Revisão 81 | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-18 | Mudar preço no checkout | T3 | 25,46,51,04,13,16 | Aplicar novo preço com flag | checkout prod, flag `price_v2` | deploy 18/10 19h–20h | desligar a flag | manter preço; A/B | teste staging + diff | usuário | sem bloqueador | aprovado |
| | | | | | | | | | | | | |
| | | | | | | | | | | | | |

## Quando houver divergência

Não escolha em silêncio. Registre as alternativas e o fundamento de cada uma, e
quem decidiu:

```text
Divergência: <resumo>
  Opção A — <quem defende> — fundamento / evidência
  Opção B — <quem defende> — fundamento / evidência
  Decisão: <A|B> por <dono>  (motivo)
```
