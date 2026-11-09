# Context Pack — <pergunta/alvo>

> Declaração de escopo (obrigatória, antes de qualquer leitura)
> ```
> PERGUNTA: <o que preciso entender>
> ALVO:     <subpasta/módulo | repositório inteiro>
> BUDGET:   S (<20) | M (20–80) | L (>80) arquivos
> SAÍDA:    CODEBASE_MAP | CHANGE_IMPACT | AGENT_HANDOFF | resposta pontual
> ```

## Orçamento
- Budget declarado: **S / M / L**
- Estimativa: <N arquivos, M linhas>
- Consumido (real): <N arquivos, M linhas>

## Fase 1 — Descoberta
Comandos executados (sem abrir arquivo):
```bash
find . -maxdepth 2 ...
rg -n "..." -l
git log --since="14 days ago" --name-only
```
Arquivos identificados (<N>):
- `<arquivo>` — <por que entrou>
- `<arquivo>` — <por que entrou>

## Fase 2 — Assinaturas
Interfaces, tipos e schemas lidos:
| Arquivo | Trecho | O que revelou |
|---|---|---|
| `src/tipos.ts` | L1–50 | contratos do domínio |

## Fase 3 — Cirurgia (Working Set)
Arquivos lidos por completo (3–7):
1. `<arquivo>` (L1–200)
2. `<arquivo>`
3. `<arquivo>`

## Custo real
- Arquivos lidos: <N>
- Linhas lidas: <M>
- Tokens estimados: ~<K>
- Estourou o budget? <não | sim — e o que fiz>

## O que NÃO foi lido (e por quê)
- `<arquivo>` — fora do escopo da pergunta
- `vendor/` — dependência externa
- `dist/` — gerado

## Conclusão do pack
<3–5 linhas respondendo à PERGUNTA, com ponteiros. Se não respondeu, diga o que falta e o custo estimado de obter.>
