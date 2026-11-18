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

### `skills/untangle-codebase/` — skill inteira (SKILL.md + 4 references + 1 template)
- **Origem:** Caldo (`caldoai/skills`), skill `untangle-codebase`. Licença **MIT lida no arquivo `LICENSE`
  da raiz** (Copyright 2026 Maze).
- **O que entrou:** a orientação da skill (diagnóstico por "estas peças mudam juntas?", quatro famílias de
  defeito, redesenho dos primeiros princípios, git como evidência), internalizada e reescrita no rito do
  arsenal — `SKILL.md` com frontmatter e seções próprias, `references/` (method, defect-taxonomy,
  verification, git-as-evidence), `templates/decision-log.md`, `evals/evals.json` com 6 cenários próprios,
  `scripts/validate_skill.py` + validadores comuns do arsenal.
- **O que NÃO entrou:** scripts, testes e fixtures da skill de origem; só a orientação, reescrita. Não é
  cópia byte a byte — é a primeira skill de terceiro trazida como skill-cidadã do arsenal (vs. só `dados-`).
- **Fora do ledger DZ23:** os 6 evals da untangle são declarados e **`NOT_TESTED`** na própria pasta, mas
  ficam **fora** do total de "144 cenários" das 10 skills DZ23 — `check-numbers.py` só soma evals de skills
  `dz23-*`, para que incorporar terceiros não mexa no denominador de cobertura das DZ23.
- **Verificação:** `scripts/validate_skill.py` próprio (6 casos exigidos, frontmatter, licença/origin,
  referências citadas existem) + o validador comum; entra no `quality-gate.py` e no CI como 11ª skill.

### `skills/prune-tests/` — skill inteira (SKILL.md + 4 references + 1 template)
- **Origem:** Caldo (`caldoai/skills`), skill `prune-tests`. Licença **MIT lida no arquivo `LICENSE` da
  raiz** (Copyright 2026 Maze) — mesma fonte da `untangle-codebase`.
- **O que entrou:** a orientação (diagnóstico por dependência; três famílias a podar — passado, nada,
  implementação — mais duplicata; reescrever contra comportamento em vez de deletar quando há rede;
  deletar a produção que só existia para o teste removido), internalizada e reescrita no rito do
  arsenal — `SKILL.md`, 4 `references/`, `templates/prune-log.md`, `evals/evals.json` com 6 cenários,
  `scripts/validate_skill.py` + validadores comuns.
- **O que NÃO entrou:** o `SKILL.md` de origem era só texto (sem scripts nem fixtures); nada além da
  orientação, reescrita em português. Não é cópia byte a byte.
- **Fora do ledger DZ23:** os 6 evals ficam fora do total de "144 cenários" das 10 DZ23 — mesma regra
  da untangle (`check-numbers.py`/`check-eval-results.py` só somam `dz23-*`).
- **Verificação:** `validate_skill.py` próprio (6 casos, frontmatter, licença/origin, refs citadas
  existem) + validador comum; entra no `quality-gate.py` e no CI como 12ª skill.

### `skills/web-design-guidelines/` — skill inteira + acervo de 104 regras
- **Origem das regras:** `vercel-labs/web-interface-guidelines`, arquivo `command.md`. Licença **MIT
  lida no arquivo `LICENSE` da raiz** (Copyright 2025 Vercel Labs), **confirmada via API do GitHub**
  (`spdx_id: MIT`, arquivo `LICENSE` presente).
- **O que entrou:** as 104 regras de interface web em 17 categorias, extraídas de `command.md` sem
  editar o texto (`dados/regras-por-categoria.csv` com `categoria`/`regra`/`origem_arquivo`/
  `origem_secao`; o documento completo em `references/web-interface-guidelines.md`). Consultor
  `scripts/consulta-web.py` (categoria em PT + busca), prova com controles negativos, SKILL/README/
  CHANGELOG/evals/validate próprios.
- **Autonomia (o ponto do dono):** a skill revisa UI **offline**, carregando as regras do acervo
  interno — **sem WebFetch** a cada uso.
- **Fora do ledger DZ23:** 6 evals, fora dos 144 cenários das 10 DZ23.
- **Por que NÃO a skill da Vercel:** ver linha em "Avaliado e NÃO incorporado".

### `skills/replica-recon/` — skill inteira (SKILL + 3 references + 2 templates)
- **Origem:** `Jakeschincariol/replica-skill` (skill `replica-recon`). Licença **MIT lida no arquivo
  `LICENSE` da raiz** (Copyright 2026 Jake Schincariol), confirmada via API do GitHub.
- **O que entrou:** a orientação de recon black-box de produto (regras de clean-room; método em 9
  passos; taxonomia de fontes), internalizada e reescrita em PT — `SKILL.md`, 3 `references/`, 2
  `templates/` (recon-map, features.csv), `evals/` com 6 cenários, `validate_skill.py` + comuns.
- **Papel:** 1ª skill da camada **produto-para-clone** (recon → entrepreneur → diff → brand → launch),
  que complementa a engenharia DZ23 sem duplicá-la. **Não** colide com `dz23-reverse-engineer-anything`
  (binário/firmware): esta é black-box de produto por fontes públicas.
- **Fora do ledger DZ23:** 6 evals, fora dos 144 cenários das 10 DZ23.

### `skills/replica-entrepreneur/` — skill inteira + `reviews.py` (script MIT)
- **Origem:** `Jakeschincariol/replica-skill` (skill `replica-entrepreneur`). Licença **MIT lida no
  arquivo `LICENSE` da raiz** (Copyright 2026 Jake Schincariol).
- **O que entrou:** orientação de pesquisa de usuário por avaliações públicas (regras de ética: nunca
  fabricar, citação verbatim+link, ler não raspar, nunca review falsa/FTC) internalizada em PT +
  `scripts/reviews.py` (stdlib, ranqueia avaliações em temas) + `scripts/themes.json` +
  `examples/reviews-exemplo.csv` + 2 references + template + 6 evals + validate.
- **Modificação no `reviews.py`:** entrou funcional, mas estourava traceback num CSV levemente
  malformado (vírgula sem aspas). Endurecido para degradar sem explodir (`ferramentas:ataque`). O
  reviews.py é exercitado no gate (`skills:scripts-executados`, 2 casos: exemplo + controle negativo).
- **Fora do ledger DZ23:** 6 evals. 2ª skill da camada produto-para-clone.

### `skills/replica-diff/` — skill inteira + `parity.py` e `imgdiff.py` (scripts MIT, stdlib)
- **Origem:** `Jakeschincariol/replica-skill` (skill `replica-diff`). Licença **MIT lida no arquivo
  `LICENSE` da raiz** (Copyright 2026 Jake Schincariol).
- **O que entrou:** orientação de medir paridade de clone (features via matriz pesada; layout por
  screenshot que ignora cor; veredito honesto) internalizada em PT + `scripts/parity.py` (score de
  features) + `scripts/imgdiff.py` (diff de layout, decoder PNG stdlib próprio) + `examples/` (CSV + 2
  PNGs) + 2 references + template + 6 evals + validate.
- **Scripts funcionais, sem edição de comportamento:** exercitados no gate (`skills:scripts-executados`,
  4 casos: parity e imgdiff com exemplo + 2 controles negativos — CSV sem coluna, arquivo não-PNG).
- **Fora do ledger DZ23:** 6 evals. 3ª skill da camada produto-para-clone.

### `skills/replica-brand/` — skill inteira + `sweep.py` (script MIT, stdlib)
- **Origem:** `Jakeschincariol/replica-skill` (skill `replica-brand`). Licença **MIT lida no arquivo
  `LICENSE` da raiz** (Copyright 2026 Jake Schincariol).
- **O que entrou:** orientação de nomear/rebrandar o clone (regras legais: não confusamente similar,
  checagem rodada não presumida, logo não parece o do original, triagem ≠ liberação jurídica)
  internalizada em PT + `scripts/sweep.py` (acha nome/domínio/cor do original no código, exit 1 se
  achar) + `examples/brand-exemplo.json` + 2 references + 2 templates + 6 evals + validate.
- **Rerota:** o passo de contraste referenciava `replica-design/contrast.py` (skill não incorporada,
  duplicava `ultimate-pro-max`); rerotado para `web-design-guidelines`/`dz23-ultimate-pro-max`.
- **sweep.py funcional, sem edição:** exercitado no gate (`skills:scripts-executados`, 3 casos: com
  sobra → exit 1, limpo → exit 0, sem alvo → exit 2).
- **Fora do ledger DZ23:** 6 evals. 4ª skill da camada produto-para-clone.

### `skills/replica-launch/` — skill inteira + `listing.py` (script MIT, stdlib)
- **Origem:** `Jakeschincariol/replica-skill` (skill `replica-launch`). Licença **MIT lida no arquivo
  `LICENSE` da raiz** (Copyright 2026 Jake Schincariol).
- **O que entrou:** orientação de lançamento (landing que lidera com a correção; preço contra o do
  original com data lida; regras — sem prova falsa, avaliações não são depoimento, nome do original
  fora) internalizada em PT + `scripts/listing.py` (lint de listagem de loja contra limites e a
  Guideline 4.1 Copycats da Apple) + `examples/listing-exemplo.json` + 2 references + 3 templates + 6
  evals + validate.
- **Rerota:** contraste da landing rerotado para `web-design-guidelines`/`dz23-ultimate-pro-max`.
- **listing.py funcional, sem edição:** exercitado no gate (3 casos: exemplo, nome do original → erro,
  JSON inválido).
- **Fora do ledger DZ23:** 6 evals. **5ª e última** da camada produto-para-clone — a suíte replica
  (recon/entrepreneur/diff/brand/launch) está completa; as 6 skills replica de engenharia ficaram fora.

### `skills/dz23-postgres-prod-preflight/dados/` — acervo de pré-deploy (Trilha A, melhora skill DZ23)
- **Origem:** ECC (`affaan-m/ECC`), skills `postgres-patterns` + `database-migrations`, que creditam o
  **time do Supabase (MIT)**. Licença **MIT lida no `LICENSE` da raiz** do ECC.
- **O que entrou:** 3 CSVs de pré-deploy (21 registros) — anti-padrões de migração, gates de
  segurança/lock, checklist de migração — extraídos das tabelas/listas da fonte, com
  `origem_arquivo`/`origem_secao`. Consultor `scripts/consulta-postgres.py` + prova, no gate.
- **Melhora uma DZ23 existente (não é skill nova):** a `dz23-postgres-prod-preflight` passa a consultar
  o próprio acervo offline (1.1.2 → 1.2.0). Primeira das 5 DZ23 restantes da Trilha A.
- **Dedup:** não repete o acervo de `dz23-backend-data-architect` (índices por query, tipos); aqui é só
  pré-deploy (gates, migração, lock). Evals da skill não mudaram (fora o acervo; verificado pela prova).

## Avaliado e NÃO incorporado

| Fonte | Licença | Motivo |
|---|---|---|
| `Jakeschincariol/replica-skill` → 6 das 11 skills (`replica-architect`, `-backend`, `-design`, `-build`, `-deploy`, `-test`) | MIT | Duplicam engenharia que as DZ23 já fazem com acervo+gate+evidência: architect→`spec-to-system`+`backend-data-architect`; backend→`backend-data-architect`; design/build→`ultimate-pro-max`; deploy→`devops-cloud-deployer`; test→`e2e-browser-verifier`. No pipeline de clone, esse papel é das DZ23. Entram as 5 da camada produto-para-clone (recon/entrepreneur/diff/brand/launch). Avaliação: `avaliacao-suite-replica.md`. |
| `vercel-labs/agent-skills` → skill `web-design-guidelines` (a casca) | **sem licença** (`license:null`, sem arquivo `LICENSE` — API do GitHub) | Não se redistribui conteúdo sem licença explícita. Além disso a skill só **busca** as regras de uma URL remota (WebFetch) a cada uso, o que feriria a autonomia. Trazido o **conhecimento real** (`web-interface-guidelines`, MIT) — ver "Incorporado". |
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
