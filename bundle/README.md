# dz23-dsh-agency

Bundle de **88 agentes especializados** com um Diretor orquestrador, para o campo `agent-instructions` do
DeepSeek Harness.

**Versão:** 1.0.0

## O que faz

Não é uma skill no formato DZ23. É uma **biblioteca de perfis de agente**: um Diretor que decompõe o
pedido e delega, e 87 especialistas por domínio (backend, frontend, dados, infra, segurança, produto,
dados/BI, mobile, etc.).

O valor está no catálogo: em vez de escrever o perfil de "especialista em migração de banco" do zero, você
pega um perfil pronto, com escopo, entradas, saídas e limites definidos.

## Estrutura

| Arquivo/pasta | Conteúdo |
|---|---|
| `AGENTS.md` | tabela dos 87 perfis |
| `DSH_COMPLETE_SPECIALIST_AGENCY.md` | documento canônico (o que vale em caso de dúvida) |
| `DSH_SPECIALIST_AGENT_CATALOG.md` | catálogo principal |
| `DSH_SPECIALIST_AGENT_CATALOG_EXPANDED.md` | versão expandida |
| `DSH_SPECIALIST_AGENT_CATALOG_VERTICALS.md` | por vertical de negócio |
| `DSH_AGENT_SHARED_CORE_UNIVERSAL.txt` | núcleo comum a todos os agentes |
| `DSH_AGENCY_DIRECTOR_OVERLAY.txt` | overlay do Diretor |
| `DSH_DECISION_LOG_TEMPLATE.md` | template de log de decisão |
| `DSH_INTEGRATIONS.md` | como integrar com outros sistemas |
| `DSH_QUICKSTART.md` | guia de 5 passos |
| `preset-engenheiro-de-sistemas.md` | preset autônomo de engenheiro de sistemas |
| `agents/` | **88 arquivos pré-gerados** (`00-diretor` + `01`..`87`) |
| `build.py` | gera `agents/` a partir do canônico |
| `check_consistency.py`, `check_sizes.py` | validadores do bundle |

## Instalação

```bash
cd bundle/dz23-dsh-agency
python build.py          # regenera agents/ a partir do canônico
python check_consistency.py
```

## Uso

1. Leia `DSH_QUICKSTART.md` (5 passos).
2. Escolha o perfil em `agents/` (ex.: `agents/00-diretor.txt` + `agents/12-....txt`).
3. Cole no campo `agent-instructions` do harness.
4. Ajuste o escopo do perfil ao seu projeto — os perfis são genéricos por desenho.

## Cuidados

- Os agentes são **prompts**, não código: a qualidade depende do modelo que os executa.
- `build.py` sobrescreve `agents/` — se você editou um perfil à mão, edite o canônico e regenere.
- 88 perfis é muita coisa; comece pelo Diretor + 1 especialista.
- O catálogo é longo e consome contexto: carregue só o perfil que vai usar.

## Versão

`VERSION` = 1.0.0. Ver `CHANGELOG.md` dentro desta pasta.
