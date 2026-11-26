# Hallmark — piso de design para UI gerada por agente

**Autor:** Nutlope (Hassan El Mghari)
**Repo:** https://github.com/Nutlope/hallmark
**Licença:** MIT (verificada: `license.spdx_id = MIT` na API do GitHub e `skills/hallmark/LICENSE`
lido — "MIT License / Copyright (c) 2026 Hallmark contributors")
**Stack:** skill em Markdown + scripts Node.js (sloplint, tema, captura, imagem) + 51 temas em CSS
**Versão instalada:** 2.0.0 · **Estado nesta máquina:** **instalado nos quatro harnesses** em 2026-11-26

## O que faz

Uma skill de *direção de design* para o que o agente gera deixe de parecer gerado. Não é inspiração
solta: é um **piso** de 48 regras numeradas (toda cor e toda fonte passam por token declarado em
`:root`, foco visível, hierarquia tipográfica, contraste, densidade) que vale mesmo quando nada mais
da skill é lido, mais um **sorteio de direção** por build para dois builds seguidos não convergirem
no mesmo visual, e **um tema por vez** entre 51 prontos.

| Peça | O que é |
|---|---|
| `SKILL.md` (18 KB) | o piso de 48 regras + o fluxo em 7 passos |
| `references/` (24 arquivos + 3 pastas) | anatomia, layout, tipografia, cor, movimento, dark mode, data-viz, macroestruturas, gates |
| `references/themes/` | **51 temas** com `tokens.css`, `style.css` e screenshot de referência |
| `scripts/sloplint.mjs` (232 KB) | o linter: gates por camada (`floor`, `reflex`, `finish`), saída JSON |
| `scripts/theme.mjs` | lista, valida e aplica tema |
| `scripts/install.mjs` | instalador com gate de validação antes de copiar |
| `scripts/install-hook.mjs` | hook de lint no Claude Code (aconselha, nunca bloqueia) |

## Por que usar junto do arsenal

O arsenal já tem direção de arte (`dz23-ultimate-pro-max`) e regras de UI (`web-design-guidelines`,
104 regras). O Hallmark não substitui nenhum dos dois: ele ataca o **default estatístico** do modelo —
o gradiente roxo→ciano, o "Transforme sua ideia em realidade", o card genérico — com um linter que
prova o desvio por número de gate.

| Necessidade | Ferramenta |
|---|---|
| direção de arte premium, marca, design system | `dz23-ultimate-pro-max` |
| auditar UI contra 104 regras de interface | `web-design-guidelines` |
| **impedir o visual de IA e provar por gate** | **Hallmark** |
| verificar fluxo no browser com evidência | `dz23-e2e-browser-verifier` |

## Instalação — o que funcionou

O instalador oficial detecta os harnesses presentes e copia o payload (`SKILL.md`, `LICENSE`,
`references`, `scripts`, `agents`), validando antes:

```powershell
git clone --depth 1 https://github.com/Nutlope/hallmark.git C:\Users\lmpra\projetos\hallmark
cd C:\Users\lmpra\projetos\hallmark\skills\hallmark\scripts
node install.mjs --claude --codex      # escreve em ~/.claude/skills e ~/.agents/skills
node install-hook.mjs --global         # hook de lint no Claude Code
```

Saída real: `indexed 50 themes` → `Claude Code: installed -> ~/.claude/skills/hallmark` →
`Codex CLI and Cursor: installed -> ~/.agents/skills/hallmark` (exit 0; os gates `refcheck` e
`theme validate` passaram).

Qwen Code não é alvo do instalador; a cópia compartilhada foi ligada por junction:

```powershell
New-Item -ItemType Junction -Path C:\Users\lmpra\.qwen\skills\hallmark `
  -Target C:\Users\lmpra\.agents\skills\hallmark
```

### Onde cada harness lê

| Harness | Caminho | Como |
|---|---|---|
| DeepSeek Harness | `~/.agents/skills/hallmark` | cópia real (root de rank 500) |
| Codex CLI | `~/.agents/skills/hallmark` | mesma cópia — **confirmado em sessão real** |
| Claude Code | `~/.claude/skills/hallmark` | cópia real + hook |
| Qwen Code | `~/.qwen/skills/hallmark` | junction para a cópia compartilhada |

Não criar junction em `~/.codex/skills`: o Codex lê `~/.agents/skills` e a skill apareceria duas vezes
(o próprio instalador avisa sobre essa duplicação).

### Hook de lint (Claude Code)

Grava em `~/.claude/settings.json` um `PostToolUse` com matcher `Write|Edit|MultiEdit` que roda
`node ~/.agents/skills/hallmark/scripts/lint-hook.mjs`. Ele **aconselha, nunca bloqueia** — o script
só tem `process.exit(0)`. Remove com `node install-hook.mjs --global --remove`.

## Uso

- Claude Code: `/hallmark` · Codex: `$hallmark` · demais: invocar a skill pelo nome.
- Formas: `<prompt>` (construir), `redesign <path>`, `audit <path>`.
- Linter avulso:

```powershell
node ~/.agents/skills/hallmark/scripts/sloplint.mjs pagina.html --json --tier floor
```

## Prova de funcionamento (nesta máquina)

Arquivo de teste com a pasta `.hallmark` e um `Hero.tsx` deliberadamente genérico; o hook devolveu:

```
Hallmark Floor check on Hero.tsx: 2 FAILs.
- gate 26a (line 1): no :focus-visible styling anywhere -> A focus ring at 3:1 or better, instant
- gate 48  (line 3): inline-style colour literal #7c3aed -> Lift the value into the token block
```

Sem a pasta `.hallmark`, o mesmo arquivo devolve `{}` e exit 0 — fora de projeto Hallmark ele não
incomoda. `INSTALADO` e `FUNCIONAL` nos quatro harnesses; qualidade visual do que a skill produz:
`NOT_TESTED` (depende do trabalho real).

## Cuidados

- **Peso**: 6,6 MB e 169 arquivos por cópia (duas cópias completas nesta máquina). `install.mjs
  --remove` apaga as duas.
- **Scripts Node executam localmente** (sloplint, tema, captura por browser). Nada disso é serviço
  nem telemetria, mas é código de terceiro rodando na sua máquina — versão 2.0.0, licença MIT lida.
- **Geração de imagem é opt-in e usa Together AI**: `scripts/imagegen.mjs` chama
  `api.together.xyz` **somente** se `TOGETHER_API_KEY` estiver no ambiente. Sem a chave ele cai para
  CSS-art/placeholder — é o estado desta máquina. Não definir a chave sem decisão explícita do dono.
- **Não é a única fonte de verdade de design**: em conflito com `dz23-ultimate-pro-max` ou
  `web-design-guidelines`, o dono do projeto decide; a skill só impõe o piso quando está ativa.
- **Atualização**: `git -C C:\Users\lmpra\projetos\hallmark pull` e repetir `install.mjs` — o
  instalador reescreve as cópias, então não editar arquivo dentro de `~/.claude/skills/hallmark` nem
  de `~/.agents/skills/hallmark`.
