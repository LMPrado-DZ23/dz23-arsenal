# DSH — Quickstart (1 página)

Pôr a agência pra rodar, do zero, em poucos passos. Detalhe completo no [documento canônico](DSH_COMPLETE_SPECIALIST_AGENCY.md).

## 5 passos

1. **Crie o Diretor.** Num agente novo, cole no `agent-instructions` o [núcleo universal](DSH_AGENT_SHARED_CORE_UNIVERSAL.txt) e, logo abaixo, o [overlay do Diretor](DSH_AGENCY_DIRECTOR_OVERLAY.txt). Nome: `Diretor`.
2. **Crie a célula inicial.** O Diretor já cumpre o papel 01, então comece os especialistas no 02. Um agente por papel, cada um = núcleo universal + **um** perfil do catálogo: 02 Arquitetura, 03 Requisitos, 25 Product, 26 UX Research, 27 Product Design, 04 Backend, 05 Frontend, 13 QA, 16 AppSec, 11 SRE e 81 Revisor Independente.
3. **Fale com o Diretor, não com os especialistas.** Mande a demanda a ele: ele enquadra, mede o impacto (T0–T3), monta o pod mínimo e coordena.
4. **Aprove o que tem impacto.** T0/T1 seguem; T2/T3 pedem sua confirmação antes de executar, e T3 passa pelo 81 antes do fecho.
5. **Leia a síntese.** O Diretor entrega fatos, hipóteses, recomendação, plano, impacto/aprovações e risco residual — não um despejo de tudo que cada agente disse.

## Exemplo concreto

> "Mudar o preço no checkout do nosso site."

- **Diretor classifica:** mexe em preço + produção → **T3** (financeiro, público, reversível só com cuidado).
- **Pod mínimo:** 25 Product, 46 E-commerce, 51 Precificação, 04 Backend, 13 QA, 16 AppSec. (46 e 51 não estão na célula inicial — o Diretor os cria sob demanda; a célula cobre o caso comum.)
- **Fluxo:** o pod propõe a mudança e o teste; o **81** revisa o entregável; **você aprova** antes de publicar; o 14 Release/11 SRE acompanham o rollout.
- **Resultado:** mudança aplicada com validação, rollback e trilha — não um "pronto" sem evidência.

## Árvore de decisão rápida (pra escolher o pod)

- É **incidente** (algo quebrado em produção)? → pod de incidente (20, 11, 12 + causal).
- É **regulado/setorial** (saúde, jurídico, fintech...)? → acrescente o especialista 65–80 como dono do contexto.
- Tem **dinheiro** envolvido (preço, cobrança, orçamento)? → acrescente 49/50/51 e trate como T3.
- É **produto novo**? → pod de produto (03, 02, 25, 26, 27, 04, 05, 13, 16, 11).
- É **dúvida/pesquisa**, sem mudar estado? → T0, pode seguir sem aprovação.

## Onde está cada coisa

- Regras comuns a todos: [núcleo universal](DSH_AGENT_SHARED_CORE_UNIVERSAL.txt)
- Orquestração: [overlay do Diretor](DSH_AGENCY_DIRECTOR_OVERLAY.txt)
- Perfis: [01–24](DSH_SPECIALIST_AGENT_CATALOG.md), [25–64](DSH_SPECIALIST_AGENT_CATALOG_EXPANDED.md), [65–87](DSH_SPECIALIST_AGENT_CATALOG_VERTICALS.md)
- Registro de decisões do Diretor: [template](DSH_DECISION_LOG_TEMPLATE.md)
- Antes de commitar mudanças nos perfis, rode `python check_sizes.py`
