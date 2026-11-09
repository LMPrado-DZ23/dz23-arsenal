# Anti-padrões de especificação e decomposição

Cada item: **sintoma** → **por que dói** → **correção**.

## Enquadramento
1. **Começar pela solução** ("vamos fazer um dashboard") → constrói o certo para o problema errado → pergunte o problema e o sintoma antes.
2. **Escopo sem fora de escopo** → todo mundo acrescenta, ninguém corta → lista explícita com motivo.
3. **Premissa virando requisito** → "assumi que o cliente tem API" vira bloqueio na entrega → marque como assumido e valide.
4. **Prazo antes do escopo** → corte automático no lugar errado → escopo primeiro, corte negociado.

## Requisitos
5. **"Deve ser rápido/ bonito/ intuitivo"** → impossível provar → número observável (p95, cliques, contraste).
6. **Requisito sem origem** → não se defende quando cortam → registrar quem pediu e quando.
7. **Só caminho feliz** → erro, vazio e permissão aparecem em produção → incluir caminho infeliz no critério.
8. **Requisito que descreve implementação** → trava a solução → descreva o comportamento observável.
9. **Requisito guarda-chuva** ("relatórios") → não cabe numa fatia, não se mede → recortar por tipo/período/formato.
10. **Requisito removido em silêncio** → o pedido desaparece sem decisão → `CUT` com motivo e aprovador.

## Decomposição
11. **Fatia por camada** ("criar tabela", "criar API", "criar tela") → nada entrega valor até o fim → fatiar por valor ponta a ponta.
12. **Fatia grande demais** (> 5 dias) → não dá para revisar nem provar cedo → cortar por variação.
13. **Fatia que não roda sozinha** → não pode ir a produção → incluir flag ou dependência explícita.
14. **Provar o fácil primeiro** → o risco aparece no fim → primeira fatia ataca a integração mais arriscada.
15. **Dependência circular** → plano impossível → quebrar a dependência ou fundir as fatias.

## Contratos
16. **Paralelizar antes do contrato** → retrabalho e integração dolorosa → contrato fechado antes de dividir.
17. **Contrato só de sucesso** → erro/timeout não previstos → contrato cobre 4xx/5xx, vazio e limite.
18. **Contrato sem consumidor** → especulação → só contrato com consumidor declarado.
19. **Contrato verbal** → cada lado lembra diferente → contrato versionado no repositório.
20. **Mudança de contrato sem versão** → cliente quebra → aditivo + versão + janela.

## Risco e estimativa
21. **Estimativa de número único** → vira compromisso irreal → intervalo com premissa explícita.
22. **Spike sem pergunta nem prazo** → vira escopo oculto → pergunta, prazo, saída esperada.
23. **Decisão irreversível sem ADR** → ninguém sabe por que está assim → registrar antes de executar.
24. **Risco sem dono** → fica no documento e acontece → dono + prazo + mitigação.
25. **Capacidade 100%** → qualquer imprevisto atrasa tudo → planejar 70–80%.

## Plano e execução
26. **Tudo no caminho crítico** → sem paralelismo, prazo inflado → separar o que é cadeia do que é paralelo.
27. **Buffer distribuído** → cada tarefa consome a folga → buffer único no fim.
28. **Plano que não é revisado** → vira ficção → reconciliar a cada fatia.
29. **Desvio escondido** → surpresa no fim → registro com causa, impacto e ação.
30. **`DONE` sem prova** → entrega fantasma → `DONE` só com evidência anexada.
31. **Matriz que não é atualizada** → rastreabilidade morta → atualizar na mesma entrega.
32. **Handoff sem DoD** → quem recebe adivinha → fatia + contrato + DoD + critério de prova.

## Como usar
Na revisão da spec, percorra a lista: **não se aplica / aplicado / pendente com risco**. Achado bloqueia a
entrega da especificação quando for BLOCKER (ver `references/quality-gates.md`).
