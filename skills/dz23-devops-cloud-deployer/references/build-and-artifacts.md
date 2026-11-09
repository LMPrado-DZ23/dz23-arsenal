# Pipeline e artefato

## Princípio: um build, muitos ambientes
O artefato que passa no gate é **o mesmo** que vai para produção. Rebuild por ambiente reintroduz diferença (versão de dependência, timestamp, cache) — proibido.

```
commit → build (imagem + digest) → gate (teste/scan) → registry → staging (mesmo digest) → produção (mesmo digest)
```

## Etapas mínimas
1. **Checkout** com SHA fixo (não branch flutuante).
2. **Lint/typecheck** — falha bloqueia.
3. **Unit + integração** — com banco/serviço efêmero.
4. **Build** com cache declarado; tag = `<commit-sha>` + semver quando houver release.
5. **Scan de imagem** (trivy/grype): falha em `CRITICAL`/`HIGH` com exceção registrada.
6. **SBOM** gerado e assinado.
7. **Push** no registry com o digest registrado.
8. **Deploy** em staging; smoke; promoção para produção com o mesmo digest.

## Determinismo e cache
- Cache de camada (BuildKit/GHA cache) é permitido — declare a chave (`hashFiles(lockfile)`).
- Cache não pode servir dependência de branch diferente.
- Lockfile versionado; `npm ci`/`pip install -r requirements.txt --require-hashes`.

## Versionamento do artefato
| Estratégia | Uso |
|---|---|
| SHA do commit | sempre; rastreabilidade exata |
| Semver/tag | release publicada |
| `latest` | **só dev**, nunca no caminho de deploy |

Promoção usa o digest, não a tag: `image@sha256:…`.

## Gates que bloqueiam
Gate que não bloqueia é telemetria. Defina: teste falha → para; scan crítico → para; política (licença, base proibida) → para; aprovação manual em produção → para até a aprovação.
Exceção é registrada com justificativa e prazo, nunca silêncio.

## Tempo de pipeline
Metas: PR ≤ 10 min, release ≤ 20 min. Acima, paralelize teste, cache agressivo e remova etapa que não bloqueia nada.

## Reprocessamento
Job que falhou por infra pode repetir; job que falhou por teste **não** — repetir até passar é mascarar. Registre a diferença no relatório.

## Critério de saída
(a) um build por commit; (b) digest registrado e usado na promoção; (c) gates que bloqueiam; (d) SBOM e scan; (e) tempo medido.
