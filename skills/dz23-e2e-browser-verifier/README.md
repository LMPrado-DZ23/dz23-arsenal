# DZ23 E2E Browser Verifier v1.1.0

Skill de automação de testes end-to-end e verificação em browser real para DeepSeek Harness e agentes compatíveis com `SKILL.md`.

Cobre o caminho completo: **mapear o risco → escolher a camada → escrever o teste → rodar em browser real → estabilizar → provar com artefato → integrar no CI → entregar**.

## Conteúdo

| Arquivo | Para quê |
|---|---|
| `SKILL.md` | Skill principal: workflow 9 etapas, tiers P0/P1/P2, módulos 5.1–5.6, mapeamento A–F, vereditos |
| `references/test-strategy.md` | O que é E2E, tiers de risco, casos negativos obrigatórios |
| `references/playwright-strategy.md` | Seletores, Page Object, storage state, mocks, cross-browser |
| `references/browser-security.md` | Autorização server-side, IDOR, tenant, sessão, CSRF/CORS |
| `references/visual-accessibility.md` | axe-core, WCAG 2.2 AA, responsividade, teclado |
| `references/flaky-debugging.md` | Sincronização web-first e protocolo Trace Viewer |
| `references/ci-and-evidence.md` | CI, shard, artifacts, trace, retenção e sanitização |
| `references/test-data-and-environments.md` | Seed, isolamento, teardown, ambientes |
| `references/quality-gates.md` | Gates e severidade (BLOCKER/MAJOR/MINOR) |
| `references/anti-patterns.md` | 38 erros recorrentes com sintoma, dano e correção |
| `templates/playwright.config.ts` | Configuração de referência (Chromium + mobile; Firefox/WebKit comentados) |
| `templates/e2e-smoke.spec.ts` | Spec de referência com fixture de console/network |
| `templates/axe-audit.spec.ts` | Auditoria de acessibilidade e teclado |
| `templates/e2e-report.md` | Estrutura do relatório com veredito |
| `scripts/validate_skill.py` | Validador documental (refs, templates, evals, versão) |

## Uso

1. Instalar no diretório de skills (`references/installation.md`).
2. Invocar por `/dz23-e2e-browser-verifier` ou por descrição ("escreva o E2E do checkout e prove com trace").
3. Combinar com `dz23-ultimate-pro-max` (UI), `dz23-backend-data-architect` (dado/contrato), `security-review`, `delivery-pipeline`.

**Prompt de ativação:** [`PROMPT-ATIVACAO.txt`](PROMPT-ATIVACAO.txt).

**Avaliação:** `evals/evals.json` — 15 cenários (schema 1). Cenários não são testes executados: rode em harness real e registre o resultado por caso.

**Versão:** [`VERSION`](VERSION) (1.1.0) · histórico em [`CHANGELOG.md`](CHANGELOG.md).

## Origem

Síntese de 3 propostas (Claude, Gemini, ChatGPT) + relatório de verificação do Manus. Os textos-fonte
ficam em `_sources/` no projeto de trabalho (`projects/dz23-e2e-browser-verifier/`) e **não** vão no
pacote de distribuição — servem de rastreabilidade.

## Princípio

Teste que passa sem provar é pior que teste ausente: cria confiança falsa. `NOT_TESTED` nunca vira `PASS`.

---

## Arsenal — resumo operacional

**Versão real (VERSION/frontmatter):** 1.1.0 · **Categoria:** testing · **Complexidade:** intermediate

### Quando usar

- Verificar fluxo crítico de UI em browser real (cross-browser).
- Provar que uma correção de interface funciona, com evidência visual.
- Auditar acessibilidade (axe + WCAG 2.2 AA).
- Capturar trace/vídeo de um bug intermitente.

### Quando NÃO usar

- Fluxo sem UI (teste de API puro).
- Quando não há ambiente no ar: declare `BLOCKED`, não simule browser.
- Como substituto de teste unitário.

### Instalação

```bash
# Já incluída no install-all. Manual:
cp -r skills/dz23-e2e-browser-verifier ~/.agents/skills/dz23-e2e-browser-verifier
```

### Uso

```bash
/dz23-e2e-browser-verifier

# ou por descrição — o agente carrega sozinho (ver SKILL.md)
```

### Pré-requisitos de CLI

`node`, `npx`, `playwright` (obrigatórias) · `rg` (recomendada).

### Evidência / Quality gates

- Todo teste com seletor estável (role/label), nunca coordenada.
- Artefato salvo: screenshot, trace ou vídeo por execução.
- Veredito `PASS` exige execução; `NOT_TESTED` quando não rodou.
- Flaky declarado como flaky, não como instabilidade do produto.

### Integração com outras skills

Recebe ambiente de `dz23-devops-cloud-deployer` e build de `dz23-ultimate-pro-max`; fecha o ciclo de release.

### Versão e changelog

Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em [`../../CHANGELOG.md`](../../CHANGELOG.md).
