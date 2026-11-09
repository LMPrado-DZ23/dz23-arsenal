# Convenções e invariantes do repositório

## Por que
Convenção do repo vence gosto pessoal. Quem entra e "melhora o estilo" gera diff ruidoso e revisão hostil. O mapa descreve o que existe — não reforma.

## Onde a convenção está escrita
| Fonte | O que revela |
|---|---|
| `.editorconfig` | indentação, fim de linha, charset |
| `.eslintrc*`, `ruff.toml`, `.golangci.yml` | regras impostas de fato |
| `.prettierrc`, `biome.json` | formatação |
| `tsconfig.json` | strict, paths, target |
| `CONTRIBUTING.md` / `AGENTS.md` | regra social do repo |
| `docs/adr/` | decisões que não se rediscutem |
| histórico de commit | padrão de mensagem (Conventional? pt/en?) |
| testes existentes | como o repo prova comportamento |

## Padrões a extrair (com exemplo real)
| Dimensão | O que registrar | Exemplo |
|---|---|---|
| Nome de arquivo | kebab, camel, Pascal | `order-service.ts` |
| Nome de função | verbo + substantivo | `createOrder`, `findByTenant` |
| Erro | resultado, throw, código | `throw new AppError('SLOT_TAKEN', 409)` |
| Log | estruturado? campos? | `logger.info({ orderId }, 'order.created')` |
| Validação | schema na borda? | zod em `src/schemas/*` |
| Teste | arquivo ao lado? pasta? | `*.test.ts` co-locado |
| Commit | Conventional Commits? | `feat(orders): ...` |
| Camada | regra de negócio onde? | serviço, não controller |

Cada linha com **um exemplo e o arquivo** — convenção afirmada sem exemplo é opinião.

## Invariantes do repo
Coisas que o código assume e que quebrar derruba o sistema:
- "todo handler assume `req.user` autenticado" (middleware global).
- "todo id é UUID v7" (parser comum).
- "toda query passa por `withTenant()`".
- "todo evento publicado tem `event_id`".

Registre onde está garantido (middleware, decorator, lint customizado) e onde **não** está.

## Inconsistências
O repo quase nunca é uniforme. Registre as exceções:
```
Padrão A (18 arquivos): service retorna Result<T>
Padrão B (3 arquivos): service lança exceção — src/legacy/*
```
Isso é mapa, não julgamento. Saber onde está o legado evita surpresa.

## Saída
Tabela de convenções com exemplo + arquivo, lista de invariantes com onde são garantidas, e a seção de inconsistências conhecidas.
