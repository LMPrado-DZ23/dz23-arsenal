# Eval: layer-sliced-plan

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Plano: 'criar tabela' → 'criar API' → 'criar tela'.

## Resposta

**Plano por camada (tabela → API → tela) não entrega valor até a última etapa — reagrupar em fatias verticais.**

Na sequência por camada, nada é demonstrável até o fim: a tabela sozinha não serve, a API sozinha não serve, e o cliente só vê algo na semana 3. Se o prazo apertar, você corta justamente a parte que dá valor.

Fatias verticais propostas:

| Fatia | Entrega ponta a ponta | Camada técnica vira passo interno |
|---|---|---|
| SL-01 | criar pedido e vê-lo na tela | tabela mínima + POST + listagem |
| SL-02 | editar status com validação | coluna + PATCH + feedback na UI |
| SL-03 | filtrar e paginar | índice + query + controle de filtro |

Cada fatia tem critério de aceite **demonstrável por um usuário**. A camada continua existindo — como passo interno de cada fatia, não como fase do projeto.

**O que eu não faço:** manter a ordem por camada como plano de entrega. Ela é boa para organizar o trabalho técnico e péssima para controlar risco de prazo.

## Esperado

Reagrupa em fatias verticais que entregam valor ponta a ponta; camada técnica vira passo interno.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Plano por camada (tabela → API → tela) não entrega valor até a última etapa

## Notas

Reagrupou em 3 fatias verticais com critério demonstrável por usuário.
