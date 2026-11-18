# Dataset de design verificado (acervo externo)

Origem, licença e motivo da incorporação: `dados-design/VENDOR.md`. Este arquivo é o **índice de uso** —
ele existe para que a skill saiba o que perguntar ao acervo em vez de improvisar estilo.

## O que é

Base estruturada incorporada do pacote `ui-ux-pro-max` (licença ISC), copiada sem modificação para
`dados-design/ui-ux-pro-max-data/`. Cada linha tem número de registro; cada recomendação sua deve citar o
número, pela mesma regra de evidência do resto do arsenal.

| Arquivo | Registros | Para que serve |
|---|---|---|
| `styles.csv` | 89 categorias | Palavras-chave, cores primárias/secundárias, efeitos, onde funciona, custo de performance e **risco de acessibilidade por estilo** |
| `ui-reasoning.csv` | 192 perfis | Dado o tipo de produto: padrão recomendado, prioridade de estilo, humor de cor e de tipografia, efeitos-chave e o *anti-padrão* a evitar |
| `products.csv` | 192 | Mesma base sob o ângulo de produto |
| `colors.csv` | 192 paletas | Paleta completa por tipo de produto (primária, sobre-primária, secundária, superfícies, texto) |
| `ux-guidelines.csv` | 120 diretrizes | Problema, plataforma, **FAZER / EVITAR** e severidade — inclui código de exemplo bom e ruim |
| `google-fonts.csv` + `google-font-licenses.json` | 1.934 famílias | Catálogo de fonte **com a licença de cada uma** |
| `icons.csv`, `charts.csv`, `motion.csv`, `landing.csv`, `app-interface.csv`, `react-performance.csv`, `stacks/*.csv` | 17–57 cada | Ícones, tipos de gráfico, presets de motion, padrões de landing page, desempenho React, orientações por stack |

## Como consultar

```bash
python scripts/consulta-design.py listar
python scripts/consulta-design.py estilo "glassmorphism"
python scripts/consulta-design.py produto fintech
python scripts/consulta-design.py ux formulario --severidade alta
python scripts/consulta-design.py cores saude
python scripts/consulta-design.py fontes --pesquisa inter
```

Português funciona: `estilo vidro`, `produto finanças`, `ux acessibilidade`. O vocabulário dos dados
é inglês e a ponte é um mapa fechado (`SINONIMOS` no script) — não tradução genérica. Se a palavra
não está no mapa, a ferramenta responde **"sem correspondência"** em vez de aproximar. Isso é
deliberado: uma consulta que devolve a linha errada engana mais que uma ausência declarada, porque o
agente passa a confiar no resultado.

## Onde usar no método

- **Passo 3 (direção visual)** — antes de escrever o brief de 10 pontos, rode `produto <tipo>` e
  `estilo <candidato>`. Use `Style_Priority` e `Anti_Pattern` como hipótese inicial, não como
  veredito: a decisão continua sendo registrada no brief com justificativa do projeto.
- **Tokens de cor** — `cores <produto>` entrega paleta de partida; ainda assim valide contraste
  (WCAG 4.5:1) por conta própria. O dataset sugere, não certifica.
- **Tipografia** — escolha a família e confirme a licença **no catálogo** antes de embutir no build.
  OFL permite redistribuição; nem toda família é OFL, e essa é exatamente a checagem que o arquivo
  existe para tornar barata.
- **Acessibilidade por estilo** — `styles.csv` traz coluna `Accessibility` com risco e pré-requisitos
  (ex.: glassmorphism exige contraste de texto 4.5, foco visível e `reduced-motion`). Copie isso para
  os critérios de aceite do passo 3, não descubra depois no QA.
- **Revisão** — em `ux <área> --severidade alta` você obtém a lista do que costuma falhar naquela
  área, com o EVITAR explícito.

## Limite honesto

É conhecimento agregado de terceiros, verificado em 2026-08/11 conforme `data-provenance.json`
(laço com W3C e GoogleChrome). Não substitui testar no seu usuário real, e a política de frescor do
próprio pacote marca revisão em 90 dias. Trate como ponto de partida informado — nunca como prova de
que ficou bom. Uma interface aprovada por dataset e reprovada por pessoa continua reprovada.
