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

### `dados-performance/` — 2 CSVs (13 linhas)
- **Origem:** ECC (`affaan-m/everything-claude-code` v2.2.3), skill `react-performance`, seções
  `Priority Index` e `Lighthouse / Web Vitals Mapping`. Licença **MIT lida no arquivo `LICENSE` da
  raiz** (texto completo, 1.071 chars).
- **O que entrou:** 8 categorias de otimização com prioridade, prefixo de regra e "quando importa";
  5 métricas Web Vitals ligadas às categorias que as movem. Só as tabelas de decisão -- a narrativa da
  skill-fonte (~17 KB) não virou dado, porque já está coberta pelas camadas 5.2–5.5 da skill DZ23;
  copiá-la criaria segunda fonte de verdade para o mesmo domínio.
- **Por que esta fonte e não a Vercel, nomeada no plano:** `vercel-labs/agent-skills` foi verificada
  antes de copiar e **não tem arquivo `LICENSE`** em lugar algum (raiz, subpastas, nem dentro de
  `skills/react-best-practices/`); a API do GitHub devolve `license: null`; o `package.json` não declara
  licença; o README traz apenas a palavra "MIT" numa seção `## License`, sem texto nem aviso de
  copyright. Pela regra deste repo ("licença lida no arquivo LICENSE, não no que o README alega"), não
  entra como cópia. As ~40 regras da Vercel continuam acessíveis como referência externa
  (`external/vercel-react-best-practices.md`) sem redistribuição. Detalhe em
  `dados-performance/PROVENIENCIA.md`.
- **Verificação:** 42 células conferidas contra a tabela na fonte (zero divergências). Consultor com
  prova no gate (`gate:autoteste-consulta-performance`): 9 consultas + **os 41 sinônimos do mapa
  exercitados um a um** + 3 controles negativos + validação de esquema. A exaustão pegou dois defeitos
  reais: quatro entradas do mapa apontavam para o radical (`waterfall` contra "Waterfalls") e nunca
  casavam nada, e um termo (`vital`) estava no dataset errado. Injetando sinônimo morto, a prova sai
  exit 1 apontando chave e valor.
- **Uso comprovado por execução:** o eval `layers-swapped` desta skill foi respondido consultando o
  acervo (`prioridade peso` → CRITICAL 2; `metrica lcp` → Waterfalls/Bundle Size/Resource Hints) e
  medindo builds reais nesta máquina (mídia 53% do artefato, JS 30%) -- não por opinião.

### `skills/dz23-codebase-cartographer/dados/` — 3 CSVs (18 linhas)
- **Origem:** ECC (`affaan-m/everything-claude-code` v2.2.3), skill `code-tour`, seções *When NOT to Use*,
  *2. Infer the reader* e *Anti-Patterns*. Licença **MIT lida no arquivo `LICENSE` da raiz** (texto
  completo, 1.071 chars).
- **O que entrou:** 8 personas com formato de pedido e profundidade sugerida, 6 antipadrões com a
  correção de cada um, 4 casos em que o tour não é o entregável certo. Cada linha carrega
  `origem_arquivo`/`origem_secao`. Consultor `scripts/consulta-codebase.py` com mapa fechado de 44
  sinônimos PT→EN; prova no gate exercitando todas as chaves contra os valores reais das tabelas +
  integridade por sha256 (autocontida: não depende da fonte ECC estar na máquina). Template
  `templates/code-tour.md` liga cada regra inegociável a um antipadrão do acervo.
- **Rejeitado dentro da mesma família:** as tabelas "Tech Stack" e "Where to Look" de
  `codebase-onboarding` têm forma de dado mas estão dentro de
  `<!-- Example ... replace with detected paths -->` — placeholder de template com valores inventados
  (`npm run dev`, `prisma migrate dev`). Copiá-las encheria o acervo de exemplo alheio disfarçado de
  conhecimento consultável.
- **Verificação:** 44 células conferidas contra a fonte na geração, zero divergências. A prova detecta
  adulteração: mudar uma célula quebra o hash e o check sai exit 1 apontando o arquivo.
- **Proveniência completa:** `skills/dz23-codebase-cartographer/dados/PROVENIENCIA.md`.

### `skills/dz23-spec-to-system-engine/dados/` — 1 CSV (8 linhas)
- **Origem:** ECC (`affaan-m/everything-claude-code` v2.2.3), skill `architecture-decision-records`, seção
  *Categories of Decisions Worth Recording*. Licença **MIT lida no arquivo `LICENSE` da raiz** (texto
  completo com aviso de copyright).
- **O que entrou:** taxonomia de quando uma decisão merece ADR (technology choices, architecture patterns,
  API design, data modeling, infrastructure, security, testing, process), cada linha com
  `origem_arquivo`/`origem_secao`. Consultor `scripts/consulta-espec.py` com mapa fechado de 40 sinônimos
  PT→EN; prova no gate com exaustão dos termos + esquema + integridade por hash **canônico**.
- **Rejeitado dentro da mesma fonte:** a tabela "ADR Index Format" está dentro de bloco ` ```markdown``` `
  com ADRs fictícios (`Use Next.js`, `PostgreSQL over MongoDB`) — placeholder de template, não conhecimento.
  O extrator checa fence antes de escrever.
- **Ganho medido antes de copiar:** a skill já declarava "decisão irreversível exige ADR" sem critério de
  *se* algo é irreversível; o acervo fornece exatamente esse critério, ligando-se ao padrão inegociável L56.
- **Verificação:** 16 células conferidas contra a fonte na geração (zero divergências). Prova detecta
  adulteração: trocar uma célula quebra o hash canônico e derruba 4 sinônimos (exit 1 apontando o arquivo).
- **Lição do item anterior já embutida:** o hash nasce EOL-independente (`\r\n`→`\n` antes do sha256), porque
  hashear bytes crus fez o CI reprovar um clone Linux cujo conteúdo era idêntico ao disco Windows só por fim
  de linha. Verificado também num clone limpo do HEAD com HOME vazio (etapa agora obrigatória do ciclo).

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
