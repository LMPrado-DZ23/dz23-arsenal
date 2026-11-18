# Roadmap e estado honesto

Este documento existe para que ninguém precise acreditar em badge. O que está aqui é o que foi **verificado**;
o que não foi testado está marcado como `NOT_TESTED`, não como "funciona".

## Onde estamos (v1.5.0)

| Componente | Versão | Estado verificado |
|---|---|---|
| 10 skills DZ23 | ver [`INDEX.md`](INDEX.md) | estrutura ✅ · validadores ✅ (10/10, antes 9/10) · cobertura de evals 46/144 |
| `mcp/dz23-subagents-universal-mcp` | 4.4.1 | instalado e configurado no ambiente de origem; **não iniciado em CI** |
| `bundle/dz23-dsh-agency` | 1.0.0 | estrutura ✅; `build.py` não executado em CI |
| 13 referências externas + registro de absorção | — | documentadas (não redistribuídas); tabela do README conferida contra o disco |

### O que roda em CI (a cada push/PR)

1. `validate_skill.py` de **cada** skill — ausência agora falha, não pula
2. `check-structure.py` — arquivos obrigatórios, frontmatter, `VERSION` × frontmatter, schema dos evals
3. `check-links.py` — todo link relativo `.md` do repositório
4. `build-manifest.py --check` — compara conteúdo canônico, não data (ver v1.5.0 abaixo)
5. `check-numbers.py` — números do README/ROADMAP contra o disco, incluindo regra órfã
6. `check-licenses.py` — licença por componente e por referência externa
7. auto-testes de `gate_candidatos.py` e `verifica_claims.py`, mais `claims:<skill>` nos 10 SKILL.md

Constantes do CI: [`.github/workflows/quality.yml`](.github/workflows/quality.yml).
Total de checks: leia de `python scripts/quality-gate.py` (a saída imprime `N/N`). Este
documento não fixa o número de propósito -- já ficou obsoleto três vezes nesta linha de
trabalho (16 → 31 → 33 → 39), e um verificador que compara a documentação contra um número
digitado nela só encontra trabalho infinito. A checagem viva está em
`scripts/audita-alegacoes.py`, que reprova qualquer `NN checks` escrito em README, ROADMAP ou
CONTRIBUTING sem fonte executável correspondendo a ele.

## Correções estruturais da v1.5.0

Detalhadas em [`CHANGELOG.md`](CHANGELOG.md) e na justificativa de
[`external/absorcao-2026-11-17.md`](external/absorcao-2026-11-17.md). O ponto que importa
para este documento: **dois gates rodavam no CI sem verificar o que prometiam.**

- `--verify-quotes` devolvia exit 0 quando `AUDIT-STATUS.json` faltava. Apagar o estado
  desligava a checagem de citação fabricada. Consertado e provado por renomeio do arquivo.
- `check-eval-results.py` prometia cruzar NOT_TESTED com o ROADMAP e só testava se a string
  `"Status de evals"` existia. Consertado e provado injetando número falso no ROADMAP.

Nenhum dos dois era detectável lendo a suíte verde. A lição virou instrumento: todo
verificador novo nasce com controle positivo **e** negativo no próprio selftest, e o
`check-numbers.py` passou a denunciar regra cujo padrão não casa em lugar nenhum — porque
uma regra órfã é indistinguível de uma checagem aprovada.

## O buraco maior: evals não executados

As 10 skills declaram **144 cenários** em `evals/evals.json`. Executados em harness real e julgados: **45**.
Os demais seguem `NOT_TESTED`; a tabela por skill abaixo é a fonte, e `scripts/check-numbers.py`
confere estes números contra o disco.

| Skill | Cenários | Executados |
|---|---|---|
| `dz23-performance-scalability-engine` | 16 | 3 (autoavaliados) |
| `dz23-autonomous-improvement-ultimate` | 12 | 1 (`pass-sem-teste`, PASS 6/6) |
| demais 7 | ~109 | 0 |

Isso significa: **o comportamento das skills em produção é não comprovado**, exceto pelos 4 casos acima. O
`evals.json` é especificação de comportamento, não certificado.

## Status de evals (atualizado 2026-11-09 · pós-Camada 4)

Fonte: `python scripts/run-evals.py --report` · estado de auditoria: `--audit` · método:
[`docs/eval-methodology.md`](docs/eval-methodology.md) · Camada 4:
[`docs/camada-4-2026-11-09.md`](docs/camada-4-2026-11-09.md).

### Por track

| Track | Pendentes | Executados | Observação |
|---|---|---|---|
| **A — reasoning-only** | 56 | 45 | executável sem infra (inclui 13 do pré-flight de banco) |
| **B — exige infra** | 40 | 0 | `BLOCKED` por Docker/Postgres/Ghidra/browser/hardware |
| **Novos (v1.4.5)** | 3 | 0 | OB-03/04/05 — nasceram depois da classificação |
| **Total pendente** | **98** | — | de 144 declarados |

### Cobertura

| Métrica | Valor |
|---|---|
| Declarados | **144** |
| Executados | **45 (31,2%)** |
| Criticidade A (crítico) identificada | 45 |
| Críticos executados | **32 (71%)** — os 13 restantes exigem infra |
| Auditados em literais | **16/16 da amostra** |
| Camada 4 | 1 tarefa (CI verde) — **não é eval**, não entra em cobertura |

### Por skill

| Skill | Total | Executados | PASS | PARTIAL | FAIL |
|---|---|---|---|---|---|
| `dz23-spec-to-system-engine` | 15 | 10 | 10 | 0 | 0 |
| `dz23-backend-data-architect` | 12 | 10 | 9 | 1 | 0 |
| `dz23-devops-cloud-deployer` | 16 | 7 | 7 | 0 | 0 |
| `dz23-autonomous-improvement-ultimate` | 13 | 5 | 5 | 0 | 0 |
| `dz23-codebase-cartographer` | 15 | 5 | 5 | 0 | 0 |
| `dz23-performance-scalability-engine` | 16 | 3 | 2 | 1 | 0 |
| `dz23-reverse-engineer-anything` | 15 | 3 | 3 | 0 | 0 |
| `dz23-e2e-browser-verifier` | 16 | 1 | 1 | 0 | 0 |
| `dz23-ultimate-pro-max` | 13 | 1 | 1 | 0 | 0 |
| `dz23-postgres-prod-preflight` | 13 | 0 | 0 | 0 | 0 |
| **TOTAL** | **144** | **45** | **43** | **2** | **0** |

### Auditoria (camada 3)

- **Válido:** `reaudit-5-2026-11-09.md` (5/5 PASS) e `reaudit-11-2026-11-09.md` (11/11 PASS), ambos com
  `input` literal.
- **Inválido como evidência:** `audit-2026-11-09.md` — parafraseou 13 de 16 inputs (em 5 removeu a
  armadilha) e citou fora do texto em 16 de 16 (54 de 68 citações não existem na resposta).
- Verificação automatizada no gate: `evals:citacoes` (`run-evals.py --verify-quotes`).

### Próximo passo

Rodada 4 dos 43 do Track A + os 3 novos. E, acima disso: **Camada 4 fora do próprio repo** — uso em projeto
de outra pessoa, onde o erro custa retrabalho e não parágrafo.

### Harness de evals (implementado na v1.4.0)

`scripts/run-evals.py` existe e roda três coisas:

| Comando | O que faz |
|---|---|
| `run-evals.py --list` | lista os cenários por skill |
| `run-evals.py --check` | auditoria **determinística**: schema, ids duplicados, `expected` × `fails_if` contraditórios, cobertura (a regra do `expected` existe no `SKILL.md`/`references`?) e eval possivelmente impossível |
| `run-evals.py --schema` | valida cada `evals.json` contra `evals.schema.json` (requer `jsonschema`; sem ele degrada para checagem parcial) |
| `run-evals.py --report` | estado consolidado: quantos cenários têm resultado |
| `run-evals.py --verify-quotes` | confere se as citações dos laudos marcados VALIDO existem nas respostas |
| `record-eval.py --skill <skill> --eval-id <id> --verdict <V>` | grava o veredito de quem executou |

Gravar veredito é outro script, não uma flag do runner: `record-eval.py` recebe
`--skill`, `--eval-id` e `--verdict` (mais `--evidence`, `--notes`, `--blocked-by`, `--data`,
`--force`) e escreve **`evals-results/<skill-curto>/<data>-<eval-id>.md`** — um arquivo por
execução, nunca sobrescrito sem `--force`. A forma antiga desta linha,
`--record <skill> <arquivo>` gerando `evals-results/<skill>.json`, não corresponde a nenhum
comando existente: copiá-la produzia `exit 2`.

**O que ele não faz:** executar o comportamento. Isso exige uma sessão de agente real por cenário; o harness
prova que o eval é **coerente e executável** e guarda o veredito de quem executou.

Auditoria de 2026-11-09: **128 cenários então existentes, 0 erros de coerência, 3 avisos de cobertura** (o total hoje é 144 — ver tabela acima). Dois defeitos reais
foram encontrados e corrigidos nesse processo (evals de UI na skill de orquestração; `ultimate-pro-max` sem
nenhum eval).

## Dívidas conhecidas

| # | Dívida | Impacto | Esforço |
|---|---|---|---|
| 1 | Evals não executados (98 de 144 cenários) | alto — comportamento não comprovado | alto |
| 2 | `install-all.sh` nunca rodou em Linux/macOS | médio — caminho Linux não exercitado | baixo |
| 3 | **CI** — resolvido: rodando desde 2026-11-09 (2 runs verdes). Verificar: `gh run list --limit 5` | — | — |
| 4 | **Parcialmente resolvido (2026-11-17):** o `bundle/` passou a rodar no gate e no CI -- `check_consistency.py`, `check_sizes.py` e um `build.py --check` que compara `agents/` com as fontes (o flag antigo só media limites de bytes). Continua aberto o `mcp/`: os testes existem (`npm run test:gate`, 293 casos, cobertura 95.4% acima do budget 90/75/80) e foram executados nesta sessão, mas **nenhum passo do `quality.yml` invoca npm** -- verificado por inspeção do workflow. | médio | médio |
| 5 | Skills em português; sem tradução para inglês | baixo — alcance | alto |
| 6 | `external/` é só documentação; nenhuma skill externa é testada junto | baixo | — |
| 7 | Sem `evals/results/` versionado (histórico de execução) | médio — falta série temporal | médio |
| 8 | **Resolvido (2026-11-17):** a ponte dependia de `.dz23-arsenal`; movido o repo, as skills instaladas pulavam as checagens comuns e ainda saíam com exit 0 — veredito inflado, não degradação visível como eu havia registrado. `skill_validator.py` e `_achar_arsenal.py` agora são conteúdo versionado de cada skill, com preferência pela cópia local; o ponteiro virou otimização. Prova: repo "movido" + referência quebrada na instalação → exit 1 apontando o caminho. | — | — |
| 8b | **Resolvido na mesma sessão:** a duplicação intencional ganhou gate. `scripts/check-copies.py` confere por SHA que as cópias de `skill_validator.py` e `_achar_arsenal.py` dentro das dez skills batem com a fonte (20 comparações), roda no `quality-gate` e no CI. Controles executados: divergir uma cópia → exit 1; apagar uma cópia → exit 1. | — | — |
| 9 | `verifica_claims.py` confere caminho de arquivo e detecta grandeza com unidade (`850ms`, `42%`) como `sem-suporte`. Citação longa, afirmação de comportamento e fato externo **nem são detectados** -- não aparecem em lugar nenhum, nem como sem-suporte. Por isso `sem_suporte = 0` não significa "nada ficou de fora". O extrator original cataloga ~30 tipos; crescer um por vez, cada um com selftest positivo e negativo. | médio | médio |
| 9b | `check-copies.py` vigia apenas os **dois módulos embutidos** listados em `MODULOS_EMBUTIDOS`. Um terceiro arquivo copiado para dentro das skills sem entrar na lista passa verde sem nenhuma conferição. A lista é explícita de propósito (evitar falso positivo), mas precisa ser revista quando algo novo for embutido. | baixo | baixo |
| 10 | `gate_candidatos.py` tem 3 gates e nenhum coletor de sinais acoplado. Sem `--sinais` produzido por ferramenta real, a triagem depende de alguém montar o JSON à mão — o que reintroduz o julgamento que o gate existe para eliminar. | alto | médio |
| 11 | Técnicas absorvidas ainda sem implementação: review fan-out com dedup por evidência, ledger de aprovação com epoch/claim único, calibração bidirecional com fixture held-out, score ponderado must/should/could, guard-rail clean-room executável. Ver `external/absorcao-2026-11-17.md`. | alto | médio–alto |
| 12 | MCP e bundle seguem com defeitos funcionais próprios, medidos nesta varredura: `mission_status` e `mission_status_job` apontam para a mesma função; jobs vivem em `Map` in-process cortado em 200 sem nenhuma tool de listagem; badge npm aponta para pacote que devolve 404; pentagi-mcp tem duas cópias divergentes e a registrada no DSH é a que **não** está versionada aqui. | alto | médio |
| 13 | **`.dsh-tmp-a33.txt` na raiz**: 20 blocos de caso de eval com nome de arquivo temporário, commitados na Rodada 3, e **nenhum script do arsenal lê esse caminho**. Conferido por cruzamento: os 20 ids já existem nos `evals.json` das skills, então não há dado perdido — mas o arquivo é um segundo lugar onde esses casos vivem, sem consumidor, e vai apodrecer em silêncio. Renomear para algo explícito (`docs/` ou `external/`) ou apagar depois de confirmar que ninguém depende; enquanto existir sem leitor, alguém vai achar que é fonte. | baixo | baixo |
| 14 | **Discriminância semântica dos evals não é verificável mecanicamente** (medido na rodada 55). Uma lente determinística acusou 102 dos 144 casos como "não discriminantes" usando padrão de negação (`não\|nunca\|evite\|rejeita`) -- errado por construção: `fails_if` deste arsenal descreve a **ação errada** em frase afirmativa ("Aceita o retry como nova cobrança", "Omite a lacuna"), com 46 verbos diferentes abrindo esses campos. Corrigida para afirmar só o que consegue ver (igualdade literal, input idêntico, expected duplicado), a lente ainda falhou no controle negativo: "Recusa X" × "Promete X" divide quase todo o vocabulário e é o padrão de um eval *bem* escrito -- contraste lexical entre os lados é esperado, não defeito. O único achado restante (input de 24 caracteres em `ultimate-pro-max/estados-vazio-erro`) é intencional: simula pedido vago, exatamente o que a skill deve tratar. Forma e cobertura já são conferidas por `run-evals.py --check` (144 casos, 0 erros, 4 avisos). Se um cenário separa boa de má resposta exige julgar português, logo executar o eval: fecha-se essa dívida registrando resultado, não acrescentando heurística. | médio | alto |

## Não objetivos (para não prometer o que não vamos fazer)

- Substituir testes reais de produto: as skills organizam trabalho, não substituem QA.
- Instalar ferramenta sem autorização: toda dependência externa é declarada e `BLOCKED` quando falta.
- Ser framework universal: cobre engenharia de software; não é CRM, não é plataforma de agentes.
- Publicar popularidade (estrelas/downloads): número sem verificação é desinformação.

## Como acompanhar

- `INDEX.md` — inventário gerado dos arquivos (sempre atualizado por CI).
- `CHANGELOG.md` — histórico do arsenal; cada skill tem o seu.
- Issues abertas — o que está em andamento.

## Regra de honestidade deste documento

Quando algo passar de `NOT_TESTED` para `PASS`, este arquivo muda **com o comando e a saída** que provaram.
Enquanto isso, `NOT_TESTED` fica escrito — inclusive aqui.


### Verificação por ataque às ferramentas (rodadas 12--14)

scripts/selftest-ferramentas.py roda no gate e no CI e submete triagem, verificador de
claims e descoberta de arsenal a entrada doente: JSON malformado em nove formas, dezesseis
textos hostis (traversal, bytes de controle, code block, imperativo, numérico, caminho
absoluto, árvore alheia), variável de ambiente inválida e ponteiro mentiroso. Tem
auto-verificação: injeta uma violação conhecida e exige detectá-la -- um harness sem teste
negativo é decoração. Regressões confirmadas ao removê-lo: clamp de prioridade ausente ->
'prioridade 99999999900 fora do teto'; guarda de traversal removida -> 'vazou como alegação
verificável'. Motivo de ser versionado: os dois crashes que originaram estes casos foram
achados em arquivos soltos fora do repo, que morrem com a máquina que os gerou.

### Verificação em ambiente limpo (rodadas 9--10)

Duas rodadas de verificação exercitaram o que os checks do repo não alcançam: um clone
virgem e o corpo do CI como shell. Resultado material:

- Clone novo com `core.autocrlf=false` nasce com `git status` limpo e roda 32/32 sem nada
  instalado -- a renormalização da v1.5.0 segurou fora desta máquina.
- `audit-zips.py` comparava SHA de bytes crus entre duas árvores montadas por mecanismos
  diferentes, e num clone assim acusava 2 arquivos idênticos como divergentes. Corrigido: texto
  conhecido é hasheado com CRLF colapsado, binários seguem byte a byte. Provas com `--dest`
  numa cópia isolada: só-EOL -> EM_DIA; conteúdo alterado -> DIVERGENTE; arquivo extra ->
  DIVERGENTE.
- Os 15 passos `run:` do `quality.yml` foram materializados num bash e passaram em
  `bash -n`. Executados de fato, revelaram fragilidade: sem `python` no PATH, o passo
  "Validador de cada skill" produzia dez `FALHOU` apontando para as skills, quando o problema
  era o interpretador ausente. Agora o passo verifica `command -v python` antes e diz a
  verdade. No runner isto não ocorre (`setup-python`), mas um passo que mente sobre a causa
  de uma falha custa mais tempo do que economiza.
