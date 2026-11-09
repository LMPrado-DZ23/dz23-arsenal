# Runbook de deploy e rollback

## Identificação
- Serviço:
- Ambiente: staging | produção
- Versão/digest atual:
- Versão/digest novo:
- Janela:
- Aprovador:

## Pré-condições
- [ ] Imagem publicada com digest e scan sem CRITICAL
- [ ] SBOM gerado e anexado
- [ ] Migração compatível com N-1 aplicada (se houver)
- [ ] Backup verificado (se muda dado)
- [ ] Rollback ensaiado em staging, tempo medido: ____
- [ ] Painel e alerta do caminho novo ativos
- [ ] Plantão avisado

## Critério de sucesso
- Erro 5xx ≤ ____% por 10 min
- p95 ≤ ____ ms
- Readiness de todos os pods
- Smoke: ____

## Critério de abortar (gatilho de rollback)
- Erro 5xx > ____% por 5 min, **ou**
- p95 > ____ ms por 5 min, **ou**
- readiness falhando em ≥ ____ pods, **ou**
- falha no smoke

## Deploy
```bash
# Argo/Flux: atualizar digest no repositório de manifesto (commit)
# kubectl direto (quando autorizado):
kubectl -n <ns> set image deploy/<app> app=<registry>/<app>@sha256:<digest>
kubectl -n <ns> rollout status deploy/<app> --timeout=5m
```

## Verificação pós-deploy
```bash
kubectl -n <ns> get pods -l app=<app> -o wide
kubectl -n <ns> logs deploy/<app> --tail=100 | grep -i error
curl -fsS https://<host>/health          # deve conter o git_sha novo
```

## Rollback
```bash
# 1. imagem anterior (segundos)
kubectl -n <ns> rollout undo deploy/<app>
kubectl -n <ns> rollout status deploy/<app> --timeout=5m

# 2. feature flag desligada (se aplicável)
# <comando/procedimento>

# 3. migração: reverter ou roll-forward — descrever
```

## Pós-rollback
- [ ] Health e smoke verdes na versão anterior
- [ ] Métrica voltou ao baseline
- [ ] Incidente registrado (ID, causa provável, ação)
- [ ] Quem foi avisado e quando

## Riscos e o que NÃO foi testado
-
