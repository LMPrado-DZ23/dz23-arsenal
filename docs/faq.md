# FAQ

## Sobre as skills

**Preciso de todas as 9?**
Não. Instale a que resolve seu problema hoje. As skills são independentes; a integração é opcional.

**Qual a diferença entre skill e prompt?**
Prompt é texto que você cola. Skill tem regra, gate de evidência, referência carregada sob demanda,
template e cenário de avaliação. A skill define **o que conta como prova** — o prompt não.

**Por que cada skill tem `evals/evals.json` se os evals não são executados?**
Porque o eval é a **especificação do comportamento esperado**. Ele serve para julgar a skill
manualmente, e para automatizar depois. Mas eval declarado ≠ eval executado: o estado honesto é
`NOT_TESTED` e está registrado no CHANGELOG de cada uma.

**Uma skill pode substituir a outra?**
Não. As sobreposições estão mapeadas em [`../docs/skills-overview.md`](skills-overview.md#sobreposições-e-como-resolver),
com a regra de desempate de cada par.

**O que é `NOT_TESTED`?**
Estado honesto de "não exercitei". É diferente de `FAIL` (testei e falhou) e de `PASS` (testei e
passou). Neste arsenal, `NOT_TESTED` é uma resposta aceitável; alegar `PASS` sem saída de comando, não.

## Sobre instalação

**O instalador sobrescreve minha skill?**
Não. Ele avisa `SKIP` e segue. Para atualizar, remova a pasta antiga primeiro.

**Funciona no Linux?**
As skills são markdown + scripts Python/shell; sim. O `install-all.sh` não foi exercitado em Linux real
nesta versão — está declarado como limitação no CHANGELOG.

**Preciso de admin?**
Para copiar, não. Para junction no Windows, em geral sim (ou Developer Mode).

## Sobre as CLIs

**Quantas CLIs são necessárias?**
Depende da skill. Base: `git`, `python`, `node`, `rg`, `jq`, `curl`. Cada skill declara as suas em
`cli/required.md`.

**O repo instala as CLIs?**
Não. Ele **documenta** e verifica. Instalação é decisão sua — algumas são pesadas (Terraform, bancos,
Grafana) e não fazem sentido em toda máquina.

**`verify-cli.ps1` diz que falta algo que eu tenho.**
Provável que esteja fora do `PATH`. O script usa `Get-Command`; se o binário existe mas não está no
`PATH`, ele conta como ausente.

## Sobre o MCP e o bundle

**Qual a diferença entre MCP e skill?**
Skill é instrução para o agente. MCP é um **servidor** que expõe ferramentas ao agente via protocolo.
O `dz23-subagents-universal-mcp` expõe 28 tools de delegação/consenso/memória.

**O bundle é uma skill?**
Não. É uma biblioteca de 88 perfis de agente para o campo `agent-instructions` do DeepSeek Harness.

**Posso usar o MCP com Claude Desktop?**
Sim, qualquer cliente MCP. A configuração está em `mcp/dz23-subagents-universal-mcp/README.md`.

## Sobre contribuição

**Aceita skill nova?**
Sim, com `evals/evals.json` e pelo menos um cenário que a skill **falharia** sem a regra. Ver
[`../CONTRIBUTING.md`](../CONTRIBUTING.md).

**Aceita tradução para inglês?**
Sim. Comece pelos `README.md` das skills; os `SKILL.md` são maiores e podem vir depois.

## Sobre licença

**Posso usar comercialmente?**
Sim, MIT. Mantenha o aviso de copyright.

**As skills externas do `external/` são suas?**
Não. Cada uma pertence ao seu autor e mantém sua licença. O `external/` documenta como usar, não
redistribui.
