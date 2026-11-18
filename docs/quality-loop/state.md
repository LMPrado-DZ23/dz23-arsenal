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

## Padrão que se consolidou nestes dois itens

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

O plano nomeava ercel-labs/agent-skills como fonte MIT do acervo de performance. Verificado antes de
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

`dz23-codebase-cartographer`, no mesmo molde já exercitado duas vezes (`7433fda` backend, `296fdd4`
performance): extrair as 31 linhas tabulares de ECC `code-tour` (4 tabelas) + `codebase-onboarding` (2),
conferir célula por célula contra a fonte, montar `consulta-codebase.py` com mapa fechado e recusa
honesta, prova **exaustiva nos sinônimos** (não amostrada — foi o que pegou quatro entradas mortas no
último item), índice dizendo quando consultar, linha no método, eval executado, VENDOR.md, gate verde,
commit atômico, CI verde, push.

Antes de investir nisso, porém, vale a pergunta registrada acima: restam ~48 linhas tabulares para seis
skills. Se o dono preferir, os itens sem dado tabular (`e2e-browser-verifier`, `devops-cloud-deployer`)
podem fechar só com `references/` destilada + proveniência, sem consultor próprio — menos cerimônia,
mesma autonomia de conhecimento. A Trilha C (selftest das MCP) tem ganho claro e independente disso:
`dz23-subagents-universal-mcp` tem 28 tools e nenhum selftest no gate hoje.

