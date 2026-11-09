# Domínio e invariantes

## Atores concretos
Nunca "o usuário". Nomeie o papel e o que ele pode ver/mutar.

| Ator | Vê | Muta | Não pode |
|---|---|---|---|
| **Owner** (dono do tenant) | tudo do tenant, financeiro, configuração | plano, usuários, dados do tenant | ver outro tenant |
| **Admin** | dados operacionais do tenant | cadastros, agenda, preços | alterar plano/faturamento |
| **Staff** (profissional/atendente) | própria agenda e clientes atribuídos | própria agenda, status de atendimento | mexer em preço/config |
| **Customer** (cliente final) | próprios dados e próprios pedidos | próprios dados, próprios pedidos | ver agenda de outro cliente |
| **Worker** (sistema/webhook) | recurso do evento | estado do recurso conforme contrato | agir como humano |

Regra de ouro: **autorização por recurso**, não só por rota. "Está logado" não é permissão.

## Fronteira multi-tenant
Escreva a matriz de quem vê o quê dentro de um `tenant_id` e o que acontece no cruzamento:

| Operação | Tenant A exige | Esperado no cruzamento |
|---|---|---|
| `GET /pedidos/{id}` de B | id de A | `404` (esconder existência) |
| `PATCH /pedidos/{id}` de B | id de A | `403/404`, sem efeito |
| listagem | filtro por tenant | nenhuma linha de B |
| relatório agregado | escopo do tenant | sem vazamento por soma |

`tenant_id` vem da **sessão/token**, nunca do payload.

## Invariantes — as leis do domínio
Invariante é regra que nunca pode ser violada, independentemente de quem chama. Se o código pode violar, o
modelo está errado.

```
INV-001 · A soma dos repasses nunca excede o valor líquido da transação.
INV-002 · Um profissional não pode ter dois agendamentos ATIVOS com interseção de horário no mesmo tenant.
INV-003 · Saldo nunca fica negativo sem uma transação explícita que o justifique.
INV-004 · Um pedido CONFIRMADO não volta para PENDENTE.
INV-005 · Valor total do pedido = soma dos itens − desconto, sempre, em centavos.
```

### Registro de invariante
| Campo | Conteúdo |
|---|---|
| ID | `INV-NNN` |
| Regra | frase única, verificável |
| Entidades | quais agregados toca |
| Garantia | banco (constraint) · domínio (validação) · ambos |
| Teste | como se prova a violação impossível |
| Efeito colateral | o que acontece quando alguém tenta violar |

## Onde a invariante é garantida
| Nível | Garante | Exemplo |
|---|---|---|
| Banco | sempre, inclusive fora da app | `CHECK (valor >= 0)`, `UNIQUE`, FK, exclude |
| Domínio | regra com contexto | estado da FSM, permissão, cálculo |
| Ambos | o caso bom | dinheiro: `CHECK` + validação com mensagem |

Invariante só na UI não é invariante.

## Atores e estado
Para cada ator, o que muda no sistema quando ele age? Isso vira transição de FSM
(`references/state-machines.md`) e permissão no contrato (`references/interface-contracts.md`).

## Saída
Tabela de atores, matriz de fronteira por tenant, lista `INV-NNN` com garantia e teste.
