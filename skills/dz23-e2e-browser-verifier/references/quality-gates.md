# Quality gates — evidência, não promessa

| Gate | PASS quando | Evidência mínima |
|---|---|---|
| Fluxo crítico coberto | Dinheiro, acesso e isolamento têm E2E | lista de fluxos + arquivos de teste |
| Seletor estável | Nenhum posicional/classe de estilo | revisão do diff |
| Sincronização | Zero `sleep`/`waitForTimeout` como espera | grep no diff |
| Isolamento de dado | Cada teste cria e limpa o seu | seed/teardown + execução paralela |
| Autorização | Usuário sem papel não acessa; tenant cruzado bloqueado | teste específico |
| Browser real | Executa em navegador, não jsdom | log do runner |
| Estabilidade | 10 execuções sem flake no fluxo novo | saída das 10 execuções |
| Evidência | Trace/screenshot/console capturados | artifact anexado |
| CI | Suíte roda em pipeline com artifact | link do run |
| Acessibilidade do fluxo | Teclado/foco no caminho crítico | teste de teclado |
| Manutenção | `skip`/`fixme` com issue e prazo | grep + issue aberta |

**Estados:** `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`, `BLOCKED_BY_EXTERNAL_DEPENDENCY`. Teste que não rodou não é `PASS`.

## Severidade — o que reprova a entrega

**BLOCKER (não entrega, corrige antes):**
- Teste que passa sem provar nada: asserção vazia, `expect(true)`, mock do próprio alvo (backend/serviço testado).
- `sleep`/`waitForTimeout` como sincronização principal.
- Seletor posicional (`nth-child`, XPath estrutural) ou dependente de classe de estilo.
- Teste destrutivo contra produção sem autorização explícita.
- Segredo/credencial real no repositório ou em artifact público.
- Suíte "verde" com teste `skip`/`fixme` sem issue (cobertura fantasma).
- Teste que depende de ordem e passa só na suíte completa.
- Autorização não testada em fluxo autenticado (usuário sem papel acessando).

**MAJOR (entrega só com ressalva registrada):**
- Flake conhecido sem quarentena/issue.
- Ausência de trace em CI (impossível diagnosticar).
- Dado compartilhado entre testes sem isolamento.
- Retry global sem política ou mascarando falha.
- Viewport mobile ausente no fluxo crítico.
- Nenhum teste de teclado/foco no caminho de dinheiro/acesso.
- Suíte sem gate de merge (roda mas não bloqueia).
- Timeout aumentado como "correção".

**MINOR (refinamento, registra e segue):**
- Nome de teste técnico em vez de comportamento.
- Page Object com asserção escondida.
- Ausência de screenshot full-page em falha de layout.
- Relatório sem resumo por fluxo.

## Matriz de teste por fluxo
| Dimensão | Casos |
|---|---|
| Caminho feliz | usuário completa o fluxo e vê o resultado |
| Erro de validação | campo inválido → mensagem no campo, sem perder o preenchido |
| Erro de servidor | API responde 500 → UI mostra erro tratado, não tela branca |
| Autorização | sem sessão → redirect; sem papel → 403/oculto; tenant B em URL de A → 404 |
| Estado persistido | após reload, o dado continua correto |
| Borda de rede | requisição lenta/timeout → skeleton/erro, sem travar |
| Idempotência | duplo clique/retry não cria duplicado |
| Mobile | mesmo fluxo em viewport 390×844 |
| Teclado | Tab/Enter/Esc completam o fluxo; foco visível |

## Checklist final
- [ ] Fluxo crítico mapeado com critério de aceite observável.
- [ ] Seletor por papel/label/testid; nenhum posicional.
- [ ] Zero sleep; espera por estado.
- [ ] Dado único por run, seed e teardown.
- [ ] Sessão preparada por API/storageState; segredo via env.
- [ ] Autorização e tenant cruzado testados.
- [ ] 10 execuções sem flake.
- [ ] Trace/screenshot/console disponíveis na falha.
- [ ] Suíte no CI com artifact e gate.
- [ ] `skip`/`fixme` auditados.
- [ ] Lacunas e o que não foi testado declarados.
