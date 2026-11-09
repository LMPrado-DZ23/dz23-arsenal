# Anthropic Skills

**Autor:** Anthropic
**Repo:** https://github.com/anthropics/skills
**Licença:** verificar no repositório (skills oficiais)

## O que faz

Bundle oficial de skills da Anthropic. Os destaques:

| Skill | Para quê |
|---|---|
| `skill-creator` | criar/estruturar uma skill nova |
| `mcp-builder` | implementar servidor MCP |
| `pdf` | ler/gerar PDF |
| `docx` | ler/editar Word |
| `xlsx` | ler/editar Excel |
| `pptx` | ler/editar PowerPoint |

As skills de Office são a forma mais confiável de o agente produzir um `.docx` real (com estilos e
tabelas) em vez de markdown renomeado.

## Por que usar em conjunto com DZ23

As 9 skills DZ23 produzem **markdown** (spec, plano, relatório, ADR). Quem precisa entregar em Office usa
estas.

| DZ23 gera | Anthropic Skills exporta |
|---|---|
| spec em markdown | `.docx` com sumário e tabelas |
| benchmark em tabela | `.xlsx` com fórmulas |
| relatório de RE | `.pdf` assinável |
| plano de release | `.pptx` para stakeholders |

Fluxo típico: `dz23-spec-to-system-engine` produz a spec → `docx`/`pdf` entrega ao cliente.

## Instalação

Como plugin:

```
/plugin install anthropic-skills
```

Manual:
```bash
git clone https://github.com/anthropics/skills.git
cp -r skills/* ~/.agents/skills/
```

## Exemplo de uso

```
"Pega o plan.md que a spec-to-system-engine gerou e produz um .docx com sumário,
 tabela de requisitos e critérios de aceite. Depois exporta também em PDF."
```

## Alternativas

- `pandoc` — conversão markdown → Office (mais controle, mais configuração).
- `python-docx` / `openpyxl` — programático, sem skill.

## Cuidados

- Skills oficiais mudam com o tempo; o catálogo acima pode estar desatualizado.
- Gerar `.docx`/`.xlsx` grande consome contexto — prefira gerar por script.
- Verifique a licença no repositório antes de redistribuir.
