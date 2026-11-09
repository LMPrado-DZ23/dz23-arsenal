# Entrypoints e spine

## Regra
Entrypoint é onde a execução começa. Spine é a cadeia mínima que liga entrada → domínio → dado. Sem os dois, não se sabe onde uma mudança encosta.

## Backend
| O que procurar | Como |
|---|---|
| onde o servidor sobe | `rg -n "app\.listen\|server\.listen\|uvicorn\.run\|http\.createServer\|func main\("` |
| middlewares globais | `rg -n "app\.use\(\|middleware\.Use\|@app\.middleware"` — auth, tenant, error handler |
| roteador principal | `rg -n "app\.use\(['\"]/api\|router\.mount\|include_router"` |
| registro de rota | `rg -n "(get\|post\|put\|patch\|delete)\(['\"]/"` |
| erro global | `rg -n "errorHandler\|exception_handler\|ErrorHandler"` |

Meia dúzia de greps responde onde o processo nasce, o que passa por toda requisição e onde a rota é declarada — sem abrir um arquivo de lógica.

## Banco
| O que procurar | Como |
|---|---|
| schema | `prisma/schema.prisma`, `models/*`, `db/schema.rb`, `*.sql` |
| migrações | `migrations/`, `alembic/`, `db/migrate/`, `prisma/migrations/` |
| client/pool | `rg -n "new PrismaClient\|createPool\|SQLAlchemy\|psycopg\|mongoose\.connect"` |
| transação | `rg -n "\$transaction\|session\.begin\|BEGIN;"` |

## Frontend
| O que procurar | Como |
|---|---|
| rotas | `app/**/page.*`, `pages/**`, `router/**`, `routes/**` |
| providers globais | `rg -n "<(QueryClientProvider\|ThemeProvider\|AuthProvider\|StoreProvider)"` |
| cliente HTTP | `rg -n "axios\.create\|fetch\(|createApi\|useQuery\("` |
| design system | `components/ui/`, `design-system/`, tokens |

## Workers e agentes
| O que procurar | Como |
|---|---|
| fila | `rg -n "queue\.add\|\.process\(\|consumer\|subscribe\("` |
| cron | `rg -n "cron\|schedule\|@Scheduled\|setInterval"` |
| agente/tool | `rg -n "tools\s*[:=]\|toolDefinitions\|functionCall"` |
| webhook | `rg -n "webhook\|/hooks/"` |

## Spine mínimo
```
<entry>:<linha>            (server sobe)
  → <middleware global>:<linha>   (auth / tenant / erro)
    → <router>:<linha>
      → <handler>:<linha>
        → <service>:<linha>
          → <repo>:<linha> → <tabela>
```

Cada seta com ponteiro. Spine sem ponteiro é desenho.

## Sinais de que o spine está errado
- Existe mais de um servidor HTTP (monorepo, dois deploys) → um spine por serviço.
- Middleware aplicado por rota em vez de global → auth pode faltar em rota nova; registre.
- Worker com lógica de domínio duplicada da API → dois spines que precisam convergir.

## Saída
Tabela de entrypoints por tipo (HTTP, CLI, worker, cron, webhook) com arquivo:linha e se exige auth/tenant; spine do caminho crítico.
