# Regras de clean-room

Esta skill refaz **o que um app faz e como o usuário se move por ele** — funcionalidade e padrões de
UX. Não refaz, não lê e não salva nada que o app **possui**: código, logo, textos, conteúdo, dados,
marca. Separar as duas coisas é o que torna o recon legítimo.

## O que PODE

- Ler páginas públicas em velocidade humana: marketing, docs/ajuda, preço, changelog, blog.
- Ler a listagem de loja (screenshots, pitch, avaliações) e vídeos públicos de walkthrough.
- Usar **a conta do próprio usuário** no app, dirigida pelo usuário, para ver estados reais.
- Ler **documentação de API pública** — o modelo de dados quase de graça.
- Guardar screenshots em `replica/screens/` como **referência de layout** (nunca entram no clone).

## O que NÃO PODE

- Entrar em conta que não é do usuário; pedir senha; passar de paywall/login por qualquer truque.
- Raspar: crawler, download em massa, loop automatizado. Leitura, não coleta.
- Ler ou salvar o **código-fonte**: bundles JS, binário decompilado, CSS minificado para copiar.
- Logar **requisições de rede** do app para copiar endpoints/payloads (isso é a API privada dele).
- Copiar conteúdo que o app possui: catálogo, textos de marketing, imagens, ícones, a marca.

## Termos de uso

Alguns produtos proíbem no contrato usar uma conta para construir concorrente. Antes de usar a conta
do usuário como fonte, verifique os termos; se proibirem, **diga ao usuário e trabalhe só com fontes
públicas**. Clonar funcionalidade é legítimo; violar um contrato que o usuário aceitou não é problema
de direito autoral, é problema contratual do usuário — e ele precisa saber.

## Por que isto importa

O pacote inteiro ("clonar qualquer app") só se sustenta porque refaz **features e fluxo**, clean-room.
No minuto em que o recon copia código, endpoints ou conteúdo, deixa de ser recon e vira cópia — com o
risco jurídico que a cópia carrega. A regra não é cautela excessiva: é o que mantém o clone defensável.
