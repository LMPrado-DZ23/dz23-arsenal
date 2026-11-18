# Fontes de avaliação e seus termos

Mire 100+ avaliações em pelo menos três fontes, recentes primeiro.

| Fonte | Onde |
|---|---|
| App Store | a página do app, Ratings and Reviews, See All; ou o feed RSS de avaliações da Apple |
| Google Play | a listagem, See all reviews, ordenar por newest |
| G2, Capterra, Trustpilot | as páginas de review do produto, filtrar também para 1–3 estrelas |
| Reddit | buscar "X alternative", "switched from X", "X sucks", "X vs" |
| Hacker News | a API Algolia ou busca do site, as mesmas queries |
| Board do próprio original | roadmap/feature-request público (Canny e similares) e as contagens de voto |
| Changelog dele | o que já lançaram, para não "consertar" o que já está consertado |

## Ler, não raspar — e os termos

- **Leia como pessoa**, no navegador, e copie as linhas para o CSV. Sem biblioteca de scraping contra
  loja ou site de review cujos **termos proíbem**.
- **Feeds/APIs públicas oficiais, dentro dos termos**, podem:
  - RSS de avaliações da Apple: `https://itunes.apple.com/us/rss/customerreviews/id=<APP_ID>/sortBy=mostRecent/json`
  - API Algolia do Hacker News: `hn.algolia.com/api/v1/search?query=...`
  - API oficial do Reddit, sob os termos dela.
- Nesta máquina há `scrapling` instalado, mas o uso aqui é **leitura dentro dos termos**, não coleta em
  massa. Se uma fonte bloqueia ou proíbe, **diga e siga** — uma amostra menor honesta vale mais que uma
  maior que quebra termos.

## A lei que não se negocia

- **Nunca review falsa** (a favor sua ou contra o original): ilegal nos EUA (regra da FTC de 2024) e
  em muitos lugares.
- **Nunca fabricar** número, citação ou fonte. Se há 14 avaliações, são 14.
- **Avaliadores são pesquisa, não depoimento.** As palavras deles não vão para a sua landing page.
- **Nome do original fica fora** do seu nome/anúncio/listagem. Comparação factual pública é questão de
  advogado local.
