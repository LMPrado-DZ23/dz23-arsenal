# Estratégia de teste — o que é E2E e o que não é

## A regra de ouro
E2E prova o que **só o browser + servidor + sessão juntos** provam: integração entre camadas, navegação real, estado após ação, autorização no fluxo, persistência visível. Se um teste de unidade ou integração já prova, repetir em E2E só adiciona tempo e flake.

| Camada | Prova | Custo | Quantidade |
|---|---|---|---|
| Unidade | regra, cálculo, transformação | ms | muitos |
| Integração | contrato, query, transação, authz no serviço | s | moderado |
| E2E (browser) | jornada do usuário ponta a ponta | 10s–min | **poucos, críticos** |
| Manual/exploratório | usabilidade, achado inesperado | h | por release |

## O que priorizar em E2E
1. **Dinheiro**: pagamento, cobrança, assinatura, estorno, cupom.
2. **Acesso**: login, logout, recuperação de senha, MFA, convite, troca de papel.
3. **Isolamento**: usuário/tenant A não vê dado de B (o defeito mais caro e mais comum).
4. **Fluxo de conversão**: cadastro, checkout, onboarding, envio de formulário com efeito.
5. **Estado crítico**: pedido criado, status atualizado, dado exibido confere com o servidor.
6. **Regressão visual de página-chave** (home, preço, checkout) — quando mudança de CSS já quebrou antes.

## O que NÃO vai para E2E
- Cálculo e formatação de valor (unidade).
- Validação de campo isolada (componente/integração).
- Contrato de API (contrato/schema).
- Toda combinação de campo e mensagem de erro (matriz explode; escolha 1 caminho feliz + 1 erro por regra crítica).
- Permissão de cada endpoint (integração; no E2E, um caso por papel crítico).
- Terceiros externos reais (pagamento real, e-mail real) — use sandbox/mock no limite, mas nunca mock do próprio alvo.

## Pirâmide invertida (anti-padrão)
Equipe com 800 E2E e 200 unitários: a suíte leva 40 min, falha por timeout e ninguém confia. Sinal: proporção de E2E > 10% do total, suíte > 15 min sem shard, flake > 2%. Correção: empurrar casos para baixo, manter E2E nos fluxos de dinheiro/acesso.

## Critério de aceite de um teste E2E
- Nome descreve comportamento do usuário ("compra com cartão aprovado mostra pedido pago").
- Pré-condição explícita e isolada.
- Passos = ação do usuário (não chamada interna).
- Asserção final = estado observável + efeito no servidor (ex.: `expect(await api.getOrder(id)).status).toBe('paid')`).
- Falha aponta o que quebrou, não "timeout aguardando seletor".

## Cobertura que importa
Não persiga % de linhas em E2E. Persiga **matriz de risco**: fluxo × papel × dispositivo. Marque coberto / não coberto / aceito o risco, com dono. Um fluxo de pagamento sem E2E é risco declarado; 40 testes de hover não compensam.

## Smoke vs regressão
- **Smoke** (5–15 min, por deploy): login, home, fluxo de dinheiro, health da API. Roda em todo ambiente e bloqueia promoção.
- **Regressão** (completa): roda em PR/nightly, com shard.
- **Visual**: screenshots comparados em páginas-chave; tolerância declarada; nunca "verde para sempre" com baseline desatualizado sem revisão.

## Contrato de saída da estratégia
Lista de fluxos com: risco, camada escolhida (E2E ou não), ambiente, papel, dados, critério de aceite e dono. Sem isso, o teste nasce sem propósito e vira dívida.

## Tiers de risco (P0/P1/P2)
| Tier | Conteúdo | Se falhar |
|---|---|---|
| **P0 — Blocker/Smoke** | login/logout, criação de conta, isolamento de tenant (A não vê B), transação principal (pedido, agendamento, lançamento) | bloqueia release |
| **P1 — Estados de borda** | validação de formulário, `409`, `422`, `429`, `5xx`, empty state, loading skeleton | bloqueia feature |
| **P2 — Cross-viewport + a11y** | fluxo crítico em desktop e mobile, teclado (Tab/Enter/Esc), foco visível, nomes acessíveis | ressalva registrada |

Regra de execução: P0 em todo PR; P1 em merge/nightly; P2 conforme escopo declarado. Não deixe P0 fora do smoke.

## Casos negativos obrigatórios
Todo endpoint que o E2E toca precisa de cobertura de erro no caminho de UI:

| Status | O que provar na tela |
|---|---|
| `400` | mensagem de dado inválido, sem perder o preenchido |
| `401` | redirect para login, sem erro 500 |
| `403` | ação negada com mensagem clara (e rota admin inacessível) |
| `404` | página/estado tratado, não tela branca |
| `409` | conflito explicado (duplicado, versão, estado) |
| `422` | regra de negócio recusada com campo indicado |
| `429` | aviso de limite e opção de tentar depois |

## Cross-tenant sempre
Se o produto é multi-tenant, **todo** fluxo P0 tem ao menos um caso de acesso cruzado: ator A em URL/API de B → `404/403`, e listagem sem linha de B. Ver `references/browser-security.md`.

