# Estratégias de deploy

## Escolha
| Estratégia | Quando | Custo | Volta |
|---|---|---|---|
| Rolling | padrão; serviço stateless | baixo | rollout undo |
| Blue-green | troca atômica, tolera 2× recurso | médio | trocar tráfego |
| Canary | medir risco em fração de tráfego | alto (análise) | retirar peso |
| Recreate | aceita downtime (batch/worker) | baixo | imagem anterior |
| Feature flag | desacoplar deploy de release | baixo | desligar flag |

Deploy ≠ release: publique com a feature desligada e ligue por flag quando fizer sentido.

## Rolling
- `maxUnavailable: 0` + `maxSurge: 1` para não reduzir capacidade; precisa de readiness correta.
- Rollout trava se o pod novo não fica Ready — configure `progressDeadlineSeconds` e observe.
```bash
kubectl rollout status deploy/app --timeout=5m
kubectl rollout undo deploy/app --to-revision=<n>
```

## Blue-green
- Duas stacks completas; tráfego troca por Service/ingress/LB.
- Valide a stack verde com smoke antes da troca; mantenha a azul pronta para voltar.
- Cuidado com estado compartilhado (banco, fila, cache) — a compatibilidade N-1 é obrigatória.

## Canary
- 5% → 25% → 100%, com análise automática de erro/latência.
- Critério de abortar explícito (ex.: erro > 1% ou p95 dobra) e automático.
- Requer métrica confiável por versão (label no pod/rota) — sem isso, canary é teatro.

## Critério de sucesso e de abortar
Antes do deploy: defina o que é sucesso (erro, latência, saturação) e o gatilho de aborto. Sem isso, ninguém decide no meio do incidente.

## Ordem com migração de dados
1. migração compatível (expand) → 2. deploy do código novo → 3. backfill → 4. remoção (contract). Ver `dz23-backend-data-architect`.

## Critério de saída
(a) estratégia escolhida com justificativa; (b) critério de sucesso e aborto escritos; (c) readiness validada; (d) volta disponível; (e) ordem com migração declarada.
