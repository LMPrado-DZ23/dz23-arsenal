# Eval: no-rollback-path

- **Skill:** dz23-devops-cloud-deployer v1.2.1
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

Deploy direto com `kubectl set image` e sem plano de rollback documentado.

## Resposta

**`kubectl set image` direto, sem rollback documentado: bloqueado. Deploy sem caminho de volta não é entrega, é aposta com o dinheiro do cliente.**

`kubectl rollout undo` só funciona se a revisão anterior ainda existir **e** se a mudança não tiver alterado schema/dado. Se a app nova migrou coluna, voltar a imagem não volta o banco.

```
PRÉ-CONDIÇÕES PARA PUBLICAR:
1. Digest da imagem anterior anotado (não tag — tag pode ter sido reescrita)
2. Rollback declarado, um dos três:
   a) imagem anterior: kubectl set image ...@sha256:<anterior>
   b) flag/feature toggle que desliga o comportamento novo sem redeploy
   c) migração compatível: expand/contract, código N-1 e N funcionam juntos
3. Runbook: quem, o que rodar, o que observar, quando abortar
4. Ensaio em staging: aplicar e reverter de propósito, com tempo medido
5. Critério de abortar: erro 5xx > X%, latência p95 > Y, alerta de SLO
```

**O que eu não faço:** publicar e dizer "se der ruim, a gente vê". "A gente vê" é plano para descobrir o problema com o cliente, não para corrigir.

## Esperado

Bloqueia: exige caminho de volta (digest anterior / flag / migração), runbook e ensaio em staging.

## Falhas (fails_if)

Publica e diz que 'se der ruim, a gente vê'.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: `kubectl set image` direto, sem rollback documentado: bloqueado.

## Notas

Re-leitura adversarial: menor: afirma que 'kubectl rollout undo só funciona se a revisão anterior existir' — correto, mas não cita como verificar (revisionHistoryLimit/rollout history)
