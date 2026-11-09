# Instalação

## DeepSeek Harness (DSH)
1. Copie `dz23-codebase-cartographer/` para `C:\Users\<usuário>\.agents\skills\`.
2. A descoberta lê `SKILL.md` na raiz — sem reinício.
3. Invoque por `/dz23-codebase-cartographer` ou por descrição ("mapeie este repositório antes de eu mexer").
4. `~/.claude/skills` e `~/.codex/skills` são junction para `~/.agents/skills`: instalar uma vez alcança os três.

## Estrutura
```
dz23-codebase-cartographer/
  SKILL.md
  README.md
  CHANGELOG.md
  VERSION
  PROMPT-ATIVACAO.txt
  references/ (11)
  templates/ (4)
  scripts/repo_probe.py
  scripts/validate_skill.py
  evals/evals.json (15)
```

## Onde os artefatos vão
No **projeto alvo**, não na pasta da skill:
```
projects/<projeto>/map/
  CODEBASE-MAP.md      (templates/codebase-map.md)
  CONTEXT-BRIEF.md     (templates/context-brief.md)
  CHANGE-IMPACT.md     (templates/change-impact.md)
  HOTSPOTS.md          (templates/hotspot-report.md)
```

## Scanner read-only
```bash
python scripts/repo_probe.py <path-do-repo>            # resumo em texto
python scripts/repo_probe.py <path> --json             # JSON para o mapa
```
Ele **só lê**: conta arquivos, detecta stack por manifest, lista entry points, encontra CI/testes/migrações, maiores arquivos e o commit atual. Não modifica, não executa código do repo.

## Verificação
```bash
python scripts/validate_skill.py
```

## Uso combinado
- `dz23-spec-to-system-engine` — o que construir (esta skill diz onde/como está hoje).
- `dz23-backend-data-architect` — mudança de schema, contrato e backend.
- `architect` — decisão estrutural ampla.
- `ponytail-audit` — auditoria de qualidade independente do mapa.
- `graphlint` — grafo de dependência e código morto com ferramenta dedicada; use como complemento quando disponível.
- `dz23-e2e-browser-verifier` — provar o fluxo depois da mudança.

## Quando **não** usar
Repositório de um arquivo, script isolado ou pergunta pontual não precisam de mapa. Para bug localizado, use `diagnosing-bugs`; para auditoria de qualidade, `ponytail-audit`.
