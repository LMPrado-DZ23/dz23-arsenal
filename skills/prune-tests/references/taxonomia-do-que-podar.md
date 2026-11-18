# Taxonomia — o que podar

A pergunta única para cada teste: *ele depende do comportamento intencional?* Mantenha só se mudar
quando o comportamento muda e falhar quando ele regride. Caso contrário, cai numa das três famílias.

## 1. Depende do passado

Afirma que código removido continua removido. Trazer o código de volta seria uma **decisão**, não uma
regressão — então o teste não guarda comportamento, guarda história.

- Uma feature foi removida e o teste afirma que ela sumiu.
- Um módulo foi movido e o teste afirma que ele não está mais no caminho antigo.
- Um endpoint foi desativado e o teste afirma que ele retorna 404 — quando voltar a existir é escolha.

**Ação:** deletar. A história fica no git, não na suíte.

## 2. Depende do nada

Nenhuma mudança no código sob teste pode fazê-lo falhar. Ele não tem razão própria de mudar.

- Testa o navegador/framework: um `<button>` renderiza, um evento de clique dispara. Já é testado por quem o fez.
- Mocka a unidade sob teste e depois afirma o que o mock devolve — testa o mock, não o código.
- Afirma o que o sistema de tipos já garante (um campo é `string`, uma enum tem N valores).
- Snapshot que ninguém lê e se "atualiza" sem olhar a cada mudança.

**Ação:** deletar. Se existe uma preocupação real por trás (ex.: acessibilidade do botão), escreva o
teste dessa preocupação — não do framework.

## 3. Depende da implementação

Muda sempre que o código muda, mesmo quando o comportamento observável não mudou. Quebra refactor
legítimo e, pior, pode passar com resultado errado.

- O valor esperado é derivado da **mesma lógica** do código (`expect(f(x)).toBe(x - x*0.2)`): um erro
  na lógica passa nos dois lados. Use um valor **literal** (`toBe(80)`).
- Afirma estado privado (`cart._items.length`), ordem interna de chamadas, ou qual helper foi invocado.
- Afirma a forma interna de uma estrutura intermediária que nenhum chamador vê.

**Ação:** reescrever contra o que o chamador observa (`cart.total()`), ou deletar se outro teste já
cobre o comportamento.

## Caso de borda — o teste duplicado

Dois testes guardam o mesmo comportamento. Mantenha o que fala no nível do comportamento (o que o
chamador vê); pode o que repete por um caminho interno. Se ambos são de comportamento e idênticos em
intenção, mantenha um.
