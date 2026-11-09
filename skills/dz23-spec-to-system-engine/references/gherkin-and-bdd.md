# Gherkin e BDD

## Por que
`Given/When/Then` é a ponte entre requisito e teste. Se o `Then` não é observável, não é teste — é prosa.

## Estrutura
```gherkin
Feature: <capacidade>
  Como <papel concreto>
  Quero <ação>
  Para que <benefício>

  Background:
    Given o tenant "Barbearia A" existe
    And existe um profissional "João" ativo

  Scenario: <caminho feliz>
    Given <pré-condição específica>
    When <ação do usuário>
    Then <resultado observável>
    And <verificação complementar>

  Scenario: <erro tratado>
    Given <pré-condição de erro>
    When <ação inválida>
    Then <status/mensagem esperada>

  Scenario Outline: validação de <campo>
    Given o formulário está aberto
    When preencho <campo> com "<valor>"
    And submeto
    Then a mensagem "<mensagem>" é exibida
    Examples:
      | campo | valor | mensagem |
      | email | abc   | E-mail inválido |
```

## Regra mínima por story
**1 cenário feliz + 2 de erro/borda.** Story com só caminho feliz está incompleta — o erro é onde o produto
quebra.

## O que é um `Then` bom
| Ruim | Bom |
|---|---|
| "a tela deve ser intuitiva" | "o botão 'Confirmar' está visível e habilitado" |
| "o sistema salva" | "ao recarregar, o pedido aparece com status 'Pago'" |
| "deve validar" | "a API responde `422` com `code: slot_taken` e a UI mostra o alerta no campo" |
| "trata o erro" | "com a API fora, a tela mostra mensagem de falha e botão 'Tentar novamente'" |

## Dado, quando, então — com contrato
`Then` deve citar o **observável do contrato**: status HTTP, código de erro, campo, estado de FSM. Isso
liga o cenário ao `references/interface-contracts.md`.

## Binding com E2E
Cada `Scenario` vira um teste em `dz23-e2e-browser-verifier`:
- `Given` → setup (seed/storageState);
- `When` → ação no browser (`getByRole`);
- `Then` → asserção visível + verificação de efeito no servidor.
Step definitions não são obrigatórias: o cenário pode ser implementado como teste nomeado com o mesmo
título. O que não vale é o cenário existir sem teste correspondente na matriz.

## Antipadrões
- Cenário com 10 `And` — teste disfarçado de roteiro; quebre.
- `Then` que verifica implementação ("chamou POST /orders") em vez de comportamento observável.
- `Background` gigante que esconde dependência.
- `Examples` com 40 linhas cobrindo a mesma regra — parametrize o essencial, não o infinito.
- Cenário sem mensagem de erro específica ("mostra erro").

## Saída
`ACCEPTANCE.feature` com features por capacidade, cenários feliz + erro + borda, e a matriz ligando cada
`Scenario` ao `REQ` e ao teste real.
