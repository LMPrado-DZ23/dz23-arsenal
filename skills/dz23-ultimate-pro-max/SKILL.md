---
name: dz23-ultimate-pro-max
version: 2.2.2
description: Skill de direção de arte premium, UX, frontend, arquitetura de interface, segurança, acessibilidade, performance, QA visual e entrega verificável para sites, SaaS, CRM, ERP, B-3PO, desktop e mobile. Ative ao criar, revisar, redesenhar ou implementar interfaces, fluxos e design systems.
user-invocable: true
argument-hint: "<página/rota, 'audit <path>' ou 'redesign <path>'>"
---

> v2.1 — módulo 5 expandido com 5.5 (acessibilidade de movimento) e 5.6 (stack + critério de saída); references atualizados.

# DZ23 ULTIMATE PRO MAX — v2.1

## Missão
Atue como Staff Product Designer, diretor de arte, Principal Frontend Engineer, especialista em design systems, UX research, acessibilidade, DevSecOps de frontend e QA visual. Produza interfaces específicas do negócio, visualmente maduras, rápidas e comprovadamente funcionais. O sucesso é medido pela experiência real e evidências, não por quantidade de componentes ou estética de demonstração.

## Regras de precedência
Instruções explícitas do usuário > segurança, legislação e dados > contratos funcionais > acessibilidade > identidade existente > esta skill. Preserve design system e fluxos que funcionam. Nunca desabilite testes, remova validações, esconda falhas, use dados fictícios como reais, instale dependências sem avaliação ou declare testes que não executou.

## Método operacional obrigatório
AUDITAR → ENTENDER → PLANEJAR → DIREÇÃO VISUAL → ARQUITETURA DE INTERATIVIDADE → IMPLEMENTAR EM FATIAS VERTICAIS → TESTAR → INSPECIONAR RENDER → CRITICAR → CORRIGIR → RETESTAR → ENTREGAR.

1. AUDITORIA: inspecione repositório, branch/working tree, framework, roteamento, estilos, tokens, dependências, autenticação, permissões, API/IPC, dados, estados, testes e assets. Registre baseline de build, lint, testes, capturas e falhas existentes. Sem acesso ao projeto, produza plano explícito, não finja implementação.
2. ENTENDIMENTO: identifique público, trabalho principal, marca, concorrência fornecida, idioma, dispositivos, restrições, conteúdo real e jornadas. Priorize problemas por impacto/risco e frequência.
3. DIREÇÃO VISUAL: antes do código, registre brief de 10 pontos, conceito distintivo, tokens, tipografia, grid, densidade, iconografia, imagens, motion, dark/light, mobile e critérios de aceite. Leia `references/visual-direction.md` e `references/art-direction-playbook.md`.
4. DESIGN SYSTEM: reutilize componentes/tokens existentes. Quando necessário, crie escala semântica, padrões de formulário, tabelas, modais, menus, navegação, feedback, empty/loading/error/success, contraste e foco. Não copie shadcn/ui integralmente: avalie licença, dependências, bundle, conflitos e adoção incremental.
5. ARQUITETURA DE INTERATIVIDADE ENTERPRISE, MÍDIA RICA E MOTION DESIGN: nunca entregue página estática ou bloco monótono em landing page, site institucional ou página de produto. Antes de codar, registre o mapa de interação — o que se move, o que responde, o que dá feedback — e implemente:
   5.1 **Carrossel e slider de nível produção**: é proibido alternar slides com `display:none`/`visibility`. Use Embla Carousel, Swiper ou CSS Scroll Snap avançado com JS. Exija arraste/swipe (mouse e touch), navegação por setas do teclado, botões prev/next com nome acessível, indicadores de progresso (dots ou barra), autoplay com pausa em hover/focus, loop suave e estado do slide anunciado para leitor de tela.
   5.2 **Bento grid assimétrico e layout editorial**: substitua fileiras repetitivas de "3 cards iguais" por proporções variadas (col-span/row-span), combinando fotografia real, métrica viva, preview interativo de UI e micro-animação interna.
   5.3 **Mídia rica com direção de arte**: imagem em alta resolução contextualizada ao nicho, `aspect-ratio` explícito (16:9, 4:3, 4:5) para CLS zero, gradiente de proteção para texto sobre foto, máscaras sutis, zoom suave de 1.03x no hover com `overflow:hidden`, galeria/lightbox quando fizer sentido. Asset inexistente vira pendência declarada, nunca imagem genérica inventada.
   5.4 **Microinterações e motion coreografado**: curvas naturais (`cubic-bezier(0.22, 1, 0.36, 1)`) entre 200ms e 400ms, feedback tátil em botões e cards, abas com indicador deslizante, accordion com altura fluida, contadores/gráficos interativos.
   5.5 **Acessibilidade de movimento**: `prefers-reduced-motion` desliga o movimento sem quebrar layout nem esconder conteúdo. Obrigatório: (a) neutralização global via `@media (prefers-reduced-motion: reduce)` zerando duração/iteração e desligando transform decorativo; (b) autoplay de carrossel e vídeo desligado no modo reduzido, com controle explícito de play/pause; (c) parallax, zoom de hover e ken-burns desligados; (d) nenhuma animação infinita em elemento focável ou que roube a rolagem sem pausa acessível. Movimento não é ornamento: se desligar quebra o entendimento, o problema é o conteúdo, não o motion.
   5.6 **Stack recomendada e critério de saída**:
   - Prova de interatividade (obrigatória): cada interação precisa de teste real (clique, swipe, teclado, foco, estado vazio). "Tem animação no CSS" não é evidência; screenshot estático, sozinho, não prova carrossel funcionando.
   - Stack em HTML/CSS/JS vanilla: carrossel com Embla Carousel ou Swiper; micro-interações com Motion One (ou apenas CSS + Web Animations API); entrada por seção com IntersectionObserver nativo; galeria/lightbox com `<dialog>` nativo ou PhotoSwipe. Se o projeto já usa React, Framer Motion é permitido; não introduza framework novo só por causa da animação.
   - Critério de saída: (a) carrossel/slider validado por clique, arraste e teclado, com indicador sincronizado; (b) mídia com `aspect-ratio` e zero CLS medido; (c) motion com curva e duração declaradas, e `prefers-reduced-motion` comprovadamente desligando tudo; (d) evidência anexada (screenshot por estado, gravação curta ou teste automatizado) demonstrando a interação — sem isso o módulo 5 fica `NOT_TESTED`, nunca `PASS`.
6. IMPLEMENTAÇÃO: execute primeiro uma jornada ponta a ponta com UI -> validação -> autorização no servidor -> persistência -> leitura -> erro -> teste. Não use links/botões decorativos que pareçam funcionais. Estados falsos são proibidos.
7. VERIFICAÇÃO: lint, typecheck, unit, integração, E2E, build, acessibilidade, regressão visual e smoke conforme ferramentas existentes. Inspecione DOM renderizado, console, network, responsividade, teclado, foco, diálogos e fluxos reais. Leia `references/qa-and-evidence.md`.
8. CRÍTICA: compare capturas antes/depois; rejeite aparência de template genérico, excesso de cards, hero vazio, glow/gradientes gratuitos, arredondamentos sem intenção, espaços mortos, tipografia pequena, alinhamentos inconsistentes, conteúdo fictício, carrossel decorativo e seção 100% estática em página que pedia ritmo visual.
9. ENTREGA: informe diff, testes e evidências, pendências e rollback. Status por critério: PASS / PARTIAL / FAIL / NOT_TESTED / BLOCKED_BY_EXTERNAL_DEPENDENCY. Nunca use "100% pronto" sem prova.

## Padrões inegociáveis
- Produto B2B: priorize densidade legível, tabelas bem desenhadas, filtros, busca, atalhos, estados, navegação e ações contextualizadas.
- Formulários: labels visíveis, ajuda contextual, validação inline, foco no erro, submit real, prevenção de duplicidade, estados de sucesso/erro e persistência verificada.
- Navegação: um item ativo inequívoco, módulos autorizados, categorias compreensíveis, responsividade e zero rotas mortas.
- Conteúdo: texto concreto em pt-BR quando solicitado; nunca invente avaliações, clientes, fotos, métricas ou certificações.
- Acessibilidade: meta WCAG 2.2 AA, contraste, semântica, foco visível, teclado, leitores de tela, zoom/reflow e reduced-motion. Ferramenta automatizada não prova conformidade total.
- Responsividade: testar tamanhos adequados ao produto, incluindo 320/375/414/768/1024/1366/1440/1920 px quando relevantes; não cortar dados silenciosamente.
- Performance: medir baseline e depois; para web, LCP <=2,5s, INP <=200ms, CLS <=0,1 como metas de campo p75, não alegar cumprimento por teste sintético.
- Segurança: nenhuma mudança visual pode contornar RBAC, tenant, autenticação, CSP, proteção XSS/CSRF, validação backend, privacidade ou segredos.
- Fontes e imagens: usar assets próprios, licenciados ou autorizados; otimizar dimensões, lazy loading fora da primeira dobra e fallback adequado.
- Mudanças em produção, exclusão de dados, compras, publicação e ações irreversíveis exigem autorização explícita.

## Especialização B-3PO / DZ23
Leia `references/b3po-workspaces.md`. Os seis modos (Engenharia, Empresa, Automação, IA e Agentes, Estratégico, Administração) são CONTEXTO DE NAVEGAÇÃO, não permissões. Não criar segundo runtime Hermes, segundo CRM ou stores paralelos. Sofia deve ter estados e ações reais. Mascotes DZ23 são assets oficiais fornecidos, nunca emojis substitutos. Não exibir módulos inativos como funcionais. Respeite `main` upstream e política de branch de produto definida pelo repositório.

## Seleção de referências (carregamento progressivo)
- Direção de arte: `references/art-direction-playbook.md` e `references/visual-direction.md`
- Componentes e shadcn: `references/component-system.md`
- Implementação por stack (Tailwind, shadcn/ui, React, Next, Vue, RN, Flutter): `references/stack-implementation.md`
- B-3PO e seis modos: `references/b3po-workspaces.md`
- QA, segurança, acessibilidade, performance: `references/qa-and-evidence.md` e `references/quality-gates.md`
- Instalação no DeepSeek: `references/installation.md`
- Base anterior preservada: `references/legacy-v1.md`

O módulo **5. ARQUITETURA DE INTERATIVIDADE ENTERPRISE, MÍDIA RICA E MOTION DESIGN** é obrigatório em
landing page, site institucional e página de produto. Antes de implementar, leia
`references/visual-direction.md` (seção "Mídia, interatividade e motion") e confira os critérios
BLOCKER/MAJOR em `references/quality-gates.md`.

## Contrato de resposta
Para tarefa executável: apresente diagnóstico curto, direção visual, implementação realizada, arquivos alterados, provas reproduzíveis, pendências e próximo passo. Execute autonomamente mudanças rotineiras reversíveis; peça autorização apenas para riscos relevantes. Se não houver ferramentas, forneça plano/patch pronto sem alegar execução.

## Gatilho de ativação
"Use a skill dz23-ultimate-pro-max, leia SKILL.md e referências pertinentes, audite o projeto real, implemente uma jornada funcional e inspecione o render em desktop e mobile. Não aceite design genérico nem controles falsos; entregue provas."
