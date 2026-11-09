# B-3PO — seis modos e UX operacional

A estrutura deve ser confirmada no checkout; exemplos abaixo são destinos conceituais, não prova de módulos implementados.

- Engenharia: projetos de código, repositórios, ferramentas, testes, builds, deploy e logs, apenas quando existentes.
- Empresa: atendimento/CRM, agenda, serviços, RH, produtos, estoque, compras, vendas, entregas, financeiro, marketing e pós-venda.
- Automação: fluxos, gatilhos, execuções, trabalhos, agendamentos, agentes, Sofia e integrações.
- IA e Agentes: bots, Sofia, capacidades, modelos, skills, memória, equipes, ferramentas e execução.
- Estratégico: indicadores, metas, relatórios, planejamento, análise financeira e operacional.
- Administração: empresa, estrutura, usuários, RBAC, privacidade, integrações, provedores e auditoria.

## Regras
Modo é navegação; autorização é backend/IPC. Não duplicar CRM, runtime, banco ou regras. Itens indisponíveis devem ficar ausentes ou explicitamente não implementados, não fingir funcionamento. Conversas e Bots podem ser atalhos globais se coerentes; evitar duplicação visual.

## Fluxos prioritários
1. Criar bot com nome, avatar DZ23 real, modelo/provedor válido, permissões, persistência, edição e conversa.
2. Criar pedido de compra -> aprovação -> recebimento -> estoque -> financeiro, com transações e autorização.
3. Sofia: planejar, atribuir, aprovar, executar no Hermes e exibir resultados e falhas reais.
4. Alternar seis modos, manter contexto, testar rotas, visibilidade e navegação por teclado.

## Localização
PT-BR integral quando selecionado; procurar strings em inglês inclusive diálogos, mensagens de erro e loading. Mascotes devem vir dos assets autorizados e da fonte de verdade, não de listas hardcoded paralelas.
