# Eval: no-risk-zones

- **Skill:** dz23-codebase-cartographer v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

Mapa de sistema com cobrança e auth não menciona áreas de risco.

## Resposta

**Mapa de sistema com cobrança e auth sem zonas de risco é mapa de arquitetura, não de engenharia. Falta a parte que evita incidente.**

Em sistema com dinheiro e autenticação, três áreas concentram a maior parte do dano possível:

| Zona | Por que é risco | Evidência mínima |
|---|---|---|
| **Núcleo de dinheiro** (cálculo, arredondamento, conciliação, estorno) | erro silencioso e irreversível; ninguém percebe até o contábil | `arquivo:linha` do cálculo e do arredondamento |
| **Auth/tenant** (middleware, RLS, policies) | vazamento entre clientes é incidente de dados, não bug | `arquivo:linha` do filtro e do teste de isolamento |
| **Migração** (schema, backfill, drop) | `DROP`/backfill sem rollback destrói dado | script de migração + presença/ausência de rollback |

Cada zona entra com: **o que é**, **por que dói**, **evidência**, **regra "não tocar sem plano"** (revisão de 2 pessoas, backup verificado, janela).

**O que eu não faço:** entregar só topologia. Sem zonas de risco, o mapa serve para onboarding e falha para mudança — que é quando ele importa.

## Esperado

Identifica núcleo de dinheiro, auth/tenant e migração como zonas, com evidência; inclui 'não tocar sem plano'.

## Falhas (fails_if)

Entrega mapa só estrutural.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Mapa de sistema com cobrança e auth sem zonas de risco é mapa de arquitetura, não de engenharia.

## Notas

Re-leitura adversarial: nenhum
