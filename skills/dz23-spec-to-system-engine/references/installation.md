# Instalação

## DeepSeek Harness (DSH)
1. Copie a pasta `dz23-spec-to-system-engine/` para `C:\Users\<usuário>\.agents\skills\`.
2. Descoberta lê `SKILL.md` na raiz — não precisa reiniciar.
3. Invoque por `/dz23-spec-to-system-engine` ou por descrição ("quebre este épico em fatias com contrato").
4. `~/.claude/skills` e `~/.codex/skills` apontam para `~/.agents/skills` (junction): instalar uma vez
   alcança os três.

## Estrutura
```
dz23-spec-to-system-engine/
  SKILL.md
  README.md
  CHANGELOG.md
  VERSION
  PROMPT-ATIVACAO.txt
  references/ (11 arquivos)
  templates/
    spec.md
    req-matrix.md
    slice-plan.md
    handoff.md
  scripts/validate_skill.py
  evals/evals.json
```

## Onde guardar os artefatos gerados
No projeto alvo, não na pasta da skill:
```
projects/<projeto>/
  spec/
    SPEC.md            (templates/spec.md)
    REQ-MATRIX.md      (templates/req-matrix.md)
    SLICE-PLAN.md      (templates/slice-plan.md)
    HANDOFF-SL-01.md   (templates/handoff.md)
    ADR/               (decisões irreversíveis)
```

## Verificação
```bash
python scripts/validate_skill.py
```

## Uso combinado
- `dz23-backend-data-architect` — schema, migração e contrato de API aprofundado.
- `dz23-ultimate-pro-max` — interface e direção visual.
- `architect` — decisão estrutural ampla.
- `api-and-contracts` — contrato isolado com versionamento.
- `dz23-e2e-browser-verifier` — prova E2E do critério de aceite.
- `dz23-devops-cloud-deployer` — entrega e rollback.
- `dz23-autonomous-improvement-ultimate` — quando a execução roda em `/goal`.

## Quando **não** usar
Pergunta rápida, ajuste de 1 linha ou bug localizado não precisam de spec executável. Use `diagnosing-bugs`,
`ponytail` ou execução direta — ritual aqui vira burocracia.
