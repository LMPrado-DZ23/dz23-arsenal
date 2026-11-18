# Defeitos verificados no dz23-arsenal (baseline HEAD 26bc28a)

Relatório de auditoria. Cada item tem comando de reprodução.

**Estado (2026-11-17):** os defeitos dos blocos medidos nesta sessão foram corrigidos e
verificados ao longo das rodadas de verificação seguintes; o registro completo está em
`CHANGELOG.md` (entradas `[1.5.0]` até a mais recente no topo do arquivo) e as dívidas
em aberto no `ROADMAP.md`. O que continua em aberto está declarado lá, não aqui -- este
documento é o retrato do baseline HEAD 26bc28a e não é atualizado depois disso, senão passa
a competir com o changelog.

Este arquivo foi escrito fora da árvore versionada a princípio, e a primeira cópia se perdeu
num `git checkout -- .` — versão solta não sobrevive. Está aqui, dentro do repo, para que a
segunda tenha o mesmo fim evitado.

## Bloco A — medidos por mim nesta sessao

### D1 — CI esta verde com o gate vermelho (o gate e uma loteria de data)

`gh run list` mostra `quality ... success` na main em 2026-11-14T13:25Z (run 43599678174). Rodando o
mesmo gate localmente no MESMO commit:

```
python scripts/quality-gate.py            -> 16/17 passaram
FALHAS: manifesto:check: Rode: python scripts/build-manifest.py
python scripts/build-manifest.py --check  -> DESATUALIZADO (exit 1)
```

**Causa:** `scripts/build-manifest.py:123` escreve `"generated_at": date.today().isoformat()`. O blob
tem `2026-11-14`; em qualquer outro dia o `--check` falha sem nada ter mudado. No dia do push a data
batia, entao passou. O gate nao mede "o inventario reflete as skills" — mede "hoje e o dia do ultimo
push". E o CI nao re-roda a main periodicamente, entao a regressao passa despercebida. A mesma data
vaza para dentro do `INDEX.md` (`:145`), entao regenerar no dia seguinte muda os dois arquivos.

**Correcao:** substituir `generated_at` por hash de conteudo. Data pode viver em comentario nao
comparado, nunca em campo que entra no diff.

### D2 — 93 blobs commitados com CRLF contra o proprio .gitattributes

Diagnostico canonico (`git ls-files --eol`):

```
i/lf    w/lf    attr/text eol=lf    arsenal.json                                  <- correto
i/crlf  w/crlf  attr/text eol=lf    bundle/dz23-dsh-agency/agents/00-diretor.txt   <- rotulo
```

`i/crlf` significa que o **blob no repositorio** contem CRLF, apesar de `attr/text eol=lf`. Nao e
capricho de editor nem config de quem clona. Provas de que nao e efeito local:

- clone novo com `core.autocrlf=false` ja vem com os 93 marcados, **sem rodar nenhum script**;
- `git grep -c -P "\r$" HEAD -- '*.txt' '*.json'` le do objeto git, nao do disco, e da 93;
- por extensao: `txt` 88 de 120 sujos, `json` 5 de 46, mas **`md` 0 de 323**, `py` 0 de 34, `sh` 0 de 3.

**Causa raiz datada:** os perfis do bundle entraram em `c70020b` ("v1.0.0 — 9 skills, 1 MCP..."); o
`.gitattributes` so aparece em `595271d` ("quality gate, CI, manifesto..."). Quem entrou antes da regra
nunca foi renormalizado — por isso o estrago e seletivo e nao global.

Consequencia pratica: **todo clone em Windows nasce com `git status` sujo em 93 arquivos**, e
`git checkout -- .` nao resolve. Quem trabalha no Windows passa a ignorar o `git status` — que e
exatamente onde se detecta edicao acidental.

Prova de que nao houve perda de conteudo: `git diff --ignore-cr-at-eol` = vazio; os 670 arquivos do zip
batem 1:1 com o HEAD.

**Correcao:** `git add --renormalize . && git commit` uma vez com `core.autocrlf=false`. Um diff unico
de 93 arquivos, e depois disso o repo fica silencioso em qualquer SO.

### D3 — README contradiz a si mesmo e ao ROADMAP sobre quantas skills publica

| Onde | Diz |
|---|---|
| `README.md:3` | "Colecao de **9 skills**, 1 MCP e 1 bundle" |
| `README.md:6` | badge `skills-9` |
| `README.md:42` | "Indice — Skills DZ23 (**10**)" |
| `README.md:132` | "tabela comparativa das **9** skills" |
| `README.md:140` | "**10 skills** + **2 MCP** + 1 bundle + **7 skills externas empacotadas**" |
| `README.md:188` | "quality-gate.py # **16 checks**" |
| `README.md:189` | "run-evals.py --report # **45/131**" |
| `README.md:243` | "As **9** skills declaram **~137 cenarios**... Executados: **3**" |
| realidade medida | **10** skills · **2** MCP · **1** bundle · **13** refs externas · **17** checks · **144** declarados · **45** executados |

Quatro numeros diferentes de eval coexistem no mesmo arquivo (131, ~137, 144, e 3-vs-45); as linhas
243–252 formam um bloco obsoleto interno que sobreviveu a atualizacao da tabela da linha 147. No
`ROADMAP.md` o mesmo: linhas 10 e 27 dizem "9 skills / 137 / executados 3", as linhas 57–78 dizem
"144 / 45".

**Consequencia:** os unicos numeros que um leitor externo confia — badge e primeira frase — estao
errados. E o projeto se vende pior do que e: 45 evals executados viram "3".

**Correcao:** derivar contagem do filesystem e do `run-evals.py --report`. Numero digitado apodrece.

### D4 — o gerador do manifesto mente sobre os proprios componentes

Em `arsenal.json`:

```json
"bundles": [ {"path":"mcp/dz23-subagents-universal-mcp"}, {"path":"bundle/dz23-dsh-agency"} ]
"counts":  { ..., "mcp": 1, "bundle": 1 }
```

O MCP principal esta classificado como **bundle** (`build-manifest.py:134-137`, paths hardcoded), e
`counts.mcp=1` (`:128`) apesar de existirem **2** diretorios em `mcp/`. O `pentagi-mcp` **nao aparece no
inventario nenhum**. Como o `--check` compara o JSON consigo mesmo e nao com o disco, nada pega. O
`INDEX.md` herdado imprime "1 MCP · 1 bundle" fixo (`:148`).

**Correcao:** iterar `mcp/*/` e `bundle/*/` com `ler_versao()`; derivar `counts` dos arrays gerados.

### D5 — dois gates rodam e nao pegam o que prometem (prova por injecao)

**(a) `run-evals.py --verify-quotes` fica verde com o verificador desligado.**
`cmd_verify_quotes` faz `return 0` quando `AUDIT-STATUS.json` nao existe ("sem AUDIT-STATUS.json — nada
a verificar"). Reproduzido em copia isolada: renomeei o arquivo para fora do caminho e o comando
continuou retornando exit 0. Apagar o estado de auditoria **desliga silenciosamente** a checagem de
citacao fabricada — a camada 5 inteira.

**(b) `check-eval-results.py` nao cruza NOT_TESTED com o ROADMAP, embora o docstring prometa.**
Docstring `L10`: "todo cenario NOT_TESTED esta mencionado no ROADMAP.md". Codigo `L95-98`:

```python
roadmap = ROADMAP.read_text(...) if ROADMAP.is_file() else ""
if "Status de evals" not in roadmap:
    problemas.append("ROADMAP.md: falta a seccao 'Status de evals'")
```

So procura a string do titulo da secao. Injetei um registro NOT_TESTED fantasma: `PROBLEMAS: 0`, exit 0.
O gate existe, roda no CI, e nunca verificou a afirmacao que anuncia.

### D6 — validadores fracos deixam passar referencia quebrada (prova por injecao)

`validate_skill.py` por skill: `ultimate-pro-max` **15 linhas**, `backend-data-architect` **34**;
`autonomous-improvement-ultimate` **nao tem**. Os bons tem 71–106.

Teste real: inseri em `skills/dz23-backend-data-architect/SKILL.md` uma citacao a
`references/NAO-EXISTE-teste.md` e rodei o validador daquela skill:

```
PASS: 15 arquivos obrigatorios; 15 arquivos Markdown; frontmatter valido.
EXIT=0
```

Referencia apontando para arquivo inexistente passa. O `cartographer` tem a checacao
(`validate_skill.py:55-56`, `ref.is_file`) — os outros quatro nao. Arquivo restaurado e hash conferido.

Somando: `README.md:4` proclama `scripts/` como parte do padrao das 10, mas a skill autonomous tem
pasta `scripts/` vazia e nenhum validador.

### D7 — mapa CURTO incompleto cria beco sem saida para a decima skill

`run-evals.py:34-44`, `check-eval-results.py:26-36` e `record-eval.py:160` mantem tres copias do mesmo
mapa apelido→pasta, **nenhuma com `dz23-postgres-prod-preflight`**. Resultado: `record-eval.py` cria a
pasta com o nome longo e `check-eval-results.py` rejeita como "pasta nao mapeada". A unica skill com
**0 de 13 evals executados** e justamente a que o instrumento nao consegue registrar.

### D8 — pentagi-mcp: duas copias divergentes e a versionada nunca roda

```
arsenal   mcp/pentagi-mcp/src/index.js      sha 60A0B921
original  projects/pentagi-mcp/src/index.js sha B3BF39C0
```

Divergem no GraphQL: arsenal `L156` usa `mutation($input: String, $provider: String)`; original usa
`String!`. Arsenal `L173` espera sub-selecao `stopFlow(flowId:$id){ message }`; original nao tem
sub-selecao. E `install-harnesses.ps1:8` registra no DSH **a copia original** — a copia versionada no
arsenal nunca e a executada, apesar de `NOTA.md` mandar manter as duas iguais.

**NAO VERIFICADO qual das duas esta certa:** o servidor PentAGI nao respondeu (`localhost:2001` timeout
e connection refused), entao nao pude validar contra o schema real. Estado honesto: **a duplicacao e a
divergencia sao fato; qual query e valida e NAO TESTADO.**

Outros problemas nessa ponte, por leitura: `fetch` sem timeout/AbortSignal/retry; TLS inseguro ligado
por padrao (`index.js:39` `!== '0'`, caindo para `NODE_TLS_REJECT_UNAUTHORIZED='0'` na linha 46);
`selftest.js:44` exige o stack de pe, entao nao serve como teste offline; e **sem LICENSE proprio**.

### D9 — bundle: o Diretor nao orquestra mecanicamente

Por leitura de codigo:

- `build.py:96` gera `core + corpo` e cola o mesmo nucleo de 4.042 bytes **88 vezes** = 355.696 dos
  421.729 bytes totais (84,3%). Cada perfil tem ~750 bytes proprios.
- Boa noticia medida: **nao ha duplicacao entre perfis** — Jaccard de shingles de 6 palavras deu 0 pares
  acima de 0,18, e zero sentencas >60 chars repetidas entre perfis. Os 87 sao distintos de verdade.
- Ruim: **zero wiring**. `grep swarm_run|delegate|consensus|memory_checkpoint agents/*.txt` = 0
  ocorrencias. O Diretor e prompt puro. Pior: `DSH_QUICKSTART.md:13` pede ao modelo "criar especialista
  sob demanda" e **nao existe API que crie agente** — a promessa central e mecanicamente inexequivel.
- `build.py` escreve LF num repo cujo blob e CRLF (D2): rodar o gerador marca os 88 arquivos.
- Contagem tripla: `README.md:3` diz 87, `DSH_INTEGRATIONS.md:26` diz 83, `CHANGELOG.md:27` diz 88. O
  `check_consistency.py` C2 so amarra "**N papeis**" ao maior numero de perfil — nao pega o 83 solto.
- Nenhum teste e nenhum CI no bundle. Os validadores (bons, 7/7 PASS agora) so checam formato.

### D10 — MCP: redundancias reais e distribuicao quebrada

- `src/mcp.js:159` e `:214`: `mission_status` e `mission_status_job` chamam **a mesma funcao**
  (`missionStatus(memory, args)`) — dois nomes, um handler.
- Jobs vivem num `Map` in-process (`mission-manager.js:8`) cortado em 200 (`:11`) e **nenhuma tool lista
  jobs**. Perdeu o `job_id` apos `mission_start`, ficou cego.
- Badge npm no `README.md:4` aponta para `@dz23/subagents-universal-mcp`; o registry responde **404**.
  Fora desta maquina, instalar exige clone + caminho absoluto em 3 formatos de config.
- `list_models` / `provider_inventory` / `discover_models` se sobrepoem; `discover_models` tem 1 mencao
  em todo `test/`. `mission_pause/resume/cancel/release/account_status` tem 1 mencao cada; nada testa
  lease expirado durante `delegate`.
- Portabilidade travada por 9 pontos concretos: Node>=22 (Claude Desktop embute runtime proprio), 108
  variaveis `DZ23_` em `.env` (nenhum harness edita .env alheio pela UI), 4 tools invisiveis sem config
  extra, estado compartilhado em `~/.dz23-subagents` entre harnesses, 7 tools `billable:true` sem
  exemplo de budget, `consensus`/`swarm_run` levando minutos contra timeout padrao do Cursor, pacote nao
  publicado, pentagi acoplado a Windows, e o bundle preso a um campo de texto do DSH.

### D11 — CI deixa passar o que o repo diz verificar

Do `quality.yml`, por leitura:

- Nunca roda `build-manifest.py` gerador (so `--check`) → combina com D1 e torna o job imprevisivel.
- Nunca roda `run-evals.py --report`: os **99 cenarios sem resultado** jamais bloqueiam merge.
- Nunca roda `audit-zips.py` nem `verify-cli.ps1` → drift repo×maquina invisivel em CI. E
  `audit-zips.py:116` default `Path.home()/.agents/skills` nao existe no runner: todas viram
  `NAO_INSTALADA` e sai exit 0 sem `--strict` — **gate verde significando zero informacao**.
- Nenhum step toca `mcp/` nem `bundle/` (que tem `test/`, `package.json`, `build.py`,
  `check_consistency.py`) → a divida #4 do ROADMAP segue viva.
- Sem secret scanning, apesar de 3 evals sobre segredo; sem checagem de licenca por componente.
- Passo "Resumo" (`quality.yml:59-73`) tem `if: always()` e `raise SystemExit(0)` quando `gate.json`
  esta ausente — imprime "o gate nao chegou a rodar" e **sai 0**. Confirmado **por leitura**: tentei
  reproduzir em Git-bash e o ambiente nao tem `python3` no PATH, entao o furo esta documentado como
  lido, nao executado.
- `run-evals.py --schema` depende de `jsonschema`; sem `requirements.txt` no ubuntu-latest cai no
  fallback manual (`:110-116`) que **nao pega** campo `expected` so-com-espaco nem propriedades extras.
  O step "validamos contra o schema" degrada silenciosamente para checagem parcial.

### D12 — instrucoes documentadas que nao funcionam como escritas

| Onde | Problema |
|---|---|
| `ROADMAP.md:101` | documenta `--record <skill> <arquivo>`; a assinatura real e `record-eval.py --skill X --eval-id Y --verdict Z` e o artefato e `<data>-<eval-id>.md`, nao JSON por skill. **O comando copiado nao roda.** |
| `README.md:29` | manda `.\scripts\install-all.ps1` sem `pwsh -File`; em cmd puro nao executa |
| `README.md:204` | "O mesmo gate roda em CI a cada push" — falso: faltam `audit-zips`, `verify-cli`, `--report`, `--verify-quotes` isolados |
| `README.md:65` | linha do pentagi-mcp tem 3 celulas para cabecalho de 4 colunas — renderiza deslocado |
| `README.md:140` | "7 skills externas empacotadas" — nada em `external/` e empacotado; sao 13 documentos explicitamente nao redistribuidos (`ROADMAP.md:120`) |
| `installation.md` da ultimate | manda "descobrir o diretorio, nao presumir"; as outras 7 hardcodam `C:\Users\<user>\.agents\skills` — que **nem e** o caminho deste ambiente (`D:\IA-Workspace\Deepseek`) |
| `cli/required.md` × `verify-cli.ps1:12-26` | duas listas independentes de CLI que divergem; nada liga uma a outra |
| `docs/harness-integration.md` | cita `agent-desktop skills get desktop` e MCPs que existem no ambiente do autor, nao no repo clonado — promessa vazia para terceiros |
| `SECURITY.md` | promete canal privado sem CODEOWNERS nem step que o sustente |

### D13 — infra compartilhada existe, mas nada confere indice com o disco

`quality-gate.py` roda 17 checks e **nenhum** compara tabela de indice com o filesystem. Por isso
sobrevivem: `skills/README.md:3` dizendo "Nove skills" e omitindo postgres; celulas com versoes velhas
(devops 1.2.1 vs 1.2.2 real, ultimate 2.2.0 vs 2.2.2); `SKILL.md:78` da autonomous dizendo "12 cenarios"
quando ha 13; `PROMPT-ATIVACAO.txt` congelado em v1.0 enquanto a VERSION avancou (backend 1.1.0, devops
1.2.2, performance 1.3.0) — nenhum validador olha esse arquivo. Contagem de evals esta hardcoded em tres
lugares independentes (validator `len(cases)==16`, README, SKILL.md): adicionar um caso quebra dois em
silencio.

Tambem: `check-links.py:10` so casa link markdown cujo alvo termina em `.md` — link para **diretorio** e link com **ancora**
escapam completamente. `check-structure.py:97` nao checa `title` nem campo
so-whitespace. `check-eval-results.py:53` faz `glob('*/*.md')` de um nivel so e `dados['cases']`/`c['id']`
sem guard (KeyError vira traceback). `check-audit-inputs.py:156` faz `Path(None)` quando chamado sem
argumento (traceback em vez de exit 2). `check-audit-quotes.py:117` casa citacao por prefixo numerico do
**arquivo** enquanto o laudo numera `### Eval NN` — se as numeracoes divergirem, confere contra a resposta
errada ou marca tudo FABRICADO em silencio. `audit-package/` guarda **copias paralelas** de 7 SKILL.md e
16 evals sem sincronismo com `skills/`: os verificadores de citacao conferem contra snapshot antigo sem
avisar.

### D14 — vocabulario de estados rival e saida so em bash numa maquina Windows

`autonomous-improvement-ultimate/SKILL.md:40` usa `NOT_RUN`; as outras nove usam `NOT_TESTED`;
`run-evals.py:218` aceita os dois por regex, entao as grafias rivais convivem no registro — que e justo
onde o numero de cobertura e lido.

E: **105 blocos ```` ```bash ```` e zero equivalente PowerShell**, numa maquina Windows sem
`rg`/`head`/`tail`/`uniq` no PATH. A receita do cartographer (`mapping-playbook.md:16`) usa
`tail|sort|uniq|head` e nao roda aqui. `reverse-engineer` concentra 36 desses blocos.

---

## Nota de metodo — meus erros nesta sessao (registrados para nao repetir)

Acusei dois scripts inocentes e perdi um arquivo meu. Os tres episodios:

1. **Acusei `build-manifest.py` e `add_arsenal_readme.py` de reescrever 93 arquivos alheios.** Falso.
   Teste isolado em clone limpo: o gerador marca **exatamente 2** arquivos (`INDEX.md`, `arsenal.json`)
   e o `add_arsenal_readme.py` marcou **0** ("já tem seção"). Os 93 ja estavam marcados **antes** de
   qualquer script rodar — causa real no D2. Eu tinha inferido culpa por correlacao temporal em vez de
   isolar a variavel. Correcao aplicada no texto do D2.
2. **Rodei `build-manifest.py` sem `--check` num clone seu antes de ler o que ele escreve.** Ele so
   escrevia 2 arquivos, entao nao houve dano — mas o habito estava errado e me levou ao erro 1.
3. **Perdi o `DEFEITOS-VERIFICADOS.md` que eu havia escrito** ao rodar `git checkout -- .` para limpar o
   ruido de EOL: o comando descartou tambem meu arquivo untracked. Reescrito. Daqui pra frente,
   entregavel meu vive fora da arvore de trabalho do git.

Estado verificado: HEAD `26bc28a` intacto, zero commits meus, nada enviado, conteudo identico ao zip
(`git diff --ignore-cr-at-eol` vazio).
