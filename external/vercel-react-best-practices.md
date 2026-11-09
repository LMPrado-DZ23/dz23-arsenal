# Vercel React Best Practices

**Autor:** vercel-labs
**Repo:** https://github.com/vercel-labs/agent-skills
**Licença:** verificar no repositório

## O que faz

Conjunto de regras de performance para React e Next.js, mantido pela Vercel Labs: padrões de renderização,
uso correto de Server/Client Components, streaming, cache, `Suspense`, tamanho de bundle e as armadilhas
clássicas de hidratação.

É específico de stack — e é justamente isso que o torna útil: as rules são acionáveis, não genéricas.

## Por que usar em conjunto com DZ23

| Skill DZ23 | Papel |
|---|---|
| `dz23-ultimate-pro-max` | direção de arte, UX, acessibilidade, design system (agnóstico de framework) |
| `dz23-performance-scalability-engine` | mede e localiza o gargalo, define budget |
| **Vercel React Best Practices** | **como** resolver o gargalo quando a stack é React/Next |

O `performance-scalability-engine` diz "o gargalo está na camada 1, no bundle"; esta skill diz o que
fazer no Next para reduzir o bundle.

## Instalação

```bash
git clone https://github.com/vercel-labs/agent-skills.git
cp -r agent-skills/skills/react-best-practices ~/.agents/skills/vercel-react-best-practices
```

## Exemplo de uso

```
"Essa página Next tem LCP de 4,1s. O performance-scalability-engine já localizou: bundle
 inicial grande e imagem sem priority. Aplica as regras do React Best Practices e me diz
 o que mudou."
```

## Alternativas

- `dz23-ultimate-pro-max` — performance de UI de forma agnóstica (não cobre Next específico).
- Documentação oficial do Next — fonte primária, mas não acionável por agente.

## Cuidados

- **Só use se o projeto for React/Next.** Aplicar regra de framework em projeto Vue/Svelte é ruído.
- Regras de Next mudam entre versões (App Router × Pages Router); confirme a versão.
- Não substitui medição: regra aplicada sem baseline é chute com aparência de engenharia.
