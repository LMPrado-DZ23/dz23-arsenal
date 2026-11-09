# Segredos, identidade e menor privilégio

## Segredo
- Vive em secret manager (Vault, AWS/GCP/Azure Secret Manager, SOPS+age, `Secret` do cluster com cifra).
- **Nunca**: no repositório, na imagem, no `ARG`, no log, no trace, na mensagem de erro, no artifact de CI.
- Rotação documentada: quem troca, janela, como o app recarrega, como validar.
- Segredo vazado é **revogado**, não "monitorado".

## Identidade do CI/CD — OIDC, sem chave estática
```yaml
permissions:
  id-token: write      # GitHub Actions → cloud via OIDC
  contents: read
```
- Provedor confia no emissor OIDC e na claim (`repo:org/repo:ref:refs/heads/main`) — não em chave longa.
- Chave estática só quando o provedor não suporta OIDC; aí: escopo mínimo, expiração, rotação e registro.

## Menor privilégio
- Pipeline de build **não** tem permissão de produção; deploy tem role própria e separada.
- Runtime com service account dedicada, `automountServiceAccountToken: false` quando não precisa.
- RBAC do cluster: `Role`/`RoleBinding` por namespace; `ClusterRole` só com justificativa.
- IAM: ação específica em recurso específico (`s3:PutObject` em bucket/recurso, não `s3:*`).

## Superfície de ataque do runtime
- `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`.
- `seccompProfile: RuntimeDefault`.
- Sem `hostPath`, sem `hostNetwork`, sem `privileged` sem justificativa escrita.

## Auditoria
- Quem publicou, o quê (digest), quando, de qual commit, aprovado por quem.
- Log de auditoria do cloud (CloudTrail/audit log) com retenção.
- Acesso a segredo é logado e revisado.

## Sealed Secrets / External Secrets Operator
Manifesto em Git não pode conter segredo em texto puro. Duas saídas:
- **Sealed Secrets** (Bitnami): `kubeseal` cifra com a chave pública do cluster; o `SealedSecret` pode ir
  no Git e só o controller decifra.
```bash
kubectl create secret generic app-secrets --from-env-file=.env.prod \
  --dry-run=client -o yaml | kubeseal --format yaml > infra/sealed-secret.yaml
```
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata: {name: app-secrets, namespace: production}
spec:
  encryptedData: {DATABASE_URL: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq...}
```
- **External Secrets Operator**: sincroniza do provedor (AWS Secrets Manager, GCP SM, Azure KV, Vault)
  para um `Secret` do cluster; o valor nunca fica no Git.
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: {name: app-secrets, namespace: production}
spec:
  refreshInterval: 1h
  secretStoreRef: {name: aws-sm, kind: ClusterSecretStore}
  target: {name: app-secrets}
  data:
    - {secretKey: DATABASE_URL, remoteRef: {key: app/prod/database, property: url}}
```

## Rotação de credenciais
Procedimento com data e responsável: gerar nova credencial → publicar no secret manager → app recarrega
(reload) ou reinicia (restart) → validar → revogar a antiga. Registre janela e rollback (voltar a antiga
por algumas horas).

## Auditoria de acesso
Quem leu/alterou segredo, quando e de onde. Acesso a segredo é logado no provedor e revisado; alerta em
leitura inesperada de produção.

## Critério de saída
(a) zero segredo no artefato/repo; (b) CI autentica por OIDC; (c) role de deploy separada; (d) securityContext restritivo; (e) trilha de auditoria do release.
