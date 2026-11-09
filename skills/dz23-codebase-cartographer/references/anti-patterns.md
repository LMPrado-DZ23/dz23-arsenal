# Anti-padrões de mapeamento

Cada item: **sintoma** → **por que dói** → **correção**.

## Escopo e processo
1. **Mapear tudo sem pergunta** → inventário inútil, tempo queimado → comece pela pergunta que o mapa responde.
2. **"Li todo o repositório"** sem amostragem → falsa autoridade → declare o critério e o que ficou de fora.
3. **Mapa sem commit/data** → não se sabe se vale → cabeçalho obrigatório.
4. **Mapa escrito uma vez e nunca revisto** → apodrece em semanas → revalidar por diff de arquivos.
5. **Mapear e já refatorar** → mistura leitura com mudança e quebra a confiança → esta skill só lê.

## Evidência
6. **Afirmação sem ponteiro** ("o serviço faz X") → boato com aparência de fato → `arquivo:linha`.
7. **Inferência apresentada como leitura** → decisão errada com base falsa → marcar `INFERIDO`.
8. **Copiar o README** e chamar de mapa → o README mente com frequência → verificar manifest contra README.
9. **"Não há teste"** sem procurar em todas as convenções → falso negativo → checar `tests/`, `*.test.*`, config do runner, CI.
10. **"Código morto"** por ausência de import → apagar o que era chamado por router dinâmico → 3 checagens obrigatórias.
11. **Ciclo afirmado sem cadeia** → alarme falso → cadeia de 3 arquivos com linha.

## Estrutura
12. **Descrever a pasta como arquitetura** → a pasta é intenção, o import é realidade → usar o grafo.
13. **Listar todos os arquivos** → ruído que ninguém lê → hubs, fronteiras e o caminho da mudança.
14. **Ignorar o monorepo** → descrever o repo como app único → mapear workspaces e dependências entre pacotes.
15. **Não olhar o CI** → o CI é a constituição do repo (o que roda, com que versão) → ler os workflows.
16. **Ignorar Dockerfile/compose** → não se sabe como roda de verdade → entry point real está lá.

## Dados
17. **Não dizer onde mora a verdade** → cinco cópias e ninguém sabe qual vale → tabela fonte × cópia.
18. **Assumir que o schema do ORM é o real** → divergência silenciosa → marcar não verificado sem banco.
19. **Ignorar quem escreve** → dois escritores, sem transação, corrida → tabela escritor/leitor.
20. **Não olhar migração** → mudou o modelo e ninguém sabe a ordem → listar e checar reversibilidade.

## Contexto para agente
21. **Brief que despeja código** → estoura o orçamento e não é lido → ponteiros.
22. **Brief sem "não tocar"** → o próximo agente mexe no núcleo de dinheiro → seção obrigatória.
23. **Brief sem comando de validação** → não se sabe se a mudança funcionou → comando + caminho manual.
24. **Brief sem lacunas** → quem usa acha que está completo → declarar o não verificado.
25. **Brief com adjetivo** ("código confuso") → não acionável → número, arquivo e linha.
26. **Brief gigante por módulo sem raiz** → fragmentos desconexos → brief raiz + briefs filhos.

## Risco
27. **Ombrear a zona de risco** → medo genérico que não ajuda → classificar com evidência (dinheiro, auth, migração).
28. **Blast radius "alguns arquivos"** → decisão de risco no escuro → lista de importadores e rotas.
29. **Área sem teste não mencionada** → regressão invisível → é o achado mais importante.
30. **Recomendar refactor no mapa** → sai do escopo e gera conflito → recomendar, não executar; execução é da skill de mudança.

## Como usar
Na revisão do mapa, percorra a lista: **não se aplica / aplicado / pendente com risco**. Achado BLOCKER impede entregar o mapa (ver `references/quality-gates.md`).
