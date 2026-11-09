# Quality gates — evidência, não promessa

| Gate | PASS quando | Evidência mínima |
|---|---|---|
| Imagem | multi-stage, digest, non-root, sem segredo | `docker history` + Dockerfile |
| Reprodutibilidade | mesmo commit → mesmo digest (ou declarado) | dois builds comparados |
| Pipeline | um build por commit, gates que bloqueiam | log do run |
| Segredos | zero no repo/imagem/log | grep + scan |
| Identidade | CI por OIDC; role de deploy separada | config do pipeline |
| Config | validada na inicialização; paridade | `/health` com `git_sha` |
| Manifesto | digest, probes, limits, securityContext | `kubectl get -o yaml` |
| Deploy | progressivo, critério de sucesso/aborto | histórico de rollout |
| Observabilidade | erro/latência por versão + alerta | painel + alerta |
| Rollback | ensaiado, tempo medido | execução em staging |
| Backup | restauração verificada | restore em ambiente separado |
| Supply chain | SBOM + scan + assinatura | artefatos do build |

**Estados:** `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`, `BLOCKED_BY_EXTERNAL_DEPENDENCY`. Deploy não executado não é `PASS`.

## Severidade

**BLOCKER (não publica):**
- Segredo em imagem, repositório, log ou artifact.
- Imagem de produção por tag mutável (`latest`) em vez de digest.
- Deploy sem health check/readiness.
- Gate desabilitado (teste/scan) para "destravar".
- Ausência de caminho de rollback.
- `DROP`/delete de namespace/PVC sem backup verificado e autorização.
- CI com credencial de admin/root na nuvem.
- Imagem com CVE crítica publicada sem exceção registrada.

**MAJOR (publica com ressalva):**
- Sem resource requests/limits.
- Rollback nunca ensaiado.
- Sem alerta/métrica no caminho novo.
- `latest` em staging.
- Sem PDB (risco em drain).
- Migração incompatível com N-1.
- Rollout sem `progressDeadlineSeconds`.

**MINOR (registra e segue):**
- Tamanho de imagem acima do necessário.
- Log sem `git_sha`.
- Runbook incompleto.
- SBOM gerado fora do build.

## Checklist final
- [ ] Imagem por digest, multi-stage, non-root.
- [ ] Dois builds do mesmo commit comparados.
- [ ] Nenhum segredo em artefato (grep + scan).
- [ ] CI autentica por OIDC; role de deploy separada.
- [ ] Manifesto com probes, limits e securityContext.
- [ ] Estratégia de deploy com critério de sucesso e aborto.
- [ ] Smoke pós-deploy executado.
- [ ] Métrica de erro/latência por versão e alerta.
- [ ] Rollback ensaiado com tempo medido.
- [ ] Backup restaurado em ambiente separado (quando muda dado).
- [ ] Runbook escrito; riscos e `NOT_TESTED` declarados.
