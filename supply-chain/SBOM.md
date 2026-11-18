# SBOM — dz23-arsenal

> **Gerado** por `scripts/gera-sbom.py` dos lockfiles reais. Não edite à mão — o gate (`sbom:verifica`) reprova divergência. Formato CycloneDX 1.5.

- **93** componentes de biblioteca (npm, do `package-lock.json`), todos com `integrity` sha512 (0 sem hash).
- **3** componentes de aplicação (os MCP + a superfície Python stdlib-only).

## Componentes de biblioteca por projeto

| Projeto | Dependências (npm) |
|---|---:|
| pentagi-mcp | 93 |

## Cadeia mínima, por desenho

- `dz23-subagents-universal-mcp`: **zero dependências** de terceiros (toda a lógica em stdlib Node) — menor superfície de ataque possível.
- Scripts Python do arsenal: **stdlib apenas** no runtime; `jsonschema` entra só no CI.
- Dependabot acompanha os lockfiles npm; Gitleaks e CodeQL cobrem segredo e SAST.

