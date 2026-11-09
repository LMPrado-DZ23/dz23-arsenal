# Política de segurança

## Versões suportadas

Apenas a **última versão** de cada skill recebe correção de segurança.

| Componente | Suportado |
|---|---|
| Skills em `skills/` | última versão (`VERSION` atual) |
| MCP em `mcp/` | última versão publicada |
| Bundle em `bundle/` | última versão publicada |
| Documentação e scripts | `main` |

## Como reportar

**Não abra issue pública para vulnerabilidade.** Use o canal privado:

- GitHub → aba **Security** → **Report a vulnerability** (GitHub Security Advisory)

Inclua:

1. componente e versão (`VERSION` ou campo `version` do `package.json`);
2. o que acontece (impacto);
3. passos mínimos para reproduzir;
4. ambiente (SO, versão de Node/Python);
5. se aplicável, prova de conceito — **sem dado real de terceiro**.

## O que conta como vulnerabilidade aqui

Este repositório distribui **instruções** (skills) e **scripts auxiliares**. São vulnerabilidades:

| Classe | Exemplo |
|---|---|
| Execução não intencional | script que executa conteúdo de binário como comando |
| Vazamento de segredo | skill que instrui a colar token em log ou em arquivo versionado |
| Gate desligado por padrão | skill que declara `PASS` sem evidência |
| Prompt injection | instrução que trata saída de ferramenta externa como confiável |
| Permissão perigosa | comando que pede `sudo`/admin sem necessidade declarada |
| Dependência comprometida | versão pinada com CVE conhecida |

## O que **não** é vulnerabilidade

- Skill não executar em ambiente sem a CLI exigida — isso é `BLOCKED_BY_EXTERNAL_DEPENDENCY`, documentado.
- Eval não executado — está declarado como `NOT_TESTED` no CHANGELOG.
- Comportamento de skill externa listada em `external/` — reporte ao projeto de origem.

## Prazo de resposta

Melhor esforço, sem SLA: confirmação de recebimento em até 7 dias; correção priorizada conforme
severidade. Projeto mantido por uma pessoa — não prometo prazo que não posso cumprir.

## Escopo de segurança do conteúdo

As skills **leem e reportam**; elas não escrevem em alvo, não fazem deploy e não instalam ferramenta sem
autorização explícita. Se você encontrar uma skill que viola isso, é vulnerabilidade — reporte.

## Divulgação

Correção publicada primeiro; detalhe técnico depois, com crédito a quem reportou (salvo pedido de
anonimato).
