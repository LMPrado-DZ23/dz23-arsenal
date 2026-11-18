# Proveniência — acervo do prune-tests

`familias-de-poda.csv` tabula a **taxonomia do que podar** da própria skill, em
`references/taxonomia-do-que-podar.md` (ORIGINAL desta skill, não terceiro): três famílias de teste
sem valor (depende do passado, do nada, da implementação) mais o caso de borda do teste duplicado.
Cada linha traz o sinal, por que é podável e a ação, com `origem_arquivo` e `origem_secao`.

O consultor `scripts/consulta-prune.py` lê este CSV offline, casa por palavra inteira com mapa
fechado de sinônimos PT, e responde "sem correspondência" quando não há — nunca aproxima, e **nunca
remove teste**: só classifica. A prova `scripts/prova-consulta-prune.py` roda no gate
(`gate:autoteste-consulta-prune`).

Fonte: conteúdo próprio da skill (MIT). Não redistribui material de terceiro.
