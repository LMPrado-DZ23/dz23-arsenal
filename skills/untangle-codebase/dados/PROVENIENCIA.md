# Proveniência — acervo do untangle-codebase

`familias-de-defeito.csv` tabula a **taxonomia dos quatro defeitos estruturais** da própria skill,
em `references/defect-taxonomy.md` (ORIGINAL desta skill, não terceiro). Uma linha por família, com
sinal no código, princípio violado e correção típica. Cada linha cita `origem_arquivo` e
`origem_secao`.

O consultor `scripts/consulta-untangle.py` lê este CSV (offline, sem rede), casa por palavra inteira
com mapa fechado de sinônimos PT, e responde "sem correspondência" quando não há — nunca aproxima. A
prova `scripts/prova-consulta-untangle.py` roda no gate (`gate:autoteste-consulta-untangle`) com
casos positivos, controles negativos e busca.

Fonte: conteúdo próprio da skill (MIT). Não redistribui material de terceiro.
