# Git como evidência

A poda de testes tem de ser **rastreável**: para cada teste removido ou reescrito, por quê. O registro
é o git, não uma nota solta no chat que some.

## Regra

Cada poda é um commit (ou um grupo coerente de commits) cuja mensagem diz:

- **Qual** teste saiu ou mudou.
- **Qual família** o justifica: passado, nada, implementação, duplicata — ou "reescrito contra
  comportamento".
- **Onde está a rede**, quando o comportamento importa: o teste que ainda guarda aquele comportamento.

## Por que commit, não relatório

- Um commit por razão deixa o `git log` responder "por que este teste sumiu?" meses depois.
- Se a poda foi longe demais, `git revert` do commit específico restaura só aquele teste, não tudo.
- A mensagem força a classificação: se você não consegue nomear a família, o teste talvez não fosse
  podável — e isso aparece na hora de escrever o commit, não depois do merge.

## Exemplo de mensagens

```
test: remove 'legacy exporter is gone' -- familia PASSADO (afirma codigo removido; voltar seria decisao)
test: reescreve 'adds item to cart' contra cart.total() -- era IMPLEMENTACAO (afirmava _items privado)
test: remove 'total includes tax' -- DUPLICATA (checkout.test.ts ja guarda o mesmo total)
refactor: remove _resetCacheForTests/_getCacheSize -- producao que so existia pro teste removido
```

## O que não fazer

- Um commit gigante "limpeza de testes" sem dizer o que saiu e por quê.
- Deletar produção junto sem mencionar que era código-só-para-teste.
- Declarar PASS num relatório sem o commit que o git pode auditar.
