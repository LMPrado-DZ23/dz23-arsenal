# Mapping playbook — receituário ripgrep

## Regra
`rg` antes de abrir. O comando devolve arquivo:linha; você decide o que abrir. `cat` é último recurso.

## Erros e tratamento
```bash
rg -n "raise |throw new " --type-add 'src:*.{ts,tsx,js,py,go,java}' -tsrc
rg -n "catch\s*\([^)]*\)\s*\{\s*\}"          # catch vazio
rg -n "except\s*:" -A1 | rg -B1 "pass\s*$"   # except/pass
rg -n "\.catch\(\(\)\s*=>"                    # promise engolida
```

## Dívida declarada
```bash
rg -n "TODO|FIXME|HACK|XXX|shortcut:" --stats | tail -5
```

## Segredo hardcoded (alerta, não relatório de valor)
```bash
rg -n "(password|passwd|secret|api_key|apikey|token)\s*[:=]\s*['\"][^'\"]{6,}" -g '!*.example' -g '!*.md'
```
Se encontrar: registre `arquivo:linha` e o **nome** da variável. Nunca copie o valor. Marque como achado P0 e recomende `secrets scan`.

## Configuração perigosa
```bash
rg -n "allow_origins\s*=\s*\[\s*['\"]\*" # CORS aberto
rg -n "debug\s*=\s*True|DEBUG\s*=\s*true"
rg -n "verify\s*=\s*False|rejectUnauthorized:\s*false"  # TLS desligado
rg -n "shell\s*=\s*True"                 # execução de shell
```

## SQL e injeção
```bash
rg -n "execute\(f\"|f\"SELECT|f\"INSERT|f\"UPDATE"     # interpolação
rg -n "\+ *\" *(SELECT|INSERT|UPDATE|DELETE)"          # concatenação
rg -n "text\(.*\+" -tsrc
```

## Log sensível
```bash
rg -n "logger\.(info|debug|warn)\(.*(password|token|secret|authorization)"
rg -n "console\.log\(.*(password|token)"
```

## Código comentado e morto
```bash
rg -n "^\s*#\s*(def |class )" -tpy            # Python comentado
rg -n "^\s*//\s*(function |const |export )"   # JS/TS comentado
rg -n "^\s*/\*" -A3                          # bloco comentado
```

## Dependência circular (pistas)
```bash
# Python relativo
rg -n "^from \.\w+ import" -tpy
# JS/TS: extrair e ordenar destinos
rg -o "from ['\"](\.[^'\"]+)['\"]" -r '$1' -tsrc | sort | uniq -c | sort -rn | head -20
```

## Por stack
| Stack | Descoberta |
|---|---|
| Python | `rg -n "^def |^class " -tpy`, `rg -n "FastAPI\(|Flask\("` |
| TS/JS | `rg -n "export (async )?function\|export class" -tts`, `rg -n "express\(\)\|createServer"` |
| Go | `rg -n "^func |package main" -tgo`, `rg -n "http.ListenAndServe"` |
| Java | `rg -n "@RestController\|@Service" -tjava` |

## Código dinâmico
Rota por string, DI por nome, `require` calculado, decorator mágico, template rendering: `rg` **não** acha. Nesse caso registre `INFERRED`/`UNKNOWN` e diga o mecanismo suspeito — não afirme "não é usado".

```bash
rg -n "require\([^)]*\+|import\([^)]*\+" # import dinâmico
rg -n "app\.use\(['\"]/:"              # rota com parâmetro
rg -n "@\w+\(\)" -tpy                  # decorator
```

## Saída
Cada comando executado entra no mapa com o resultado resumido (contagem + top hits), não com o dump inteiro.
