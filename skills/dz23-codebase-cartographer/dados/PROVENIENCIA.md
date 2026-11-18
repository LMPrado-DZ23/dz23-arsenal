# Proveniência de `dados/` (acervo de code tour)

> **dimensoes-de-impacto.csv** (6 linhas) vem da skill `change-impact` do ECC (MIT): as 6 dimensoes de impacto (codigo, dados, interfaces, testes, documentacao, release) a verificar antes de mudar. Cada linha cita `ECC change-impact/SKILL.md`.

## Fonte e licença

- **Projeto:** ECC (`affaan-m/everything-claude-code` v2.2.3), baixado como `ECC-main.zip`.
- **Licença:** MIT — lida no arquivo `LICENSE` da raiz do repositório (1.071 caracteres, texto MIT
  completo). Não é a alegação de um README nem o campo `license` da API do GitHub.
- **Skill-fonte:** `skills/code-tour/SKILL.md`, seções *When NOT to Use*, *2. Infer the reader* e
  *Anti-Patterns*.

## O que entrou

| Arquivo | Linhas | sha256 canônico (16 primeiros) | Seção na fonte |
|---|---|---|---|
| `quando-nao-usar-code-tour.csv` | 4 | `1b5186b7870d882f` | When NOT to Use |
| `leitor-e-profundidade.csv` | 8 | `0eff7227776d5b38` | 2. Infer the reader |
| `antipadroes-de-code-tour.csv` | 6 | `d8f5312863fc0177` | Anti-Patterns |

Os hashes são do conteúdo **normalizado** (`\r\n` → `\n`), não dos bytes crus: `.gitattributes` converte
CSV para LF no índice, enquanto o gerador escreve CRLF no disco Windows. Um digest de bytes crus divergiria
entre checkout e clone limpo — foi exatamente assim que o CI reprovou esta prova (`d8f531…` no git ≠
`f0a10a…` no disco) enquanto localmente passava verde. Normalizar antes de hashear torna a integridade
independente da plataforma de quem gerou, como as rodadas 47/48/51 já exigem para qualquer comparação de
conteúdo neste arsenal.

Cada linha carrega `origem_arquivo` e `origem_secao` na própria célula: um CSV sem procedência passa a
ser "verdade" solta dentro do repo, que é o defeito que este arsenal combate desde a rodada 1. Os hashes
acima são verificados por `scripts/prova-consulta-codebase.py`; mudar um byte em qualquer célula quebra
a comparação e obriga a reconferir a fidelidade antes de aceitar.

## Por que o acervo mora AQUI e não na raiz do repositório

`install-all.ps1` copia apenas a pasta da skill para `~/.agents/skills/<nome>/`. Um consultor que sobe
dois níveis e procura `dados-codebase/` na raiz funciona no checkout e falha na instalação — a habilidade
fica com a instrução de rodar um script cujo dado não existe onde ela foi parar. É a classe das rodadas
47 e 55 aplicada ao ambiente de execução do usuário. Nos acervos pequenos (este, backend, performance) o
dado viaja com a skill; em `dados-design/` (3 MB) a duplicação não compensa, e lá o script localiza o
checkout pelo ponteiro `.dz23-arsenal`.

## O que foi REJEITADO, e por quê

Da ECC `codebase-onboarding`, duas tabelas têm forma de dado mas não são conhecimento:

| Tabela | Linhas | Motivo da rejeição |
|---|---|---|
| Tech Stack | 5 | Está dentro de `<!-- Example for a React project — replace with detected paths -->` |
| Where to Look | 5 | Dentro de `<!-- Example for a Next.js project — replace with detected paths -->` |

São placeholders de template com valores inventados (`npm run dev`, `prisma migrate dev`). Copiá-las
encheria o acervo de exemplo alheio disfarçado de conhecimento consultável — e um acervo com ruído faz o
agente confiar numa linha que não significa nada. Verificado lendo o contexto HTML de cada seção, não
presumido pela presença de `|---|`.

## Verificação registrada na geração

- **Fidelidade célula por célula contra a fonte:** 44 células conferidas (comparação normalizada de
  crase, negrito e aspas tipográficas), zero divergências. Feito na geração, porque a fonte ECC não é
  versionada neste repositório — por isso a prova do gate verifica invariantes + hash em vez de reler a
  fonte, e não vira N/A silencioso.
- **Sinônimos PT→EN:** os 44 do mapa foram exercitados um a um contra os valores reais das colunas. Na
  primeira versão, **nove apontavam para personas plausíveis e inexistentes** (`debugger`, `pm`,
  `executive`, `verified anchors`) e um décimo tinha a célula truncada porque eu li uma prévia de 46
  caracteres em vez do valor inteiro. Corrigidos contra as células reais (`bug-fixer`, `pr-reviewer`,
  `rca-investigator`, `security-reviewer`, `feature-explainer`).
- **Esquema:** toda coluna listada em `busca_em` existe nos CSVs.
