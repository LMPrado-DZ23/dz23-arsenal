# Orçamento de contexto

## Por que orçamento
Ler por impulso queima contexto e ainda produz mapa pior: você termina com 40 arquivos abertos, três versões do mesmo módulo na cabeça e nenhuma conclusão. Orçamento explícito força priorização.

## Declare antes de ler
```
BUDGET: S (<20 arquivos) | M (20–80) | L (>80)
ESTIMATIVA: N arquivos, M linhas
CONSUMIDO: (preencher no fim — real)
```

## As 3 fases
| Fase | Objetivo | O que se abre | Custo |
|---|---|---|---|
| **1 — Descoberta** | localizar | nada: só `rg`/`find` (nome + linha) | baixo |
| **2 — Assinaturas** | contratos | interfaces, `export type`, schemas, migrations | médio |
| **3 — Cirurgia** | entender de fato | 3–7 arquivos do working set, completos | alto |

Ordem obrigatória. Abrir arquivo grande sem ter passado pela fase 1 é o antipadrão nº 1 desta skill.

## Regra por tamanho de budget
| Budget | Fase 1 | Fase 2 | Fase 3 |
|---|---|---|---|
| **S** (<20) | completa | se houver git/histórico que ajude | completa (3–7) |
| **M** (20–80) | completa | nos módulos do alvo | só no módulo alvo |
| **L** (>80) | apenas | só interfaces do caminho crítico | grep cirúrgico; **sem `cat` inteiro** |

## Regras de leitura
- Nunca abrir arquivo > 500 linhas sem `rg` antes.
- Arquivo > 200 linhas: cabeçalho + hits ± 10 linhas (não o arquivo todo).
- Nunca abrir `node_modules/`, `vendor/`, `.git/`, `dist/`, `build/`, `.next/`, `coverage/`.
- Migrations, `.min.js`, `.lock`, `*.map` → **listar**, não ler.
- Arquivo já lido nesta sessão: não reabrir (anote o ponteiro).
- `package-lock.json`/`poetry.lock`: só conclusão de dependência, nunca integral.

## Working set
No máximo 7 arquivos que você realmente precisa entender de ponta a ponta. Se passar de 7, o escopo está errado — reduza o ALVO.

```
WORKING SET
1. src/services/order.ts        (núcleo da mudança)
2. src/repositories/order.ts    (dado)
3. src/schemas/order.ts         (contrato)
4. tests/order.test.ts          (prova existente)
```

## Custo real
Ao final, registre: arquivos lidos, linhas lidas, e o que ficou de fora **com motivo**. Isso calibra o próximo mapeamento e é a prova de que o orçamento foi respeitado.

## Quando estourar
Estourou o budget? Não "abre mais um pouco". Pare, reduza o ALVO (um módulo em vez do repo), ou declare `BUDGET: L` e refaça a fase 1 com pergunta mais estreita.

## Saída
Declaração de budget, working set numerado, custo real e lista do não lido.
