---
tipo: estado-de-execucao
agente: dsh
projeto: dz23-arsenal
data: 2026-11-18
tags: [arsenal, handoff, trilha-a, qwen]
---

# Estado de execução — plano `plano-execucao-qwen.md`

Construtor: DSH (Qwen). Auditor ao reassumir: Claude. Plano lido na íntegra em 2026-11-18; a versão
vigente tem a **regra 4 invertida** (internalizar conhecimento permissivo é o default) e o **molde
obrigatório de 5 entregáveis** por skill da Trilha A.

## Onde estamos agora

- Branch `main`, HEAD **`296fdd4` publicado**, **em sync com `origin/main` (0/0)**.
- Gate: **55 checks, exit 0**. CI do GitHub verde no commit publicado (run 44286241293,
  `checks: 55 | falhas: 0`).
- Evals: **48 cenários cobertos de 144 (33,3%)**, 96 pendentes. Régua corrigida em 18/11 — ver
  "Correção de contagem".

## Trilha A — progresso por skill

| Skill | Estado | Commit |
|---|---|---|
| `dz23-ultimate-pro-max` | **feito** (antes deste checkpoint): `dados-design/` + `consulta-design.py` + prova de 11 casos | anterior |
| `dz23-backend-data-architect` | **feito**: `dados-backend/` (6 CSVs, 30 linhas, ECC/MIT) + `consulta-backend.py` + prova de 15 casos + `references/dataset-backend.md` + linha no passo 3 do método + 2 `.sql` autoverificáveis executados contra Postgres vivo + eval registrado | `7433fda` |
| `dz23-performance-scalability-engine` | **feito**: `dados-performance/` (2 CSVs, 13 linhas: 8 categorias priorizadas + 5 métricas Web Vitals→categoria) + `consulta-performance.py` + prova com **os 41 sinônimos exercitados um a um** + `references/dataset-performance.md` + linha no passo 1 (MEDIR) do workflow + eval `layers-swapped` executado com medição própria (mídia 53% / JS 30% em três builds reais). Skill 1.3.3 → 1.3.4. Fonte Vercel **não** copiada por falta de arquivo LICENSE — ver "Bloqueio de licença", resolvido pelo caminho 1. | `296fdd4` |
| `dz23-codebase-cartographer` | **PRÓXIMO.** Fontes ECC `code-tour` (4 tabelas, 21 linhas) e `codebase-onboarding` (2 tabelas, 10 linhas) — o maior acervo tabular restante. MIT já confirmado no `LICENSE` da ECC; não reler de zero, só conferir a skill-fonte. | — |
| `dz23-spec-to-system-engine` | pendente. `architecture-decision-records` (2 tabelas, 11 linhas). | — |
| `dz23-postgres-prod-preflight` | pendente. Reaproveita `dados-backend/` (índices, tipos, anti-padrões) — **não duplicar**; decidir se aponta para o mesmo acervo ou extrai subconjunto próprio. | — |
| `dz23-e2e-browser-verifier` | pendente. Fontes ECC `e2e-testing`, `browser-qa`, `click-path-audit`: **0 tabelas cada** (medido). Sem dado tabular → o "acervo" vira `references/*.md` destiladas com proveniência; consultor e prova continuam obrigatórios. | — |
| `dz23-devops-cloud-deployer` | pendente. `deployment-patterns`: 0 tabelas. Idem acima. | — |
| `dz23-reverse-engineer-anything` | pendente. `replica-recon` — localizar fonte, ler LICENSE. | — |
| `dz23-autonomous-improvement-ultimate` | sem acervo novo por design (integração via CLI `ocr`). | — |

**Total de linhas tabulares disponíveis nas 15 fontes ECC examinadas: 89** (30 backend + 13 performance
+ 31 code-tour/onboarding + 11 ADR + ~4 produção). O plano fala em "acervo" como se cada domínio tivesse
um banco de dados; depois de backend e performance restam ~48 linhas para as outras seis skills. Vale
confirmar com o dono se o molde de consultor faz sentido para datasets de 4–11 linhas, ou se basta
`references/` destilada nesses casos — construir seis consultores sobre meia centena de linhas pode ser
cerimônia, não capacidade.

## Skills fechadas no molde completo -- com hash de cada uma

Regra aceita do auditor: nenhuma skill é "pronta" sem ciclo completo (commit → resync → push → CI
verde) registrado aqui com o hash.

| # | Skill | Conteúdo | Commit | CI na época |
|---|---|---|---|---|
| 1 | `dz23-backend-data-architect` 1.1.2 | `dados/` 30 decisões + consultor + prova 15 casos + 2 `.sql` executados + eval | `7433fda` | run 44282647790 ✓ |
| 2 | `dz23-performance-scalability-engine` 1.3.4 | `dados/` 13 linhas + consultor + prova 41 sinônimos + eval medido | `296fdd4` | run 44286241293 ✓ |
| 3 | `dz23-ultimate-pro-max` 2.2.6 | `dados-design/` 3 MB + consultor (7 comandos) + prova 15 casos + `grafico`/`motion` + correção de `--severidade` | `9fd4a3f` | run 44294369696 ✓ |
| 4 | `dz23-codebase-cartographer` 1.2.0 | `dados/` 18 decisões da ECC `code-tour` + `consulta-codebase.py` (44 sinônimos) + template `code-tour.md` + prova exaustiva com integridade por hash; 2 tabelas de `codebase-onboarding` rejeitadas por serem placeholder de template | `94381d8` → `77d642b` | run 44308868486 ✓ |
| 5 | `dz23-spec-to-system-engine` 1.3.0 | `dados/` 8 categorias de ADR (ECC architecture-decision-records) + `consulta-espec.py` (40 sinônimos PT→EN) + prova com hash **canônico** EOL-independente desde o nascimento; "ADR Index Format" rejeitado por ser placeholder em bloco markdown | `95cf3db` | run 44311576695 ✓ |
| C | `dz23-subagents-universal-mcp` 4.4.1 (Trilha C) | gate agora executa os 293 testes proprios da MCP via `scripts/selftest-subagents-mcp.py` (node --test, zero deps). Criterio: fail 0 E tests>0; sem node => NOT_TESTED declarado, nao PASS falso. Verificado no runner ubuntu (63 checks / 0 falhas, 0 NOT_TESTED) | `06b8a25` | run 44314217971 OK |

Gate foi de 51 → **62 checks**; os quatro commits acima têm CI verde no `main`.

### O que o item 4 ensinou: verde local ≠ verde no runner
Pela primeira vez nesta consolidação commitei com gate 60/60 **e** o CI ficou vermelho (run
44302652416). Reproduzi na única condição que eu ainda não testava — `git clone` limpo do HEAD com HOME
vazio — e a causa era real e minha: `gate:autoteste-consulta-codebase` hasheava os CSVs crus, mas
`.gitattributes` converte CSV para LF no índice enquanto o gerador escreve CRLF no disco Windows. O
verificador de *integridade* não media integridade do conteúdo, media a plataforma de quem gerou
(`d8f531…` no git ≠ `f0a10a…` no disco). Corrigido com `_digest_canonico()` normalizando `\r\n`→`\n` antes
do sha256 — mesma regra das rodadas 47/48/51, aplicada ao verificador que eu havia escrito naquela rodada.
**Aprendizado operacional: rodar o gate num clone limpo passa a ser parte do ciclo, não opcional.**

Dois defeitos da mesma classe apareceram pelo caminho: `audita-sensibilidade` e `audita-alegacoes`
injetavam violação com string literal fixa (`"| 1.1.1 | Explora"`) que deixou de existir quando a skill
subiu para 1.2.0 — o `re.sub` virava no-op e o auditor reportava corretamente "medição vazia". Agora
localizam a linha pelo nome da skill e trocam a versão que ela realmente carrega, sobrevivendo a bump futuro.

## Padrão que se consolidou nestes itens

Copiar tabela ≠ incorporar. Cada item seguiu seis passos, e os últimos três são os que evitam dano:

1. Ler licença no **arquivo** `LICENSE` (não README, não campo da API).
2. Medir o ganho: comparar termo a termo contra o que a skill DZ23 já tem. Se cobre, não copiar.
3. Extrair só tabela de decisão; narrativa que já existe na skill fica de fora (senão são duas fontes).
4. **Conferir célula por célula contra a fonte**, porque regex desloca coluna sem avisar.
5. Prova do consultor **exaustiva no mapa de sinônimos**, não amostrada.
6. **Executar os comandos como o documento os promove** -- e verificar na *instalação*, não só no
   checkout. Um passo 6 ausente foi o que deixou três habilidades instruindo script inexistente, e um
   passo 5 amostrado foi o que escondeu 15 sinônimos apontando para valores inventados.

## Pendência 1 da auditoria: aceita e corrigida
O HEAD publicado estava vermelho (`instalacao:conteudo`, 3 divergentes) porque eu rodei `git add -A`
**antes** de mover os CSVs dos acervos: o índice ficou conhecendo 49 arquivos apagados do disco, e
`repo_inventory` devolvia `INVENTORY_PARTIAL` por `stat()` falhando. Confirmei a causa contando ausentes
(49 → 0 após re-staging) e validei o conserto num **worktree destacado no HEAD**, não só na árvore de
trabalho -- que era justamente o erro metodológico apontado. A regra "quem constrói não homologa; verde
na minha árvore não é verde" valeu contra mim mesmo desta vez.

## Pendência 2 da auditoria: premissa medida antes de agir, e o diagnóstico estava parcialmente errado
Pedi para alinhar backend/performance ao "padrão texto-livre do design". Verificado: **o design também é
por subcomando** -- `consulta-design.py "estilo vidro"` retorna exit 2 igual. Os três já eram
consistentes entre si; o único exemplo em texto livre do repo era um placeholder de documentação
(`<domínio> <termo>`). Reformar três scripts nessa base teria criado interface nova por leitura errada.

Mas o teste certo para a queixa real ("comando copiado e colado falha") era executar os exemplos, e aí
apareceu defeito genuíno: `ux formulario --severidade alta` devolvia **zero** -- a planilha guarda
`High`, o código comparava `alta` normalizado contra `high`. Opção que aceita qualquer string e filtra
para nada é pior que opção ausente. Corrigido com ponte PT→EN e recusa explícita; e o verificador novo
`checa-exemplos-executaveis.py` agora roda os 18 comandos promovidos pelos documentos, para a classe não
voltar. Ou seja: o apontamento produziu valor, mas pela rota de medir, não de executar literalmente.



Copiar tabela ≠ incorporar. Cada item seguiu cinco passos, e os dois últimos são os que evitam dano:

1. Ler licença no **arquivo** `LICENSE` (não README, não campo da API).
2. Medir o ganho: comparar termo a termo contra o que a skill DZ23 já tem. Se cobre, não copiar.
3. Extrair só tabela de decisão; narrativa que já existe na skill fica de fora (senão são duas fontes).
4. **Conferir célula por célula contra a fonte** (`confira-csv`), porque regex desloca coluna sem avisar.
5. Prova do consultor **exaustiva no mapa de sinônimos**, não amostrada.

O passo 5 é o que mais pegou defeito meu: quatro entradas do mapa apontavam para o radical
(`waterfall` contra "Waterfalls") e nunca casavam nada — invisíveis enquanto eu testava só os termos que
havia escolhido para a prova. Agora injetar sinônimo morto faz o gate sair vermelho apontando chave e
valor.

## Correção de contagem feita neste ciclo (importante para auditoria)

Dois instrumentos liam premissas diferentes e ambos davam verde: `run-evals.py --report` contava
**arquivos** `.md` (48 registrados / 96 pendentes); `check-eval-results.py` contava **ids soltos** em
set (47/97). Causa: reexecutar um cenário já registrado somava +1 de cobertura. Eu havia feito isso ao
gravar `migration-without-rollback` em 18/11 sem saber que existia registro de 09/11.

Corrigido nos dois lados: cobertura por cenário distinto declarado, veredito mais recente por cenário,
identidade `(skill, id)` em vez de id solto. Commit `fix: cobertura de evals contava arquivos`. Os
números caíram porque estavam errados para cima.

Ao auditar: qualquer número de cobertura que não bata com esta nota está desatualizado.

## Regras que valem em cada item (do plano, reforçadas pelo que deu errado aqui)

1. Gate 53/53 exit 0 antes de commitar. Nunca commitar vermelho.
2. Licença lida no arquivo `LICENSE`, não no README. `license:null` → não copiar.
3. Cada item = 1 commit atômico.
4. Toda incorporação registrada em `dados-design/VENDOR.md` com o que **não** entrou e por quê.
5. **Medir o ganho antes de copiar**: comparação termo a termo entre o que a skill já tem e a fonte.
   Se a skill já cobre, copiar é duplicar fonte de verdade.
6. **Executar, não ler.** Os `.sql` do ECC foram rodados contra Postgres vivo antes de entrar. Um dado
   que "parece correto" não é evidência.
7. Editar Python/markdown com ferramenta de edição, nunca por substituição em shell: as aspas são
   destruídas pelo PowerShell. Isso quebrou esta sessão seis vezes.
8. Prova de verificador precisa de controle negativo. Uma prova que passa em tudo não mede nada — e um
   caso de teste malformado pode levar a remover funcionalidade correta para ficar verde (aconteceu
   duas vezes neste ciclo).

## Licença da Vercel: resolvida pelo caminho 1, questão continua aberta para o dono

O plano nomeava 
ercel-labs/agent-skills como fonte MIT do acervo de performance. Verificado antes de
copiar: **não existe arquivo LICENSE** no repositório (raiz, subpastas, nem dentro de
skills/react-best-practices/); a API do GitHub devolve license: null; o package.json não declara
licença; o README tem uma seção `## License` com a palavra MIT sozinha — sem texto, sem aviso de
copyright, sem ano. A regra 3 do plano é literal: ler o arquivo, não o que o README alega.

**Executado (caminho 1):** ECC `react-performance` cobriu o mesmo terreno prioritário com MIT verificável
em arquivo, e `dados-performance/` saiu assim. As ~40 regras detalhadas da Vercel seguem como
referência externa em `external/vercel-react-best-practices.md`, onde podem ser consultadas sem que o
arsenal redistribua o texto. Recomendação técnica mantida: o ganho de esperar pela Vercel era marginal
para o caso de performance, e ambiguidade de licença num repo público é risco nosso.

**Ainda aberto, se o dono quiser:** abrir issue na Vercel pedindo arquivo `LICENSE` (caminho 3). Se
vier, os itens de design (`web-design-guidelines`) e otimização (`vercel-optimize`) da Trilha B/D
passam a poder internalizar as tabelas deles também. Não é bloqueante para nada do que resta agora.

## Próximo passo concreto

Trilha A com dado tabular real esgotada nas fontes ECC nomeadas pelo plano: backend (30), performance (13), design (via dados-design), code-tour (18), ADR (8). Restam as skills sem tabela -- `e2e-browser-verifier` e `devops-cloud-deployer` fecham com `references/` destilada + proveniência, sem consultor próprio (menos cerimônia, mesma autonomia). `postgres-prod-preflight` reaproveita `dados-backend/` (não duplicar); `reverse-engineer-anything` e `autonomous-improvement-ultimate` não têm acervo novo por design.

Próxima frente de maior ganho, independente da Trilha A: **Trilha C — selftest das MCP**. `dz23-subagents-universal-mcp` tem 28 tools e nenhum selftest no gate hoje; é cobertura ausente do mesmo tipo que a rodada 46 achou nos scripts embutidos. Ciclo obrigatório agora inclui o clone limpo: commit → resync → gate na árvore → **gate num clone limpo do HEAD com HOME vazio** → push → CI verde → anotar hash aqui.
