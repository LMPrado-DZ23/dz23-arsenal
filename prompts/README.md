# Prompts de origem

Os prompts que deram origem a algumas skills deste arsenal. Ficam aqui porque servem a dois usos:

1. **Uso direto** — copiar e colar em qualquer agente, sem instalar skill nenhuma.
2. **Rastreabilidade** — mostra de onde veio cada skill, e o que a skill acrescentou.

## Índice

| Prompt | O que pede | Virou a skill | O que a skill acrescenta |
|---|---|---|---|
| [`performance-4-camadas.md`](performance-4-camadas.md) | plano de otimização em 4 camadas, 20 itens | [`dz23-performance-scalability-engine`](../skills/dz23-performance-scalability-engine/) | baseline obrigatório, percentis, budget, evidência antes/depois, gates de bloqueio |

## Diferença entre prompt e skill

O prompt diz **o que fazer**. A skill diz **como provar que foi feito** — e o que fazer quando não há como.

| | Prompt | Skill |
|---|---|---|
| Entrada | pedido em linguagem natural | pedido + pré-condições (ALVO, BASELINE, THRESHOLD, CAMADA) |
| Saída | plano de 20 itens | plano **ordenado por impacto ÷ esforço**, com 1 gargalo escolhido |
| Verificação | nenhuma | baseline medido, prova antes/depois, portão de regressão |
| Falha | não prevista | `NOT_TESTED` / `BLOCKED_BY_EXTERNAL_DEPENDENCY` / `PARTIAL` |
| Risco de uso | aplicar tudo "por precaução" | proibido otimizar fora da camada do gargalo |

## Nota sobre `performance-4-camadas.md`

O texto está **verbatim**, inclusive erros de digitação do original. O item 3.4 diz *"Filas para
Processamento **Assalariado**"* — é typo de *"assíncrono"*. A skill interpreta como processamento
assíncrono em workers e registra a correção em
[`skills/dz23-performance-scalability-engine/README.md`](../skills/dz23-performance-scalability-engine/README.md)
e em comentário no topo de `references/backend-layer.md`.

Prefiro manter o typo no arquivo de origem a "corrigir" o prompt: quem comparar prompt × skill precisa ver
o que estava escrito, não o que deveria estar.

## Como usar um prompt daqui

```bash
cat prompts/performance-4-camadas.md | pbcopy      # macOS
Get-Content prompts\performance-4-camadas.md | Set-Clipboard   # Windows
```

Cole no agente com o contexto do seu projeto. Sem a skill, o resultado tende a ser genérico — porque o
prompt não tem acesso a baseline. Com a skill instalada, o agente sabe que precisa medir antes.

## Contribuir com um prompt

Aceito prompt que:
- resolva um problema recorrente e específico (não "escreva um bom código");
- tenha saída verificável;
- diga o que **não** fazer, não só o que fazer.

Se o prompt virar skill, ele entra aqui como origem e a skill ganha link para ele.
