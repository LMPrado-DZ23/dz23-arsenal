# Priorização, estimativa e caminho crítico

## Priorização
Ordene por **valor ÷ esforço**, ajustado por risco e dependência, não por facilidade nem por quem gritou
mais alto.

| Critério | Pergunta |
|---|---|
| Valor | o que muda para o usuário/negócio quando existe? |
| Risco | essa fatia reduz uma incerteza grande? (aprendizado tem valor) |
| Esforço | intervalo de dias, não número |
| Dependência | destrava quantas outras? é pré-requisito? |
| Custo de atraso | o que quebra se não sair neste mês? |

MVP = menor conjunto que **entrega valor real** e **reduz o maior risco**. Não é "o que é mais barato".

## Estimativa honesta
- **Intervalo + premissas**: "2–4 dias, assumindo API legada acessível e sem migração".
- Quebre até a tarefa estimável (< 1 dia). Acima disso, a incerteza não está resolvida.
- Registre o que faria o intervalo mudar (a premissa que, se cair, dobra o esforço).
- Nunca apresente número único sem premissa; nunca use "média histórica" sem histórico real.

## Caminho crítico
Grafo de fatias → a maior cadeia de dependência é o caminho crítico. Ele define o prazo mínimo real,
independente de quantas pessoas você colocar.

```
SL-01 (contrato) → SL-02 (API) → SL-04 (UI) → SL-07 (E2E) = caminho crítico
SL-03 (export) pode ir em paralelo após SL-01
```

Regra: adicionar gente fora do caminho crítico não antecipa a entrega.

## Capacidade
- Capacidade real = pessoas × dias − reuniões − suporte − imprevisto (reserve ~20%).
- Planeje 70–80% da capacidade; 100% no papel é 100% de atraso na prática.
- Uma pessoa em duas frentes é meia pessoa em cada — declare, não esconda.

## Buffer
Buffer de integração no fim do caminho crítico, não distribuído em cada tarefa (senão vira folga consumida).
Quando o buffer acaba, o escopo é cortado explicitamente.

## Sinais de plano ruim
- Tudo no caminho crítico (nada em paralelo).
- Estimativas redondas e iguais ("3 dias" para 8 coisas).
- Nenhuma folga para integração/teste.
- Escopo maior que capacidade, sem corte registrado.

## Saída
Ordem de execução, caminho crítico, intervalos com premissas, capacidade considerada e buffer declarado.
