# Taxonomia dos quatro defeitos estruturais

Referência de consulta rápida durante o passo 2. O teste unificador para todos: **estas peças deveriam mudar
juntas?** Cada família é uma resposta errada a essa pergunta.

| Família | Sinal no código | Princípio violado | Correção típica |
|---|---|---|---|
| **Elo oculto** | cópias de lógica/valor; leitura de global escrito alhures; feature espalhada por camadas; convenção implícita entre chamador e chamado | *explicit over implicit*, *self-contained code* | tornar o vínculo visível: tipo único, módulo que exporta, colocação por domínio |
| **Elo desnecessário** | chamador depende de interno; estável importa volátil; parâmetro que só um fluxo usa; módulo raso (interface == implementação) | *encapsulation*, *dependency direction*, *deep modules*, *caller vocabulary* | inverter dependência, esconder interno, aprofundar módulo, remover parâmetro vazamento |
| **Sobra** | wrapper pass-through; config/ponto de extensão para o que nunca varia; código morto | *speculative generality*, YAGNI | deletar ou inlinear; não manter "por precaução" |
| **Caso especial** | `if` de valor único; parâmetro de chamador específico; exceção engolida; retry/sleep; teste desabilitado | design que não previu o requisito | redesenhar o sistema para que o caso deixe de ser especial — não remendar o caso |

## Como usar

- Um problema pode pertencer a mais de uma família. Registre na primária e aponte as outras no log.
- A correção certa raramente se parece com o sintoma. Se sua solução for literalmente envolver cada `if` em
  função, você está consertando casos especiais isolados — o anti-padrão central. Procure a causa comum.
- **Caso especial ≠ bug.** É requisito não previsto. Conte quantos sobram ao fim: é a métrica de conclusão.

## Fronteira com outras skills

- Esta taxonomia é sobre **estrutura de mudança**, não sobre qualidade de comentário nem estilo.
- Para podar só testes (subconjunto da família "sobra" aplicada a arquivos de teste), use `prune-tests`.
- Mapear o grafo atual antes de decidir por onde começar é trabalho de `dz23-codebase-cartographer`.
