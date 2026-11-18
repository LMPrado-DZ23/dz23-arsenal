---
name: replica-launch
version: 1.0.0
description: >
  Escreve o lançamento de um clone: a landing page construída sobre o ângulo de posicionamento, o preço
  fixado contra o preço público do original e as reclamações dos usuários, e a listagem de App Store e
  Google Play conferida contra os limites das lojas e as regras anti-cópia. Use ao pedir "landing page",
  "preço", "quanto cobrar", "listagem da App Store", "screenshots da loja", "plano de lançamento",
  "Product Hunt", ou depois de replica-brand. É a última etapa de clonar um app. Sem prova falsa, sem
  usar avaliações como depoimento, e o nome do original fica fora da listagem.
user-invocable: true
argument-hint: "[listing.json a conferir]"
metadata:
  origin: Jakeschincariol/replica-skill (skill replica-launch), MIT lida no arquivo LICENSE da raiz (Copyright 2026 Jake Schincariol)
  license: MIT
  source-file: skills/replica-launch/SKILL.md
  method: internalizado em PT; o script listing.py entrou funcional (MIT, stdlib); contraste rerotado para as skills de UI do arsenal (replica-design não foi incorporada)
---

# replica-launch

Esta skill lê o que o replica-entrepreneur e o replica-brand vão **gravar** — `replica/fixes.md`, `replica/brand.md`, `replica/brand.json` — e então deve **gravar** `replica/launch/` com `landing.md`, `pricing.md`, `listing.json` e `launch-plan.md`. A ferramenta `scripts/listing.py` confere a listagem; comece do `examples/listing-exemplo.json`.

## As regras

- **Sem prova falsa.** Nenhum depoimento, contagem de usuários, nota, logo de imprensa ou linha
  "confiado por" inventados. Uma seção de prova vazia é melhor que uma falsa. Beta users reais, com
  permissão, podem.
- **Avaliações do original não são depoimento.** As reviews são pesquisa, não vão na sua landing.
- **O nome do original fica fora** do seu nome, listagem, keywords e anúncios. Apple e Google rejeitam
  e isso convida um takedown.

## Como fazer (o detalhe mora nas referências)

Método completo em `references/metodo.md`; os limites e regras das lojas em `references/lojas.md`.

1. **Landing** (`landing.md`, seção a seção, depois construa no projeto): hero com o ângulo como
   headline; o problema (os dois temas de "ódio", parafraseados, não citados); como funciona (3 passos
   do core flow); features (cada uma ligada a uma correção de `fixes.md` — lidere com as correções, não
   com as features de paridade); preço; FAQ (as objeções reais); CTA final. Copy na voz da marca;
   confira contraste com `web-design-guidelines`/`dz23-ultimate-pro-max`.
2. **Preço** (`pricing.md`): o preço público do original + 2–3 alternativas numa tabela, com URL e
   **data lida** (preço muda); o que as reviews disseram de preço/billing com contagens; o modelo
   (free/trial, por assento/flat, mensal/anual); no máximo 3 tiers nomeados por para quem são; conserte
   as queixas de billing no produto (cancelar em 1 clique, e-mail de renovação claro); os produtos
   Stripe a criar (o usuário cria).
3. **Listagem:** **gere** `replica/launch/listing.json` (comece do exemplo) e rode `python scripts/listing.py replica/launch/listing.json`:
   ele confere os limites da App Store (name 30, subtitle 30, promo 170, keywords 100, desc 4000) e do
   Google Play (title 30, short 80, full 4000), conta caracteres como uma pessoa, sinaliza claims de
   ranking/preço em campos curtos, emoji, keywords desperdiçadas, e **qualquer nome de `avoid`** em
   qualquer lugar. Exit 1 em erro. A Guideline 4.1 da Apple (Copycats) rejeita app que só copia outro
   popular ou muda pouco o nome/UI — suas correções e sua marca são o que passa na revisão, então
   deixe-as visíveis nos screenshots e nas primeiras linhas.
4. **Plano** (`launch-plan.md`): waitlist/beta antes; analytics e error tracking vivos; onde os usuários
   infelizes do original falam (as threads da pesquisa); um post de Product Hunt/HN que lidera com a
   correção; os 10 primeiros usuários para falar à mão.

## A ferramenta (listing)

`scripts/listing.py` (stdlib): lint da listagem contra limites e regras anti-cópia; **exit 1 em erro**
(pode bloquear o envio). Exemplo completo em `examples/listing-exemplo.json`. Deixe de fora a loja para
a qual não vai publicar.

## Estados de evidência

| Estado | Critério |
|---|---|
| PASS | landing/pricing/listing/plano escritos, listing.py sem erro, prova real ou vazia (nunca falsa) |
| PARTIAL | peças escritas mas listing.py ainda com erro, ou preço sem a data lida |
| NOT_TESTED | listagem escrita sem rodar o listing.py |

## Veredito

Pronto quando: a landing lidera com as correções; o preço cita o do original com a data; a listagem
passa no `listing.py` sem erro e sem o nome do original; nenhuma prova é falsa; o plano existe. Caso
contrário, PARTIAL com o que falta. Próximo passo é o deploy (engenharia DZ23: `dz23-devops-cloud-deployer`).

## Roteamento com outras skills

- Ângulo e evidência vêm de `replica-entrepreneur`; nome/marca de `replica-brand` (roda antes desta).
- Contraste da landing: `web-design-guidelines` ou `dz23-ultimate-pro-max`. Deploy: `dz23-devops-cloud-deployer`.
