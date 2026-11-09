# Supply chain — SBOM, assinatura e scan

## Por que
A imagem é o que roda. Se você não sabe o que tem dentro, não sabe o que está exposto.

## SBOM
- Gerar (Syft, `docker sbom`, `npm sbom`) no mesmo commit do build.
- Formato SPDX ou CycloneDX; guardar junto do artefato (release/registry).
- SBOM desatualizado é pior que ausente — gere no build, não "depois".

## Scan de secrets

**Primário (se instalado):**
```bash
gitleaks detect --source . --report-path security/secrets-scan.json
# exit 0 = limpo · exit 1 = findings (bloqueia)
```

**Fallback (se gitleaks ausente):**
```bash
trivy fs --scanners secret --format json \
  --output security/secrets-scan.json \
  --exit-code 1 \
  .
# exit 0 = limpo · exit 1 = findings (bloqueia)
# NÃO instalar gitleaks só para este gate; trivy cobre
# segredo em arquivo e em imagem.
```

**Critério de aceite:** `security/secrets-scan.json` existe **E** `.Results[] | length == 0`. Se ambos
falharem, `BLOCKED_BY_EXTERNAL_DEPENDENCY` com a dependência exata.

## Scan de vulnerabilidade
| Camada | Ferramenta típica |
|---|---|
| Imagem/SO | Trivy, Grype |
| Dependência | Dependabot, `npm audit`, `pip-audit` |
| IaC/manifesto | Checkov, kube-linter, Conftest |
| Segredo | gitleaks/trufflehog no diff |

Política: `CRITICAL` bloqueia; `HIGH` bloqueia com prazo de exceção; exceção registrada com issue e data.

## Assinatura e proveniência
- Assinar imagem (cosign/Sigstore) e verificar no admission controller.
- Attestation de build (SLSA) quando o provedor oferece; registrar o digest assinado.
- Registry privado com imutabilidade de tag habilitada quando possível.

## Base e atualização
- Base renovada por pipeline agendado (rebuild semanal) — imagem com 6 meses sem rebuild está desatualizada mesmo com código igual.
- Dependência com licença incompatível bloqueia (política no gate).

## Critério de saída
(a) SBOM por build; (b) scan com política e exceção registrada; (c) assinatura verificada; (d) base com rebuild agendado; (e) digest auditável.
