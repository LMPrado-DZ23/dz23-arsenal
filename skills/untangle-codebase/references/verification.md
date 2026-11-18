# Verificação: como provar que o comportamento não mudou

O veredito desta skill é `NOT_TESTED` até este arquivo ser cumprido. Reorganizar dependência sem prova de
comportamento é exatamente a "quebra silenciosa" que a skill existe para evitar — vale também contra quem
executa a skill.

## Regra

Depois do passo 4 (aplicar), antes de declarar pronto, o **comportamento intencional** deve estar igual ao do
início, exceto por bugs que o refactor deliberadamente corrigiu. Isso se prova executando, não lendo diff.

## Procedimento mínimo

1. **Baseline antes de mexer.** Rode a suíte no commit inicial e registre o que já falhava. Sem baseline, uma
   regressão sua é indistinguível de um teste quebrado pré-existente.
2. **Mesmo instrumento depois.** A mesma suíte, no mesmo ambiente. Compare contagem de pass/fail/skip item a
   item, não só "parece verde".
3. **Diferença exige explicação.** Todo teste que passou a falhar, ou mudou de resultado, precisa de uma linha
   no registro de decisão dizendo qual bug intencional isso reflete. Teste que muda de cor sem explicação é
   regressão, não melhoria.
4. **Cobertura dos caminhos tocados.** Para cada correção estrutural (ex.: inverter dependência Stripe/PayPal),
   garanta que existe teste exercitando aquele caminho. Se não existia, adicione — reorganização cega em código
   sem teste é a classe da rodada em que um gate ficou verde porque ninguém rodava o check.

## Estados

| Estado | Quando |
|---|---|
| PASS | suíte verde vs. baseline, e toda diferença tem explicação registrada |
| NOT_TESTED | reorganização aplicada mas suíte não foi corrida, ou não havia baseline |
| PARTIAL | itens na lista ainda sem correção, ou testes faltando nos caminhos tocados |

## Anti-padrões de verificação

- Declarar "não alterei lógica, só movi arquivos" como prova. Mover import muda ordem de side-effect; ordem
  muda comportamento. Prove executando.
- Rodar os testes *antes* de terminar as mudanças e reportar aquele resultado. O veredito é sobre o estado final.
- Tratar suíte vazia/passthrough como verde. Zero testes executados ≠ nenhum teste falhou.
