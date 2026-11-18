# Proveniência de `dados/` (acervo de categorias de ADR)

## Fonte e licença

- **Projeto:** ECC (`affaan-m/everything-claude-code` v2.2.3), baixado como `ECC-main.zip`.
- **Licença:** MIT — lida no arquivo `LICENSE` da raiz do repositório (1.071 caracteres, texto completo com
  aviso de copyright). Não é a alegação de um README nem o campo `license` da API do GitHub.
- **Skill-fonte:** `skills/architecture-decision-records/SKILL.md`, seção *Categories of Decisions Worth
  Recording*.

## O que entrou

| Arquivo | Linhas | sha256 canônico (16 primeiros) | Seção na fonte |
|---|---|---|---|
| `categorias-de-decisao-adr.csv` | 8 | `21226a0132c4c7bb` | Categories of Decisions Worth Recording |

Cada linha carrega `origem_arquivo` e `origem_secao`. O hash é do conteúdo **normalizado** (`\r\n`→`\n`):
`.gitattributes` converte CSV para LF no índice enquanto o gerador escreve CRLF no disco Windows; hashear
bytes crus faria a prova reprovar um clone Linux cujo conteúdo é idêntico só por fim de linha — foi
exatamente assim que o CI pegou o item anterior desta consolidação.

## O que foi REJEITADO, e por quê

A outra tabela com forma de dado na mesma fonte, **"ADR Index Format"**, está dentro de um bloco
` ```markdown …``` `: é exemplo de template com ADRs fictícios (`Use Next.js`, `PostgreSQL over MongoDB`).
Copiá-la encheria o acervo de valores inventados apresentados como decisões consultáveis — a mesma classe
das tabelas placeholder de `codebase-onboarding` rejeitadas no item anterior. O extrator checa se a linha
da tabela cai entre dois fences ``` antes de escrever qualquer coisa.

## Verificação

- **Fidelidade célula por célula contra a fonte:** as **16 células** foram conferidas (comparação
  normalizada de crase/negrito/espaço), zero divergências. Feito na geração.
- **Consultor com prova no gate** (`gate:autoteste-consulta-espec`): 5 consultas legítimas + os **40 termos
  do mapa PT→EN exercitados um a um** contra os valores reais da coluna + 2 controles negativos + validação
  de esquema + integridade por hash canônico. Verde, e detecta adulteração: trocar uma célula quebra o hash
  e derruba 4 sinônimos, exit 1 apontando o arquivo.

## Limite honesto

São **8 linhas**: uma taxonomia de quando gravar um ADR, não um corpo de decisão. O valor prático é impedir
o erro comum de registrar demais (cada detalhe vira ADR) ou de menos (decisões estruturais ficam só na
cabeça de quem decidiu). O *como* escrever o ADR (contexto, alternativas, consequências) já existe em
`references/` desta skill; aqui só se consulta *se algo merece* um registro.
