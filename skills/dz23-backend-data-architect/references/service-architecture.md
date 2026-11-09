# Arquitetura de serviço — fronteiras, eventos e resiliência

## Como escolher a fronteira
Fronteira boa é a que **fecha uma transação** e **tem dono**. Pasta é organização; serviço é unidade de falha, deploy e dado.
- Monolito modular é o padrão. Microserviço só com um destes motivos comprovados: escala muito diferente por domínio, time autônomo com deploy independente, isolamento de falha exigido por contrato, ou linguagem/runtime obrigatório.
- Fronteira por dado: quem escreve é dono. Dois serviços escrevendo a mesma tabela é acoplamento disfarçado.
- Fronteira por transação: se precisa de atomicidade entre A e B, A e B são o mesmo serviço ou você aceita consistência eventual com compensação.

## Comunicação
| Necessidade | Escolha |
|---|---|
| Chamador precisa do resultado para responder | síncrono (HTTP/gRPC), com timeout curto |
| Efeito colateral que pode esperar | evento/fila, com consumidor idempotente |
| Notificar muitos interessados | evento publicado (fan-out), nunca chamada em cadeia |
| Consultar dado de outro domínio | cópia local via evento ou API de leitura — nunca join entre bancos |

Toda chamada externa: **timeout declarado**, retry com backoff exponencial e jitter, limite de tentativas, e idempotência do lado de quem executa. Sem timeout, o serviço herda a latência do outro.

## Idempotência
Operação com efeito colateral precisa ser segura em repetição:
- chave de idempotência persistida (tabela `idempotency_keys` com hash da requisição, resposta e TTL);
- chave repetida com payload diferente → conflito explícito (`409`), não execução dupla;
- processamento de fila com `event_id` único e deduplicação;
- webhook: guardar id do evento do provedor e ignorar repetido.

## Consistência e eventos
- **Outbox**: grava o estado e o evento na mesma transação; um processo lê o outbox e publica. Evento perdido por falha de broker deixa de ser possível.
- **Inbox**: o consumidor registra o evento processado na mesma transação do efeito.
- **Saga**: só quando a operação cruza serviços. Cada passo tem compensação explícita; documente o que acontece no meio do caminho.
- Consistência eventual exige estado observável (status da operação), não promessa.

## Falha parcial
- Circuit breaker nas dependências caras; degradar com resposta útil em vez de erro genérico.
- Bulkhead: pool/fila separada para dependência lenta não derruba o resto.
- Timeout de banco menor que o timeout da requisição; requisição nunca espera mais que o cliente.
- Falha de escrita em lote: processar por item com resultado parcial explícito (`207`/relatório), não abortar tudo silenciosamente.
- Reprocessamento: toda fila tem DLQ e procedimento documentado de replay.

## Jobs e agendamento
- Job idempotente, com lock (advisory lock, `SELECT ... FOR UPDATE SKIP LOCKED` ou lease) para não rodar duas vezes com réplica.
- Todo job tem métrica de duração, falha e atraso; job silencioso é job quebrado há semanas.
- Backfill é job com cursor persistido e retomável.

## Critério de saída da arquitetura
Antes de codar: (a) fronteiras e donos escritos; (b) fluxos síncronos e assíncronos desenhados; (c) timeouts/retries/idempotência definidos para cada dependência; (d) modo de falha de cada integração descrito; (e) ADR registrado em `templates/adr.md`.
