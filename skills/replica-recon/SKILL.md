---
name: replica-recon
version: 1.0.0
description: >
  Engenharia reversa black-box de um app em um mapa de recon: inventário de telas, fluxos de usuário,
  lista de componentes, modelo de dados inferido e matriz de features — a partir de páginas públicas,
  screenshots, listagem de loja, docs de ajuda e a conta do próprio usuário. É a primeira etapa de
  "clonar um app": refaz o que o app FAZ e como o usuário se move, clean-room, nunca o que o app possui.
  Use quando pedirem "clonar este app", "mapear o X", "quais telas o X tem", "quero minha versão do X",
  ou colarem a URL/link de loja de um app. Não é engenharia reversa de binário (isso é
  dz23-reverse-engineer-anything) nem leitura de código-fonte alheio — é recon de produto por fontes
  públicas, com regras de clean-room inegociáveis.
user-invocable: true
argument-hint: "<app, URL ou link de loja>"
metadata:
  origin: Jakeschincariol/replica-skill (skill replica-recon), MIT lida no arquivo LICENSE da raiz (Copyright 2026 Jake Schincariol)
  license: MIT
  source-file: skills/replica-recon/SKILL.md
  method: internalizado e adaptado ao rito do arsenal (eval executável, referências, gate), não copiado byte a byte
---

# replica-recon

Tudo no fluxo de clone é construído a partir do que esta skill escreve. Mapa ruim = clone ruim; gaste
o tempo aqui. **Crie** a saída no projeto do usuário: `replica/recon.md` (mapa) e `replica/features.csv` (matriz).

## Regras de clean-room (antes de qualquer coisa)

Esta skill refaz **funcionalidade e padrões de UX**, clean-room. Estuda o que o app faz e como o
usuário se move. **Não pega nada que o app possui.** Detalhe em `references/clean-room.md`.

- **Só fontes públicas e a conta do próprio usuário.** Nunca entrar em conta que não é do usuário,
  nunca pedir senha, nunca passar de paywall ou login por truque.
- **Ler, não raspar.** Sem crawler, sem download em massa, sem loop. Páginas em velocidade humana, com
  o usuário presente.
- **Sem código-fonte, sem API privada.** Não ler/salvar bundles JS, não decompilar binário, não logar
  requisições de rede para copiar endpoints. Doc de API pública pode ler.
- **Conferir os termos.** Alguns produtos proíbem usar a conta para construir concorrente — se for o
  caso, dizer e trabalhar só com fontes públicas.
- **Screenshots são referência** (`replica/screens/`), para comparar layout; nunca entram no clone.

## O método (9 passos)

Detalhe completo em `references/metodo.md`; taxonomia de fontes em `references/fontes.md`.

1. **Escopo:** qual app/plataforma, qual fatia (o core loop que o usuário paga), para quem.
2. **Fontes:** tabela com URL em toda linha, em ordem de valor (ajuda > preço > changelog > loja > …).
3. **Inventário de telas:** uma linha por tela, IDs estáveis (S01…), com estados vistos (vazio,
   carregando, cheio, erro, permissão negada, mobile).
4. **Fluxos:** F01… cada um um objetivo e as telas que percorre; conte os cliques do caminho feliz.
5. **Componentes:** toda parte de UI repetida (nome, variantes, estados, telas que usam).
6. **Modelo de dados inferido:** entidades, campos, relações — cada uma com evidência e confiança;
   marque chute como chute.
7. **Matriz de features:** escreva em `replica/features.csv` (feature, área, prioridade must/should/could,
   original, clone, notas). `clone` começa `no`.
8. **O que NÃO dá para clonar:** honestamente, como linhas `skip` com motivo (conteúdo licenciado, a
   rede e seus usuários, dados do app, deals, hardware, licença regulada).
9. **Dimensione:** telas, fluxos, entidades e as partes difíceis (realtime, sync, pagamento,
   integrações); dê um tamanho S/M/L/XL. Sem promessa de clone perfeito.

## Entregáveis

- Crie `replica/recon.md` — o mapa (modelo em `templates/recon-map.md`).
- Crie `replica/features.csv` — a matriz (modelo em `templates/features.csv`).
- Resumo de 5 linhas: core loop, contagem de telas/fluxos, as 3 partes mais difíceis, o que fica fora
  de escopo, e o próximo passo (o planejamento de stack — `dz23-spec-to-system-engine`).

## Estados de evidência

| Estado | Critério |
|---|---|
| PASS | recon.md + features.csv escritos, toda tela/fluxo com evidência de fonte pública citada |
| PARTIAL | fatia mapeada mas faltam estados, fluxos ou entidades com evidência |
| NOT_TESTED | mapa escrito sem evidência conferível (fonte não citada por linha) |

## Veredito

Pronto quando: a fatia está escopada; cada tela e fluxo cita a fonte pública de onde veio; o modelo de
dados marca chutes como chutes; a matriz separa must/should/could/skip; o "não dá para clonar" está
honesto; há um tamanho. Caso contrário, PARTIAL com o que falta.

## Roteamento com outras skills

- Alvo é **binário/firmware**, não produto: use `dz23-reverse-engineer-anything` (Ghidra), não esta.
- Planejar stack, schema e API a partir do mapa: `dz23-spec-to-system-engine` + `dz23-backend-data-architect`.
- Ler o que os usuários reais do app odeiam (para o clone corrigir): `replica-entrepreneur`.
- Pontuar a paridade do clone contra o original depois: `replica-diff`.
