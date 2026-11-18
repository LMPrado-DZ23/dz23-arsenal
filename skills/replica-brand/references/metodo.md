# Método — do clone à marca própria

## Passo 1 — o nome

Leia o ângulo de `replica/fixes.md` (do replica-entrepreneur). Gere **20 candidatos** em estilos:
descritivo (Booklink), composto (Slotwise), inventado (Calvo), metáfora (Harbor), verbo (Book). Corte
para **5** pelos filtros: não confusamente similar ao original nem a app da categoria; curto e
soletrável de ouvido; diz algo do ângulo (ou ao menos não briga com ele).

## Passo 2 — as checagens, rodadas

Para cada um dos 5, a tabela de checagens (ver `checagens-legais.md`). Cada checagem marcada **a
rodar** ou com o resultado e a **data**. Nunca "disponível" sem rodar.

## Passo 3 — paleta

Uma paleta nova nos mesmos papéis de token que o design usa. A cor primária de uma **família diferente**
da do original (se a deles é azul, a sua não é um azul vizinho). Confira contraste com o acervo de
acessibilidade (a skill `web-design-guidelines`, consultando a categoria acessibilidade) ou
com a `dz23-ultimate-pro-max`: **zero falha AA**. Adicione as cores de marca do original a `brand.json`
para o sweep pegar qualquer uma que sobreviva.

## Passo 4 — brief de logo

Não um logo, um **brief** para quem o fizer (o usuário, um designer, um modelo de imagem):
- a ideia em uma linha, ligada ao nome e ao ângulo;
- tipo de marca: wordmark, símbolo + wordmark, ou monograma;
- funciona a 16px (favicon) e como ícone 1024px;
- entregáveis: SVG, ícone 1024×1024 sem transparência (iOS), set de favicon, imagem social 1200×630;
- **não pode parecer o do original**: sem forma, par de cor ou truque de letra compartilhados. Ponha o
  logo do original ao lado dos rascunhos e confira.

## Passo 5 — voz

Três palavras de como soa, com o que cada uma **não** significa ("direto, não ríspido"). Cinco pares
faz/evita. Reescreva as 10 strings mais vistas do clone (cadastro, estados vazios, o botão principal, a
confirmação, o erro) nessa voz — nenhuma ecoando a frase do original.

## Passo 6 — o sweep

Substitua todo nome, cor e string placeholder. Então **rode**
`python scripts/sweep.py . --config replica/brand.json`. Exit 1 = sobrou algo; conserte até dizer
**clean**. Confira também a olho: favicon, títulos de página, templates de e-mail, imagem OG, ícone do
app. O sweep também entra no preflight do replica-deploy, bloqueando o lançamento com sobras.
