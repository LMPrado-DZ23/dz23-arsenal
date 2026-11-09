# Requisitos não funcionais e thresholds

## Regra
NFR sem **número** e sem **método de verificação** não é requisito — é desejo. "Deve ser seguro" não
especifica nada; "OWASP Top 10 sem achado crítico, verificado por ZAP no CI" especifica.

## Categorias e threshold típico
| Categoria | Threshold exemplo | Como verificar |
|---|---|---|
| Performance | p50 < 100 ms, p95 < 500 ms, p99 < 2 s | k6/artillery sob carga declarada |
| Segurança | sem crítico no OWASP Top 10; TLS 1.2+; 0 segredo no scan | ZAP, trivy, gitleaks |
| Acessibilidade | WCAG 2.2 AA; Lighthouse a11y ≥ 90 | axe + revisão manual de teclado |
| Disponibilidade | 99,9% (≈ 43 min/mês); RTO 15 min; RPO 5 min | medição de SLO + restore ensaiado |
| Observabilidade | 100% das rotas críticas com log estruturado e trace | inspeção + alerta |
| Escalabilidade | N usuários simultâneos, M req/s | teste de carga no cenário de pico |
| Manutenibilidade | cobertura > X% no núcleo; complexidade < Y | cobertura + lint |

## Template
```
NFR-NNN · <categoria> — <título>
Threshold: <métrica concreta e janela>
Verificação: <ferramenta/comando>
Responsável: <quem implementa> / <quem verifica>
Risco se violado: ALTO | MÉDIO | BAIXO
```

## Onde cada NFR é verificado
- Performance e escalabilidade: `dz23-e2e-browser-verifier` (fluxo) + teste de carga próprio.
- Acessibilidade: `dz23-e2e-browser-verifier` (axe + teclado).
- Segurança: `security-review`.
- Disponibilidade, rollback, backup: `dz23-devops-cloud-deployer`.
- Cobertura e complexidade: pipeline do projeto (`delivery-pipeline`).

## NFR por contexto
Nem todo projeto precisa de todos. Declare `N/A` **com motivo**:
```
NFR-004 · Disponibilidade — N/A nesta entrega: ferramenta interna, sem SLA contratado (ADR-012).
```

## Antipadrões
- "Rápido" sem percentil e sem carga.
- Threshold impossível de medir (sem ferramenta, sem ambiente).
- NFR que ninguém vai verificar (declarado e esquecido).
- NFR copiado de template sem relação com o produto.

## Saída
Lista `NFR-NNN` com threshold, método, responsável, risco e a nota de onde é verificado — ou `N/A` motivado.
