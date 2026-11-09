# Quality gates — evidência, não promessa

| Gate | PASS quando | Evidência mínima |
|---|---|---|
| Identidade | Conceito e escolhas visuais refletem negócio real | Direção de arte + screenshot |
| Integridade | Fluxos, auth, APIs, permissões e dados preservados | Testes relevantes e diff |
| Conteúdo | Sem dados, depoimentos ou claims inventados | Revisão de conteúdo/assets |
| Interação | Controles, formulários e menus realmente funcionam | Testes de fluxo/E2E ou inspeção |
| Responsividade | Sem sobreposição/overflow indevido nos viewports relevantes | Capturas por viewport |
| Acessibilidade | Sem problemas críticos conhecidos, teclado/contraste revisados | axe + inspeção manual |
| Performance | Sem regressão injustificada, metas documentadas | Medidas comparáveis antes/depois |
| Qualidade de código | Lint/typecheck/build/testes pertinentes aprovados | Logs/comandos |
| Revisão visual | Identidade e composição revisadas após renderização | Screenshot + registro de correções |
| Interatividade | Carrossel, tabs, accordion e mídia respondem a clique, swipe e teclado | Teste real (Playwright/manual) + captura por estado |

**Estados:** PASS = verificado; PARTIAL = parcialmente verificado; FAIL = falhou; NOT_TESTED = não executado; BLOCKED_BY_EXTERNAL_DEPENDENCY = indisponível por dependência externa identificada. Não converta NOT_TESTED em PASS. Não confunda meta com medição.

## Severidade — o que reprova a entrega

**BLOCKER (não entrega, corrige antes):**
- **Carrossel quebrado**: sem suporte a swipe/arraste ou clique, controles decorativos que não mudam o
  slide, indicador que não reflete a posição, autoplay que não pausa em hover/focus, ou navegação por
  teclado ausente.
- Slide trocado por `display:none`/`visibility:hidden` em vez de mecanismo real de carrossel.
- Imagem sem `aspect-ratio`/dimensões causando CLS visível, ou texto sobre foto sem proteção de contraste.
- Movimento que ignora `prefers-reduced-motion` em qualquer animação da entrega, não só quando esconde conteúdo.
- Botão/link/aba decorativo que promete ação e não executa.

**MAJOR (entrega só com ressalva registrada):**
- **Layout 100% estático** em landing page/site institucional: sequência de blocos iguais, sem mídia rica,
  sem bento assimétrico e sem microinteração onde o produto pedia ritmo visual.
- Carrossel funcional, mas sem loop suave, sem indicador de progresso ou sem ponto de pausa na autoplay.
- Mídia genérica (banco de imagem sem contexto do nicho) usada como se fosse fotografia do produto.
- Tabs sem indicador deslizante ou accordion que "salta" em vez de animar altura.
- Fileira de N cards idênticos ocupando seção inteira sem variação de span ou tipo de conteúdo.
- Carrossel sem `aria-label`/nome acessível nos controles (o `display:none` já é BLOCKER acima).
- Easing `linear` ou `ease` em microinterações diretas.

**MINOR (refinamento, registra e segue):**
- Parallax leve que não desliga em `prefers-reduced-motion`.
- Vídeo mudo em loop no lugar de foto estática, sem controle de pausa.
- Contador animado sobre métrica que já existe na página.

## Matriz de teste por componente
- Botão/link: destino/ação, hover, foco, disabled, loading e feedback conforme aplicável.
- Formulário: labels, required, erro inline, submit, sucesso, teclado, envio duplicado.
- Menu: item ativo, navegação, mobile, Esc, foco, acessibilidade.
- Tabela/lista: vazio, loading, erro, dados reais, paginação/filtros se oferecidos, mobile.
- Modal: foco inicial, contenção, Esc, retorno do foco, fechamento seguro.
- Imagem: licença/origem, alt, proporção, carregamento, resolução, `aspect-ratio`.
- Carrossel: clique prev/next, swipe/toque, setas do teclado, indicador sincronizado, autoplay com pausa,
  loop, e estado anunciado para leitor de tela.
- Tabs: teclado (setas/Home/End), indicador deslizante, painel correto visível, foco preservado.
- Accordion: abrir/fechar por teclado, altura animada, `aria-expanded` coerente.
- Galeria/lightbox: abrir, fechar (Esc), navegar, retorno de foco, alt de cada imagem.

## Checklist final
- [ ] Baseline registrado e regressões separadas.
- [ ] Direção visual contextual documentada.
- [ ] Sem claims inventados, lorem ipsum ou controles falsos.
- [ ] Testes de código executados conforme projeto.
- [ ] Fluxo principal inspecionado em navegador.
- [ ] Mobile/tablet/desktop revisados.
- [ ] Contraste, teclado, foco e zoom avaliados.
- [ ] Console/rede e estados de erro verificados.
- [ ] Screenshot final comparado com referência e corrigido.
- [ ] Carrossel/slider testado por clique, swipe e teclado (não só por screenshot).
- [ ] Mídia com `aspect-ratio`, alt e proteção de contraste sobre foto.
- [ ] Motion com curva/duração definidas e desligado em `prefers-reduced-motion`.
- [ ] Riscos, pendências e dependências externas declarados.
