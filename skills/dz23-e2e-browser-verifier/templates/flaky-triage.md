# Triagem de teste flaky

## Identificação
- Teste:
- Arquivo / linha:
- Taxa de falha: __/10 execuções (isolar) · __/10 (na suíte)
- Última execução verde (commit):
- Primeira falha conhecida (commit/data):

## Sintoma
- Passo que falha:
- Mensagem literal:
- Screenshot: (anexar)
- Trace: (caminho)
- Console/network no momento:

## Hipótese (marque uma principal)
- [ ] Seletor frágil (posição/classe/texto)
- [ ] Espera fixa curta / condição não esperada
- [ ] Dado compartilhado ou dependência de ordem
- [ ] Concorrência na mesma conta/tenant
- [ ] Animação/transição
- [ ] Terceiro externo lento
- [ ] Relógio/fuso
- [ ] Recurso esgotado (workers/banco)
- [ ] Bug real do produto

## Diagnóstico
- Reproduz isolado? sim | não
- Reproduz com `--repeat-each=10`? sim | não
- Muda com 1 worker? sim | não
- Passa com retry? sim | não → **se sim, a causa continua desconhecida**

## Ação
- Correção aplicada:
- Alternativa descartada (e por quê):
- Quarentena: sim | não
- Issue: nº
- Dono:
- Data de revisão:

## Regra
Flaky não é fechado como "passou". Fecha quando: causa identificada e corrigida, **ou** quarentena com issue e prazo. Retry não é fechamento.
