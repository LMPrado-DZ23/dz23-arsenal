## [1.5.30] — 2026-11-18

### Incorporado (mudança de política: destilar → incorporar)
Cobrança do dono: *"vc deveria copiar pq as skills que montam a UI designer tinham muitas
referências... a ideia é pegar o que cada um pode servir e unificar"*. As rodadas anteriores triavam
e descreviam; nada de código ou dado alheio entrava no repositório. A varredura mostrou por que a
cobrança procedia: **11,8 MB de conhecimento verificável** em 667 arquivos `.md`/`.csv`/`.json`
estavam parados na máquina, tratados como "marginais" sem que o custo de jogar fora fosse medido.

- **`vendor/ui-ux-pro-max-data/`** — 39 arquivos, ~3 MB, licença ISC, cópia byte a byte dos dados
  (scripts e testes da skill de origem ficaram fora): 89 estilos de interface com risco de
  acessibilidade por estilo, 192 perfis por tipo de produto com anti-padrão, 120 diretrizes de UX em
  formato fazer/evitar com severidade, 192 paletas, e catálogo de 1.934 famílias de fonte **com a
  licença de cada uma**. Os dados carregam proveniência própria (`data-provenance.json`) laçando W3C
  e GoogleChrome.
- **`scripts/consulta-design.py`** — acesso ao acervo. Dado sem meio de consulta vira referência
  morta, exatamente a classe que a rodada 47 achou. Resolve em português (`estilo vidro`, `produto
  finanças`, `ux acessibilidade`) via mapa fechado de sinônimos, e responde "sem correspondência"
  quando não há -- nunca aproxima.
- **`skills/dz23-ultimate-pro-max/references/dataset-design.md`** + linha no índice de referências:
  diz *quando* consultar no método operacional (passo 3, direção visual), para que o acervo mude
  comportamento e não só ocupe disco. Skill 2.2.4 → 2.2.5.
- **Licenças lidas antes de copiar**, no arquivo `LICENSE` e não no que o README alega: ECC MIT,
  ui-main MIT, modern-web-guidance Apache-2.0, open-code-review Apache-2.0, impeccable Apache-2.0,
  hallmark/diagram-design/design-system/banner-design MIT, ui-ux-pro-max ISC. Nada restritivo
  encontrado. O que ficou de fora está justificado item por item em **`vendor/VENDOR.md`** --
  inclusive por que incorporar 30 MB de componentes React de terceiro seria pior que usá-los por
  dependência.

### Corrigido
- Dois falsos positivos meus no `consulta-design.py`, ambos achados por prova e não por inspeção:
  escore de substring solta fazia `ux formulario` responder com "Animation :: Duration **Timing**"
  (porque "for" vive dentro de "performance"), e o fallback de plural amplificava o efeito. Removida
  a categoria de match -- casar por palavra inteira resolve o caso legítimo e elimina o engano. Um
  acervo que responde a pergunta certa com a linha errada é pior que um acervo ausente, porque o
  agente passa a confiar. Prova com 11 casos (8 legítimos + 3 controles negativos) em `gate`.
- Três defeitos na minha própria prova de lacuna: ela ancorava `RAIZ` no diretório errado (exit 2 em
  tudo), copiava só uma lista de pastas deixando `CODE_OF_CONDUCT.md` de fora -- o que quebrava
  `check-links` e `.git`, que quebrou `repo_inventory` -- e então declarava "baseline vermelho". Uma
  prova cujo baseline falha não mede nada; corrigida para copiar o checkout inteiro.

### Registrado
- **Dívida 14**: discriminância semântica de eval não é verificável mecanicamente -- fecha-se
  executando os 97 pendentes, não com mais heurística.
- **Dívida 15**: nenhum check exige bump de versão quando o conteúdo de uma skill muda. Medido em
  cópia de baseline verde: linha nova no `SKILL.md`, `VERSION` intacto, gate verde. O único
  reclamante compara hash e silencia ao reinstalar. Não é hipótese -- aconteceu nesta sessão com a
  `ultimate-pro-max`, cuja versão eu teria deixado para trás se não tivesse olhado a saída do
  `install-all`.

Gate 47 → 51 checks (higiene de documento + autoteste, consulta de design + autoteste). CI 31 passos.

## [1.5.29] — 2026-11-18

### Executado
- **Segundo eval de `dz23-postgres-prod-preflight` contra banco vivo**: ``no-statement-timeout``,
  registrado como PASS em ``evals-results/postgres/2026-11-18-no-statement-timeout.md``. Cobertura da
  skill: 0 → 2 de 13; arsenal: 45 → 47 de 144 (97 pendentes). Evidência obtida por comando, com
  medição de tempo real -- não leitura de docstring:

  | Medição | Resultado |
  |---|---|
  | ``pg_settings`` global | statement_timeout / idle_in_transaction / lock_timeout = 0, source=default |
  | consulta cara sem teto | **18,5 s** ocupando a conexão |
  | mesma consulta com ``statement_timeout='1500'`` | cancelada em **1,6 s** |
  | role ``app_web`` com 3s/10s/2s | cortada aos **3,2 s**; os três ``SHOW`` confirmam herança |
  | role ``batch_job`` com 30min | job longo existe separado, como o expected exige |

  Dois achados que o cenário não cobre, registrados como defeito do próprio eval em ``--defects``:
  **(a)** as roles de API deste Supabase **já** têm teto configurado pela plataforma (anon 3s,
  authenticated 8s, service_role 15s, lock_timeout 5s), enquanto a role ``postgres`` -- a que roda
  migration e consolo, onde se executa DDL e query manual -- não tem override nenhum. Quem conferir
  só o default do cluster (que lê 0) conclui o contrário de quem conferir role por role. O risco
  crítico aqui é administrativo, não de aplicação. **(b)** o lugar correto para verificar é
  ``pg_db_role_setting``; ``pg_roles.roloptions`` não existe nesta versão, e consultá-lo produz erro
  em vez de evidência.

### Corrigido
- Contagens de pendência no ROADMAP sincronizadas com o estado real (duas células), e a dívida 1
  atualizada para 97.

## [1.5.28] — 2026-11-18

### Executado
- **Primeiro eval de `dz23-postgres-prod-preflight` rodado contra banco vivo** (a skill estava em
  0/13 desde a criação). ``rls-enabled-without-force`` registrado como PASS em
  ``evals-results/postgres/2026-11-18-rls-enabled-without-force.md``, com evidência obtida por
  ``docker exec psql`` no Postgres 17.11 do container local, schema isolado ``eval_rls`` e duas roles
  criadas para o teste. Cobertura: 45 → 46 de 144 (99 → 98 pendentes). Não foi heurística nem leitura
  de docstring -- é o tipo de registro que a dívida 14 dizia só fechar por execução.

  A cadeia obtida excede o esperado do cenário: ``ENABLE`` sem ``FORCE`` deixa o dono ver as 2 linhas
  dos dois tenants (vazamento confirmado); ``FORCE`` reduz isso a zero; **mas com uma role que tem
  ``rolbypassrls = t`` -- caso do ``postgres`` deste ambiente, que não é superuser -- o vazamento
  persiste mesmo após ``FORCE``**. Nem ``expected`` nem ``fails_if`` mencionam isso. Registrado como
  lacuna do próprio eval em ``--defects``: a receita completa exige três condições simultâneas
  (FORCE + role não-owner + role sem BYPASSRLS), e um guia que ensina duas delas deixa o usuário com
  vazamento aberto e checklist verde.

### Corrigido
- **Duas violações da ``audita-sensibilidade.py`` tinham valor fixo e apodreceram na hora.** O
  ``check-eval-results`` era violado gravando o dígito 99; ao executar o primeiro eval o ROADMAP
  passou a dizer 98, o regex não casou, nenhum arquivo mudou, e a guarda anti-violação-imaginária
  reportou "medição vazia" -- funcionou como desenhada. Mesma sorte tinha o ``checa-ancoras``,
  ancorado em ``## [1.5.``, que teria morrido no primeiro release ``1.6.0``. Agora lê o valor atual e
  escreve outro (``_viola_pendente``), e a âncora virou padrão genérico ``\d+\.\d+\.\d+``; verificado
  simulando ``[1.6.0]`` no topo. Uma violação com literal fixo vence uma revisão e apodrece na
  seguinte.
- Célula da tabela de pendências do ROADMAP, que meu próprio ``re.sub`` havia corrompido para
  ``****Total pendente** | **98****`` ao atualizar o número.

## [1.5.27] — 2026-11-18

### Corrigido — contagens citadas em prosa de skill sem nenhum verificador comparando
Medida a coerência interna do texto que um agente lê ao ativar uma skill (conteúdo, não estrutura).
Duas divergências:

- ``dz23-autonomous-improvement-ultimate`` declarava "12 cenários" com 13 em ``evals.json``
  (2.1.7 → 2.1.8). O validador desta skill confere marcas de seção, anti-loop e vocabulário -- e foi
  ele que, na v2.1.5, encontrou o ``NOT_RUN`` rival. A mesma classe de desvio continuou aberta nos
  números porque ninguém escreveu a checagem correspondente: vocabulário virou regra, contagem não.
  Agora virou, com ``raise SystemExit(1)`` em vez de ``assert`` (que ``python -O`` apagaria), provada
  em três casos e nos dois modos do interpretador.
- ``dz23-e2e-browser-verifier`` guardava no cabeçalho "4 templates e 15 evals", valores da v1.1, com
  6 templates e 16 evals atuais (1.1.2 → 1.1.3). Não era contagem estrutural e sim resíduo de versão
  -- reescrito para não fixar número corrente em prosa, porque cada bump o deixaria mentindo.

### Registrado
Um erro meu durante esta rodada introduziu caracteres chineses no texto português de um SKILL.md
(``conte当前es``), visível só por inspeção. Daí uma varredura de sistema de escrita em todo o repo: 12
ocorrências de CJK, todas legítimas (carga útil de teste em ``selftest-ferramentas.py`` e o caractere
``。`` dentro de um regex em ``skill_validator.py``). Nenhum verificador deste arsenal olhava essa
classe; não virou checagem porque as doze ocorrências atuais estão todas corretas, e um verificador
sem falso positivo conhecido seria decorativo.

## [1.5.26] — 2026-11-18

### Corrigido -- `UNVERIFIED` sobreviveu à unificação de vocabulário da v2.1.5
A rodada 7 unificou `NOT_RUN` → `NOT_TESTED` em quatro arquivos e registrou que a checagem do
próprio validador fora o que encontrou o desvio. Mas deixou um segundo estado rival na mesma skill:
a seção 6 definia `UNVERIFIED` como critério de parada enquanto a seção 2 e as outras nove usavam
`NOT_TESTED`. Trocado, com nota explícita de que não existe vocabulário paralelo por tipo de
trabalho (autonomous 2.1.6 → 2.1.7).

Também corrigido: o eval `visual-proof` esperava «Declara NOT_RUN ou UNVERIFIED» -- dois termos
aposentados nesta skill. Um cenário de avaliação ensinando grafia morta é pior que ausente: quem o
executa aprende o vocabulário errado de propósito.

### Por que nada pegou antes
A checagem de vocabulário procurava apenas `\bNOT_[A-Z_]+\b`. Um rival sem prefixo `NOT` era
invisível ao mecanismo criado para impedir exatamente isso. Reescrita para comparar qualquer rótulo
em CAIXA ALTA entre crases contra lista fechada, reportando com `raise SystemExit(1)` -- a versão
com `assert` desaparecia sob `python -O`, o mesmo defeito banido das dez skills na v2.1.5, que
eu reintroduzi ao escrever a checagem nova.

Prova executada injetando `UNVERIFIED`, `PENDING` e `UNTESTED`: os três recusam nos dois modos;
baseline passa nos dois. Uma variante minha foi corrigida no caminho -- copiar a skill para pasta de
outro nome fazia o baseline falhar por `frontmatter name != diretório`, motivo alheio ao testado.

## [1.5.25] — 2026-11-18

### Verificado sem defeito (varredura de classes, fim de sessao)
Lente aplicada a todo o repo em quatro eixos descobertos uma por uma nas rodadas anteriores, em vez
de um incidente por vez:

| Eixo | Origem | Resultado |
|---|---|---|
| Identidade derivada de bytes crus | r47/r48 | **zero** occorencias restantes |
| Estado externo determinando resultado | r39/r42 | 1 suspeito, descartado: `record-eval` usa `date.today()` para nomear arquivo NOVO de registro -- nao conditiona nenhum check, e `check-eval-results` nao le data |
| Verde devolvido sem medicao | r15/r30/r44 | 13 linhas de `return 0` final, todas o caminho correto de saida depois de imprimir problemas |
| Asserciona sem controle negativo | r43/r46 | **13 verificadores, todos com prova executada** de que sabem reprovar |

Nenhum conserto necessario. Registrado porque ausencia de achado em varredura ampla e resultado, nao
ausencia de varredura -- e as duas primeiras linhas desta tabela sao exatamente os dois defeitos que
as rodadas 47 e 48 corrigiram, agora confirmados como fechados em todo o repo, nao so nos dois
arquivos onde apareceram.

## [1.5.24] — 2026-11-18

### Corrigido -- `check-copies.py` tinha o mesmo defeito da rodada 47
Varredura sistematica por todo ponto que derivava identidade de bytes crus achou `sha()` do
`check-copies` hasheando `read_bytes()` sem normalizar. Convertendo uma das vinte copias
embarcadas para CRLF, o verificador saia com 'DIVERGENCIA ... conteudo difere' -- sugerindo
reescrever um arquivo ja identico semanticamente. Corrigido com a disciplina do arsenal (EOL nunca
e divergencia de conteudo). Tres comportamentos medidos: EOL sozinho passa, conteudo diferente
falha com instrucao de conserto, baseline passa.

### Verificado sem defeito
- `audit-zips.py` ja normalizava texto e mantinha binarios byte a byte desde a rodada 9 -- prova
  executada com instalacao em CRLF deu 10/10 em dia.
- `check-licenses.py` le bytes crus de proposito: decodificar com `errors='strict'` para
  denunciar UTF-8 invalido e mojibake exige ver os bytes como estao. Normalizar ali apagaria o
  sintoma que a checagem procura. Nao e defeito.

## [1.5.23] — 2026-11-18

### Corrigido -- `build-manifest` gravava hash dependente do checkout
O CI real (run 44248537821) falhou em 'Manifesto atualizado' enquanto o gate local dava 46/46
minutos antes. `sha256()` lia bytes crus de `SKILL.md`, entao o manifesto commitado registrava o
hash do disco de quem gerou. Meu working tree tinha CRLF em 15 arquivos versionados -- os blobs estao
LF (confirmado objeto por objeto), mas `core.autocrlf=false` nao converte ao materializar, e
ferramentas Windows escrevem CRLF sem que o git reclame: `git status` limpo, nada denuncia. Um clone
limpo materializa LF, produz hash diferente e declara o manifesto desatualizado para sempre. O check
era verde ou vermelho conforme **quem clonou**, nao conforme o conteudo do repositorio.

Corrigido normalizando `\r\n` -> `\n` antes de hashear texto; binarios continuam byte a byte,
onde CRLF seria dado real. Mesma disciplina de `audit-zips`, `check-copies` e `build.py --check`.
O passo de CRLF do CI nao pegou isto porque compara blobs com `--cached` -- e os blobs estavam
certos; o defeito era derivar identidade de bytes do disco.

Prova da correcao: clone novo com 371 arquivos convertidos para CRLF no disco -> `--check` passa.
Com a funcao antiga, as dez skills divergiriam (0 bateram, 10 divergiram). Working tree tambem
normalizado para LF, alinhando disco e blob.

# Changelog — dz23-arsenal

Histórico de releases **do arsenal**. O changelog de cada skill fica dentro da própria pasta
(`skills/<nome>/CHANGELOG.md`).

## [1.5.22] -- 2026-11-18

### Corrigido -- duas referencias existiam sem nenhum texto da skill as enderecar
Medida nova: das 110 referencias nas dez skills, quais sao citadas por alguma instrucao que o
agente efetivamente carrega. Duas nao eram -- `diagnostic-playbook.md` (performance, 3.724
caracteres de sintoma -> camada -> primeira medicao) e `verificacao.md` (postgres, registro do
que foi executado contra banco real). Ambas apareciam so no README da skill, arquivo que o agente
nao le ao ativar. Resultado: conteudo correto, mantido, versionado -- e inalcanavel em uso.

Bump PATCH nas duas (1.3.2->1.3.3, 1.1.1->1.1.2), com PROMPT-ATIVACAO regenerado onde necessario.
O validador da performance pegou a dessincronizacao sozinho e recusou ate o arquivo ser corrigido.

### Registrado
Um medidor meu acusou uma terceira referencia quebrada que nao existia: a frase
`dz23-devops-cloud-deployer (`references/supply-chain-security.md`)` nomeia a skill dona do
arquivo -- leitura correta, nao defeito. O medidor so conhecia a propria pasta. Corrigido para
resolver referencias entre skills antes de reclamar.

## [1.5.21] -- 2026-11-18

### Adicionado
- **`scripts/executa-scripts-skills.py`** -- roda os onze scripts que os proprios SKILL.md mandam
  o agente executar (`skills/<x>/scripts/*.py`), com controle negativo por verificador. Ate agora
  nada neste arsenal os executava: `validate_skill.py`, `check-structure` e o gate conferem
  arquivos, frontmatter, referencias e evals -- nenhum dos onze foi exercitado uma vez sequer. Um
  script de skill que quebrasse no primeiro uso transformaria a habilidade inteira em instrucao
  falsa sem sinal algum. Entra no gate (**44 checks**) e no CI.
- Casos cobertos (15): `repo_probe` (JSON com tipo conferido), `repo_inventory`, `file_triage`
  (confirma `read_only=true`), `validate_spec` contra o exemplo que a propria skill distribui +
  spec vazia reprovada, `check_gherkin` valido e invalido, `check_budget` dentro e estourado
  (`BUDGET_FAIL` exigido), mais cinco scripts de ambiente externo ao menos respondendo ao
  `--help` sem traceback.

### Verificado sem defeito
Os onze rodam corretamente. As duas primeiras tentativas desta suite acusaram problemas inexistentes
porque eu inventei o formato de entrada: passei JSON onde `check_budget` le tabela markdown
(`INVALID bm.json: nenhuma tabela markdown encontrada`) e markdown onde `validate_spec` le JSON
(`Expecting value: line 1 column 1`). Ambos documentam o formato na docstring, e a skill distribui
`examples/spec-example.json` -- usar a entrada que o alvo declara, nao a que parece natural, e o
que tornou a medida valida.

## [1.5.20] -- 2026-11-18

### Adicionado
- **`instalacao:conteudo` no `quality-gate`** (43 checks) e passo proprio no CI. O verificador
  da instalacao existia desde a rodada 9 e nunca rodou em lugar nenhum automatizado -- nem no gate,
  nem no workflow -- porque em runner efemero nada esta instalado. Roda agora sem `--strict`,
  escolha deliberada e registrada no comentario: divergencia de conteudo entre repo e
  `~/.agents/skills` e defeito real e deve quebrar o build; ausencia de instalacao e condicao
  normal do ambiente, nao violacao do repositorio. Com `--strict` o check seria vermelho em todo
  CI e alguem acabaria removendo-o. Os tres estados foram medidos: maquina com instalacao exit 0;
  `HOME` vazio exit 0; instalacao adulterada (linha injetada num SKILL.md instalado) -> gate
  42/43 denunciando `1 divergentes`, restaurado volta a 43/43.

## [1.5.19] -- 2026-11-18

### Adicionado
- **`scripts/audita-sensibilidade.py`** -- aplica aos verificadores do gate a regra da rodada 43:
  para cada um, injetar uma violacao do dominio que ele enuncia (em copia) e exigir exit != 0.
  Nove cobertos: `check-structure`, `check-copies`, `check-numbers`, `check-licenses`,
  `check-links`, `check-docs-runnable`, `check-eval-results`, `checa-ancoras`,
  `gera-indice-skills`. Todos reprovam. Entra no gate (**42 checks**) e no CI.
- **Guarda contra violacao imaginaria**, com prova propria (`scripts/prova-sensibilidade.py`).
  Duas das primeiras execucoes desta auditoria acusaram `check-licenses` e
  `check-eval-results` de ser ocos -- eram meus testes inventando violacoes: apaguei o
  `LICENSE` da raiz (o verificador percorre `mcp/` e `bundle/`) e reescrevi
  `Total pendente 99` quando o ROADMAP guarda tabela `**Total pendente** | **99**`. Agora a
  assinatura compara conteudo por texto com EOL normalizado; se nada mudou semanticamente, o caso
  sai como `SETUP! violacao sem efeito` e nunca como verificador oco nem como aprovado.

### Corrigido
- A primeira versao da guarda usou tamanho+mtime (enganada por `write_text` reescrevendo o
  arquivo identico) e depois SHA de bytes crus -- `Path.write_text` aplica newline universal,
  entao converter CRLF→LF altera os bytes (medido: 15 345 → 15 559 num ROADMAP de 214 linhas) sem
  nenhuma edicao pretendida. Normalizar as quebras de linha antes de hashear resolve, e e a mesma
  disciplina ja aplicada em `audit-zips` e `build.py --check`: EOL nunca e divergencia de
  conteudo.

## [1.5.18] -- 2026-11-18

### Corrigido -- quatro alegacoes dependiam de `exit != 0` sem dizer o que reprovou
Varredura da fragilidade achada na rodada 42 (prova que aceita qualquer reprovação) sobre todo o
`audita-alegacoes.py`: quatro provas mediam apenas codigo de saida. Cada uma agora exige tambem
que a violacao correspondente ao que ela enuncia seja detectada, em copia:

| Alegacao | Risco anterior | Reforco |
|---|---|---|
| validador nao aprova sob `python -O` | a referencia injetada e pega tambem pela checagem propria; qualquer exit != 0 bastava | reproduz o padrao antigo (`assert not _erros_comuns`) numa copia e exige que ele mude o resultado sob `-O`; medido: normal=1, `-O`=0 com bug historico, hoje ambos =1 |
| indice de skills bate com o disco | `--check` virar no-op daria 0 para sempre | viola a versao numa copia e exige reclame |
| `agents/` do bundle sincronizado | foi literalmente um verificador oco por meses (rodada 28) | adultera um agente em copia e exige reclame |
| comandos da documentacao resolvem | idem; alem disso poderia ler zero docs | injeta comando quebrado em copia, exige reclame e confere que houve contagem de linhas lidas |

Custo medido: auditor de 6 s para 12 s. Nenhuma escrita fora de diretorio temporario (arvore
verificada limpa apos a execucao).

## [1.5.17] -- 2026-11-18

### Corrigido
- **A prova da alegação `skill instalada reprova mesmo sem o repo` não distinguia os dois
  mecanismos que poderiam sustentá-la.** Ela exigia apenas `exit != 0`, mas a resistência vem da
  cópia embarcada de `skill_validator.py` (primeiro ramo de `importar_validador_comum`), não do
  ponteiro: com ponte morta, `localizar_arsenal` devolve `None` e ainda assim o validador
  resolve o módulo de dentro da própria cópia. Um teste que aceita qualquer reprovação passaria
  verde numa regressão em que a cópia embarcada sumisse -- desde que a checagem própria da skill
  reprovasse por outro motivo. Agora a prova exige que um validador comum tenha sido carregado e
  que ele venha de dentro da cópia. Provado no sentido inverso: removendo a cópia embarcada,
  `importar_validador_comum` devolve `None` e a nova prova levanta AssertionError.

### Verificado sem defeito
- **Alegação da rodada 7 continua verdadeira.** Três violações distintas reprovam com ponte morta
  (referência quebrada, `name` divergente, markdown vazio). O que parecia contradição era erro de
  medição minha, em três formas diferentes registradas aqui para não repetir: usar alvo coberto por
  ambas as camadas, deixar de aplicar a violação (regex com `\$` escapado dentro de here-string)
  e reusar o mesmo diretório temporário entre estados.
- **Clone em outro caminho** roda o gate inteiro (40 checks sem dependências npm, 41 com elas), as
  quatro suítes de prova passam lá, instalar a partir dele funciona e a instalação resultante
  valida contra o clone. Restaurada ao repo original depois.
- Nenhuma perda real de cobertura no ramo de arsenal ausente na configuração que o
  `install-all` produz.

## [1.5.16] -- 2026-11-18

### Corrigido -- alegacoes sem medidor inventavam sucesso
- **`audita-alegacoes.py` `crlf()`**: sem `bash` acessível, `subprocess.run` com caminho
  inexistente levanta erro? Não -- nas condições testadas o resultado vinha com stdout vazio, e
  `return not p.stdout...strip()` lia vazio como "sem CRLF" = **OK inventado sem medir nada**.
  Um gate-fantasma da classe mais antiga desta sessão, criado por mim ao escrever a prova. Agora
  retorna `NA` quando não há medidor (a função irmã já tinha a guarda; esta não).
- **`check-numbers.py`** pulava em silêncio toda alegação cujo medidor não existia (node
  ausente): a saída continuava dizendo `nenhuma divergência numérica`, lida como "tudo
  conferido". Passa a listar `N/A (sem medidor aqui): ...` e a encerrar com a contagem do que
  faltou. Comportamento provado comparando as duas versões no mesmo ambiente sem node: antes
  silenciava, depois declara -- e ausência de medidor continua sem quebrar o build.

### Registrado
O terceiro estado (OK / CAIU / N/A) aplicado a claims existe desde a rodada 3; levou trinta e nove
rodadas para eu aplicá-lo aos instrumentos que escrevi depois dele.

## [1.5.15] -- 2026-11-18

### Corrigido (descoberto pela primeira execucao real do CI, apos 38 rodadas locais)
- **Testes de descoberta usavam caminho Windows como "inexistente".** D:\caminho\que\nao\existe
  e absoluto em Windows; no Linux backslash nao e separador, entao virou um nome de arquivo
  RELATIVO ao cwd -- e como o CI roda dentro do checkout, resolveu para o proprio arsenal. O
  teste media presenca, nao ausencia: passou 38 rodadas aqui e falhou la. Trocado por caminho
  derivado de `tempfile.gettempdir()` + pid, ausente em qualquer sistema. Varredura do padrao
  em todos os `.py` achou uma segunda ocorrencia adormecida (retornava cedo quando a skill nao
  estava instalada, logo nunca exercitada); corrigidas as duas.
- **O auditor nao tinha estado "nao aplicavel".** Duas provas dependem de `~/.agents/skills`,
  inexistente num runner efemero; retornavam `False` querendo dizer "sem como aferir", e o
  `afirma()` lia isso como reprovacao -- exit 1 sem defeito no repo. Ganhou terceiro estado
  explicito (`NA`), impresso e contabilizado a parte, com a contagem final comparando
  identidade (`ok is False`) porque `not None` e verdadeiro. E a mesma disciplina que
  `verifica_claims` aplica a claims ha muito tempo (`nao-verificavel` fora do denominador),
  ausente no instrumento que escrevi depois dele.

### Estado
CI verde em execucao real: run 44238184690, commit `2ba2cb4`, 28 passos,
`checks: 40 | falhas: 0`. Antes disto, nada desta linha de trabalho havia passado por um
runner -- o workflow existia configurado desde 2026-11-09, mas so rodara em commits anteriores.

## [1.5.14] — 2026-11-17

### Corrigido
- **`CHANGELOG.md` estava fora de ordem.** As entradas `[1.5.9]`–`[1.5.13]` apareciam
  *depois* da `[1.5.0]`, e `[1.5.1]` antes de `[1.5.2]`. Causa minha: inseri cada entrada
  nova usando sempre o mesmo cabeçalho como âncora, em vez do topo corrente -- resultado: um
  changelog onde a versão mais antiga vem primeiro, que não conta história, inverte a leitura.
  Reordenado por bloco, byte a byte, com prova de preservação (multiconjunto de linhas idêntico
  antes e depois: zero linhas sem par). `[1.5.1]`/`[1.5.2]` já estavam trocados antes desta
  sessão; mesma correção se aplicou.
- **`.github/workflows/quality.yml` passo `Resumo`** lia `gate.json` com
  `read_text()` sem encoding -- funciona no Ubuntu por sorte de locale, quebra fora dele.

### Adicionado
- Alegação permanente no `audita-alegacoes.py`: `CHANGELOG em ordem de versão descendente`.
  Provada ao mover a `[1.0.0]` para o topo numa cópia -- exit 1.

## [1.5.13] — 2026-11-17

### Corrigido
- **`run-evals.py --schema` dizia "OK" com validação parcial.** Sem `jsonschema` instalado, o
  código caía num checador manual (campos obrigatórios + padrão de `id`) e imprimia a mesma
  linha `skills validadas contra evals.schema.json: OK` que o caminho completo -- sem
  `enum`, `minLength`, `additionalProperties` nem verificação de tipo. Um ambiente sem a
  dependência parecia ter aprovado uma validação de schema integral. O CI foi corrigido na v1.5.0
  para instalar `jsonschema` justamente por causa desse fallback silencioso; o código em si
  continuou mentindo. Agora imprime `AVISO: ... validação PARCIAL` em stderr antes do resultado.
  Verificado desinstalando a lib num venv limpo: aviso aparece, exit 0 (o parcial ainda é
  verdade), e removendo um `fails_if` real o mesmo modo parcial denuncia -- ou seja, degradar
  não é o mesmo que falhar.

### Verificado sem defeito
Execução em ambiente isolado (venv novo, só stdlib + `jsonschema`, como o runner): os dez
verificadores, o `quality-gate` completo (**39/39**), os três validadores do bundle e o
`build.py --check` rodam sem depender de pacote oculto do Python global desta máquina.
## [1.5.12] — 2026-11-17

### Adicionado
- **Prova da cadeia de citação** em `scripts/audita-alegacoes.py` (14ª alegação): copia laudo +
  respostas para diretório temporário, inventa texto dentro de uma citação real de um laudo
  `VALIDO` e exige que `--verify-quotes` saia com erro. Resultado: `fabricado= 1`, exit 1,
  apontando exatamente o laudo violado -- a checagem que protege contra evidência inventada
  (o defeito original da auditoria de 2026-11-09) está viva nos dois sentidos.
- Auditor mapeou também a cobertura de execução: dos 27 scripts em `scripts/`, 21 são
  alcançáveis pelo gate ou pelo CI por cadeia de chamada. Os seis restantes são instaladores
  (`install-all.*`, `verify-cli.ps1`), gerador pontual (`add_arsenal_readme.py`) e o
  próprio `prova-verificadores.py`, que altera disco e por isso roda à mão.
## [1.5.11] — 2026-11-17

### Corrigido — o auditor de alegações corrompia o repositório que auditava
`scripts/audita-alegacoes.py` entrava na sessão com oito provas, escritas no padrão
"corrompe o arquivo real do repo, restaura em `finally`". Duas falhas nesse desenho apareceram
ao estender o arquivo:

- **`TimeoutExpired` dentro do `try` pula o `finally`.** Uma das alegações novas chamava o
  `quality-gate`, que por sua vez executa este mesmo auditor -- recursão. Em 241 s de execução
  o prazo estourou, o `finally` não rodou e ficaram **38 linhas injetadas** em
  `skills/dz23-e2e-browser-verifier/SKILL.md` mais um README mentiroso. Como cada execução
  acrescentava uma linha sem remover a anterior, o dano era cumulativo e invisível ao
  `git status` de quem só olha a última linha. Restaurado do HEAD.
- Um auditor que precisa danificar o alvo para testá-lo está mal desenhado, não destemido: além
  do timeout, qualquer crash entre escrever e restaurar faz o mesmo, e duas verificações
  concorrentes leem o estado que a outra corrompeu. O dano na instalação do usuário nem aparece
  no git.

Reescrito sem mutação: as provas copiam skill/instalação para diretório temporário e corrompem a
cópia (`audit-zips` aceita `--dest`; o validador resolve arsenal pela própria localização,
então uma cópia fora de `~/.agents/skills` reproduz o cenário "repo movido" fielmente). A
verificação de contagem passou a ler `.gate-contagem` em vez de invocar o gate, eliminando a
recursão. Resultado: **13/13 alegações sustentadas em 5 s** (eram 241 s com estouro), árvore
intacta após a execução.

Também corrigido no mesmo lance: `afirma()` fazia `ok = fn()`, então qualquer função no estilo
"lança em vez de retornar bool" devolvia `None` e era contada como falha -- cinco verificações
corretas apareceram como "alegação não sustentada" contra um repo verde. Aceita os dois contratos.

Alegações cobertas agora: os dois gates-fantasma originais fechados, `check-audit-inputs` sem
argumento, regra órfã denunciada, referência quebrada reprovada, `python -O` sem desligar
validador, skill instalada auto-validando sem checkout, índice sem CRLF, EOL não confundido com
divergência, contagem derivada da execução, índice de skills em dia, `agents/` do bundle
sincronizado e comandos da documentação apontando para arquivos reais.
## [1.5.10] — 2026-11-17

### Adicionado
- **`scripts/prova-verificadores.py`** -- corrompe de propósito o estado que cada `--check` do
  repo promete caçar e exige exit ≠ 0 em todos os nove (contagem do manifesto, versão no índice de
  skills, agente adulterado no bundle, cópia embutida divergente, número mentiroso no README,
  comando de doc apontando para arquivo inexistente, link quebrado, `VERSION` diferente do
  declarada, instalação fora do sync). Termina conferindo que a árvore voltou ao HEAD.
  Rodado: **9/9 recusam**, restauração limpa. Provado também no sentido inverso -- um dano real não
  restaurado é denunciado (exit 1), então a checagem de integridade não é decorativa.
  Não entra no `quality-gate` porque o gate executa esses mesmos checks e um teste que altera o
  disco concorrente consigo mesmo daria resultado instável; roda à mão antes do PR, com seção
  própria no CONTRIBUTING ("Verificadores: provar que reprovam") listando o mínimo de um check
  novo extraído das rodadas desta sessão.
## [1.5.9] — 2026-11-17

### Corrigido
- **`bundle/dz23-dsh-agency/build.py --check` não comparava nada.** O flag media limites de
  bytes e imprimia "RESULTADO: OK (modo --check, nada foi escrito)" -- um `--check` que não
  confere o que o nome promete é pior que ausência, porque alguém chama, vê OK e confia. Os 88
  arquivos de `agents/` são gerados e versionados sem verificador algum. Agora compara com as
  fontes e denuncia `FALTA`, `DIVERGE` e `SOBRA` (arquivo que nenhuma fonte produz).
  Provado nas duas direções: linha injetada → `DIVERGE agents/00-diretor.txt` exit 1; arquivo
  apagado → `FALTA …` exit 1; restaurado → OK.
- **`build.py` escrevia CRLF em Windows**, então rodar o gerador sujava o repositório inteiro
  -- reproduzido no repo real: 88 arquivos como "modificados" contra o `*.txt text eol=lf` do
  `.gitattributes`. Conteúdo idêntico ignorando EOL, mas ninguém distingue isso de edição real.
  Corrigido com `newline="\n"`; provado gerando os 88 e vendo `git status` limpo.

### Adicionado
- Três validadores próprios do bundle (`check_consistency.py`, `check_sizes.py`,
  `build.py --check`) entraram no `quality-gate` (**39 checks**) e no CI como passo próprio.
  Existiam e eram executados à mão desde sempre; nenhum estava automatizado. Dívida 4 do
  ROADMAP parcialmente fechada -- falta o `mcp/`, que tem `npm run test:gate` mas nada o
  chama neste workflow.
## [1.5.8] — 2026-11-17

### Corrigido — índice de skills descrevia um repositório que não existe
Verificado lendo skills/README.md contra o disco: **as 9 linhas da tabela divergiam** e uma
décima skill não tinha linha nenhuma. Não era detalhe cosmético -- é o índice que um agente lê
para decidir qual skill carregar. Amostra do que estava errado:

| Skill | Tabela dizia | Disco tinha |
|---|---|---|
| ultimate-pro-max | 0 evals, versão 2.2.0 | 13 cenários, 2.2.4 |
| devops-cloud-deployer | 7 templates, 15 evals, v1.2.1 | 3 templates, 16 evals, v1.2.3 |
| autonomous-improvement-ultimate | 0 scripts, 12 evals, "Nove skills" | 3 scripts, 13 evals, 10 skills |
| postgres-prod-preflight | ausente da tabela | existe, 13 evals |

Nenhuma checagem via isso porque check-numbers.py só varria README.md e ROADMAP.md, e o
texto dizia "Nove" por extenso -- fora do alcance de qualquer regex de dígito.

### Adicionado
- **`scripts/gera-indice-skills.py`** -- regenera a tabela a partir do filesystem (versão,
  contagens de refs/templates/scripts/evals). Categoria e complexidade continuam julgamento
  humano, agora explicitamente no script em vez de na tabela. `--check` integra o gate
  (36 checks) e o CI: editar a tabela à mão volta a ser visível. Provado mudando uma versão na
  mão → `DESATUALIZADO`, exit 1; regenerado → em dia. Resultado: 10 linhas, zero divergência,
  110 referências e 144 cenários conferidos contra o declarado.
## [1.5.7] — 2026-11-17

### Adicionado
- **`scripts/check-docs-runnable.py`** -- confere que todo arquivo citado num bloco de comando
  da documentação existe, com ancoragem correta (caminho em seção de skill resolve dentro dela).
  Roda no gate (35 checks) e no CI. Nasce de uma lacuna que nenhuma checagem cobria: links
  apontam para arquivos, mas ninguém verificava os **comandos** que o repo manda executar. Na
  rodada 25 isso deixou passar um CONTRIBUTING que mandava copiar um validador não-copiável e
  mostrava `evals.json` rejeitado pelo schema -- visível só para quem seguisse o guia à mão.
  Reconhece três escapes legítimos: placeholder de modelo (`skills/<nome>/...`), comentário
  dentro do bloco e contingência explícita (`|| echo`, `2>/dev/null`), que é como
  `cli/verify.md` declara a ausência do `verify-cli.sh`. Medido: 196 linhas de comando em 22
  documentos, zero referências quebradas. Prova de que detecta: injetando
  `python scripts/validador-que-nao-existe.py` no CONTRIBUTING, denunciou na linha certa.
## [1.5.6] — 2026-11-17

### Corrigido — `CONTRIBUTING.md` não permitia criar uma skill
Verificado atuando como mantenedor novo: criei uma skill seguindo **somente** o documento e o
gate recusou em sete checks. Três defeitos eram do próprio texto:
- Mandava copiar os três arquivos de `scripts/` de uma skill existente. O
  `validate_skill.py` carrega a lista própria de referências e templates daquela skill (a
  cartographer fixa 19 nomes, a spec-to-system 23), então herdar o validador alheio faz a skill
  nova exigir arquivos que nunca vão existir. Passou a mandar copiar só os dois módulos
  compartilhados e escrever o `validate_skill.py` próprio, com esqueleto mínimo.
- Nada dizia que `skill_validator.py` e `_achar_arsenal.py` precisam estar dentro de cada
  skill -- exigência que o `check-copies` (v1.5.1) reprova sem avisar o porquê. Agora há seção
  própria com a razão funcional (auto-validação fora do checkout) e o comando de propagação.
- A forma de `evals.json` estava errada: listava quatro campos omitindo `title`, obrigatório
  no schema, e mostrava `expected`/`fails_if` como listas quando o schema declara string com
  `minLength: 5` -- os 144 casos do repo usam string. Também usava `skill_name` e
  `schema_version: "1.0"`, ambos rejeitados pelo topo do schema (`additionalProperties: false`,
  número inteiro). Reescrito copiando do `evals.schema.json`, com a fonte apontada.

Re-testado ao pé da letra: skill criada pelo documento passa em `validate_skill.py`,
`run-evals.py --schema` e `check-copies.py`; o gate reclama apenas das contagens que a skill
nova muda de fato (145 cenários, 100 pendentes) -- comportamento correto, não defeito.

### Registrado sem corrigir
Nove `validate_skill.py` acumulam ~120 `assert` de checagens próprias. Não são exploráveis
hoje: as checagens comuns usam `SystemExit` e pegam os mesmos casos (verificado removendo um
template e rodando com e sem `-O` -- exit 1 nos dois modos). Documentado no CONTRIBUTING para
converter ao tocar nesses arquivos, em vez de mexer em nove validadores às vésperas de fechar a
sessão.
## [1.5.5] — 2026-11-17

### Corrigido
- **`install-all.sh` mandava rodar `scripts/verify-cli.sh`, arquivo que nunca existiu.** Só
  há o `.ps1`. Quem seguisse o passo final de uma instalação em Linux/macOS recebia "No such
  file or directory" logo depois de um instalador bem-sucedido -- a pior hora para um comando
  errado. A linha também usava `python3`, ausente em alguns ambientes Windows (Git-bash sem
  Python no PATH, verificado aqui). Instrução substituída pelas verificações reais, com nota
  explícita de que não existe variante shell do contador de CLIs. Achado seguindo o
  `docs/getting-started.md` literalmente num clone limpo, não lendo o código.
## [1.5.4] — 2026-11-17

### Corrigido
- **`install-all.ps1` propagava `__pycache__` obsoleto para a instalação.** O repo guarda o
  diretório no disco (ignorado pelo git, mas presente); `Copy-Item -Recurse` levava o bytecode
  junto. Medido nesta máquina: 53 arquivos `.pyc`, dos quais **10 com mtime/size diferente do
  fonte** -- justamente os `validate_skill.py` reescritos na v1.5.2. Não é risco de execução:
  verificado que o Python re-compila sozinho e o validador detecta referência quebrada mesmo com
  o `.pyc` velho. Mas faz inspeção humana mentir sobre qual versão está instalada, e foi
  descoberto exatamente porque alguém (eu, nesta sessão) olhou o conteúdo. A instalação agora é
  limpa em origem; provado sujando de propósito (2 pastas antes, 0 depois).
## [1.5.3] — 2026-11-17

### Corrigido
- **`verifica_claims.py` tratava prosa como caminho de arquivo.** O filtro de placeholder era
  aplicado ao texto inteiro, então qualquer frase contendo "placeholder" ou "inexistente" fazia o
  caminho citado na mesma linha virar não-verificável. Medido: 24 ocorrências ignoradas no repo --
  inclusive um documento que descreve o próprio defeito ("Referencia apontando para arquivo
  inexistente passa") e assim se auto-censurava. Restrito a candidatos com forma de caminho
  (`RE_PARECE_CAMINHO`), com sufixos de placeholder insensíveis a caixa: `nao-existe-*` em
  minúsculas escapava porque o ramo exigia `[A-Z0-9._-]*`. Versão 1.3.0 → 1.4.0.
- **`quality-gate` chamava `verifica_claims` sem `--min`,** isto é, em modo relatório: o
  script detecta o caminho quebrado, imprime, e sai 0. Injetando uma referência plausível
  inexistente, o `validate:` da skill pegava e o `claims:` saía OK -- dois checks do mesmo
  gate discordando. Agora `--min 1.0` torna o check decisório.

### Adicionado
- **`scripts/audita-alegacoes.py`** -- re-executa a experiência por trás de cada afirmação
  qualitativa desta linha de trabalho (oito delas: gates-fantasma fechados, skill instalada
  auto-validando sem checkout, `python -O` sem desligar validador, CRLF decidido pelo índice,
  EOL não confundido com divergência, regra órfã denunciada). Número quebra alto porque algum
  check reclama; frase do tipo "X agora falha quando Y" apodrece em silêncio -- alguém remove a
  guarda e o CHANGELOG continua descrevendo um sistema que não existe. Roda no gate (34 checks)
  e no CI.
## [1.5.2] — 2026-11-17

### Corrigido — validadores desligáveis por flag do interpretador
- **`assert not _erros_comuns` nas dez skills**: sob `python -O` o interpretador remove a
  instrução, e o `validate_skill.py` imprimia `OK — ... 13 evals · 5 referências` com uma
  referência quebrada, saindo **0**. Reproduzido em todas as dez antes da correção. Um gate que
  desaparece por uma flag é pior que ausência dele — continua parecendo conferido. Trocado por
  impressão em stderr + `SystemExit(1)`, válido nos dois modos. Bump PATCH em cada skill
  (autonomous 2.1.6, backend-data 1.1.1, cartographer 1.1.1, devops 1.2.3, e2e 1.1.2,
  performance 1.3.2, postgres 1.1.1, reverse-engineer 1.1.4, spec-to-system 1.2.1,
  ultimate-pro-max 2.2.4).
- **Caso permanente** em `selftest-ferramentas.py` (grupo `rejeicao`): espelha uma skill,
  injeta referência inexistente e exige exit ≠ 0 **com e sem `-O`**. Provado ao reverter uma
  skill ao `assert`: a suíte acusou "validador aprovou referência quebrada sob python -O".

### Corrigido — erros meus no processo desta versão
- O script de bump **não era idempotente** e rodou duas vezes: seis skills subiram dois
  PATCHes para um único defeito, com o mesmo parágrafo sob dois números. Detectado ao
  inspecionar a sequência de versões, não pela checagem automática.
- A primeira tentativa de detectar essa duplicação reportou **"nenhuma entrada duplicada"** —
  falso negativo: eu contava `` `assert` `` com crase simples num texto que usa crase dupla,
  então o padrão nunca casava. Falso negativo em ferramenta de verificação é o pior resultado
  possível, porque fabrica confiança. Reescrito comparando o corpo normalizado das entradas;
  aí sim apareceu a repetição, e sete foram colapsadas.
- As lacunas de número (ex.: 2.1.5 → 2.1.7 sem 2.1.6) foram reindexadas para o passo correto,
  ajustando VERSION, frontmatter e PROMPT-ATIVACAO juntos.

### Verificado sem defeito
Idempotência e concorrência: `build-manifest.py` produz bytes idênticos em execuções
sucessivas; `install-all.ps1` duas vezes seguidas resulta no mesmo estado; `quality-gate` e
`check-numbers` rodando em paralelo não corrompem `.gate-contagem`. Árvore suja: o passo de
CRLF do CI mantém a decisão no índice (`--cached`) e não acusa a cópia de trabalho; referência
quebrada não commitada é pega pelo gate pelo conteúdo, não pelo git.

## [1.5.1] — 2026-11-17

**Verificação por ataque.** Quatro rodadas seguintes à v1.5.0 mudaram o método: em vez de
exercitar as ferramentas, passar a atacá-las com entrada doente e perguntar "o que acontece
quando não há nada?". Cada pergunta rendeu um defeito real.

### Corrigido
- **`gate_candidatos.avaliar()` explodia com `AttributeError`** diante de
  `{"endpoints": {...}}` — dict onde se espera lista, formato que um coletor quebrado produz
  naturalmente. O JSON de sinais vem de fora, então entrada malformada é caso esperado. Agora
  cada forma doente vira linha em `nao_avaliaveis`. `GATE_VERSION` 1.0.0 → 1.2.0.
- **`check-numbers.py` morria com `.gate-contagem` contendo `[]`** (`AttributeError` em
  `.get`) e com `arsenal.json` `{}`, truncado ou sem `counts` (`KeyError`). A correção não foi
  envolver em try/except: o checker lia um artefato **gerado**, comparando dois artefatos entre
  si — se `build-manifest.py` atrasasse, README e manifesto dariam verde juntos sobre números
  velhos. Passou a medir o filesystem; contagens idênticas antes e depois, imunidade inclusa.
- **`check-copies.py` caía com `FileNotFoundError`** se `skills/` não existisse (clone
  interrompido, worktree novo). Verificador que explode é indistinguível de repo que falhou.
- **`check-links.py` era gate-fantasma**: imprimia "verificados: 0 / QUEBRADOS: 0" e saía 0.
  Caminho errado, pasta vazia ou checkout parcial aprovavam o repositório inteiro sem abrir um
  arquivo — e ele está no CI desde o início. Zero conferidos agora falha com a causa.
- **`check-licenses.py` aprovava árvore vazia** ("licenças consistentes", exit 0) porque cada
  laço usa `continue` em pasta ausente. Mesmo padrão da v1.5.0 por outra porta. Conta o que
  conferiu (17 componentes no repo) e reclama em zero.
- **`README.md` dizia "28 tools"** quando `tools/list` devolve 24 numa instalação mínima; as
  outras quatro são habilitadas por `DZ23_WORKSPACE_ROOTS`/`DZ23_SANDBOX_ENABLED`. Medido por
  sessão JSON-RPC real, não lido de doc.
- **`ROADMAP.md` documentava `run-evals.py --record <skill> <arquivo>`** gravando
  `evals-results/<skill>.json`. Nenhum dos dois existe — copiar da doc produzia exit 2.
  Tabela completa refeita e conferida comando por comando.
- **`audit-zips.py` chamava de divergente o que só diferia em fim de linha**: comparava SHA de
  bytes crus entre uma árvore que o git monta LF (`core.autocrlf=false`) e a instalação com
  CRLF. Num clone virgem acusava 2 arquivos idênticos. Texto conhecido é hasheado com CRLF
  colapsado; binários seguem byte a byte.
- **`check-audit-inputs.py` sem argumento** dava `TypeError` (`Path(None)`) antes da mensagem de
  uso, que existia três linhas abaixo mas nunca era alcançada.
- **Dividas 8 e 8b resolvidas**: skill instalada dependia do checkout para rodar as checagens
  comuns — movido o repo, ela pulava tudo e ainda saía com exit 0, apenas um WARN que ninguém
  lê (minha nota anterior no ROADMAP subestimava isso como "degradação visível").
  `skill_validator.py` e `_achar_arsenal.py` viraram conteúdo versionado de cada skill, com
  preferência pela cópia local; a duplicação resultante ganhou `check-copies.py`.

### Adicionado
- **`scripts/selftest-ferramentas.py`** — suíte versionada de ataque, no gate e no CI. Cinco
  grupos: triagem (nove formas doentes de JSON), claims (dezesseis textos hostis), descoberta
  de arsenal (env inválida, ponteiro mentiroso), guardas (quatro árvores incompletas) e
  **rejeição** (baseline válido precisa ser aceito e seis casos inválidos reprova­dos). Tem
  auto-verificação: injeta violação conhecida e exige detectá-la. Custo medido: 2,3 s.
- **`scripts/check-copies.py`** — SHA-256 das 20 cópias embutidas contra a fonte.
- **`--raiz <pasta>`** em `check-structure`, `check-licenses`, `check-copies` e `run-evals`.
  Existia uma armadilha concreta sem isto: apontar `cwd` para uma fixture faz o script escanear
  o repo real ao lado e devolver verde sem ler nada — foi exatamente como um ataque anterior a
  estes scripts reportou "casos inválidos aceitos" que nunca foram lidos. Em `run-evals` o
  reposicionamento inclui `SKILLS`/`RESULTADOS`/`PROMPTS`/`SCHEMA`, congelados no import.
- **`docs/defeitos-verificados-2026-11-17.md`** dentro do repo. A primeira versão desse
  relatório — base de toda a v1.5.0 — foi perdida num `git checkout -- .` porque era arquivo
  solto fora da árvore versionada.
- **`external/absorcao-2026-11-17.md`** indexado no README (estava órfão).

### Estado medido
`quality-gate.py`: **33/33** em 5,5 s (orçamento de 300 s por check). Escala verificada:
200 skills em 3,4 s; 5.000 casos de eval; 200.000 links em 35 s; caminho Windows de 204
caracteres. Clone virgem com `core.autocrlf=false` nasce com `git status` limpo e roda o gate
inteiro sem nada instalado.

## [1.5.0] — 2026-11-17

**Instrumentos absorvidos de pacotes externos + dois gates que mentiam consertados.**
Auditoria de 12 repositórios baixados (ECC, replica-skill, agent-skills/Vercel,
modern-web-guidance, open-code-review, agent-desktop, rea, shadcn/ui, pomerado,
suparagent, playwright-mcp, REA) e das skills instaladas nesta máquina. As técnicas foram
reimplementadas, não copiadas; a triagem por pacote está em `external/absorcao-2026-11-17.md`.

### Corrigido — verificadores que davam verde sem verificar
- **`run-evals.py --verify-quotes` retornava exit 0 quando `AUDIT-STATUS.json` não
  existia.** Apagar o arquivo de estado desligava silenciosamente a checagem de citação
  fabricada — a camada 5 inteira. Agora ausência ou ilegitibilidade é falha. Prova:
  renomear o arquivo → antes `exit 0`, agora `exit 1`.
- **`check-eval-results.py` não cruzava NOT_TESTED com o ROADMAP**, embora o docstring
  prometesse. O código só testava se a string `"Status de evals"` existia; um registro
  fantasma dava `PROBLEMAS: 0`. Agora compara declarados × registrados e confere o
  "Total pendente" escrito no ROADMAP. Prova: mudar para 7 → `diz 7, mas há 99 sem registro`.
- **`build-manifest.py` usava `date.today()` no `generated_at`**, então `manifesto:check`
  falhava em qualquer dia diferente do último push sem nada ter mudado. O CI da main estava
  verde em 2026-11-14 porque rodou no dia certo; no mesmo commit, em 17/11, dava 16/17.
  Trocado por comparação de conteúdo canônico.
- **`bundles` era lista hardcoded** que punha o MCP principal dentro de "bundles" e omitia
  `mcp/pentagi-mcp` do inventário. `mcp/` e `bundle/` agora são enumerados do disco.
- **93 blobs commitados com CRLF** contra o próprio `.gitattributes` (`* text=auto eol=lf`),
  entrada anterior à regra. Todo clone em Windows nascia com `git status` sujo em 93
  arquivos, e quem trabalha no Windows para de confiar no diff — onde justamente se veria
  edição indevida. Renormalizados; o CI agora tem passo que impede regressão.
- **Skill sem `validate_skill.py` contava como OK** (`sem validate_skill.py (pulado)`), no
  gate e no CI. A skill que define o contrato de evidência — `dz23-autonomous-improvement-ultimate`
  — era justamente a não verificada. Ganhou validador próprio e a ausência passou a falhar.
- **Passo "Resumo" do CI saía 0 quando `gate.json` estava ausente**: imprimia "o gate não
  chegou a rodar" e aprovava. Agora falha, com escrita atômica e `set -euo pipefail`.
- **Ponte de checagem comum não funcionava na instalação**: `parents[3]` a partir de
  `~/.agents/skills` aponta para `~/.agents`, sem o módulo — a skill em produção era a menos
  verificada. Novo `_achar_arsenal.py` sobe a árvore, lê `~/.agents/skills/.dz23-arsenal`
  (gravado pelo install-all) ou respeita `DZ23_ARSENAL`.
- **Números da documentação divergiam do disco** (7 casos): README dizia "9 skills" com 10,
  badge `skills-9`, "1 MCP" com 2, "16 checks" com 19, "45/131" (131 não existe; são 144),
  e um bloco obsoleto afirmando "executados: 3" quando a tabela do próprio arquivo diz 45.
- **`dz23-performance-scalability-engine` alegava preservação falsa**: "o original está
  preservado em `_sources/user-spec.md`". Os arquivos existem na máquina de origem, mas
  `_sources/` está no `.gitignore` e `git log --all -- '*_sources*'` não retorna nenhum
  commit — quem clona recebe promessa vazia. SKILL.md corrigido; CHANGELOG ganhou entrada
  de correção em vez de reescrita da linha antiga.
- **Vocabulário de estados rivais**: `NOT_RUN` em 4 arquivos da autonomous contra
  `NOT_TESTED` nas outras nove, aceitos ambos pelo regex do runner. Unificado.
- **`PROMPT-ATIVACAO.txt` congelado em v1.0/v1.0.0** em 7 skills cujas VERSION tinham
  avançado (1.1.0, 1.2.2, 1.3.0). Quem colasse o prompt usaria texto velho.
- **`references/legacy-v1.md` carregava frontmatter de skill descontinuada**
  (`name: dz23-premium-ui-ultimate`) — uma segunda skill se passando por referência,
  carregável por agente. Virou cabeçalho explícito de arquivo histórico.

### Adicionado — técnicas absorvidas
- **`scripts/gate_candidatos.py`**: triagem determinística *antes* de investigar. Função pura,
  threshold como expressão, `GATE_VERSION` rastreável, três cestos (lançado / contido com
  motivo / não-avaliável). Ausência de sinal nunca vira zero. Auto-teste cobre positivo,
  negativo, vazio, determinismo e guarda de amostra pobre. De `vercel-optimize/lib/gates/*.mjs`.
- **`scripts/verifica_claims.py`**: evidência conferida por comando, com
  `passRate = verificados/(verificados+falhos)`; não-verificável e sem-suporte ficam fora do
  denominador. Ancorado na skill auditada, não em "existe em qualquer pasta". De
  `vercel-optimize/references/verification.md`.
- **`scripts/skill_validator.py`**: checagens comuns reunificadas (frontmatter, VERSION ×
  frontmatter, PROMPT-ATIVACAO defasada, referências quebradas, evals coerentes, nome morto
  em frontmatter vivo). Havia dez cópias divergentes; a maior tinha 15 linhas. Provado por
  injeção: citar `references/NAO-EXISTE-teste.md` dava PASS.
- **`scripts/check-numbers.py`**: confere números da documentação contra o disco e denuncia
  **regra órfã** (padrão que não casa em lugar nenhum = autoengano; foi o que aconteceu com a
  regra de contagem de checks). Lê a contagem real do artefato `.gate-contagem`; a primeira
  tentativa, parsear o fonte do gate por regex, contou 24 contra 31 reais.
- **`scripts/check-licenses.py`**: licença obrigatória por componente e por referência
  externa. Achou `bundle/dz23-dsh-agency` sem LICENSE algum (criado, herdando MIT do repo) e
  8 externas com "verificar no repositório". Resolvidas com prova: 4 lidas do arquivo LICENSE
  do projeto baixado, 3 via API do GitHub. `anthropic-skills` e `vercel-react-best-practices`
  seguem sem licença — a API devolve `license: null` — e agora dizem isso explicitamente,
  porque sem licença explícita não se redistribui conteúdo.
- **`scripts/_tracks.py`**: mapa skill ↔ pasta derivado do disco. Eram três cópias iguais,
  nenhuma com `dz23-postgres-prod-preflight`: `record-eval` criava a pasta e
  `check-eval-results` a rejeitava como "não mapeada". A única skill com 0 de 13 evals
  executados era justamente a que o instrumento não conseguia registrar.
- **CI**: instala `jsonschema` (sem ele, "Evals contra o schema" caía em fallback parcial com
  selo de completa), publica o `--report` no resumo do run, e falha ante CRLF fora da norma.

### Bumps de versão nas skills (regra dura do CONTRIBUTING: conteúdo mudou, versão muda)
- `dz23-autonomous-improvement-ultimate` 2.1.4 → **2.1.5** — vocabulário `NOT_RUN` →
  `NOT_TESTED` unificado com as outras nove; ganhou validador próprio.
- `dz23-performance-scalability-engine` 1.3.0 → **1.3.1** — retirada a alegação de que a spec
  original estava preservada em `_sources/user-spec.md`, caminho que o clone não tem.
- `dz23-ultimate-pro-max` 2.2.2 → **2.2.3** — `references/legacy-v1.md` deixou de declarar
  frontmatter da skill descontinuada; `PROMPT-ATIVACAO.txt` ganhou cabeçalho de versão, que
  nunca teve (as irmãs têm).

Conferência cruzada aplicada às dez skills: VERSION × frontmatter × seção do CHANGELOG ×
cabeçalho do PROMPT-ATIVACAO. Foi o validador novo da autonomous que encontrou o `NOT_RUN`,
e o check comum que encontrou o PROMPT-ATIVACAO defasado depois do próprio bump — os dois
defeitos apareceram por ferramenta, não por leitura.
### Estado medido
`quality-gate.py`: **31/31** (eram 16/17 no mesmo commit base). `audit-zips.py`: 10/10 em dia
com esta máquina. `verifica_claims`: passRate **1.00** nos dez SKILL.md.

## [1.4.9] — 2026-11-09

**Camada 4** — 3 skills do arsenal usadas no próprio repo, com o CI como juiz.

### Adicionado
- **--verify-quotes** no 
un-evals.py: verifica se as citações dos laudos marcados VALIDO existem nas
  respostas. xit 1 quando há citação fabricada.
- **quality-gate.py: 16 checks** (era 15) — vals:citacoes roda no CI.
- **docs/camada-4-2026-11-09.md** — spec (REQ-001..008), contrato de exit code, 5 iterações com o defeito
  de cada uma, o que quebrou, o que funcionou, lições e o que **não** foi testado.

### O que a Camada 4 produziu de diferente
A ferramenta acusou o laudo **válido** cinco vezes durante a construção: cabeçalho ## vs ###, citação do
input antigo confundida com citação da resposta, anotação do auditor (...) contada como citação, linha
quebrada em duas, e guarda de tamanho que matava citação curta. Cada uma virou regra no extrator
(RESUMO, isolar seção de resposta, juntar linha quebrada) e caso no --selftest.

O controle negativo (--laudo audit-2026-11-09.md → exit 1, 54 de 68 fabricadas) é o que prova que a
ferramenta discrimina; sem ele, "passou nos válidos" não significaria nada.

### Estado
- Gate **16/16** · CI verde · execução de evals inalterada (45/131)
- Camada 4: **PASS** — tarefa com consequência entregue e provada pelo CI, não por declaração

## [1.4.8] — 2026-11-09

Re-auditorias recebidas: camada 3 fecha em literais. E o laudo original cai como evidência.

### Recebido
- udit-results/reaudit-5-2026-11-09.md — os 5 casos que eu havia marcado NOT_AUDITED, re-auditados com o
  input literal: **5/5 PASS**.
- udit-results/reaudit-11-2026-11-09.md — os outros 11: **11/11 PASS**.

### Achado maior que o meu
A re-auditoria apontou **citação fabricada** no laudo original. Verifiquei com ferramenta própria
(scripts/check-audit-quotes.py, novo): **55 de 68 citações não aparecem na resposta**, em **16 de 16**
evals. O laudo original passa a INVALIDO_COMO_EVIDENCIA.

O veredito 16/16 PASS sobreviveu — mas por mérito das respostas, que citam o input literal dentro delas
mesmas. Os PASS anteriores estavam certos **por acaso**, não por análise válida.

### Corrigido no meu código (Fix 2)
check-audit-inputs.py classificava o caso 02 (SL-02 → SL-03) como LITERAL porque os tokens do original
estavam todos presentes. Regra nova, mais honesta:
- LITERAL exige cópia fiel (texto normalizado igual) ou cobertura ≥95% **sem nenhum termo inventado**;
- CONTRADIÇÃO TÉCNICA quando o laudo troca o termo decisivo (DECIMAL no lugar de FLOAT);
- COBERTURA BAIXA (<15% dos termos) quando o cenário provavelmente é outro;
- PARÁFRASE no resto — **sempre revisar à mão**, porque o script não lê semântica (perder a ordem de um
  passo, como no caso 19, sai como paráfrase).

--selftest com 6 casos, incluindo o 02: **6/6 ok**. Aplicado aos 16, só o **caso 02** mudou de classe
(LITERAL → PARÁFRASE); os outros 15 mantiveram.

### Estado
- Camada 3: **16/16 PASS com input literal** (2 re-auditorias válidas).
- Laudo original: INVALIDO_COMO_EVIDENCIA (input parafraseado em 13/16; citação fabricada em 16/16).
- Execução: **45/131 (34,4%)** — inalterada.

## [1.4.7] — 2026-11-09

Os 5 evals cujo veredito não se aplica passam a estado explícito NOT_AUDITED.

### Adicionado
- **vals-results/_audit-notes/AUDIT-STATUS.json** — estado de auditoria dos 16: **4 LITERAL · 7 PARÁFRASE ·
  5 NOT_AUDITED**, com o motivo de cada um.
- **
un-evals.py --audit** — comando que mostra o estado da camada 3 por eval.
- Seção **Camada 5 — conferência do método** em docs/eval-methodology.md: a camada que confere a auditoria
  também erra (a primeira conferência reportou 2 de 16 porque olhou só o óbvio).
- Os 5 registros ganharam o bloco ## Auditoria externa — NOT_AUDITED com o motivo e o link para o prompt de
  re-auditoria.

### Números
- Camada 3: **11/16 com veredito aproveitável** · **5 NOT_AUDITED** (05, 12, 13, 16, 19).
- Executados: **45/131 (34,4%)**, inalterado — este release corrige *status*, não cobertura.

### Pendente (não é dívida de código)
- Re-auditar os 5 em sessão limpa com udit-package/REAUDIT-PROMPT.md. Se confirmarem PASS, a camada 3 passa
  a 16/16 em literais; se divergirem, o veredito do auditor vale e o registro é corrigido.

## [1.4.6] — 2026-11-09

Conferência pós-auditoria: o laudo da camada 3 julgou cenários parafraseados.

### Achado
python scripts/check-audit-inputs.py audit-results/audit-2026-11-09.md compara o input citado no laudo
com o do pacote. Resultado: **4 literais, 7 paráfrases com armadilha preservada, 5 com cenário alterado**.

Nos 5 alterados, a paráfrase removeu justamente o que o eval testa:
loat-for-money (leu DECIMAL, que é a resposta certa, no lugar de FLOAT), checkpoint-ausente
(sem o "continue de onde estava"), locked-secret (sem a instrução "use mock permanente"),
inference-as-fact (sem a afirmação falsa) e migration-before-code (perdeu a **ordem** do DROP).

**Correção de uma afirmação anterior:** eu havia dito "2 de 16 divergem". Errado — o texto difere em 16 de
16, e em 5 a diferença invalida o veredito. A primeira contagem olhou só os dois casos mais gritantes.

### Adicionado
- scripts/check-audit-inputs.py — triagem automática de fidelidade de input em laudo de auditoria.
- udit-package/rubrica-em-branco.md — regra obrigatória: copiar o input literalmente; auditor que
  parafraseia invalida a auditoria.
- udit-package/REAUDIT-PROMPT.md — prompt pronto para re-auditar os 5, com o que cada paráfrase mudou.

### Estado da camada 3
- **4/16** auditados em literais · **7/16** em paráfrase com armadilha preservada · **5/16** a re-auditar.
- O "16/16 PASS" do laudo **não** pode ser declarado como auditoria em literais.

## [1.4.5] — 2026-11-09

Rodada de fixes a partir da auditoria externa (camada 3).

### Contexto
Laudo: [udit-results/audit-2026-11-09.md](audit-results/audit-2026-11-09.md) — **16 PASS / 0 PARTIAL / 0 FAIL**,
com **5 observações de regra vizinha** abaixo do limiar de PARTIAL. Três foram tratadas como gaps reais.

### Corrigido (3 skills, patch)
- **dz23-autonomous-improvement-ultimate 2.1.3 → 2.1.4** (OB-03): nova etapa **9. Retomada após
  desbloqueio** — confirmar o que destravou, retomar do checkpoint, rodar o gate que estava bloqueado,
  registrar o evento. BLOCKED só sai do estado pelo gate executado.
- **dz23-devops-cloud-deployer 1.2.1 → 1.2.2** (OB-04): seção **Backup e DR com RTO/RPO numéricos** —
  alvo obrigatório, "medir" é etapa e não resposta, default explícito quando o dono não declarou.
- **dz23-e2e-browser-verifier 1.1.0 → 1.1.1** (OB-05): seção **Snippet executável quando o cenário é
  teste** — Playwright/Cypress com seletor + ação + asserção; prosa só em planejamento declarado.

### Adicionado
- **3 evals novos** (denominador 128 → **131**): credential-unblock-without-resume,
  
to-rpo-without-numeric-target, 	est-in-prose-not-code. Agora as três regras são testadas
  explicitamente em vez de depender de re-leitura.
- [vals-results/_audit-notes/AUDIT-2026-11-09-OBSERVATIONS.md](evals-results/_audit-notes/AUDIT-2026-11-09-OBSERVATIONS.md)
  — as 5 observações classificadas, os 3 fixes e o defer de OB-01/OB-02 para v1.5.0.

### Achado de método (registrado, não corrigido por ser do processo de auditoria)
Dois input citados no laudo **não batem literalmente** com udit-package/evals/*.json: o auditor
parafraseou o cenário e, no eval 01, acrescentou um número (< 100 ms) que não existe no original. O
veredito vale para o que ele leu; a rubrica da próxima rodada passa a exigir cópia literal.

### Números
- Declarados: 128 → **131** · Executados: **45** (sem rodada 4) · Cobertura: 35,2% → **34,4%**
- Críticos executados: **32/45 (71%)** · Regras de skill corrigidas: **3**

## [1.4.4] — 2026-11-09

Rodada 3: os críticos executáveis, com re-leitura adversarial como método novo.

### Adicionado
- **20 evals críticos executados** (categoria A, reasoning-only): autonomous 4, backend 5, cartographer 5,
  devops 4, e2e 1, ultimate-pro-max 1.
- **`docs/eval-methodology.md`** — o que um eval prova, o que não prova, as 4 camadas de verificação e o
  estado de cada uma.
- **`evals-results/_audit-notes/BLOCKED-TRACK-B.md`** — os 40 evals que exigem infra, cada um com a dependência nomeada.
- **11 registros** adicionados à amostra de auditoria externa (total **16**), `method: auto-then-reaudit`.

### Método novo: re-leitura adversarial
A resposta é relida como se fosse outro leitor, procurando violação de regra **vizinha** — não só do
`expected`. Produziu 5 defeitos menores que a autoavaliação simples deixaria passar (números ilustrativos
apresentados como dados, teto de paginação fixado sem justificativa, checkpoint assumido sem varrer o disco).

### Números reais (e correção do plano)
- Cobertura: **25/128 (19,5%) → 45/128 (35,2%)**
- Track A: **45/78 (58%)**
- **Críticos: 32/45 (71%)** — não 45/45

**Por que não 100% dos críticos:** dos 33 restantes, **13 exigem infraestrutura** (Postgres, Playwright com
app rodando, Ghidra, hardware). Executá-los sem a dependência daria `PASS` falso. O teto real neste ambiente
é 32/45.

### Vereditos
43 PASS · 2 PARTIAL · **0 FAIL**. Nenhuma skill teve 3+ FAIL, então nenhuma regra foi corrigida.

## [1.4.3] — 2026-11-09

Auditoria da amostra da Rodada 2 (5 registros).

### Resultado (mesmo autor — não independente)
- [`evals-results/AUDIT-RESULT.md`](evals-results/AUDIT-RESULT.md): releitura adversarial dos 5 selecionados.
  **4 PASS · 1 PARTIAL**. `float-for-money` rebaixado de PASS para PARTIAL: o `expected` exige explicar o
  **erro de arredondamento fiscal** e a resposta apenas definiu a regra de arredondamento.
- **Achado de infra corrigido:** o template do `record-eval.py` não gravava `fails_if`, então o auditor não
  conseguia julgar a segunda dimensão só pelo registro. Template corrigido e **backfill nos 25 registros**.
- 3 defeitos menores documentados (decisão padrão sem prazo, inferência não marcada, afirmação sem prova) e
  1 lapso de aplicação de regra que **já existe** na skill (estimativa por intervalo).

## [1.4.2] — 2026-11-09

Rodada 2: classificação dos 118 evals restantes e lote de 15 reasoning-only.

### Adicionado
- **`evals-results/_audit-notes/CLASSIFICATION.md`** — os 118 evals classificados por criticidade:
  **A = 45** (segurança, integridade de dados, honestidade) · **B = 62** (fluxo, anti-pattern) ·
  **C = 11** (borda/cosmético). Separados também por track: **78 reasoning-only** × **40 que exigem infra**
  (Docker/Postgres/Ghidra/browser/hardware).
- **15 evals executados**, 10 de `spec-to-system-engine` e 5 de `backend-data-architect`, todos categoria A
  ou B e todos reasoning-only.
- **`evals-results/_audit-notes/AUDIT-SAMPLE.md`** — **5 dos 15** separados para auditoria externa, escolhidos entre os que
  exigem julgamento (conflito de requisitos, dependência circular, risco no fim do plano, contrato publicado,
  exatidão monetária).

### Números
- Cobertura: **10/128 (7,8%) → 25/128 (19,5%)**.
- Vereditos acumulados: **24 PASS · 1 PARTIAL · 0 FAIL · 0 BLOCKED**.
- Track A (reasoning): 25 de 78 executados (**32%**).

### Sem correção estrutural nesta rodada
Nenhum `expected` autocontraditório, `input` ambíguo ou `fails_if` brando apareceu nos 15 executados — e
`FAIL` foi zero, então nada a corrigir em regra. **Isso é resultado da autoavaliação, não homologação:**
os 15 registros têm `method: auto` e 5 estão marcados para revisão independente. Se o auditor externo
divergir, o veredito dele prevalece e a regra é corrigida na rodada seguinte.

## [1.4.1] — 2026-11-09

Rodada 1: fechar honestidade, distribuição e infraestrutura de evals.

### Corrigido
- **Drift do "CI nunca rodou"** (2 lugares): o workflow executou em **2026-11-09, verde** (2 runs). Corrigido
  em `ROADMAP.md` (dívida #3, agora resolvida) e no `CHANGELOG` da v1.3.0. A dívida #2
  (`install-all.sh` em Linux) **permanece** — é outro assunto e continua verdadeira.
- **0 assets nas releases**: **18 zips** anexados à `v1.4.0` (9 skills + 1 MCP + 1 bundle + 7 externos).
  Download testado: 18 baixados, SHA-256 igual ao original.

### Adicionado
- **`evals-results/`** — histórico versionado de execução, um arquivo por execução, com método, veredito,
  cenário, resposta, esperado, trecho literal e notas.
- **`evals.schema.json`** — JSON Schema 2020-12. Aceita `skill`/`version`/`note` como metadados opcionais de
  topo (os 9 arquivos já os tinham; o schema original os rejeitaria).
- **`scripts/run-evals.py`** reescrito: `--list`, `--check`, `--schema`, `--prompts`, `--record`, `--report`,
  `--skill`, `--batch`. Gera prompts prontos em `evals-prompts/` para execução manual.
- **`scripts/record-eval.py`** — registro com regras de honestidade embutidas: `PASS` exige resposta **e**
  trecho literal; `BLOCKED` exige a dependência; `NOT_RECOVERED` é aceito sem artefato (e não reconstruído).
- **`scripts/check-eval-results.py`** — valida os registros: seções obrigatórias, veredito reconhecido, eval-id
  existente na skill, PASS com trecho, ROADMAP com seção "Status de evals".
- **Títulos nos evals** de `autonomous` (12) e `ultimate-pro-max` (13) — 25 casos passaram a cumprir o schema.
- **10 evals registrados** formalmente: 7 execuções anteriores (devops ×3 com Docker real, autonomous ×1,
  performance ×3) + **3 pilotos novos** na `reverse-engineer-anything`.
- `quality-gate.py`: **15 checks** (era 13) — agora inclui schema e registros de evals.

### Cobertura de evals
- Antes: **0/128** registrados no repositório (4 executados fora do repo).
- Depois: **10/128 (7,8%)** — 9 PASS, 1 PARTIAL, 0 FAIL, 0 BLOCKED.
- Próximo passo: Rodada 2 (lote de 15–20, começando por `spec-to-system-engine` e `backend-data-architect`).

## [1.4.0] — 2026-11-09

Auditoria de **todos os evals** do arsenal e criação do harness que faltava.

### Adicionado
- **`scripts/run-evals.py`** — harness de evals com quatro comandos:
  - `--list` lista cenários por skill;
  - `--check` auditoria determinística (schema, id duplicado, `expected` × `fails_if`, **cobertura** — a regra
    do `expected` existe no `SKILL.md`/`references`? — e eval possivelmente impossível);
  - `--record <skill> <arquivo>` grava veredito de execução real em `evals-results/`;
  - `--report` mostra quantos cenários já têm resultado.
- `evals-audit.json` — relatório da auditoria, gerado pelo `--check`.
- Check de evals no `quality-gate.py` (**13 checks**) e step próprio no CI.

### Corrigido (defeitos reais encontrados pela auditoria)
- **`dz23-autonomous-improvement-ultimate` 2.1.1 → 2.1.2**:
  - `tailwind3`, `tailwind4` e `streaming-chat` testavam **regra de UI** numa skill de **orquestração**. O
    `--check` acusou cobertura de 1/5 termos — a regra simplesmente não existia na skill. Foram para
    `dz23-ultimate-pro-max`, que tem a reference de stack.
  - No lugar entraram três cenários de orquestração: `checkpoint-ausente`, `escopo-inflado`,
    `delegacao-sem-skill`.
  - Nova regra no `SKILL.md`: **falha repetida exige mudança de estratégia diagnóstica** (três tentativas com
    a mesma hipótese produzem a mesma falha; na quarta, trocar o instrumento e preservar as evidências).
- **`dz23-ultimate-pro-max` 2.2.0 → 2.2.1**: a skill tinha **zero evals** — justamente a de output mais
  subjetivo do arsenal. Agora tem **13 cenários** (tokens semânticos, Tailwind v3 × v4 com `@theme`, estados
  interativos, focus-visible, `prefers-reduced-motion`, CLS de mídia, adoção de shadcn/ui, badge sem quebra,
  contraste, estados vazio/erro, prova visual, streaming de chat).
- `references/stack-implementation.md`: explicitado `@theme` do Tailwind v4 (CSS como fonte dos tokens) e
  `aspect-ratio`/`width`/`height` contra CLS.

### Números
- **128 cenários** auditados · **0 erros** de coerência · **3 avisos** de cobertura baixa.
- **128 cenários ainda sem resultado de execução** — `python scripts/run-evals.py --report` retorna exit `1`.
  Coerência do eval ≠ comportamento provado da skill.

## [1.3.0] — 2026-11-09

Transformação de "coleção de zips" em **arsenal verificável**: gate único, CI, inventário gerado e política
de contribuição/segurança.

### Adicionado
- **`scripts/quality-gate.py`** — roda tudo (validador de cada skill, estrutura, links, manifesto) e dá um
  veredito com exit code. Um comando, um veredito.
- **`scripts/check-structure.py`** — arquivos obrigatórios por skill, frontmatter (`name`/`version`/
  `description`/`user-invocable`), `name` == pasta, `VERSION` == frontmatter, `CHANGELOG` com a versão atual,
  README com seção Arsenal, schema dos evals, detecção de skill-esqueleto.
- **`scripts/check-links.py`** — valida todo link relativo `.md` do repositório (133 links).
- **`scripts/build-manifest.py`** + **`arsenal.json`** + **`INDEX.md`** — inventário legível por máquina e
  índice gerado dos próprios arquivos; `--check` falha se estiver desatualizado.
- **CI** em [`.github/workflows/quality.yml`](.github/workflows/quality.yml) — roda o gate em push/PR e
  publica `gate.json` como artefato.
- **`SECURITY.md`** — canal privado, o que conta como vulnerabilidade neste projeto, prazo de melhor esforço.
- **`CODE_OF_CONDUCT.md`** — regra de convivência curta, centrada em evidência.
- **`ROADMAP.md`** — estado honesto: o que foi verificado, as 7 dívidas conhecidas e os não-objetivos.
- **`.github/ISSUE_TEMPLATE/{bug,feature}.md`** e **`pull_request_template.md`** — formulários que exigem
  evidência literal.
- **`.gitattributes`** — normaliza LF no repositório (CRLF só em `.ps1`/`.cmd`), evitando churn de fim de linha.

### Corrigido
- `dz23-autonomous-improvement-ultimate` **2.1.0 → 2.1.1**: `evals/evals.json` estava no schema antigo
  (`prompt` + `expectations`), enquanto as outras 8 skills usam `input`/`expected`/`fails_if`. Isso gerava
  **36 problemas** no `check-structure` e quebrava qualquer harness que lesse só aquela skill. Os 12 casos
  foram migrados preservando conteúdo, e cada um ganhou `fails_if` (antes inexistente).
- README: seção de qualidade, tabela de ferramentas, documentos do repositório e aviso de evals reescrito
  com o número real (3 de ~137).

### Estado de verificação
- `python scripts/quality-gate.py` → **12/12 checks passaram** (local, Windows).
- `CI no GitHub`: workflow executou em **2026-11-09, verde** (2 runs — `gh run list --limit 5`).
  *(Esta linha dizia "nunca executou"; corrigida na v1.4.1 — o run aconteceu no push da própria v1.3.0.)*

## [1.2.0] — 2026-11-09

### Adicionado
- **`external/ui-ux-pro-max.md`** — skill de design intelligence da nextlevelbuilder (MIT, 192 regras de
  raciocínio, 80 estilos de UI). Preenche o gap de **direção visual por segmento** antes do código.
- **`skills/dz23-ultimate-pro-max/references/stack-implementation.md`** (v2.1.0 → **2.2.0**) — tokens em 3
  camadas → Tailwind, adoção de shadcn/ui, estados obrigatórios por componente, especificidades
  React/Next/Vue/Nuxt/RN/Flutter, 8 bugs visuais recorrentes e checklist pré-e2e.
- **`skills/dz23-backend-data-architect/references/threat-modeling-and-appsec.md`** (v1.0.1 → **1.1.0**) —
  threat model em 6 passos, STRIDE com controle e teste por ameaça, OWASP Top 10 → controle verificável,
  ASVS L2, segredos/dependências/upload, hardening e gates de AppSec que bloqueiam merge.
- `VERSION` da `dz23-ultimate-pro-max` — existia só no frontmatter, o que quebrava empacotamento.

### Corrigido (diagnóstico do usuário, com ressalvas)
- O diagnóstico dizia que **faltava skill de frontend/UI**. Não faltava: `dz23-ultimate-pro-max` já
  existia (8 references, gates de acessibilidade e QA visual). Faltava **instanciação por stack** —
  resolvida com `stack-implementation.md`.
- O diagnóstico dizia que **filas/webhooks não estavam cobertos**. Estavam, em
  `references/service-architecture.md` (idempotency key, outbox, DLQ, retry com backoff+jitter, dedup de
  webhook, `SKIP LOCKED`). Nada a criar; só registro aqui para não duplicar.
- Gap **real** identificado: **AppSec ofensivo** (threat modeling/OWASP/ASVS) — fechado nesta versão.
- `external/superpowers.md` atualizado: licença MIT verificada, suporte multi-harness documentado
  (plugins `.codex-plugin`, `.cursor-plugin`, `.opencode`, `.pi`…), diagrama de pipeline.

### Estado de verificação
- `validate_skill.py` PASS nas duas skills alteradas · `skills-check.py` 0 erros · 9/9 skills `EM_DIA`
  contra o pacote publicado (`audit-zips.py`).
- Evals: continuam `NOT_TESTED` — nenhum dos ~125 cenários foi executado.

## [1.1.0] — 2026-11-08

### Adicionado
- **`prompts/`** — pasta para os prompts de origem das skills:
  - `prompts/performance-4-camadas.md` — prompt original em 4 camadas / 20 itens que deu origem à
    `dz23-performance-scalability-engine`, copiado **verbatim** (inclusive o typo "Processamento
    Assalariado", que a skill interpreta como assíncrono)
  - `prompts/README.md` — índice, comparação prompt × skill e regra de contribuição

## [1.0.0] — 2026-11-08

Primeira release pública.

### Adicionado
- **9 skills DZ23** em `skills/`:
  - `dz23-autonomous-improvement-ultimate` 2.1 — loop autônomo de correção
  - `dz23-backend-data-architect` 1.0.1 — backend, banco, contratos, migrações
  - `dz23-codebase-cartographer` 1.1.0 — mapeamento de codebase
  - `dz23-devops-cloud-deployer` 1.2.1 — DevSecOps, containers, CI/CD, IaC
  - `dz23-e2e-browser-verifier` 1.1.0 — E2E com Playwright + a11y
  - `dz23-performance-scalability-engine` 1.3.0 — otimização em 4 camadas
  - `dz23-reverse-engineer-anything` 1.1.1 — RE de binários e firmware
  - `dz23-spec-to-system-engine` 1.2.0 — especificação executável
  - `dz23-ultimate-pro-max` 2.1 — frontend, UI/UX, design system
- **1 MCP** em `mcp/dz23-subagents-universal-mcp/` (v4.4.1, 28 tools)
- **1 bundle** em `bundle/dz23-dsh-agency/` (v1.0.0, 88 agentes)
- **8 referências externas** em `external/` (Superpowers, REA, Cloudflare, Anthropic, Vercel,
  Supabase, Playwright MCP, Terraform AWS VPC)
- **Guia de CLIs** em `cli/` — inventário real da máquina, faltantes por prioridade, instalação por SO
- **Documentação** em `docs/` — getting started, overview, mapa de integração, instalação, FAQ
- **Scripts** em `scripts/` — `install-all.ps1`, `install-all.sh`, `audit-zips.py`, `verify-cli.ps1`

### Estado de verificação (honesto)
- **Integridade dos pacotes**: ✅ verificada — cada skill em `skills/` foi extraída do zip publicado e
  comparada por hash contra a skill instalada (0 divergências no momento da montagem).
- **Exemplos dos READMEs**: ⚠️ comandos verificados quanto a existência/sintaxe, **não** executados em
  todos os ambientes (Windows testado; Linux/Mac não).
- **Evals das skills**: ❌ **`NOT_TESTED`** — dos ~125 cenários declarados entre as 9 skills, apenas 3
  foram executados em harness real até esta release. Ver o `CHANGELOG.md` de cada skill.
- **Scripts das skills**: parcialmente testados — os que têm `selftest` (ex.: `re_toolkit.py`, 15/15)
  rodaram; o restante é `NOT_TESTED`.

### Limitações conhecidas
- As skills foram escritas e validadas primariamente em **Windows + PowerShell**; os caminhos Linux/Mac
  dos instaladores não foram exercitados.
- O bundle `dz23-dsh-agency` gera `agents/` via `build.py`, que depende de Python 3.10+.
- O MCP requer `npm install` (150 arquivos, dependências declaradas em `package.json`).
