---
name: replica-brand
version: 1.0.0
description: >
  Nomeia e rebranda um clone de app para ser o do próprio usuário: candidatos a nome com as checagens
  de trademark, domínio, loja e handle a rodar; uma paleta nova conferida para contraste; um brief de
  logo; um guia de voz; e uma ferramenta de sweep que acha qualquer coisa do original que sobrou no
  código. Use ao pedir "dê um nome ao meu app", "rebranda o clone", "faça meu", "escolha nome e cores",
  "brief de logo", "voz da marca", "checar sobras", ou depois de replica-entrepreneur. Roda sempre
  antes de replica-launch. Nada lança sob a identidade do original — esta skill é a linha entre "um
  clone" e "o seu app".
user-invocable: true
argument-hint: "[nome do original a evitar]"
metadata:
  origin: Jakeschincariol/replica-skill (skill replica-brand), MIT lida no arquivo LICENSE da raiz (Copyright 2026 Jake Schincariol)
  license: MIT
  source-file: skills/replica-brand/SKILL.md
  method: internalizado em PT; o script sweep.py entrou funcional (MIT, stdlib); contraste rerotado para as skills de UI do arsenal (replica-design não foi incorporada)
---

# replica-brand

Nada lança sob a identidade do original. Esta skill é a linha entre "um clone" e "o seu app".
Ferramenta: `python scripts/sweep.py . --config replica/brand.json` — acha sobras do original no código. Esta skill vai **gravar** `replica/brand.md` e `replica/brand.json`.

## Regras inegociáveis

- **Não confusamente similar ao original** em som, aparência ou sentido — nem a outro app da mesma
  categoria. É o teste que os escritórios de marca usam, então é o teste aqui. Sem trocadilho com o
  nome deles, sem gêmeo "-ly". Detalhe em `references/checagens-legais.md`.
- **Checagem rodada, não presumida.** Nunca escreva "disponível" para uma checagem que ninguém rodou:
  marque **a rodar**, ou o resultado com a data.
- **Logo não pode parecer o do original**: sem forma, par de cor ou truque de letra compartilhados.
- **O nome do original não entra** no seu nome, anúncio ou listagem (isso é do replica-launch também).
- Estas são checagens de triagem, **não liberação jurídica**: antes de gastar dinheiro no nome, um
  advogado de marcas faz a busca de verdade.

## Como fazer (o detalhe mora nas referências)

Método completo em `references/metodo.md`; as checagens legais em `references/checagens-legais.md`.

1. **O nome:** leia o ângulo que o replica-entrepreneur vai **gravar** em `replica/fixes.md`. Gere 20 candidatos em estilos variados
   (descritivo, composto, inventado, metáfora, verbo); corte para 5 pelos filtros (não confusamente
   similar; curto, soletrável de ouvido; diz algo do ângulo).
2. **As checagens, rodadas:** para cada um dos 5, uma linha por checagem (trademark US/EU/CA/global,
   domínio, App Store/Play, handles, web), marcada **a rodar** ou com o resultado e a data.
3. **Paleta:** uma paleta nova nos mesmos papéis de token, com a cor primária de uma **família
   diferente** da do original. Confira contraste com o acervo de acessibilidade do arsenal
   (`web-design-guidelines`, categoria `acessibilidade`) ou com a `dz23-ultimate-pro-max`: zero falha
   AA. Ponha as cores do original em `brand.json` para o sweep pegar as que sobraram.
4. **Brief de logo:** não um logo, um brief (a ideia em uma linha; tipo de marca; funciona a 16px e
   1024px; entregáveis SVG/ícone/favicon/social) que **não pode parecer o do original**.
5. **Voz:** três palavras de como soa (com o que cada uma **não** significa), cinco pares faz/evita, e
   reescreva as 10 strings mais vistas do clone nessa voz — nenhuma ecoando a frase do original.
6. **O sweep:** substitua todo nome, cor e string placeholder; então rode
   rode e **grave** o resultado: `python scripts/sweep.py . --config replica/brand.json`. Ele busca no conteúdo e nos nomes de
   arquivo o nome do original (inclusive dentro de identificadores como `CalendlyEmbed`), domínios e
   cores, pulando `node_modules`, build e a pasta `replica/`. Exit 1 = sobrou algo; conserte até dizer
   clean. Confira também a olho: favicon, títulos de página, templates de e-mail, imagem OG, ícone.

## A ferramenta (sweep)

`scripts/sweep.py` (stdlib): busca nome/domínio/cor do original no código e **sai com 1 se achar algo**
— pode bloquear um deploy. Com `--config`, lê o `replica/brand.json` que você vai **gravar** (`{avoid, domains, colors}`). Exemplo de
config em `examples/brand-exemplo.json`.

## Estados de evidência

| Estado | Critério |
|---|---|
| PASS | nome escolhido com checagens rodadas (ou marcadas a rodar), paleta AA, sweep clean |
| PARTIAL | nome e paleta prontos mas checagens não rodadas ou sweep ainda com sobras |
| NOT_TESTED | identidade escrita sem rodar o sweep (sobras não verificadas) |

## Veredito

Pronto quando: o nome passou os filtros e tem a linha de checagens (rodadas ou a rodar, nunca
"disponível" sem rodar); a paleta é de família diferente e sem falha AA; o brief de logo proíbe
semelhança com o original; a voz é própria; e o `sweep.py` diz **clean**. Caso contrário, PARTIAL.

## Roteamento com outras skills

- O ângulo vem de `replica-entrepreneur`. Contraste/acessibilidade da paleta: `web-design-guidelines`
  ou `dz23-ultimate-pro-max`. O lançamento (landing, preço, listing): `replica-launch` (roda depois).
