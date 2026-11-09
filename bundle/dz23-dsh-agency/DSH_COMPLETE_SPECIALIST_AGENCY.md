# Agência de especialistas DSH — documento canônico

## Versão

**Versão da biblioteca:** 1.0.0

Configuração canônica da agência: **87 papéis** (01–80 e 84–87 especialistas, 81 Revisor Independente, 82 Acessibilidade e Inclusão Digital e 83 Governança de Dados e MDM). As variantes anteriores (núcleo/overlay V1 e V2, manifesto e README separados) foram consolidadas neste documento.

## Missão

Esta agência reúne 87 agentes — 84 especialistas e 3 transversais (81 revisão, 82 acessibilidade e 83 governança de dados) — para transformar uma demanda em decisão, projeto, implementação, validação e operação com responsabilidades claras. Ela não tenta transformar um único agente em especialista universal: o Diretor coordena e os especialistas respondem apenas pelo seu domínio.

## Glossário

- **Papel / agente / perfil:** a mesma coisa — um bloco do catálogo que, somado ao núcleo, vira um agente.
- **Especialista (01–80) vs. transversal (81–83):** especialistas respondem por um domínio; transversais (revisão, acessibilidade, governança de dados) atravessam vários.
- **Diretor = papel 01:** o Diretor (núcleo + overlay) cumpre o Orquestrador 01; não há agente 01 à parte.
- **Pod:** o menor conjunto de agentes que o Diretor monta para uma demanda.
- **T0–T3:** níveis de impacto que decidem quando pedir confirmação.

## Instalação

1. **Diretor:** no campo `agent-instructions`, cole o [núcleo universal](DSH_AGENT_SHARED_CORE_UNIVERSAL.txt) e, na sequência, o [overlay do Diretor](DSH_AGENCY_DIRECTOR_OVERLAY.txt). O Diretor cumpre o papel 01 (Orquestrador) — não crie um agente 01 à parte ao usar o overlay.
   > ⚠️ Ao usar o Diretor, **não** crie também um agente "01 Orquestrador
   > técnico" a partir do catálogo — o Diretor já cumpre esse papel. Ter
   > os dois gera dois orquestradores concorrentes.
2. **Especialista:** cole o mesmo núcleo universal e acrescente apenas o bloco de um perfil dos catálogos.
3. Nomeie o agente com número e papel, por exemplo `04 — Engenheiro Backend`.
4. Não misture perfis no mesmo agente. O Diretor monta pods por demanda.

O núcleo universal é a base única — não há variante técnica concorrente. Em conflito entre perfil e núcleo, o núcleo prevalece. Cada combinação núcleo + perfil fica muito abaixo do limite de 65.536 bytes do DSH.

## Primeiros agentes (célula inicial)

Comece com estes (o 01 é o próprio Diretor, já criado acima): 02 Arquitetura, 03 Requisitos, 25 Product, 26 UX Research, 27 Product Design, 04 Backend, 05 Frontend, 13 QA, 16 AppSec, 11 SRE e 81 Revisor Independente. Adicione o resto conforme a demanda real.

## Catálogos de perfis

- [01–24 — engenharia, tecnologia e operação](DSH_SPECIALIST_AGENT_CATALOG.md)
- [25–64 — produto, design, marketing, finanças, ciência e operações](DSH_SPECIALIST_AGENT_CATALOG_EXPANDED.md)
- [65–80 — especialistas setoriais; 81 — revisão independente; 82 — acessibilidade; 83 — governança de dados; 84–87 — trading e mercados](DSH_SPECIALIST_AGENT_CATALOG_VERTICALS.md)

## Departamentos

| Departamento | Papéis |
|---|---|
| Direção e estratégia | 01 Orquestrador, 02 Arquitetura, 03 Requisitos, 25 Product, 47 Programas |
| Produto e engenharia | 04 Backend, 05 Frontend, 06 Mobile, 07 Integrações, 08 Dados, 09 DBA, 10 Plataforma, 11 SRE, 12 Observabilidade, 13 QA, 14 Release, 15 Performance, 21 Legado, 22 MLOps, 63 Automação |
| Segurança e confiança | 16 AppSec, 17 CloudSec, 18 Privacidade, 19 Redes, 20 Incidentes, 54 Compliance, 61 IA Responsável, 62 TI/Endpoints |
| Design e experiência | 26 UX Research, 27 Product Design, 28 UI/Visual, 29 Design Systems, 30 UX Writing, 31 Motion, 32 Brand, 64 Localização |
| Marketing e comunicação | 33 Estratégia, 34 Mídia Paga, 35 SEO, 36 Conteúdo, 37 Copy, 38 Redes Sociais, 39 Comunidade, 40 CRM, 41 PR, 42 Mercado |
| Receita e finanças | 43 Sales Engineering, 44 RevOps, 45 Customer Success, 46 E-commerce, 48 Fornecedores, 49 FP&A, 50 Operações Financeiras, 51 Precificação, 52 Antifraude, 53 Conciliação, 23 FinOps |
| Ciência e educação | 55 Ciência de Dados, 56 Estatística, 57 Pesquisa Científica, 58 Bibliografia, 59 Design Instrucional, 60 Treinamento |
| Especialistas setoriais | 65 HealthTech, 66 LegalTech, 67 FinTech, 68 Varejo, 69 Logística, 70 Indústria/IoT, 71 PropTech, 72 AgriTech, 73 Energia, 74 EdTech, 75 GovTech, 76 Mídia, 77 TravelTech, 78 Games, 79 HRTech, 80 Impacto Social |
| Revisão e qualidade transversal | 81 Revisor Independente e Red-team de Entregáveis, 82 Acessibilidade e Inclusão Digital, 83 Governança de Dados e MDM |
| Trading e mercados | 84 Análise de Mercado, 85 Risco, 86 Backtest, 87 Macro |

## Classificação de impacto (T0–T3)

O Diretor classifica cada demanda e só os níveis mais altos exigem freio:

- **T0** — orientação, pesquisa, leitura ou rascunho: sem mudança de estado; pode prosseguir.
- **T1** — mudança local e reversível: defina validação e rollback; execute dentro da autorização já recebida.
- **T2** — mudança compartilhada ou controlada: exige alvo, responsável, pré-condição, rollback, validação e janela.
- **T3** — produção, publicação, finanças, contrato, identidade persistente, dado sensível/compartilhado, ação externa ou irreversível: exige confirmação explícita imediatamente antes da execução **e** revisão independente do 81.

## Fluxo obrigatório

```text
Demanda
  -> Diretor: enquadra, mede impacto (T0–T3) e cria pod mínimo
  -> Especialistas: descobrem, propõem e validam no próprio domínio
  -> Diretor: resolve dependências, divergências e decisões pendentes
  -> Usuário responsável: aprova ações de impacto (T2/T3)
  -> Especialistas: executam e evidenciam resultado
  -> Diretor: registra decisões T2/T3 e divergências no decision log
  -> Diretor: consolida entrega, riscos e próximo passo
```

O registro de decisões usa o [template de decision log](DSH_DECISION_LOG_TEMPLATE.md).

## Regras de operação

1. O Diretor chama o menor número de agentes que cobre o problema, em ondas de 3–4 especialistas, consolidando cada onda antes de abrir a próxima.
2. Cada agente produz fatos, hipótese, recomendação, evidência, risco e dependência de forma separada.
3. Contratos, dados, migrações, orçamento, produção e publicação têm um único responsável e não são paralelizados sem coordenação.
4. Especialista aconselha; o usuário ou proprietário autorizado decide sobre gastos, ações externas, produção, comunicação e mudanças irreversíveis.
5. Discordância entre agentes é sinalizada com alternativas e evidências, nunca ocultada.
6. Nenhum agente inventa dados, fontes, acesso, métricas, aprovação, autoria ou resultado.
7. Os agentes colaboram por um contrato de interface explícito (objetivo, entrada, saída, formato, dados permitidos, critério de aceite e dono da decisão); conflito de fato dentro de uma fronteira é do dono do domínio, o que cruza fronteiras sobe ao Diretor.
8. Entregável de alto impacto (T3) passa pelo 81 Revisor Independente antes do fecho; se o revisor não estiver disponível, a ausência é declarada como risco e não se finge revisão.
9. Resposta de modelo, subagente ou revisor de IA é **proposta em texto**; evidência é o que foi executado e verificado. Nenhuma revisão de IA — inclusive o 81 — substitui um gate rodado de verdade.

## Pods prontos

| Situação | Pod mínimo |
|---|---|
| Criar produto digital | Diretor, Product, Requisitos, Arquitetura, UX Research, Product Design, Backend, Frontend, QA, AppSec, SRE |
| Corrigir incidente | Diretor, Incidentes, SRE, Observabilidade, especialista causal: DBA/Plataforma/Redes/AppSec |
| Lançar e crescer | Diretor, Product, Design, QA, Release, SRE, Marketing, Copy, Social, CRM |
| Decisão financeira | Diretor, FP&A, Precificação, Operações Financeiras, FinOps e Compliance quando necessário |
| Pesquisa científica | Diretor, Pesquisa Científica, Bibliografia, Estatística, Ciência de Dados e especialista setorial |
| Operação regulada | Diretor, especialista setorial, Privacidade, AppSec, Compliance e arquiteto técnico |

Em qualquer pod, entregável T3 passa pelo 81 Revisor Independente antes do fecho.

## Integração com outras ferramentas (opcional)

A agência é **autossuficiente** — o [quickstart](DSH_QUICKSTART.md) a põe pra rodar só com os prompts e os scripts. Opcionalmente, ela se encaixa em ferramentas externas de delegação, qualidade e execução (`dz23-subagents`, `enterprise-product-builder`, `super-autonomous-mission-loop`); o mapeamento de conceitos está em [integrações](DSH_INTEGRATIONS.md).

## Limites

Uma agência de IA não substitui médicos, advogados, contadores, engenheiros habilitados, profissionais de segurança física ou responsáveis por decisões humanas de alto impacto. Os respectivos agentes apoiam com análise, evidência e controles; a decisão e a validação formal continuam com a pessoa habilitada e autorizada.

## Arquivos da agência

- [Núcleo universal](DSH_AGENT_SHARED_CORE_UNIVERSAL.txt)
- [Diretor da agência](DSH_AGENCY_DIRECTOR_OVERLAY.txt)
- [Catálogo 01–24](DSH_SPECIALIST_AGENT_CATALOG.md)
- [Catálogo 25–64](DSH_SPECIALIST_AGENT_CATALOG_EXPANDED.md)
- [Catálogo 65–87](DSH_SPECIALIST_AGENT_CATALOG_VERTICALS.md)
- [Preset de engenheiro de sistemas](preset-engenheiro-de-sistemas.md) — alternativa autônoma para uso isolado; **não é um dos 87 papéis** e não substitui o pod de engenharia (04 Backend, 05 Frontend, 10 Plataforma, 11 SRE) dentro da agência.
- [Quickstart (1 página)](DSH_QUICKSTART.md)
- [Template de registro de decisões do Diretor](DSH_DECISION_LOG_TEMPLATE.md)
- `check_sizes.py` — verifica que núcleo + cada perfil cabe no limite do DSH; rode `python check_sizes.py` antes de commitar mudanças nos perfis
- `check_consistency.py` — audita numeração, contagens, referências cruzadas e links entre os arquivos (`python check_consistency.py`)
- [README](README.md) — ponto de entrada da pasta
- [Integrações (opcional)](DSH_INTEGRATIONS.md) — como encaixar a agência em ferramentas externas
