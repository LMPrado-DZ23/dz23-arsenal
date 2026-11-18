# Método — podar testes em um passe

## Passo 0 — baseline

Rode a suíte e registre: quantos testes, quantos verdes, tempo. Um teste que já falha não é candidato
a poda até você saber por quê (pode ser a regressão que ele deveria pegar).

## Passo 1 — mapeie de que cada teste depende (sem apagar)

Para cada teste, responda uma pergunta: *que mudança no código de produção o faz falhar?*

- Se a resposta é "uma regressão do comportamento X" → **mantenha** (é o que você quer).
- Se é "nenhuma" → família **nada**.
- Se é "só mudar a forma interna, sem mudar o que o chamador vê" → família **implementação**.
- Se é "nada, porque ele afirma que algo foi removido" → família **passado**.
- Se outro teste já falha na mesma regressão → **duplicata**.

Escreva a lista: teste → família → ação (deletar / reescrever / manter). É o artefato do passo, e
precede qualquer deleção. Um diff sem essa lista é poda por gosto.

## Passo 2 — pode

- Delete todo teste marcado `deletar`.
- Reescreva os `reescrever` contra o comportamento observável (valor literal, API pública), não contra
  a implementação.
- **Delete o código de produção que só existia para os testes removidos** — helpers `_resetForTests`,
  getters de estado interno, flags de teste. Se nada de produção usa, sai junto.

## Passo 3 — verifique

Rode a suíte. Deve ficar verde com a **mesma cobertura de comportamento** de antes — você removeu
testes que não guardavam comportamento, não comportamento guardado. Se a cobertura de um comportamento
real caiu, você deletou demais: restaure ou reescreva. Ver `verification.md`.

## Quando parar

Pare quando todo teste restante responde "uma regressão do comportamento X" à pergunta do passo 1.
Quantos testes suspeitos restam é a medida de quão perto você chegou.
