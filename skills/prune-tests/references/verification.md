# Verificação — provar que nada de comportamento caiu

Podar testes tem um risco: deletar o único teste que guardava um comportamento real. A poda só é PASS
quando você prova que isso não aconteceu.

## O que provar

1. **Suíte verde antes e depois.** Rode no baseline (passo 0) e no fim. Os dois verdes.
2. **Cada deleção justificada por família.** Para todo teste removido, a lista do método diz passado,
   nada, implementação ou duplicata. Nenhuma deleção "porque era chato".
3. **Nenhum comportamento perdeu sua rede.** Para cada teste deletado que *parecia* tocar comportamento,
   aponte o teste que ainda guarda esse comportamento. Se não há nenhum, o teste não era podável —
   reescreva contra o comportamento em vez de deletar.
4. **Mutação opcional, mas forte.** Se há ferramenta de mutation testing, rode antes e depois: a poda
   não pode baixar o mutation score dos comportamentos que importam. Um teste que você removeu e que
   matava mutantes guardava comportamento — não era podável.

## Estados honestos

- **PASS** — suíte verde nos dois pontos, toda deleção classificada, nenhum comportamento sem rede.
- **NOT_TESTED** — você podou mas não rodou a suíte depois (ou não tinha baseline). Não declare PASS.
- **PARTIAL** — restam testes sem decisão, ou um comportamento ficou sem rede e você ainda não
  reescreveu o teste.

## Anti-engano

O pior resultado não é deixar um teste inútil — é **deletar um teste que pegava uma regressão** e
chamar de limpeza. Na dúvida entre "implementação" e "comportamento", trate como comportamento e
reescreva, não delete. Reescrever é reversível no mesmo PR; uma regressão que vaza, não.
