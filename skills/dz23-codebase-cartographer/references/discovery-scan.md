# Varredura inicial e inventário

## Objetivo
Em 10–15 minutos: saber o que é este repo, como se constrói, onde começa e onde estão os testes. Sem isso, qualquer leitura profunda é chute.

## Topografia em 60 segundos
Três comandos e você sabe onde está:
```bash
# 1. árvore limpa (2 níveis, sem ruído)
find . -maxdepth 2 -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/vendor/*' | sort | head -60

# 2. contagem por extensão (o que é este repo de verdade)
find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15

# 3. manifests e config na raiz
ls -1 | rg -i "package.json|pyproject|Cargo.toml|go.mod|compose|Dockerfile|\.env\.example|Makefile|tsconfig|\.github"
```
Saída esperada: `STACK | ENTRYPOINTS | CONFIG | TAMANHO`. Se em 60 s você não sabe a stack, o repo tem mais de um projeto — encontre os manifests filhos.

## Bash concreto (Claude — fase 1)
```bash
git ls-files | wc -l                                   # tamanho real (tracked)
git ls-files | rg -c "\.(ts|tsx)$"                     # por linguagem
rg -n "if __name__ ==|func main\(|app\.listen\(|http\.createServer" --type-add 'src:*.{py,go,ts,js}' -tsrc
rg --files -g "Dockerfile*" -g "*.yml" -g "*.yaml" -g "*.toml" -g "*.json" | head -30
```

## Git intelligence (Claude — fase 2)
```bash
# hotspots: arquivos que mais mudaram nos últimos 6 meses
git log --since="6 months ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20

# últimos 14 dias: onde o time está mexendo agora (risco de conflito)
git log --since="14 days ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -15

# branches ativas
git branch -r --sort=-committerdate | head -10
```
Isso responde "onde dói" antes de abrir qualquer arquivo — e é o insumo dos hot spots.

## Ordem da varredura
1. **Raiz**: `ls` da raiz e de `src/`, `app/`, `packages/`. Nome de pasta já conta história.
2. **Manifestos**: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `*.csproj`, `composer.json`, `Gemfile`.
3. **Build e run**: scripts do manifest, `Makefile`, `justfile`, `turbo.json`, `nx.json`, `vite.config.*`, `webpack.config.*`.
4. **Runtime**: `Dockerfile`, `docker-compose*.yml`, `Procfile`, `*.service`, `vercel.json`, `fly.toml`.
5. **CI**: `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`.
6. **Testes**: `tests/`, `__tests__/`, `*.test.*`, `*.spec.*`, `e2e/`, `playwright.config.*`, `jest.config.*`, `vitest.config.*`.
7. **Dados**: `migrations/`, `prisma/schema.prisma`, `alembic/`, `db/`, `seeds/`.
8. **Docs**: `README.md`, `docs/`, `ADR*/`, `CONTRIBUTING.md`, `.editorconfig`, `AGENTS.md`/`CLAUDE.md`.

## Manifesto mínimo do mapa
| Campo | Como obter |
|---|---|
| Commit | `git rev-parse HEAD` |
| Data da leitura | data corrente |
| Branch | `git branch --show-current` |
| Linguagens | extensão × contagem de arquivos/linhas |
| Tamanho | nº de arquivos rastreados (`git ls-files | wc -l`) |
| Entry points | scripts do manifest + `main`/`index`/`app` + Dockerfile `CMD` |
| Testes | comando declarado + existe suíte rodando? |
| Migrações | pasta e ferramenta |
| Monorepo? | workspaces/packages/turbo/nx |

## Sinais de alerta na varredura
- README descreve stack que o manifest não confirma → **documentação mentindo**.
- Nenhum teste e nenhum CI → mudança é às cegas; registre como risco P0.
- `Dockerfile` com `COPY . .` e sem `.dockerignore` → build não reprodutível.
- Vários lockfiles de gerenciadores diferentes → conflito de toolchain.
- `node_modules`/`vendor` versionado → repo poluído; exclua da contagem.
- Monorepo sem workspace declarado → pacotes duplicando dependência.

## Amostragem declarada
Escreva no mapa:
```
LIDO: package.json, src/app.ts (entry), src/routes/*(3 de 12), prisma/schema.prisma, .github/workflows/ci.yml
NÃO LIDO: src/services/* (14 arquivos), frontend/* (62 arquivos)
CRITÉRIO: entry points + caminho da mudança pedida + schema
```
Amostragem sem critério é leitura aleatória disfarçada.

## Saída
Bloco de inventário no `codebase-map.md` + lista do que não foi lido.
