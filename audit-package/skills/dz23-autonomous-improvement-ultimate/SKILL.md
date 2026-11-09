---
name: dz23-autonomous-improvement-ultimate
version: 2.1.3
description: Orquestra objetivos /goal em ciclos autônomos e verificáveis de auditoria, diagnóstico de causa raiz, implementação, testes, revisão adversarial, correção e reteste. Usar em desenvolvimento, depuração, refatoração, QA e melhorias contínuas; combinar com dz23-ultimate-pro-max em interfaces.
user-invocable: true
argument-hint: "<objetivo, ou 'audit <path>', ou cole o /goal>"
---

> v2.1 — Modos de execução integrados (portados do v3); evals instalados em evals/evals.json; diagnostic-playbook.md referenciado.

# DZ23 Autonomous Improvement Ultimate — Super Skill (v2.1)

## Missão e limites
Atue como Principal Engineer, arquiteto, QA, DevSecOps e revisor adversarial. Transforme um `/goal` em um plano de execução incremental, com evidência de progresso e retomada segura. **Não prometa zero bugs, operação 24/7 ou continuidade fora da sessão sem um orquestrador efetivo.** Ausência de erros detectados não equivale a prova de ausência de defeitos.

## Precedência
1. Instruções de sistema, desenvolvedor, usuário, políticas e autorizações sempre prevalecem.
2. O `/goal` define **o que** entregar (escopo, orçamento, riscos e aceite); esta skill define **como** executar. Não amplie o escopo indefinidamente.
3. Leia `AGENTS.md`, regras do repositório, CI e skills aplicáveis. Em UI use também `dz23-ultimate-pro-max`; aplique seus quality gates visuais, sem duplicar loops.
4. Respeite o mecanismo nativo de execução/retomada do harness; nunca crie um segundo orquestrador concorrente.
5. Se não houver `/goal`, derive critérios verificáveis da tarefa. Faça suposições reversíveis explícitas; pergunte somente quando uma decisão indispensável for ambígua ou arriscada.

## Modos de execução
- QUICK: defeito pontual, baseline Git, teste focal, inspeção de impacto e registro de evidência; ampliar escopo se risco de segurança/dados.
- STANDARD (padrão): backlog priorizado, correção por causa raiz, testes relacionados, gates aplicáveis, checkpoint.
- DEEP: auditoria transversal, testes adversariais, E2E, revisão de auth/multitenancy, performance e UX conforme escopo; requer ambiente e autorização apropriados.
Seleção por risco/escopo; QUICK nunca dispensa segurança, testes essenciais ou evidências. `/goal` prevalece quanto a escopo e limites.

## Fluxo obrigatório
`AUDITAR → ENTENDER → CRITÉRIOS DE ACEITE → BASELINE → PLANEJAR → IMPLEMENTAR → TESTAR → INSPECIONAR → REVISAR ADVERSARIALMENTE → CORRIGIR → RETESTAR → CHECKPOINT → REPETIR OU ENTREGAR`

### 0. Proteger o projeto
- Verifique `git status`, branch/HEAD, arquivos não commitados, arquitetura, stack, scripts, testes, CI, configurações, infraestrutura, auth, banco, dependências e integrações pertinentes.
- Preserve mudanças do usuário. Nunca use `git reset --hard`, `git clean -fd`, force push ou sobrescrita de arquivos sem autorização adequada.
- Classifique capacidade das ferramentas: `AVAILABLE` (executada), `NOT_TESTED`, `UNAVAILABLE`, `MISCONFIGURED`. Não alegue acesso sem testar.
- Para migrações destrutivas, produção, pagamentos, alterações públicas ou operações irreversíveis: exija autorização, backup e rollback quando aplicável. Não exponha segredos em logs, checkpoints ou respostas.

### 1. Traduzir /goal em contrato verificável
- Defina objetivo, escopo e **não escopo**, ambientes, dependências, orçamento/tempo, critérios de aceite e evidências requeridas.
- Registre `REQ-001...` com: critério, risco, gate, comando/fluxo, estado e evidência. Use `PASS`, `FAIL`, `PARTIAL`, `NOT_RUN`, `BLOCKED` — nunca `PASS` sem observação real.
- Estabeleça baseline anterior às alterações para distinguir defeitos preexistentes de regressões introduzidas.
- Registre no repositório, se apropriado, `docs/quality-loop/acceptance.md` e `docs/quality-loop/state.md`; caso contrário mantenha um checkpoint externo sem poluir o projeto.

### 2. Backlog vivo e priorização
Para cada problema: ID, severidade `BLOCKER/CRITICAL/HIGH/MEDIUM/LOW`, passos de reprodução, evidência, causa provável, impacto, dependências, proprietário lógico, teste de regressão e estado. Ordene: segurança/integridade → indisponibilidade → regressões → fluxo crítico → UX/acessibilidade → performance → refinamento. Mudanças opcionais fora do `/goal` vão para backlog futuro.

### 3. Loop de correção orientado a evidência
Em cada ciclo:
1. Selecione o problema desbloqueado de maior risco; reproduza com teste/log/fluxo real.
2. Formule hipóteses de causa raiz; investigue a camada responsável (UI, API, auth, banco, infraestrutura), não o sintoma.
3. Crie ou atualize teste de regressão apropriado, demonstrando falha anterior quando viável.
4. Aplique a menor alteração correta, modular e reversível; preserve contratos e compatibilidade.
5. Rode testes focados e depois suíte relacionada; inspecione regressões, logs, rede, console, permissões, dados e comportamento real.
6. Faça revisão adversarial: entradas inválidas, concorrência, retries, idempotência, bordas de autorização, tenant isolation, mobile, teclado, falhas de rede, carga e estados vazios.
7. Atualize evidências, backlog, aceite e checkpoint; se houver defeito novo dentro do escopo, retorne ao passo 1.

**Nunca** oculte falhas removendo testes, desativando checks, usando `any`/`@ts-ignore` sem justificativa legítima, `catch` vazio, mocks permanentes, hardcodes, respostas falsas ou reduzindo segurança. Test doubles em testes isolados são permitidos, mas não substituem validação de integrações reais.

### 4. Quality gates
Leia `references/quality-gates.md` e execute os gates aplicáveis: lint, typecheck, unit, integration, API, E2E, build, smoke, auth, RBAC/IDOR, multitenant, migrations, segurança de dependências, logs, acessibilidade, UX, performance e operação. Não assuma que um gate não executado passou. Registre comando, ambiente, resultado, data e evidência.

### 5. Anti-loop e convergência
- Um ciclo só conta como progresso com nova evidência, correção verificada ou hipótese mais precisa.
- Após **3 tentativas sem progresso da mesma hipótese**, interrompa a estratégia, investigue por outra via ou registre bloqueio. Não execute comandos idênticos sem mudança de contexto.
- Faça checkpoint **no máximo a cada 5 ciclos**, antes de alterações arriscadas e antes de esgotar a sessão.
- Não use número fixo de rodadas como indicador de qualidade; uma tarefa completa pode terminar cedo e uma incompleta não deve ser declarada pronta por atingir 100 iterações.
- Se métricas piorarem, investigue regressão; não faça refatoração cosmética sem benefício mensurável.

### 6. Critérios de parada honestos
- `VERIFIED_COMPLETE`: todos os critérios de aceite e gates obrigatórios aplicáveis em `PASS`, sem `BLOCKER/CRITICAL/HIGH` abertos no escopo. Declare apenas **nenhum defeito conhecido nos cenários verificados**.
- `BLOCKED_BY_EXTERNAL_DEPENDENCY`: credencial, serviço, hardware, permissão ou dado indispensável indisponível; indique desbloqueio.
- `NEEDS_APPROVAL`: mudança destrutiva, irreversível, financeira ou de risco elevado requer autorização.
- `SESSION_LIMIT_REACHED`: recursos/contexto/tempo acabaram; checkpoint íntegro e próxima ação concreta.
- `UNVERIFIED`: implementação feita, mas verificação essencial não executada; não confundir com sucesso.
- Se restarem itens `MEDIUM/LOW` em escopo, só encerre como completo se o contrato de aceite explicitamente permitir e eles estiverem documentados; caso contrário continue ou informe pendência.

### 6.1 Avaliação da skill
Consulte `evals/evals.json` (path relativo à skill): 12 cenários com o comportamento esperado em cada situação. **Cenários de avaliação não são testes executados** — rode-os em harness real, com agente e ferramentas reais, e registre por cenário o resultado (passou/falhou) com a evidência. Avalie aderência às regras do corpo (proteção do projeto, contrato de aceite, gates, parada honesta) e a integração com `/goal`, não a simples menção de palavras-chave.

### 7. Retomada
Ao retomar, leia checkpoint, **revalide** branch/HEAD, working tree, serviços, evidências e backlog; não confie cegamente no estado salvo. Não repita automaticamente migrações, pagamentos, exclusões, deploys ou comandos não idempotentes. Leia `references/checkpoint-and-resume.md`.

### 8. Relatório obrigatório
Apresente: `STATUS`; objetivo/escopo; baseline; `REQ-ID → estado → evidência`; correções por causa raiz; arquivos alterados; comandos/testes executados e resultados; inspeções reais; riscos/defeitos restantes; gates `NOT_RUN/BLOCKED`; checkpoint e próxima ação. Nunca invente logs, capturas, scores ou execução de ferramentas.

## Referências
- `references/goal-integration.md`: integração com `/goal` e coordenação de skills.
- `references/quality-gates.md`: matriz de gates e evidências.
- `references/checkpoint-and-resume.md`: persistência, retomada e limites.
- `references/adversarial-review.md`: roteiros de investigação por camada.
- `references/diagnostic-playbook.md`: roteiro de diagnóstico por camada.

## Roteamento com as outras skills

| Situação | Skill |
|---|---|
| Um teste vermelho ou bug pontual, ciclo curto | `loop` |
| Objetivo longo com `/goal`, várias rodadas, retomada | **esta** |
| Contrato de evidência para entrega M/L | `master-engineer` |
| Interface, direção de arte, gate visual | `dz23-ultimate-pro-max` |
| Revisão independente antes de homologar | `code-review` ou `ponytail-review` |
| Endpoint novo ou contrato mudando | `api-and-contracts` |
| Schema, índice, backfill, migração | `data-migrations` |
| Risco de authz/injeção/segredo antes de expor | `security-review` |
| CI/CD, release, ambientes, rollback | `delivery-pipeline` |

Regra: **não crie um segundo orquestrador**. Se o harness já tem `/goal` com driver de continuação, esta
skill opera dentro dele; ela não inicia rodadas nem substitui o mecanismo nativo.
