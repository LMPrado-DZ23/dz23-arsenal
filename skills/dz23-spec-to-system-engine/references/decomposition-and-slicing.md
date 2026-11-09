# Decomposição em fatias

## O que é uma fatia
Fatia é a menor unidade que **entrega valor verificável de ponta a ponta**: UI ou entrada → contrato →
dado → prova. Ela pode ir para produção sozinha (com flag desligada, se preciso).

| É fatia | Não é fatia |
|---|---|
| "Listar pedidos do cliente com filtro de status" (tela + API + query + teste) | "Criar a tabela `orders`" |
| "Exportar CSV do período" (botão + endpoint + job + teste) | "Refatorar camada de serviços" |
| "Bloquear acesso de outro tenant" (middleware + teste de vazamento) | "Adicionar camada de repositório" |

Camada técnica é **passo interno** dentro de uma fatia, não entrega.

## Como cortar
1. Pegue a jornada do usuário e corte por **valor**: "ver", "criar", "editar", "exportar", "bloquear".
2. Para cada fatia, liste o caminho mínimo que já entrega: dados necessários, contrato, tela/ação, prova.
3. Se a fatia não cabe numa sessão de trabalho, corte por **variação** (poucos campos → todos), não por camada.
4. Marque dependência entre fatias (bloqueia / combina).

## Regra do "primeiro dia"
A primeira fatia de um épico deve provar a **integração mais arriscada** (contrato desconhecido, integração
externa, permissão). Provar o fácil primeiro e descobrir o difícil no fim é o jeito mais caro de falhar.

## Tamanho
- Fatia ideal: 1–3 dias de trabalho, entregável e testável.
- Acima de 5 dias: corte por variação ou por persona.
- Abaixo de meio dia: provavelmente é tarefa interna; agrupe.

## Definição de pronto por fatia
```
DONE quando:
- [ ] critério de aceite do(s) REQ coberto(s) demonstrado
- [ ] teste (unit/integ/integração/E2E) verde e citado
- [ ] erro e vazio tratados
- [ ] permissão/tenant verificado quando aplicável
- [ ] doc/observabilidade mínima (log, métrica) quando o caminho é novo
- [ ] rollback/flag declarado quando o risco pede
```
Sem isso, a fatia está em `IN_PROGRESS`, não `DONE`.

## Ordem e caminho crítico
Monte o grafo: fatias como nós, dependência como aresta. O **caminho crítico** é a cadeia mais longa —
é o que define o prazo real. Paralelize apenas o que não está nessa cadeia e só depois do contrato fechado.

## Fatias verticais em 4 estágios (granularidade de entrega)
Quando o épico é grande, ordene em quatro estágios que **não quebram o build** entre um e outro:

| Slice | Conteúdo | Prova |
|---|---|---|
| **1 — Fundação & Schema** | migração, índices, constraints, testes de repositório | `pnpm test:db` |
| **2 — Domínio & Contratos** | schemas, serviço com regra, multi-tenant, contrato da rota | `pnpm test:integration` |
| **3 — Experiência Visual** | UI com Loading/Empty/Success/Error, validação, integração | `pnpm test:component` |
| **4 — Prova E2E & Hardening** | browser real (feliz + erros 4xx), observabilidade, deploy | `pnpm playwright test` |

Cada slice declara: **arquivos alvo**, **escopo exato** (o que não fazer) e **comando de verificação**.
DAG: 1 → 2 → 3 → 4, com 2 e 3 podendo sobrepor só depois do contrato fechado.

Isso **não** é entrega por camada: cada slice termina com prova executável e o estágio 4 fecha o valor
ponta a ponta para o usuário. O que é proibido é "banco semana 1, backend semana 2, UI semana 3" sem
nenhuma tela funcionando no meio.

## Saída
Plano de fatias em `templates/slice-plan.md`: `ID | Fatia | REQs | Depende de | Dono | Tamanho | DoD | Estado`.
