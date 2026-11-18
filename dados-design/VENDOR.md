# Proveniência do material externo (`vendor/`)

Este arquivo registra **o que entrou de fora, de onde veio, sob qual licença e o que foi feito com
isso**. Não existe para burocracia: um repositório que incorpora código alheio sem rastreabilidade
perde o direito de relicenciar, não consegue responder a um pedido de remoção e quebra a própria
política que declara. Ver `docs/OSS_FUSION_POLICY.md` do projeto irmão e `external/` aqui.

## Regra operacional

| Situação | O que entra no arsenal |
|---|---|
| Licença permissiva identificada (MIT, Apache-2.0, ISC, BSD, CC0) | **Código ou dados copiados**, com aviso de origem ao lado |
| Licença ausente ou ambígua | **Nada.** Só a ideia, reimplementada do zero, registrada como `ORIGINAL` |
| Licença copyleft (GPL, AGPL, CC-BY-SA) | **Nada copiado.** Excluído explicitamente |

Nenhuma linha foi incorporada antes de a licença ser lida no arquivo `LICENSE`, não no que o README
alega. Foi assim que `osime-osint-investigation` (CC-BY-SA-4.0) ficou de fora na triagem inicial.

## Incorporado

### `dados-design/ui-ux-pro-max-data/` — 39 arquivos, ~3 MB
- **Origem:** skill `ui-ux-pro-max` (instalada em `~/.agents/skills/ui-ux-pro-max`).
- **Licença:** ISC, declarada no corpo da habilidade.
- **O que é:** base de conhecimento estruturada e consultável — 80 estilos de interface ativos,
  192 perfis de paleta e raciocínio por tipo de produto (`styles.csv`, `ui-reasoning.csv`,
  `products.csv`), 74 diretrizes de UX (`ux-guidelines.csv`), 105 ícones, 17 stacks, 25 tipos de
  gráfico, presets GSAP, e catálogo de fontes com a licença de cada família
  (`google-fonts.csv`, `google-font-licenses.json`: 1.934 famílias, quase todas OFL).
- **Como foi usado:** referência de consulta pela skill `dz23-ultimate-pro-max`. Os CSVs têm
  proveniência própria em `data-provenance.json`, apontando para W3C e GoogleChrome — dados
  verificados, não opinião gerada.
- **Modificações:** nenhuma. Cópia byte a byte dos `.csv`/`.json` de dados; scripts, testes e
  fixtures da skill de origem **não** foram trazidos.

### `skills/dz23-backend-data-architect/examples/` + referência de migrações — 2 arquivos, ~5 KB
- **Origem:** skill `database-migrations` do ECC (`affaan-m/everything-claude-code`, v2.2.3),
  extraído de `ECC-main.zip`. Licença **MIT lida no arquivo `LICENSE` do repositório** (1.071 chars,
  "MIT License") — não no que o README alega. O próprio arquivo credita a montante as Supabase Agent
  Skills (MIT); o crédito em cascata está preservado na nota de proveniência da referência.
- **O que entrou:** `postgres-add-column.sql` e `postgres-column-rename.sql` — exemplos
  autoverificáveis, que usam tabela temporária, afirmam com `RAISE EXCEPTION` e fazem `ROLLBACK` no
  fim. E dez conceitos destilados para `references/migrations-and-zero-downtime.md`: lock ≠ rewrite,
  `CONCURRENTLY` fora de transação, migração aplicada imutável, forward-only em produção, DDL separado
  de DML, teste com volume real, drenar writers antes do backfill, validar paridade antes do cutover,
  `IS DISTINCT FROM` como predicado de reconciliação, `FOR UPDATE SKIP LOCKED` por lote.
- **Medido antes de copiar:** comparação termo a termo entre a referência existente da skill e a fonte
  mostrou 10 conceitos ausentes do nosso texto — e um deles é **correção**, não acréscimo: nossa
  tabela recomendava `CREATE INDEX CONCURRENTLY` sem avisar que ele falha dentro de transação.
- **Verificação por execução, não leitura:** os dois `.sql` foram rodados nesta máquina contra o
  Postgres 17.11 do container Supabase local (`psql -X -v ON_ERROR_STOP=1`). Saída: 7 asserções PASS
  (`nullable ADD COLUMN takes AccessExclusiveLock without a rewrite`, `volatile default rewrites the
  table`, `NOT NULL without default fails with SQLSTATE 23502`, `old ordering leaves a stale non-NULL
  value`, `reconciliation repairs stale values and reruns update zero rows`, entre outras), exit 0,
  e `leftover_temp=0` — nenhum resíduo no banco.
- **Modificações:** conteúdo técnico dos exemplos mantido; adicionada nota de proveniência ao fim da
  referência. Não copiamos o `SKILL.md` do ECC inteiro nem suas 327 skills — só o trecho que preenche
  lacuna medida. A regra 4 do plano continua valendo: ECC permanece, na geral, material de referência.

### `dados-backend/` + `skills/dz23-backend-data-architect/examples/` — 6 CSVs (30 linhas) + 2 `.sql`
- **Origem:** ECC (`affaan-m/everything-claude-code` v2.2.3), `ECC-main.zip`. Licença **MIT lida no
  arquivo `LICENSE` da raiz** (1.071 chars). As três skills-fonte declaram `metadata.origin: ECC`; duas
  creditam montante as Supabase Agent Skills (MIT).
- **O que entrou:** só **tabelas de decisão** extraídas de `postgres-patterns`, `database-migrations` e
  `api-design` (índice por padrão de query, tipos de dado, anti-padrões de migração, semântica HTTP,
  paginação, rate limit), cada linha com `origem_arquivo`/`origem_secao` embutidos; mais os dois
  exemplos SQL autoverificáveis de `database-migrations`. A narrativa dessas mesmas skills não virou
  dado — foi destilada para `references/` quando acrescentava algo. Proveniência completa em
  `dados-backend/PROVENIENCIA.md`.
- **Ganho medido antes de copiar:** comparação termo a termo entre a referência existente da skill e a
  fonte achou 10 conceitos ausentes -- e um deles é **correção**, não acréscimo: nossa tabela
  recomendava `CREATE INDEX CONCURRENTLY` sem avisar que ele falha dentro de transação.
- **Verificação por execução, não leitura:** os dois `.sql` rodados nesta máquina contra Postgres 17.11
  (`psql -X -v ON_ERROR_STOP=1`) → 7 asserções PASS, exit 0, `leftover_temp=0`. E cada uma das **95
  células** dos CSVs foi conferida contra a tabela na fonte (comparação normalizada de crase/espaço),
  zero divergências.
- **Consultor + prova no gate:** `scripts/consulta-backend.py` (30 decisões, português por mapa fechado
  de termos) e `scripts/prova-consulta-backend.py` (12 casos legítimos + 3 controles negativos +
  validação de esquema). Dois checks novos no gate: `backend:consulta`, `gate:autoteste-consulta-backend`.
- **Modificações:** conteúdo técnico dos exemplos preservado; títulos dos datasets ajustados ao que as
  colunas realmente contêm (um deles se chamava "estilo de API" e era tabela de paginação — corrigido
  pela própria prova).

## Avaliado e NÃO incorporado

| Fonte | Licença | Motivo |
|---|---|---|
| `ECC-main.zip` (no todo) | MIT | 38 MB / 4.878 arquivos de skills e agentes de terceiros. Copiar inteiro criaria duas fontes de verdade para a mesma orientação e apagaria a autoria das nossas. Colheita cirúrgica, item por item com lacuna medida, é o que entra — ver acima. |
| `modern-web-guidance-src-main.zip` | Apache-2.0 | 38 MB, sendo 428 `.patch` e 329 `.html` de casos de teste upstream. A versão destilada já está instalada (`modern-web-guidance`, 210 arquivos/1,9 MB) e é o que as skills consomem. |
| `open-code-review-main.zip` | Apache-2.0 | Código Go de ferramenta externa, executável por CLI (`ocr`). Integrar por comando é mais honesto que duplicar 551 arquivos `.go`. |
| `ui-main.zip` | MIT | 30 MB de componentes React/Next (.tsx). São componentes de biblioteca alheia; o arsenal orienta *como* construir UI, não distribui catálogo de widgets. Usar via dependência quando um projeto específico precisar. |
| `astryx-main.zip` | MIT | 290 MB de design system com binários. Já disponível pelo comando `astryx` nesta máquina; a skill `astryx` instalada aponta para ele. |
| `rea-main.zip` | MIT (referência a GPLv3 em dependência) | Ferramenta já instalada e operada por MCP neste ambiente. |
| `osime-osint-investigation` | CC-BY-SA-4.0 | Copyleft de atribuição compartilhada: incorporar obrigaria relicenciar o arsenal. Excluído na triagem. |

## Pendente de decisão

Nada nesta pasta depende de decisão sua para continuar válido. Se algum dia o arsenal deixar de ser
MIT, revisar antes: `ui-ux-pro-max-data` (ISC, compatível com sublicenciamento).
