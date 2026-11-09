# Rollback, backup e continuidade

## Regra
Toda release tem volta. Se você não sabe reverter em minutos, não sabe publicar.

## Três formas de voltar
1. **Imagem anterior** por digest (`kubectl rollout undo`, retarget de Service, retag no GitOps) — segundos.
2. **Feature flag desligada** — desacopla o código novo do comportamento novo; segundos e sem redeploy.
3. **Migração reversível** ou roll-forward documentado — minutos; a mais arriscada.

## Rollback automático
Dispare por métrica, não por "achismo": erro 5xx acima do limite, p95 dobrou, readiness falhando em N pods, health check externo falhando. Ferramentas: `argo rollouts`, Flagger, alerta + automação de pipeline.
Automatizar rollback exige teste do próprio rollback — automação não ensaiada é risco.

## Ensaio obrigatório
Em staging: publicar versão N, publicar N+1, reverter para N, verificar health e funcionalidade. Registre tempo. Rollback que nunca rodou é hipótese.

## Backup e restauração
- Backup **verificado**: restaurar em ambiente separado e provar que o dado está íntegro. Backup nunca restaurado não é backup.
- Antes de mudança destrutiva (drop, migração irreversível, delete de namespace/PVC): snapshot + confirmação.
- RPO/RTO declarados por serviço; quem chama o restore e em quanto tempo.
- Delete de namespace/PVC é irreversível: exige confirmação explícita e lista do que será perdido.

## Migração no rollback
Código N-1 deve funcionar com schema N (expand/contract). Se a migração quebra N-1, rollback de aplicação **não** salva: o plano precisa incluir o dado.

## Runbook mínimo
`templates/deploy-runbook.md`: gatilho, comando de rollback, verificação pós-rollback, quem avisar, tempo alvo, critério de escalar.

## Critério de saída
(a) volta definida por digest; (b) rollback automático por métrica (quando aplicável); (c) rollback ensaiado com tempo medido; (d) backup verificado; (e) runbook escrito; (f) RPO/RTO declarados.
