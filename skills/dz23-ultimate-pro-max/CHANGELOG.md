# Changelog — dz23-ultimate-pro-max

## [2.2.4] — 2026-11-17

### Corrigido
- `scripts/validate_skill.py` não usa mais `assert` para reportar falha das checagens comuns. Sob `python -O` a instrução é removida pelo interpretador e o validador imprimia OK com referência quebrada, saindo 0 — verificado nas dez skills desta data. Agora imprime cada erro em stderr e sai 1 nos dois modos.
- Reprodução: injetar ``Ver `references/quebrada-O-teste.md`.`` no SKILL.md e rodar `python -O scripts/validate_skill.py` → antes exit 0, agora exit 1. Coberto por caso permanente em `scripts/selftest-ferramentas.py` (grupo `rejeicao`).

## [2.2.3] — 2026-11-17

### Corrigido
**Referência histórica deixou de ser uma segunda skill carregável**

- `references/legacy-v1.md` carregava frontmatter próprio com `name: dz23-premium-ui-ultimate` — a skill descontinuada, declarada viva dentro de uma referência. Substituído por cabeçalho explícito de arquivo histórico; o conteúdo metodológico permanece intacto.
- Motivo pelo qual passou despercebida: o testes de nome morto existia nos outros validadores, mas este era justamente o que faltava nesta skill (15 linhas, sem checagem de eval nem de nome).

## [2.2.2] — 2026-11-09

### Corrigido
- `evals/evals.json`: os casos não tinham `title`, exigido pelo `evals.schema.json` do arsenal (25 casos em 2 skills). Título derivado do id — mecânico, sem inventar conteúdo.

## [2.2.1] — 2026-11-09

### Adicionado
- **`evals/evals.json` com 13 cenários** — a skill tinha **zero** evals, sendo a de output mais subjetivo do
  arsenal. Cobre: tokens semânticos, Tailwind v3 × v4 (`@theme`), estados interativos, focus-visible,
  `prefers-reduced-motion`, CLS de mídia, adoção de shadcn/ui, badge sem quebra de linha, contraste,
  estados vazio/erro, prova visual e streaming de chat.
- `references/stack-implementation.md`: explicitado `@theme` do Tailwind v4 (CSS como fonte dos tokens) e
  `aspect-ratio`/`width`/`height` contra CLS.

### Recebido de `dz23-autonomous-improvement-ultimate`
- `tailwind3`, `tailwind4` e `streaming-chat` — estavam lá, mas testam regra desta skill.

## [2.2.0] — 2026-11-08

### Adicionado
- `references/stack-implementation.md` — cobre o que a direção de arte não cobre: como o design system vira
  código na stack real.
  - tokens em **3 camadas** (primitiva → semântica → componente) e mapeamento para Tailwind (proibido valor
    mágico no JSX)
  - **shadcn/ui**: adoção como código-fonte (você vira dono), não dependência copiada cega
  - tabela de **estados obrigatórios** por componente interativo (hover, active, focus-visible, disabled,
    loading, error) com como verificar cada um
  - especificidades de **React, Next.js (App Router), Vue/Nuxt, React Native/Expo, Flutter**
  - **8 bugs visuais recorrentes** com causa e correção (badge quebrando linha, falta de `cursor-pointer`,
    CLS por mídia sem dimensão, fonte tardia, `prefers-reduced-motion` ignorado, contraste variável, focus
    trap, toaster sobre ação no mobile)
  - checklist de pré-entrega para o `dz23-e2e-browser-verifier`
- `VERSION` — arquivo criado; a skill só declarava versão no frontmatter, o que quebrava o empacotamento.

### Corrigido
- A skill tinha direção de arte, contratos de componente e gates, mas **não dizia como implementar na stack
  do projeto** — Tailwind, shadcn e framework ficavam a cargo da improvisação do agente.

## v2.1.0 — 2026-11-08

feat(skill): v2.1 — módulo de interatividade enterprise, mídia rica e motion

- SKILL.md: item 5 expandido com 5.1–5.6 (carrossel produção, Bento assimétrico, direção de
  arte em mídia, motion coreografado, acessibilidade de movimento, stack + critério de saída)
- visual-direction.md: §6 (direção de arte) e §7 (checklist v2.1)
- quality-gates.md: BLOCKER estendido (reduced-motion global), MAJOR +3 (fileira de cards,
  aria-label em carrossel, easing), MINOR (parallax/vídeo/contador)
- legacy-v1.md intocado; `.bak-v1` e `.bak-v2` preservados no diretório de instalação e fora do pacote

## v2.0.0 — 2026-11-07

- Sucessora da `dz23-premium-ui-ultimate`; v1 preservada em `references/legacy-v1.md`.
- base: direção de arte, design system, B-3PO, QA/evidência, validador documental.
