# Método — do clone ao lançamento

Lê `replica/fixes.md`, `replica/brand.md`, `replica/brand.json`. **Grava** `replica/launch/`:
`landing.md`, `pricing.md`, `listing.json`, `launch-plan.md`.

## Passo 1 — landing page

`landing.md`, seção a seção, depois construída no projeto:

1. **Hero:** o ângulo como headline (o que você faz, para quem), uma linha abaixo, um botão. Screenshot
   do produto real.
2. **O problema:** os dois principais temas de "ódio", em palavras simples. **Parafraseie**, não cite
   avaliadores.
3. **Como funciona:** três passos, do core flow.
4. **Features:** cada uma ligada a uma correção de `fixes.md`. **Lidere com as correções**, não com as
   features de paridade — paridade é o preço de entrada.
5. **Preço:** a tabela do passo 2.
6. **FAQ:** as objeções reais, incluindo "dá para importar de ferramentas de {{categoria}}?" se você
   construiu um importador.
7. **CTA final.**

Copy na voz da marca. Confira contraste da página com `web-design-guidelines`/`dz23-ultimate-pro-max`.

## Passo 2 — preço

`pricing.md`:
- O preço público do original + 2–3 alternativas, numa tabela, com a URL e a **data lida** (preço muda).
- O que as reviews disseram de preço e billing, de `feedback.md`, com contagens.
- O modelo: free/trial, por assento ou flat, mensal e anual (anual costuma dar 2 meses grátis).
- No máximo 3 tiers, nomeados por para quem são.
- Conserte as queixas de billing no produto: cancelar em 1 clique, e-mail de renovação claro, sem salto
  de preço por assento surpresa.
- Os produtos e preços Stripe a criar (o usuário cria).

## Passo 3 — listagem de loja

Preencha `listing.json` (comece de `examples/listing-exemplo.json`), então rode
`python scripts/listing.py replica/launch/listing.json`. Ver `references/lojas.md` para os limites e a
regra de copycat da Apple. Prepare também: screenshots nos tamanhos exigidos no momento (confira na App
Store Connect/Play Console ao enviar — mudam), privacy labels e data safety, política de privacidade e
URLs de suporte, age rating, e notas de revisão com uma conta demo para o revisor usar.

## Passo 4 — plano de lançamento

`launch-plan.md`: waitlist/beta antes; analytics e error tracking vivos; onde os usuários infelizes do
original falam (as threads e comunidades da pesquisa); um post de Product Hunt/Hacker News que lidera
com a correção; os 10 primeiros usuários para falar à mão.
