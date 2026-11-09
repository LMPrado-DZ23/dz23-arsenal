# Anti-padrões de E2E

Cada item: **sintoma** → **por que dói** → **correção**.

## Sincronização
1. **`sleep(2000)` antes do clique** → falha em máquina lenta e desperdiça tempo em máquina rápida → espere o estado (`toBeVisible`, `waitForResponse`).
2. **Aumentar timeout para resolver flake** → esconde a causa e dobra o tempo de falha → medir, achar a condição, corrigir.
3. **`networkidle` como espera universal** → trava com polling/websocket → espere o evento específico.
4. **Loop `while (!visible) sleep(100)`** → reinventa o auto-wait pior → `expect(locator).toBeVisible()`.

## Seleção
5. **`nth-child` / XPath posicional** → quebra com qualquer mudança de layout → `getByRole`, `getByText`.
6. **Classe CSS de estilo** (`.btn-primary`) → refactor visual quebra teste sem quebrar produto → papel/testid.
7. **Texto traduzido como seletor** → quebra com i18n → `getByRole(name)` + locale fixo.
8. **`page.$('div')` com índice** → pega o elemento errado silenciosamente → filtro por conteúdo único.
9. **Seletor com id gerado (`#react-123`)** → muda a cada build → role/label/testid.

## Dado e estado
10. **Usuário padrão compartilhado** → teste em paralelo muda o dado do outro → usuário único por run.
11. **`truncate` no banco compartilhado** → apaga dado de outro job → teardown por `runId`.
12. **Dependência de ordem** → sozinho falha, na suíte passa → teste independente.
13. **Fixture global mutável** → estado vaza entre testes → criar no `beforeEach`/teste.
14. **Teste contra produção** → cria pedido real, manda e-mail real → staging + autorização.

## Asserção
15. **`expect(await page.title()).toBeTruthy()`** → passa com qualquer coisa → asserte o valor esperado.
16. **Só screenshot, sem asserção** → "parece ok" não é prova → asserção de estado.
17. **Asseverar UI e não o efeito no servidor** → UI otimista esconde falha de persistência → verificar API/DB.
18. **`expect(page).not.toThrow()`** → nunca falha → asserção real.

## Mock
19. **Mock do próprio backend** → o E2E deixa de provar integração → mock só no limite externo.
20. **Mock de tudo e chamar de E2E** → é teste de componente caro → mover para unidade/componente.
21. **Terceiro real em teste instável** (pagamento, e-mail) → flake e custo → sandbox/mock no limite.

## CI e operação
22. **Suíte de 45 min** → ninguém espera, gate vira decoração → shard + smoke no PR.
23. **Retry global 3×** → bug real fica verde no 3º → retry 1, relatório com `flaky`, issue.
24. **Sem artifact** → falha não investigável → trace/vídeo/screenshot sempre.
25. **`test.skip` sem issue** → cobertura fantasma → gate quebra `skip` sem issue.
26. **Quarentena sem prazo** → exclusão disfarçada → issue, dono, data.

## Autenticação e autorização
27. **Login por formulário em todo teste** → lento e frágil → setup com `storageState`.
28. **Credencial real no repo** → vazamento → env/secret.
29. **Nenhum teste de permissão** → usuário sem papel acessa em produção → teste 403/redirect.
30. **Multi-tenant "testado" só na listagem** → URL direta vaza → teste de acesso direto entre tenants.

## Manutenção
31. **Page Object com regra de negócio** → teste ilegível e acoplado → PO só de página.
32. **Helper que engole erro** (`try/catch` no teste) → falha vira verde → deixar falhar.
33. **Nome `teste 1`, `fluxo novo`** → relatório inútil → nome = comportamento.
34. **Baseline visual atualizado automaticamente** → regressão aceita em silêncio → revisão humana do diff.

## Sincronização fina e hidratação
35. **Asserção síncrona sem espera** → `expect(await locator.isVisible()).toBe(true)` avalia o instante e não aguarda o DOM → use `await expect(locator).toBeVisible()`.
36. **Clicar antes da hidratação do SSR** → HTML chegou, listener do JS ainda não; o primeiro clique se perde → espere o estado interativo real (habilitado/pronto), não um sleep.
37. **Usuário mutável compartilhado em paralelo** → teste A troca a senha/esvazia o carrinho enquanto B compra com a mesma conta → conta e tenant isolados por teste/worker.
38. **Testar implementação em vez de comportamento** → valida nome de estado interno do framework → valide o que o usuário vê, a URL resultante e o efeito persistido na API.


## Como usar
Na revisão do diff de teste, percorra a lista e responda **não se aplica / aplicado / pendente com risco**. Achado vira issue com severidade de `references/quality-gates.md`.
