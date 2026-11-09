# Changelog — dz23-arsenal

Histórico de releases **do arsenal**. O changelog de cada skill fica dentro da própria pasta
(`skills/<nome>/CHANGELOG.md`).

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
