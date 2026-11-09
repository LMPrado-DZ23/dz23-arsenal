# language: pt
@autenticacao @p0
Feature: Reserva de horário
  Como cliente da barbearia
  Quero reservar um horário com o profissional
  Para que eu seja atendido no dia e hora escolhidos

  Background:
    Given o tenant "Barbearia A" existe
    And existe o profissional "João" ativo
    And o profissional "João" atende das 09:00 às 18:00

  # --- caminho feliz ---
  Scenario: reserva com sucesso de horário livre
    Given o horário "14:00" está livre
    When reservo o horário "14:00" com "João"
    Then a reserva é criada com status "CONFIRMED"
    And a API responde 201 com o id da reserva
    And ao recarregar a agenda o horário "14:00" aparece ocupado

  # --- erro 1 ---
  Scenario: horário já ocupado retorna conflito
    Given o horário "14:00" já está reservado por outro cliente
    When tento reservar o horário "14:00" com "João"
    Then a API responde 409 com code "slot_taken"
    And a UI exibe o alerta "Horário indisponível"

  # --- erro 2 ---
  Scenario: horário fora do expediente é recusado
    Given o profissional "João" atende até "18:00"
    When tento reservar o horário "19:00"
    Then a API responde 422 com code "outside_business_hours"
    And a reserva não é criada

  # --- borda / parametrizado ---
  Scenario Outline: validação de <campo>
    Given o formulário de reserva está aberto
    When preencho <campo> com "<valor>"
    And submeto a reserva
    Then a mensagem "<mensagem>" é exibida

    Examples:
      | campo    | valor      | mensagem                    |
      | telefone | abc        | Telefone inválido           |
      | telefone | 119        | Telefone inválido           |
      | nome     |            | Nome é obrigatório          |

  # --- autorização ---
  Scenario: outro tenant não acessa a reserva
    Given existe a reserva "R-1" no tenant "Barbearia B"
    When acesso a reserva "R-1" autenticado no tenant "Barbearia A"
    Then a API responde 404
    And nenhum dado da reserva é exibido
