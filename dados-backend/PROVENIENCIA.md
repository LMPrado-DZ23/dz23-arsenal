# Proveniência de `dados-backend/`

Cada CSV aqui é derivado, não escrito à mão. Este arquivo diz de onde veio cada linha e como foi
verificado — sem isso, um dado tabulado no repo vira "verdade" sem procedência, que é exatamente o
defeito que este arsenal combate desde a rodada 1.

## Fonte única das seis tabelas

- **Projeto:** ECC (`affaan-m/everything-claude-code`, v2.2.3), baixado como `ECC-main.zip`.
- **Licença:** MIT — lida no arquivo `LICENSE` da raiz do repositório (1.071 chars, "MIT License"),
  não no que o README alega. As três skills-fonte declaram `metadata.origin: ECC`; duas delas creditam
  montante as Supabase Agent Skills (MIT) e o material de API/design segue o mesmo regime permissivo.
- **Recorte:** apenas **tabelas de decisão** em markdown. A narrativa dessas mesmas skills (prosa de
  orientação) não virou dado — foi destilada para `references/` quando acrescentava algo ao que a skill
  DZ23 já tinha. Copiar os `SKILL.md` inteiros criaria segunda fonte de verdade para o mesmo domínio.

## Como foi gerado

Script de extração (fora do arsenal, área de trabalho da sessão): localiza blocos de tabela markdown
com separador `|---|`, captura cabeçalho + linhas sob a seção nomeada, e escreve um CSV por tabela com
duas colunas de procedência anexadas a cada registro (`origem_arquivo`, `origem_secao`).

| Arquivo | Linhas | Skill-fonte | Seção na fonte |
|---|---|---|---|
| `indices-por-padrao-de-query.csv` | 6 | `postgres-patterns` | Index Cheat Sheet |
| `tipos-de-dado.csv` | 5 | `postgres-patterns` | Data Type Quick Reference |
| `antipadroes-de-migracao.csv` | 6 | `database-migrations` | Anti-Patterns |
| `semantica-de-metodo-http.csv` | 5 | `api-design` | Method Semantics |
| `estilo-de-api-quando-usar.csv` | 4 | `api-design` | When to Use Which |
| `faixas-de-rate-limit.csv` | 4 | `api-design` | Rate Limit Tiers |

## Verificação

**Célula por célula contra a fonte.** Uma checagem independente (fora do arsenal) relê o `.md` da
skill-fonte, recorta o bloco da seção nomeada e exige que cada valor não-procedência do CSV apareça
literal ali, normalizando crase e espaço. Resultado na geração deste acervo: **95 células conferidas,
zero divergências**. Motivo de existir: regex que desloca uma célula por uma barra vertical dentro do
texto produz um CSV plausível e errado — e um dado errado versionado é pior que dado ausente, porque
deixa de ser questionado.

**Consultor com prova no gate.** `scripts/prova-consulta-backend.py` roda 12 termos em português
(`dinheiro`→numeric, `tempo de serie`→BRIN, `interno`→10000/min…) e 3 controles negativos que exigem
recusa honesta sem entregar linha de decisão. Inclui validação de esquema: toda coluna listada em
`busca_em` precisa existir no CSV. Essa checagem pegou dois bugs reais durante a construção — um nome
de coluna inexistente que silenciava um dataset inteiro, e um rótulo de título que prometia "estilo de
API" para uma tabela de paginação.

## O que NÃO está aqui, e por quê

- **Padrões de backend em prosa** (`backend-patterns`: 0 tabelas). Nada tabular para extrair; o valor é
  narrativo e já existe coberto por `references/service-architecture.md`.
- **Deploy, E2E, code tour, ADR** — pertencem a outras skills do arsenal; entram nos itens próprios da
  Trilha A, não misturados neste acervo.
- **Os `.sql` autoverificáveis** do ECC vivem em `skills/dz23-backend-data-architect/examples/`, não
  aqui: são executáveis, não dado consultável.

## Reexecutar a extração

O script gerador ficou na área de trabalho da sessão (`_meta/gera-dados-backend.py`), junto da checagem
de fidelidade (`_meta/confira-csv.py`). Para regenerar é preciso ter `ECC-main.zip` extraído. Não há
dependência de rede nem de ferramenta externa: leitura de texto, escrita de CSV.
