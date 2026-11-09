# Direção de arte e crítica visual

## Brief de 10 pontos
1. Segmento, público e principal tarefa.
2. Marca atual e o que não pode mudar.
3. Três adjetivos visuais e três antipadrões específicos.
4. Uma ideia visual distintiva, em frase concreta.
5. Paleta, contraste e tokens semânticos.
6. Tipografia (display/texto/mono opcional), escala, largura de leitura.
7. Grid, densidade, espaços e ritmo das seções.
8. Fotografia/ilustração reais ou licenciadas, tratamento e ícones.
9. Navegação, responsividade, estados e motion.
10. Critérios de aceite e restrições de conteúdo.

## Mídia, interatividade e motion (obrigatório em landing e site institucional)

Página estática não é entrega completa quando o produto pede ritmo. O brief precisa nomear, antes do
código:

1. **Mapa de interação**: o que se move, o que responde ao cursor/toque, o que dá feedback de ação.
2. **Carrossel/slider**: qual mecanismo (Embla, Swiper, Scroll Snap + JS), como se arrasta (mouse e
   toque), como se navega (setas do teclado, prev/next), como se indica posição (dots ou barra) e como
   o autoplay pausa em hover/focus. `display:none` trocando slide é proibido.
3. **Composição editorial**: bento grid com proporções variadas (col-span/row-span), não fileira de
   cards idênticos. Onde entra foto real, métrica viva e preview de UI.
4. **Direção de imagem**: `aspect-ratio` fixo por slot (16:9, 4:3, 4:5), gradiente de proteção para
   texto sobre foto, máscara, zoom 1.03x no hover, galeria/lightbox quando aplicável.
5. **Coreografia de movimento**: curva (ex.: `cubic-bezier(0.22, 1, 0.36, 1)`), duração 200–400ms,
   entrada por seção, indicador deslizante de tabs, altura fluida de accordion, contador/gráfico
   interativo — e desligamento completo em `prefers-reduced-motion`.

### 6. Direção de arte para mídia rica

**Fotografia**
- Resolução de pelo menos 2x o slot renderizado; nunca esticar imagem pequena.
- Imagem contextualizada ao nicho (barbearia mostra cadeira, navalha, ambiente real — não stock genérico).
- `aspect-ratio` declarado por slot (16:9 hero, 4:3 conteúdo, 4:5 retrato) **e** `width`/`height` no `<img>`.
- Texto sobre foto exige scrim (gradiente de proteção) testado com o pior caso da imagem.
- Zoom de hover entre 1.03x e 1.05x, com `overflow:hidden` no contêiner; nunca deslocar o layout.
- Galeria/lightbox com `<dialog>` nativo ou PhotoSwipe: foco preso, Esc fecha, retorno de foco.
- Hero com `fetchpriority="high"` e sem `loading="lazy"`; resto da página pode ser lazy.

**Motion tokens**
- Curvas: `cubic-bezier(0.22, 1, 0.36, 1)` (entrada) e `cubic-bezier(0.4, 0, 0.2, 1)` (movimento).
- Durações: 200ms (feedback), 300ms (transição), 400ms (entrada de seção). Acima disso só com justificativa.
- Proibido `transition: all` — declare a propriedade. Proibido animar `width`/`height`/`top`/`left`; use
  `transform` e `opacity` (compostas, sem reflow).
- Entrada por seção com `IntersectionObserver` nativo, uma vez por elemento, sem loop infinito.

**Bento grid**
- Grade de 12 colunas; células com `col-span`/`row-span` variados.
- Mínimo 3 categorias de célula por grade (ex.: mídia, métrica, ação/preview) — não 3 do mesmo tipo.
- Colapso mobile: 12 → 6 → 1 coluna, nessa ordem, com gap constante (4/8/12/16/24).

### 7. Checklist de direção visual (v2.1)

- [ ] Carrossel funcional por clique, swipe e teclado (não só visual).
- [ ] Bento grid com ≥3 categorias de célula, nenhuma fileira de 3 cards iguais.
- [ ] `aspect-ratio` (ou `width`/`height`) em toda imagem, zero CLS.
- [ ] Scrim legível sob qualquer texto sobre foto.
- [ ] Zoom de hover ≤1.05x, sem deslocar layout.
- [ ] Tabs com indicador animado ou accordion com altura fluida.
- [ ] Easings conformes; nenhum `linear`/`ease` em microinteração direta.
- [ ] `prefers-reduced-motion` neutralizando tudo (`@media` global).
- [ ] Zero `display:none` para trocar slide.
- [ ] Zero fileira de N cards idênticos ocupando seção inteira.

**Anti-padrões (reprovam a direção visual):**
- Carrossel trocando slide por `display:none`.
- Fileira de N cards idênticos ocupando uma seção inteira.
- Imagem sem `aspect-ratio` ou `width`/`height` (CLS).
- `prefers-reduced-motion` ignorado em qualquer animação da entrega.
- `outline:none` sem substituto visível de foco.

## Quando houver referência visual
Descrever com evidência: hierarquia acima da dobra, proporção imagem/texto, alinhamentos, número de colunas, pesos tipográficos, CTA primário, tratamento de imagens, espaçamento, comportamento mobile. Separar **princípios reutilizáveis** de **identidade/ativos protegidos**. Não clonar sem autorização.

## Revisão visual pós-render
1. A primeira dobra explica claramente o produto e a próxima ação?
2. A composição tem ritmo e contraste, ou todas as seções parecem iguais?
3. Os elementos parecem da mesma marca sem recorrer a efeitos artificiais?
4. Há conteúdo falso, genérico ou imagem desconectada?
5. Tipografia, linhas, bordas e espaçamento estão precisos?
6. O mobile foi recomposto ou apenas espremido?
7. Foco, erro, loading, vazio e sucesso são compreensíveis?
8. Existe algo que parece template de IA? Corrigir e comparar nova captura.
9. O carrossel foi testado com clique **e** swipe **e** teclado — ou só "aparece bonito na foto"?
10. A página tem ao menos um momento de ritmo (mídia rica, bento assimétrico, microinteração) com
    propósito, ou é uma sequência de blocos iguais?
