# DZ23 Ultimate Pro Max v2.1

Skill de engenharia de interfaces premium para DeepSeek Harness e agentes compatíveis com SKILL.md.

Inclui a skill principal, guias de direção de arte, componentes, B-3PO, QA, instalação, prompt de ativação e validador documental.

**Novo em v2.1:** módulo obrigatório de arquitetura de interatividade enterprise (carrossel/slider de produção, bento grid assimétrico, mídia rica com direção de arte, motion coreografado) e critérios BLOCKER/MAJOR de interatividade nos quality gates.

**Escopo:** instruções e metodologia, não código de componentes nem garantia automática de qualidade. O pacote preserva a skill v1 em `references/legacy-v1.md` e usa princípios de shadcn/ui sem redistribuir seu repositório.

**Uso:** instalar no diretório de skills configurado e verificar que o agente leu o arquivo; seguir `references/installation.md`.

---

## Arsenal — resumo operacional

**Versão real (VERSION/frontmatter):** 2.1 · **Categoria:** frontend · **Complexidade:** advanced

### Quando usar

- Criar ou redesenhar interface com identidade própria (não template).
- Revisar UI/UX: hierarquia, tipografia, cor, motion, estados.
- Definir ou corrigir design system e tokens.
- Auditar acessibilidade e performance de render.

### Quando NÃO usar

- Backend, banco ou contrato de API (`dz23-backend-data-architect`).
- Deploy ou infra (`dz23-devops-cloud-deployer`).
- Quando não há requisito visual nem usuário definido: primeiro a spec.

### Instalação

```bash
# Já incluída no install-all. Manual:
cp -r skills/dz23-ultimate-pro-max ~/.agents/skills/dz23-ultimate-pro-max
```

### Uso

```bash
/dz23-ultimate-pro-max

# ou por descrição — o agente carrega sozinho (ver SKILL.md)
```

### Pré-requisitos de CLI

`node`, `npx` (obrigatórias) · `playwright`, `lighthouse` (recomendadas para verificação visual e de performance).

### Evidência / Quality gates

- Direção de arte declarada antes do primeiro componente.
- Estados completos: loading, vazio, erro, sucesso, permissão negada.
- Contraste e foco de teclado verificados, não presumidos.
- Verificação visual com screenshot antes de declarar pronto.

### Integração com outras skills

Recebe requisitos de `dz23-spec-to-system-engine`; recebe gargalo de render de `dz23-performance-scalability-engine`; entrega build para `dz23-e2e-browser-verifier`.

### Versão e changelog

Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em [`../../CHANGELOG.md`](../../CHANGELOG.md).
