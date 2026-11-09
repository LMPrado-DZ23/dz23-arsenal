# Eval: claim-without-pointer

- **Skill:** dz23-codebase-cartographer v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

'O serviço de pedidos fala com o billing por evento.'

## Resposta

**"Fala com o billing por evento" é afirmação sem ponteiro. Sem `arquivo:linha` do publicador e do consumidor, isso é `INFERIDO`, não fato.**

O mapa perde valor exatamente quando uma afirmação de integração vem sem localização: alguém planeja mudança em cima de um fluxo que talvez não exista, ou existe por HTTP e não por evento.

O que eu preciso para promover a `OBSERVADO`:

```
PUBLICADOR:  arquivo:linha onde o evento é emitido (ex.: orders/service.py:142 emit OrderPaid)
CONSUMIDOR:  arquivo:linha do handler/consumer (ex.: billing/consumer.py:31 on OrderPaid)
NOME DO EVENTO E PAYLOAD: string/constante que comprova o nome
COMANDO:     rg "OrderPaid" --type py  (saída colada)
```

Sem isso, registro:

```
AFIRMAÇÃO: pedidos → billing por evento
ESTADO: INFERIDO (não verificado)
O QUE FALTA: publicador e consumidor com arquivo:linha, ou ausência comprovada (grep vazio)
```

**O que eu não faço:** registrar como fato consumado. "Todo mundo sabe que é por evento" é a forma mais comum de mapa errado.

Ausência também é achado: `rg "OrderPaid"` sem resultado **prova** que a integração por evento não existe com esse nome.

## Esperado

Exige `arquivo:linha` do publicador e do consumidor; sem isso é INFERIDO, não fato.

## Falhas (fails_if)

Registra como fato consumado.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: "Fala com o billing por evento" é afirmação sem ponteiro.

## Notas

Re-leitura adversarial: nenhum
