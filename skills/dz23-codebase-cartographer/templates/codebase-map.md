# CODEBASE MAP — <projeto>

> repo: <path> · commit: <sha> · branch: <branch> · lido em: <AAAA-MM-DD>
> validade sugerida: 30 dias ou 50 commits · revalidar por `git log --oneline <sha>..HEAD --name-only`
> pergunta que este mapa responde: <ex.: mudar o cálculo de frete sem quebrar cobrança>

## Nível de confiança
| Seção | Nível | Nota |
|---|---|---|
| Inventário | Confirmado | manifest + Dockerfile + CI lidos |
| Grafo | Inferido | baseado em imports, sem execução |
| Dados | Não verificado | banco não acessível |

## Inventário
- Stack real (verificada no manifest, não no README):
- Tamanho: <n> arquivos · <n> linhas · linguagens: <...>
- Entry points: `<arquivo:linha>` (comando: `<...>`)
- Build: `<comando>` · Testes: `<comando>` (existe? <sim/não>)
- CI: `<arquivo>` · Migrações: `<pasta>` + ferramenta
- Monorepo? <sim/não — workspaces>

## Amostragem
- **LIDO**: <arquivos>
- **NÃO LIDO**: <pastas/contagens>
- **CRITÉRIO**: <entry points + caminho da mudança + schema>

## Topologia (uma tela)
```
<entrada> → <camada> → <domínio> → <dado>
```

## Grafo e camadas
| Achado | Evidência |
|---|---|
| Hubs (mais importados) | `<arquivo>` (n imports) |
| Ciclos | `<a> → <b> → <a>` com linhas |
| Camada violada | `<arquivo:linha>` |
| Órfãos | `<arquivo>` — confirmado/candidato |

## Dados e estado
| Onde | O que guarda | Fonte/cópia | Evidência |
|---|---|---|---|
| | | | |

Fluxo do caminho crítico:
```
<rota:linha> → <validação> → <serviço> → <repo> → <tabela>
```
Escritor/leitor por entidade: `<entidade>` — escritores: <...> · leitores: <...>

## Convenções do repo
| Dimensão | Regra | Exemplo |
|---|---|---|
| | | `<arquivo:linha>` |

## Zonas de risco
| Zona | Classificação | Evidência |
|---|---|---|
| | dinheiro/auth/migração/fila/integração/performance | |

### NÃO TOCAR SEM PLANO
- `<arquivo:linha>` — <motivo>

## Hot spots
| Arquivo | Mudanças (6m) | Linhas | Por quê |
|---|---|---|---|
| | | | |

## Blast radius de uma mudança em <alvo>
1. Importadores: <lista>
2. Rotas: <lista>
3. Jobs/workers: <lista>
4. Tabelas: <lista>
5. Teste que cobre: `<comando>` ou **não existe**

## Lacunas conhecidas
- <o que não foi verificado> — como verificar: <...>
