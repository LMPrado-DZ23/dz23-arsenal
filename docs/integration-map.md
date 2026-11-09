# Mapa de integração

Como as skills se conectam, quem chama quem e onde a informação muda de mão.

## Fluxo principal (feature nova)

```mermaid
graph TD
    A[spec-to-system-engine] -->|spec + fatias + Gherkin| B[backend-data-architect]
    A -->|requisitos de UI| C[ultimate-pro-max]
    B -->|imagem + pipeline| D[devops-cloud-deployer]
    C -->|build de UI| E[e2e-browser-verifier]
    D -->|ambiente no ar| E
    E -->|fluxo verde| F[release]
```

O ponto de controle: **a spec é o contrato**. Se `backend` e `frontend` divergirem sobre o formato de um
payload, o que vale é o que está na spec — não o que foi implementado primeiro.

## Fluxo de mudança em código existente

```mermaid
graph TD
    A[codebase-cartographer] -->|mapa + zonas de risco| B[decisão: mexer ou não]
    B --> C[backend-data-architect]
    B --> D[ultimate-pro-max]
    C --> E[performance-scalability-engine]
    D --> E
    E -->|gargalo localizado| C
    E -->|gargalo no render| D
```

O `cartographer` vem **antes** de qualquer mudança em código legado. Nenhuma skill deve "dar uma olhada
no código" por conta própria quando o repo é desconhecido.

## Fluxo de otimização

```mermaid
graph TD
    A[performance-scalability-engine] -->|mede baseline| B[gargalo localizado]
    B -->|camada 1: frontend| C[ultimate-pro-max]
    B -->|camada 2: rede| D[backend-data-architect]
    B -->|camada 3: banco| D
    B -->|camada 4: infra| E[devops-cloud-deployer]
    C --> F[mede de novo]
    D --> F
    E --> F
```

Regra: **uma camada por vez.** Duas mudanças simultâneas = nenhuma conclusão sobre qual funcionou.

## Fluxo de análise de artefato fechado

```mermaid
graph TD
    A[reverse-engineer-anything] -->|entende o binário| B[dossiê técnico]
    B --> C[codebase-cartographer]
    C -->|mapa do que foi descoberto| D[spec-to-system-engine]
    D -->|reconstrução como especificação| E[implementação]
```

Usado quando o artefato é entregue sem fonte: app fechado, firmware, biblioteca sem código.

## Orquestração autônoma

```mermaid
graph TD
    G[/goal/] --> H[autonomous-improvement-ultimate]
    H -->|auditoria| A[skill de domínio]
    H -->|correção| A
    H -->|revisão adversarial| A
    H -->|checkpoint| I[(estado persistido)]
    H -.não implementa.-> A
```

`autonomous-improvement-ultimate` **não implementa**: ela decide o quê, delega para a skill de domínio,
cobra evidência e persiste o estado. É a única que pode chamar todas as outras.

## Regras de conexão

1. **Nunca dois orquestradores.** Só `autonomous-improvement-ultimate` orquestra; as outras decidem
   dentro do próprio domínio.
2. **A execução de código pertence à skill do domínio.** Performance mede e localiza; quem altera o
   código é backend ou frontend.
3. **O artefato da anterior é a entrada da próxima.** Spec → código → imagem → verificação. Se falta o
   artefato de entrada, a próxima skill declara `BLOCKED`, não improvisa.
4. **Nenhuma skill instala ferramenta sozinha.** Falta de CLI é `BLOCKED_BY_EXTERNAL_DEPENDENCY` com a
   dependência nomeada.

## Tabela de handoff

| De | Para | Artefato passado | Formato |
|---|---|---|---|
| spec | backend | requisitos + Gherkin + contrato | markdown |
| spec | frontend | requisitos de UI + estados | markdown |
| cartographer | qualquer | mapa + zonas de risco + ledger | markdown |
| backend | devops | Dockerfile + pipeline + envs | arquivos |
| frontend | e2e | rotas + fluxos críticos | lista |
| devops | e2e | URL do ambiente | string |
| performance | backend/frontend | gargalo + budget + evidência | markdown |
| RE | cartographer | dossiê do binário | markdown |
