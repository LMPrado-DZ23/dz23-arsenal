# SBOM — dz23-arsenal

> **Gerado** por `scripts/gera-sbom.py` dos `package.json` committados. Não edite à mão — o gate (`sbom:verifica`) reprova divergência. Formato CycloneDX 1.5.

- **3** dependências diretas de npm (faixa declarada no `package.json`).
- **3** componentes de aplicação (os MCP + a superfície Python stdlib-only).

## Política de versão (deliberada neste repo)

Lockfiles npm **não são versionados** aqui (ver `.gitignore`): a reprodutibilidade vem das faixas no `package.json`, não de um lock gerado por máquina. Por isso o SBOM committado lista as **dependências diretas declaradas**; a árvore resolvida completa + integrity sha512 é artefato de CI (gerado por `npm install`), não entra aqui — assim o `--check` é determinístico em qualquer SO.

## Dependências diretas por projeto

| Projeto | Deps diretas (npm) |
|---|---:|
| pentagi-mcp | 3 |

## Cadeia mínima, por desenho

- `dz23-subagents-universal-mcp`: **zero dependências** de terceiros (toda a lógica em stdlib Node) — menor superfície de ataque possível.
- Scripts Python do arsenal: **stdlib apenas** no runtime; `jsonschema` entra só no CI.
- Dependabot acompanha os `package.json`; Gitleaks e CodeQL cobrem segredo e SAST.

