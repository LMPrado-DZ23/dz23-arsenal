# Rollback Plan — <projeto> — <release>

## Pré-deploy (preencher ANTES do deploy)
- Trigger: health check falha **OU** smoke FAIL **OU** erro > 1% em 5 min
- Ação: <comando kubectl/helm específico>
- Última versão estável: <digest>
- Tempo esperado: <min>
- Validação: `/healthz` e `/readyz` verdes na versão anterior + smoke PASS
- Responsável: <nome/role>
- Comunicação: <canal + template da mensagem>
- Impacto em dados: <migração reversível? forward-fix?>

## Durante o rollback
- [ ] Notificar o canal combinado
- [ ] Executar o comando de rollback
- [ ] Validar `/healthz` e `/readyz`
- [ ] Rodar smoke E2E
- [ ] Registrar em `deployment-report.md`
- [ ] Abrir RCA de incidente se a indisponibilidade passar de 5 min

## Pós-deploy (se não acionado)
- Rollback permanece disponível por 30 dias
- Revisar e arquivar o plano em: <data>

## Referência rápida
```bash
# kubectl
kubectl rollout undo deployment/app -n <ns>
kubectl rollout status deployment/app -n <ns> --timeout=120s
kubectl get deployment app -n <ns> -o jsonpath='{.spec.template.spec.containers[0].image}'

# helm
helm rollback app -n <ns> --wait
helm history app -n <ns>
```
