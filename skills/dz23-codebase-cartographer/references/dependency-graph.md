# Grafo de dependências e camadas

## Pasta não é arquitetura
`controllers/`, `services/`, `repositories/` é a intenção. O grafo de import revela o que existe de fato — e onde a intenção foi abandonada.

## Como levantar o grafo (read-only)
```bash
# JS/TS — imports por arquivo
rg -n "^(import|export).*from ['\"]\./" src --no-heading

# Python — imports absolutos e relativos
rg -n "^(from|import) " src --no-heading

# quem importa um módulo específico
rg -n "from ['\"].*<modulo>['\"]" src

# arquivos mais importados (hot spots de acoplamento)
rg -o "from ['\"]([^'\"]+)['\"]" -r '$1' src | sort | uniq -c | sort -rn | head -20
```
Ferramenta de grafo quando existir: `madge` (JS), `pydeps`/`import-linter` (Python), `go list -deps`, `cargo tree`. Se não existirem, `rg` acima resolve o essencial — e o mapa diz qual método usou.

## O que registrar
| Achado | Por que importa |
|---|---|
| **Ciclos** (A → B → A) | acoplamento que impede extrair/testar |
| **Camada violada** (controller importando ORM direto) | regra do repo quebrada; risco em mudança |
| **Hub** (módulo importado por 20+ arquivos) | mudança ali tem blast radius grande |
| **Folha** (sem dependência interna) | candidato seguro para testes/mudança |
| **Módulo órfão** (ninguém importa) | código morto ou entrada por rota dinâmica — verificar antes de apagar |
| **Dependência circular de pacote** no monorepo | build quebra em ordem aleatória |

## Camadas de fato
Descreva o fluxo real de uma chamada, não o desenho bonito:
```
HTTP (src/routes/orders.ts:12)
  → controller (src/controllers/order.ts:34)
    → service (src/services/order.ts:88)      ← regra de negócio aqui?
      → repo (src/repositories/order.ts:41)
        → ORM (prisma) → Postgres
```
Se a regra de negócio está no controller, o mapa diz isso — não corrija, registre.

## Dependência externa crítica
Liste os pacotes que, se mudarem, quebram o sistema: ORM, framework web, auth, fila, SDK de pagamento. Versão e onde é usada. Dependência crítica sem teste é risco P1.

## Ciclo: como provar
```
A importa B (src/a.ts:3) → B importa C (src/b.ts:5) → C importa A (src/c.ts:9)
```
Ciclo afirmado sem a cadeia de três linhas é boato.

## Classificação de impacto
Toda mudança cai num dos três níveis — e o nível define o rigor do teste:

| Nível | Critério | Exemplos | Rigor |
|---|---|---|---|
| **BAIXO** | função privada/folha, 1 consumidor, sem contrato exposto | helper interno, formatter | teste unitário do arquivo |
| **MÉDIO** | contrato interno, 2–5 consumidores, mesmo domínio | service usado por 3 rotas | integração do domínio + revisão |
| **ALTO** | middleware de auth, `tenant_id`, schema de produção, tipos globais, design system base | `src/middleware/tenant.ts` | teste E2E + revisão + plano de rollback |

Regra prática: **se o arquivo é importado por mais de 20 arquivos ou aparece no spine, é ALTO** até prova em contrário.

## Callers e consumidores
```bash
# quem importa o módulo
rg -n "from ['\"].*<modulo>['\"]" -l

# quem chama a função
rg -n "<funcao>\(" -l

# testes que cobrem o caminho
rg -n "<funcao>\(" tests/ e2e/ -l

# co-change: arquivos que costumam mudar junto
git log --since="6 months ago" --name-only --pretty=format: -- <arquivo> | sort | uniq -c | sort -rn | head -10
```
Co-change alto é sinal de fronteira mal cortada — mudar um sempre exige mudar o outro.

## Saída
Grafo textual do caminho crítico, tabela de hubs/hubs/órfãos, ciclos com a cadeia, e a nota do método usado (`rg` ou ferramenta).
