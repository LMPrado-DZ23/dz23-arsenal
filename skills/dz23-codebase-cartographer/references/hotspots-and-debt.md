# Hot spots, dívida e código morto

## Hot spot = churn × complexidade
Arquivo que muda muito **e** é complexo é onde o bug nasce. Uma das duas dimensões sozinha não diz nada.

```bash
# churn: arquivos que mais mudaram nos últimos 6 meses
git log --since="6 months ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20

# tamanho como proxy de complexidade (quando não há métrica)
git ls-files | xargs wc -l 2>/dev/null | sort -rn | head -20
```

Se houver métrica real (`eslint complexity`, `radon cc`, `sonar`, `gocyclo`), use — e diga qual. Sem métrica, declare que o proxy é tamanho.

## Tabela de hot spots
| Arquivo | Mudanças (6m) | Linhas | Por que importa |
|---|---|---|---|
| `src/services/order.ts` | 41 | 820 | núcleo de negócio, muito churn |

## Código morto — como provar
Não basta "parece morto". Precisa de:
1. nenhuma referência de import (`rg "from .*modulo"` retorna 0);
2. nenhuma entrada dinâmica óbvia (router por string, DI por nome, `require` dinâmico, template);
3. nenhuma referência em config, script ou CI.

Faltando qualquer um, o estado é **"candidato a morto, não confirmado"**. Apagar sem essa checagem é como funciona o incidente de sexta.

## Duplicação
Não persiga DRY por estética. Registre duplicação quando:
- a mesma regra de negócio existe em dois lugares (risco de divergir);
- o mesmo cálculo financeiro aparece duas vezes;
- dois módulos leem a mesma tabela com regras diferentes.

## Acoplamento que dói
| Sintoma | Evidência |
|---|---|
| Módulo importado por 20+ arquivos | contagem de imports |
| Classe com 30 métodos | `rg -c "^\s+(async )?\w+\(" arquivo` |
| Função com 200 linhas | leitura dirigida |
| `utils/` com tudo | número de arquivos e importadores |
| Estado global mutável | `rg "let .*=" src/*.ts` |

## Dívida declarada × dívida escondida
- **Declarada**: `TODO`, `FIXME`, `HACK`, `shortcut:` no código. Conte e agrupe por área.
```bash
rg -n "TODO|FIXME|HACK|shortcut:" --stats | tail -5
```
- **Escondida**: ausência de teste em área crítica, tratamento de erro engolido (`catch {}`), retry sem limite, query em loop (N+1).

## Prioridade do achado
| Nível | Critério |
|---|---|
| P0 | risco de perda de dado ou de segurança, área crítica sem teste |
| P1 | hot spot com bug recorrente, acoplamento que impede mudança |
| P2 | dívida de legibilidade, duplicação sem divergência |
| P3 | cosmético |

## Saída
Tabela de hot spots com evidência, lista de mortos confirmados vs candidatos, dívida declarada agrupada, e o que **não** foi possível medir.
