# Prompts de origem

Os prompts que deram origem a algumas skills deste arsenal — e a biblioteca de métodos de análise que
exigem evidência. Ficam aqui porque servem a três usos:

1. **Uso direto** — copiar e colar em qualquer agente, sem instalar skill nenhuma.
2. **Rastreabilidade** — mostra de onde veio cada skill, e o que a skill acrescentou.
3. **Método verificável** — oito prompts com `prompt.yaml`, que exigem baseline, evidência e critério de
   aceitação objetivo em vez de opinião.

## Índice

| Prompt | O que pede | Virou a skill | O que a skill acrescenta |
|---|---|---|---|
| [`performance-4-camadas.md`](performance-4-camadas.md) | plano de otimização em 4 camadas, 20 itens | [`dz23-performance-scalability-engine`](../skills/dz23-performance-scalability-engine/) | baseline obrigatório, percentis, budget, evidência antes/depois, gates de bloqueio |
| [`arquitetura-escalabilidade.md`](arquitetura-escalabilidade.md) | plano em 7 camadas, sem tecnologia sem necessidade demonstrada | [`dz23-backend-data-architect`](../skills/dz23-backend-data-architect/) + [`architect`](../external/) | ADRs, matriz de decisão, migração reversível |
| [`seguranca-owasp.md`](seguranca-owasp.md) | auditoria em 6 camadas, com exploração autorizada | [`security-review`](../external/) + [`dz23-postgres-prod-preflight`](../skills/dz23-postgres-prod-preflight/) | severidade, risco residual, teste de regressão |
| [`banco-de-dados.md`](banco-de-dados.md) | modelagem, índices, transações, migrações | [`dz23-postgres-prod-preflight`](../skills/dz23-postgres-prod-preflight/) | gates de banco, verificação em Postgres real |
| [`testes-qualidade.md`](testes-qualidade.md) | estratégia em 8 tipos de teste, partindo do baseline | [`dominios`](../skills/) de QA + [`prune-tests`](../external/caldoai-skills.md) | baseline, PASS/FAIL por teste, poda de teste sem valor |
| [`engenharia-reversa-autorizada.md`](engenharia-reversa-autorizada.md) | RE defensiva em escopo autorizado | [`dz23-reverse-engineer-anything`](../skills/dz23-reverse-engineer-anything/) + [`rea`](../external/rea.md) | evidência por artefato, grau de confiança |
| [`ui-ux-acessibilidade.md`](ui-ux-acessibilidade.md) | UI/UX/a11y em 10 dimensões | [`dz23-ultimate-pro-max`](../skills/dz23-ultimate-pro-max/) + [`web-design-guidelines`](../skills/) | auditoria por componente, teste manual e automatizado |
| [`agentes-skills-mcp.md`](agentes-skills-mcp.md) | arquitetura de skills/agentes/MCP com permissões | [`dz23-autonomous-improvement-ultimate`](../skills/dz23-autonomous-improvement-ultimate/) + [`dz23-spec-to-system-engine`](../skills/dz23-spec-to-system-engine/) | contrato de permissão, avaliação, fallback |
| [`devops-supply-chain.md`](devops-supply-chain.md) | build reprodutível, SBOM, segredos, rollback | [`dz23-devops-cloud-deployer`](../skills/dz23-devops-cloud-deployer/) + [`delivery-pipeline`](../external/) | gates de CI, assinatura, recuperação |

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

O texto começou **verbatim**, inclusive com erros do original. Em 2026-11-18 foi **corrigido na origem**:

| Antes | Depois | Por quê |
|---|---|---|
| "Filas para Processamento **Assalariado**" | "**Assíncrono**" | typo; a skill já interpretava assim |
| "**extremamente rápida**" | metas mensuráveis (LCP/INP/TTFB por p75) | adjetivo não é critério de aceitação |
| "**obrigatoriamente** WebP ou AVIF" | "quando a medição mostrar ganho real" | formato é meio, não regra |
| "Camada de Cache (**Redis**)" | cache se houver leitura repetida medida | tecnologia exige evidência |
| "**CDN global**" / "**balanceamento**" | quando a latência/saturação medida justificar | nem todo sistema precisa |

A skill [`dz23-performance-scalability-engine`](../skills/dz23-performance-scalability-engine/) mantém a
interpretação de "assíncrono" e o histórico da correção em `references/backend-layer.md`.

## Biblioteca de métodos de análise

Além do prompt de performance, esta pasta reúne **métodos de análise verificáveis**: oito prompts que
exigem evidência, baseline e critério objetivo de aceitação. Cada um tem um `prompt.yaml` ao lado, com
metadados legíveis por máquina.

| Prompt | O que pede | Metadados |
|---|---|---|
| [`arquitetura-escalabilidade.md`](arquitetura-escalabilidade.md) | plano em 7 camadas, sem introduzir tecnologia sem necessidade demonstrada | `risk: high` · exige evidência e baseline |
| [`seguranca-owasp.md`](seguranca-owasp.md) | auditoria de segurança em 6 camadas, com cenário de exploração autorizado | `risk: high` · exige evidência |
| [`banco-de-dados.md`](banco-de-dados.md) | modelagem, índices, transações, migrações e rollback | `risk: high` · exige evidência e baseline |
| [`testes-qualidade.md`](testes-qualidade.md) | estratégia em 8 tipos de teste, partindo do baseline atual | `risk: medium` · exige evidência e baseline |
| [`engenharia-reversa-autorizada.md`](engenharia-reversa-autorizada.md) | RE defensiva, só em escopo autorizado, com grau de confiança | `risk: high` · exige evidência |
| [`ui-ux-acessibilidade.md`](ui-ux-acessibilidade.md) | UI/UX/a11y em 10 dimensões, com teste manual e automatizado | `risk: medium` · exige evidência |
| [`agentes-skills-mcp.md`](agentes-skills-mcp.md) | arquitetura de skills/agentes/MCP com permissões e avaliação | `risk: high` · exige evidência |
| [`devops-supply-chain.md`](devops-supply-chain.md) | build reprodutível, SBOM, segredos, rollback e incidentes | `risk: high` · exige evidência e baseline |

Formato do `prompt.yaml`:

```yaml
name: arquitetura-escalabilidade
version: 1.0.0
risk: high
requires_evidence: true
requires_baseline: true
destructive_actions: false
dominios:
  - architecture
  - scalability
  - reliability
```

`destructive_actions: false` em **todos** os oito quer dizer o mesmo: nenhum deles autoriza deploy,
force-push, migração destrutiva ou alteração de produção. Prompt não concede permissão — permissão se pede.

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
