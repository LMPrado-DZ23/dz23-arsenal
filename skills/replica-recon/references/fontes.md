# Fontes de recon (em ordem de valor)

Toda linha da tabela de fontes leva uma URL. Sem URL, não é fonte — é memória, e memória não é
evidência. Em ordem de quanto cada uma rende:

| Fonte | O que dá |
|---|---|
| Central de ajuda / docs | a lista de features mais completa que existe, e as configurações |
| Página de preço | quais features importam (o produto as separa por plano) |
| Changelog | o que foi adicionado recentemente, o que o time acha importante |
| Listagem de loja (App Store / Play) | screenshots de cada tela-chave, o pitch, as avaliações |
| Vídeos públicos de walkthrough | fluxos reais, clique a clique |
| Site de marketing | posicionamento, o core loop nas palavras deles |
| A conta do próprio usuário | o produto real, todos os estados, dirigido pelo usuário |
| Docs de API pública | o modelo de dados quase de graça |

## Como usar cada uma

- **Ajuda/docs** primeiro: é onde a feature list vive por extenso, com nomes e configurações.
- **Preço** diz prioridade: o que é pago é o que importa — vira `must`/`should` na matriz.
- **Loja** dá o inventário visual de telas sem precisar entrar no app.
- **Conta do usuário** é a fonte dos **estados** (vazio, erro, permissão) que nenhuma página pública
  mostra — mas só a conta do usuário, dirigida por ele, respeitando os termos (ver `clean-room.md`).
- **API pública** colapsa o passo 6: os endpoints documentados revelam entidades e campos reais.

## O que NÃO é fonte

Código-fonte, bundles JS, requisições de rede capturadas, API privada, conteúdo que o app possui.
Isso não entra na tabela de fontes — ver `clean-room.md`. Uma linha de fonte que você não poderia
mostrar ao dono do app sem constrangimento provavelmente cruzou a linha.
