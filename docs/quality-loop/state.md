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

- Branch `main`, HEAD publicado, **em sync com `origin/main` (0/0)**.
- Gate: **53 checks, exit 0**. CI do GitHub verde no commit publicado (run 44282647790,
  `checks: 53 | falhas: 0`).
- Evals: **47 cenários cobertos de 144 (32,6%)**, 97 pendentes. Ver aviso na seção "Correção de
  contagem" abaixo — os números anteriores a 18/11 estavam inflados.

## Trilha A — progresso por skill

| Skill | Estado | Commit |
|---|---|---|
| `dz23-ultimate-pro-max` | **feito** (antes deste checkpoint): `dados-design/` + `consulta-design.py` + prova de 11 casos | anterior a este ciclo |
| `dz23-backend-data-architect` | **feito**: `dados-backend/` (6 CSVs, 30 linhas) + `consulta-backend.py` + `prova-consulta-backend.py` (15 casos) + `references/dataset-backend.md` + linha no passo 3 do método + 2 `.sql` autoverificáveis em `examples/` + eval executado | `7433fda` |
| `dz23-performance-scalability-engine` | **PRÓXIMO — aguarda decisão do dono sobre licença.** Ver "Bloqueio de licença" abaixo. Alternativa MIT sem ambiguidade: ECC `react-performance` (2 tabelas, 13 linhas). | — |
| `dz23-e2e-browser-verifier` | pendente. Fontes ECC `e2e-testing`, `browser-qa`, `click-path-audit`: **0 tabelas cada** (medido). Sem dado tabular → o "acervo" vira `references/*.md` destiladas com proveniência; consultor e prova continuam obrigatórios. | — |
| `dz23-devops-cloud-deployer` | pendente. `deployment-patterns`: 0 tabelas. Idem acima. | — |
| `dz23-postgres-prod-preflight` | pendente. Reaproveita `dados-backend/` (índices, tipos, anti-padrões) — **não duplicar**; decidir se aponta para o mesmo acervo ou extrai subconjunto próprio. | — |
| `dz23-codebase-cartographer` | pendente. `code-tour` (4 tabelas/21 linhas) e `codebase-onboarding` (2/10) têm dado real. | — |
| `dz23-spec-to-system-engine` | pendente. `architecture-decision-records` (2 tabelas/11 linhas). | — |
| `dz23-reverse-engineer-anything` | pendente. `replica-recon` — localizar fonte, ler LICENSE. | — |
| `dz23-autonomous-improvement-ultimate` | sem acervo novo por design (integração via CLI `ocr`). | — |

**Total de linhas tabulares disponíveis nas 15 fontes ECC examinadas: 89.** O plano fala em "acervo"
como se cada domínio tivesse um banco de dados; em backend/postgres/API há ~30, em code-tour ~31, em
ADR ~11. É pouco comparado aos 3 MB de design. Vale confirmar com o dono se o molde de consultor faz
sentido para datasets de 4–11 linhas, ou se basta `references/` destilada nesses casos.

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

## Bloqueio de licença — Vercel `agent-skills` (medido, não presumido)

O plano nomeia `vercel agent-skills/react-best-practices` como fonte do acervo de performance e a lista
como MIT. Fui conferir antes de copiar e o resultado é **ambíguo**, não MIT:

| Verificação | Resultado |
|---|---|
| API do GitHub (`/repos/vercel-labs/agent-skills`) | `"license": null` |
| Arquivo `LICENSE` na raiz | **não existe** |
| `LICENSE` em subpastas ou em `skills/react-best-practices/` | **não existe** |
| `package.json` → campo `license` | ausente |
| `README.md`, seção `## License` | contém apenas a palavra **"MIT"**, sem texto da licença, sem copyright, sem ano |

A regra 3 do plano diz: *"Licença lida no arquivo `LICENSE`, não no que o README alega"* e classifica
*"Ausente/ambígua → nada; só a ideia, reimplementada do zero, marcada `ORIGINAL`"*. Uma linha "MIT" sem
texto e sem aviso de copyright é literalmente o caso "o README alega" — e este projeto é público e
redistribui conteúdo, então o risco de estar errado é nosso, não deles.

Contraste com o que foi incorporado: o ECC tem `LICENSE` de 1.071 chars com o texto MIT completo, e
`ui-ux-pro-max` declara ISC. Nesses havia arquivo para ler.

**Três caminhos possíveis — decisão do dono, não minha:**
1. **Não copiar** (padrão estrito da regra 3): usar ECC `react-performance` (MIT com arquivo), 13 linhas
   tabulares, e manter o material da Vercel como referência externa — já existe `external/`.
2. **Copiar aceitando o README**: registrar em VENDOR.md a base exata ("declaração de MIT na seção
   License do README, sem arquivo LICENSE") e seguir. Defensível — MIT é a licença mais permissiva e o
   autor é a Vercel — mas depende de uma alegação, não de um texto.
3. **Perguntar ao autor** (issue no repositório pedindo arquivo LICENSE) e tratar como `NOT_TESTED` até
   resposta.

Recomendação de engenharia: caminho 1 agora, caminho 3 em paralelo. O ganho do caminho 2 é marginal —
são 40 regras de React, e as 13 linhas do ECC cobrem o mesmo terreno prioritário (`Priority Index`,
`Lighthouse / Web Vitals`). Não vale carregar ambiguidade de licença por isso.

## Próximo passo concreto

Resolver o bloqueio de licença acima (caminhos 1/2/3). Sem decisão do dono, seguir com **caminho 1**:
`dz23-performance-scalability-engine` recebe `dados-performance/` a partir de ECC `react-performance`
(MIT com arquivo `LICENSE`), no mesmo molde do item `7433fda`: extrair tabelas → conferir célula por
célula contra a fonte → consultor PT com mapa fechado e recusa honesta → prova com controles negativos
→ índice dizendo quando consultar → linha no método → eval executado → VENDOR.md → gate verde → commit.

Depois: `dz23-codebase-cartographer` (`code-tour`, 21 linhas tabulares — o maior acervo restante).

