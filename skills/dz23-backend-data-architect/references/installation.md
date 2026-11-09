# Instalação

## DeepSeek Harness (DSH)
1. Copie a pasta `dz23-backend-data-architect/` para o diretório de skills:
   - Windows: `C:\Users\<usuário>\.agents\skills\dz23-backend-data-architect\`
   - O DSH descobre `SKILL.md` na raiz da pasta; não é preciso reiniciar.
2. Confirme que aparece no catálogo de skills da sessão.
3. Carregue por comando (`/dz23-backend-data-architect`) ou por descrição: peça "modele o schema e escreva a migração reversível" que o agente seleciona a skill.
4. Sempre que a tarefa envolver produção, siga `references/quality-gates.md` para o critério de entrega.

## Claude Code / Codex / outros harnesses com SKILL.md
- Mesma estrutura: uma pasta por skill com `SKILL.md`, `references/`, `templates/` e `scripts/`.
- `~/.claude/skills` e `~/.codex/skills` apontam para `~/.agents/skills` (junction no Windows): instalar uma vez reached todos.
- O nome do comando é o `name:` do frontmatter (kebab-case), não o nome da pasta.

## Verificação
```bash
python scripts/validate_skill.py
```
Confere arquivos obrigatórios, frontmatter e Markdown não vazio.

## Estrutura
```
dz23-backend-data-architect/
  SKILL.md
  README.md
  CHANGELOG.md
  PROMPT-ATIVACAO.txt
  references/
    service-architecture.md
    data-modeling.md
    api-contracts.md
    migrations-and-zero-downtime.md
    security-and-tenancy.md
    performance-and-observability.md
    quality-gates.md
    anti-patterns.md
    installation.md
  templates/
    adr.md
    contract-review.md
  scripts/
    validate_skill.py
```

## Uso combinado
Esta skill decide **backend, dados e contrato**. Combine com:
- `security-review` — revisão de segurança com evidência antes de expor.
- `data-migrations` — quando a tarefa é só schema/migração.
- `api-and-contracts` — quando a tarefa é só contrato/versionamento.
- `delivery-pipeline` — CI/CD, ambientes e rollback de deploy.
- `dz23-ultimate-pro-max` — quando houver interface envolvida.
- `dz23-autonomous-improvement-ultimate` — quando a tarefa roda dentro de um `/goal`.
