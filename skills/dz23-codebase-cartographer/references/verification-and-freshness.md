# Verificação e frescor do mapa

## Mapa é hipótese
A frase "o serviço X chama o Y" é hipótese até alguém apontar `arquivo:linha`. A verificação é o que separa mapa de folclore.

## Checagem por afirmação
| Tipo de afirmação | Como verificar |
|---|---|
| "entry point é X" | manifest script + `CMD` do Dockerfile |
| "A importa B" | `rg "from .*B"` na pasta de A |
| "a regra está no service" | ler a função e ver o cálculo |
| "não há teste" | `rg --files -g "*test*"` + config do runner |
| "código morto" | 3 checagens de `hotspots-and-debt.md` |
| "ciclo" | cadeia de 3 arquivos com linha |
| "endpoint X existe" | rota registrada + handler |

Afirmação sem verificação possível → marque `INFERIDO` e diga o que faltaria para confirmar.

## Frescor
Todo mapa carrega no topo:
```
repo: <path> | commit: <sha> | branch: <branch> | lido em: <data>
```
Regra de validade (sugestão): **30 dias ou 50 commits**, o que vier primeiro. Passou disso, revalidar antes de usar.

## Revalidação barata (5 minutos)
```bash
git log --oneline <sha>..HEAD --name-only | sort | uniq -c | sort -rn | head -20
```
Os arquivos que mudaram desde a leitura são exatamente onde o mapa pode estar errado. Atualize só eles — não refaça o mapa inteiro.

## Sinal de mapa podre
- Cita arquivo que não existe mais → `git ls-files | rg <arquivo>`.
- Cita linha que não corresponde → o código mudou.
- Fala de módulo removido.
- Não tem commit/data.

Mapa podre é pior que mapa nenhum: ele dá confiança falsa.

## Nível de confiança por seção
| Nível | Critério |
|---|---|
| **Confirmado** | li e tenho ponteiro |
| **Inferido** | deduzi de estrutura/nome, sem ler o corpo |
| **Não verificado** | depende de acesso que não tenho (banco, produção, credencial) |

Uma seção sem nível declarado é uma seção que não se sabe se pode confiar.

## O que nunca fazer
- Copiar README e chamar de mapa.
- Dizer "li todo o repositório" sem amostragem declarada.
- Apresentar inferência como fato.
- Omitir que não teve acesso ao banco/produção.

## Saída
Bloco de cabeçalho com commit/data/branch, nível de confiança por seção, e o comando de revalidação.
