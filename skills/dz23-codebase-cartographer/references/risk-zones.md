# Zonas de risco e blast radius

## O que é zona de risco
Área onde uma mudança pequena pode causar dano grande — ou porque é central, ou porque é frágil, ou porque ninguém entende.

## Classificação
| Zona | Sinal | Consequência de errar |
|---|---|---|
| **Núcleo de dinheiro** | cálculo de preço, cobrança, repasse, estorno | perda financeira, auditoria |
| **Autenticação/autorização** | middleware, guard, policy de tenant | vazamento entre clientes |
| **Migração/schema** | alteração de coluna, drop, backfill | perda de dado |
| **Fila/evento** | consumidor, idempotência, retry | duplicidade, efeito colateral duplo |
| **Integração externa** | pagamento, e-mail, gateway | falha silenciosa, estado inconsistente |
| **Caminho crítico de performance** | query quente, endpoint principal | indisponibilidade |
| **Código sem teste** | área central sem cobertura | regressão invisível |

## Blast radius de uma mudança
Responda, com evidência:
1. Quem **importa** o arquivo alterado? (lista, não "alguns")
2. Quais **rotas/endpoints** passam por ele?
3. Quais **jobs/workers** dependem dele?
4. Quais **tabelas** são lidas/escritas a partir dele?
5. Existe **teste** cobrindo esses caminhos? qual comando?

Se o item 5 é "não", o blast radius é **desconhecido** — e isso é o achado mais importante do mapa.

## Áreas frágeis (fragilidade estrutural)
- `catch` que engole erro e segue.
- Retry sem backoff, sem limite, ou retry de operação não idempotente.
- Estado compartilhado mutável entre requests.
- Query dentro de loop.
- Timeout ausente em chamada externa.
- `any`/`unknown` generalizado em área crítica (perde a checagem que protege).

Cada item com arquivo:linha. Frase genérica não entra no mapa.

## "Não tocar sem plano"
Seção obrigatória do mapa:
```
NÃO TOCAR SEM PLANO
- src/billing/calc.ts — núcleo de cálculo; sem teste; 3 escritores concorrentes.
- migrations/2025_*.sql — irreversível, sem down.
- src/auth/tenant.ts — toda query depende; erro aqui vaza dados.
```
O valor da skill é metade mapa, metade aviso.

## Como reduzir risco (sugestão, não execução)
Teste de caracterização antes de refatorar; flag para desligar caminho novo; comparação de saída antiga × nova; migração expand/contract. A skill recomenda — não implementa.

## Saída
Tabela de zonas com classificação, blast radius por mudança pedida (com respostas 1–5), lista de fragilidades com ponteiros, e a seção "não tocar sem plano".
