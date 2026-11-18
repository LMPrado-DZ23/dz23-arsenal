# Caldo Skills — poda de testes e desemaranhado de codebase

**Autor:** caldoai
**Repo:** https://github.com/caldoai/skills
**Licença:** MIT
**Instalação:** via [Skills CLI](skills-cli.md) — `npx skills add caldoai/skills`

## O que faz

Duas skills, ambas sobre **reduzir o que atrapalha** antes de continuar construindo. Nenhuma delas escreve
código novo: são operações de limpeza com critério.

| Skill | Pergunta que responde |
|---|---|
| **`prune-tests`** | quais testes não protegem comportamento nenhum e podem sair? |
| **`untangle-codebase`** | o que está emaranhado neste repositório a ponto de toda mudança custar caro? |

`prune-tests` é a mais delicada das duas: apagar teste é fácil, provar que ele não guardava nada é o
trabalho. A skill existe justamente para forçar essa distinção — teste que só repete a implementação, teste
que nunca falha, teste que mede o framework.

`untangle-codebase` trabalha no nível do repositório: acoplamento desnecessário, fronteiras que vazaram,
caminhos de leitura que obrigam o agente a abrir 20 arquivos para mudar uma linha.

## Por que usar em conjunto com DZ23

| Skill DZ23 | Papel | O que falta nela |
|---|---|---|
| `dz23-codebase-cartographer` | **mapeia** o repositório e produz o brief de contexto | não decide o que **remover** |
| `master-engineer` | exige baseline e prova de que nada quebrou | não escolhe onde cortar |
| **`prune-tests`** | decide **o que sai** da suíte, com critério | — |
| **`untangle-codebase`** | decide **onde** o emaranhado cobra pedágio | — |

A ordem que funciona: mapear (`codebase-cartographer`) → desembaraçar (`untangle-codebase`) → podar testes
(`prune-tests`) → só então implementar, com baseline do `master-engineer` para provar que a poda não
derrubou cobertura real.

## Instalação

```powershell
npx skills add caldoai/skills -g -y -a universal -a claude-code -a codex
```

Verificado nesta máquina em 2026-11-18: as duas skills caíram em `~/.agents/skills` (lido por DSH, Codex,
OpenCode, Cline, Cursor) e nos diretórios próprios de Claude Code e Codex.

## Uso

```
"Untangle esse repo: quero saber onde as mudanças custam caro antes de mexer."
"Roda o prune-tests em src/services e me mostra o que pode sair, com a razão de cada um."
```

## Cuidados

- **Poda de teste é irreversível no fluxo normal.** Rode em branch separada e guarde o baseline da suíte
  antes. Skill nenhuma substitui `git` como rede de segurança.
- **Skill de terceiro roda com as permissões do agente.** Leia o `SKILL.md` antes de instalar — são dois
  arquivos curtos, sem dependência de rede.
- As duas fazem **análise**, não execução: não há script embutido que mexa no repositório sozinho.
