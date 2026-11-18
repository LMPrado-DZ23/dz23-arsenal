# Método completo de desembaraço (5 passos)

Este arquivo é o corpo operacional da skill. O `SKILL.md` resume; aqui está o detalhe que um agente segue
durante a execução. Adaptado do método Caldo (`untangle-codebase`, MIT) ao rito deste arsenal.

## Passo 1 — Pergunte o escopo extra

Além de desembaraçar, há duas coisas opcionais. Liste-as para o usuário **com estas descrições exatas** e
faça só o que ele escolher:

| Extra | O que faz |
|---|---|
| **Comentários** | Remove comentários que apenas repetem o código. |
| **Testes** | Remove testes que não pegariam um bug real, e conserta os que falham sem um. |

Se o usuário não escolher nenhum, faça só a reorganização estrutural. Não infira consentimento.

## Passo 2 — Catalogue todos os problemas (não mude nada)

Percorra o codebase fazendo uma pergunta: **estas peças deveriam mudar juntas?** Registre cada lugar onde o
código erra a resposta, no formato de `templates/decision-log.md`. Só há três formas de errar, mais os casos
especiais.

### Elos ocultos (mudam juntos, mas o código não mostra)

- Cópias de lógica ou valores: muda uma, as outras têm que mudar, mas nada diz isso.
- Módulo que lê global/arquivo escrito por outro: muda aquele módulo e esse quebra, sem nada mostrar
  (*self-contained code*).
- Feature espalhada por pastas por camada, ou código relacionado em pastas diferentes: uma mudança precisa de
  todas, mas o layout esconde isso (*domain-driven / colocation*).
- Ordem de chamada ou convenção que chamador tem que saber de cor: muda e chamadores quebram sem aviso
  (*explicit over implicit*).

### Elos desnecessários (amarrados, mas mudam por razões diferentes)

- Chamadores que dependem de internos: os internos mudam por conta própria e os chamadores quebram mesmo
  assim (*encapsulation*).
- Código estável importando algo mais volátil: o estável muda sempre que o volátil muda (*dependency direction*).
- Função geral com parâmetro que só um fluxo entende: a função muda sempre que aquele fluxo muda (*caller vocabulary*).
- Módulo raso: sua interface muda sempre que os internos mudam, então os chamadores mudam junto (*deep modules*).

### Sobra (sem razão própria para mudar)

- Wrappers pass-through: só mudam quando o embrulhado muda.
- Pontos de extensão/config para coisas que nunca variam (*speculative generality*).
- Código morto: ninguém usa, então ninguém vai precisar mudar.

### Casos especiais (código para uma situação, não derivado do sistema)

Cada um é um requisito que o design não previu — use-os para descobrir o que o sistema precisa ser:

- um `if` para um valor específico;
- um parâmetro para um chamador específico;
- uma exceção engolida;
- um retry/sleep;
- um teste desabilitado.

## Passo 3 — Redesenhe dos primeiros princípios

Resolva como se o sistema soubesse dos requisitos atuais desde o início. Procure **a única correção atrás de
vários problemas**, que muitas vezes não se parece com eles. Não conserte casos especiais um por um.

Pergunte o mesmo de toda correção: peças que mudam juntas terminam juntas; peças que não mudam juntas não
são amarradas; tudo depende do que muda menos. Escreva cada correção acima dos problemas que resolve
(`templates/decision-log.md`).

## Passo 4 — Aplique tudo da lista

Remova os casos especiais que o redesenho torna desnecessários; mantenha os que o sistema ainda precisa. Não
saia caçando bugs à parte — uma correção estrutural pode resolver alguns no caminho, e isso é aceitável.

**Se escolheu Comentários:**
- Comentário que repete a implementação (`// ordena antes para o binary search funcionar`) só muda quando ela
  muda — sem razão própria. Remova, mesmo formulado como "porquê".
- Comentário sobre algo fora do código (`// o proxy derruba websockets, então fazemos polling`) muda quando
  aquilo muda, e o código não mostra. Mantenha.
- Comentário explicando workaround (`// espera 100ms porque o cache ainda não está pronto`) só muda quando o
  problema por trás do workaround muda. Vai embora quando o redesenho remove o problema.

**Se escolheu Testes — faça por último**, porque testes são a rede de regressão. Um teste deve falhar numa
regressão, e só então:
- Teste que repete a implementação só muda quando ela muda — confere a mesma interpretação contra si mesma.
  Remova.
- Teste preso a internos quebra quando o código muda mas o comportamento não — muda pela razão errada.
  Reescreva para depender de comportamento, que muda menos.
- Teste que não pode falhar passa independente do código — não checa nada. Remova.

## Passo 5 — Confira e repita até terminar

Tenha subagentes procurando casos especiais, elos ocultos, elos desnecessários e sobra. **Não pare enquanto
houver algo que valha corrigir.**

Critérios de "terminado":
- O mínimo possível de casos especiais restou. Quantos sobram é a melhor medida de proximidade.
- Uma mudança típica cai num lugar só.
- Todo import é razoável; nada importa algo mais volátil que si.
- Subagentes não reportam mais nada que valha corrigir.
- Comportamento intencional igual ao do início, exceto bugs que o refactor corrigiu. Prove no fim
  (`references/verification.md`).

## Dicas operacionais

- **Comece por um esqueleto:** apague corpos de função por script, para o codebase inteiro caber em contexto.
- **Resuma com subagentes:** peça resumos de partes, para raciocinar sobre tudo de uma vez.
- **Confira o grafo de dependências com frequência:** gere um script mostrando quem importa quem, e rode de
  novo a cada avanço.
- **Entre onde a alavanca é maior:** comece olhando lá.
- **Mantenha registro de decisão:** compactação vira menos problema.
- **Use Git como evidência:** ver `references/git-as-evidence.md`.
