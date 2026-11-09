# DZ23 Autonomous Improvement Ultimate v2.1

Super Skill consolidada a partir de cinco materiais enviados pelo usuário. Instalar a pasta completa no diretório de skills suportado pelo DeepSeek Harness; o caminho varia conforme a instalação. O arquivo de entrada é SKILL.md. Confirmar descoberta e leitura da skill com um /goal de teste antes de usar em produção.

O arquivo DeepSeek fornecido continha somente um fragmento de ativação; não foi tratado como uma implementação completa. A skill não fornece execução persistente fora da sessão sem suporte do harness.

---

## Arsenal — resumo operacional

**Versão real (VERSION/frontmatter):** 2.1 · **Categoria:** orchestration · **Complexidade:** advanced

### Quando usar

- Qualquer `/goal` de engenharia com critério de aceite medível.
- Tarefa longa que precisa sobreviver a interrupção (checkpoint persistido).
- Correção de bug com causa raiz não óbvia.
- Refactor com risco de regressão que exige baseline + reteste.

### Quando NÃO usar

- Pergunta rápida ou ajuste de 1 linha — o ritual custa mais que o trabalho.
- Sem critério de aceite medível: o ciclo não tem fim.
- Junto com outro orquestrador — só um conduz.
- Como ferramenta de operação em produção: ela orquestra mudança de código.

### Instalação

```bash
# Já incluída no install-all. Manual:
cp -r skills/dz23-autonomous-improvement-ultimate ~/.agents/skills/dz23-autonomous-improvement-ultimate
```

### Uso

```bash
/dz23-autonomous-improvement-ultimate

# ou por descrição — o agente carrega sozinho (ver SKILL.md)
```

### Pré-requisitos de CLI

`git`, `python` (3.10+) e o que a skill de domínio chamada exigir.

### Evidência / Quality gates

- Matriz de requisitos com critério verificável, evidência e estado.
- Baseline registrado antes de mexer (o que já falhava).
- Veredito explícito: `PASS` / `PARTIAL` / `FAIL` / `NOT_TESTED` / `BLOCKED_BY_EXTERNAL_DEPENDENCY`.
- Checkpoint retomável a cada rodada, com o que **não** foi testado declarado.

### Integração com outras skills

Chama todas as outras skills. É a única que orquestra; as demais decidem dentro do próprio domínio.

### Versão e changelog

Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em [`../../CHANGELOG.md`](../../CHANGELOG.md).
