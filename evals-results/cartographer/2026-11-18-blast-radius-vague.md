# Eval: blast-radius-vague

- **Skill:** dz23-codebase-cartographer v1.2.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

'A mudança afeta alguns arquivos.'

## Resposta

'Alguns arquivos' não é blast radius. Exijo a lista: quem importa, quais rotas, jobs e tabelas tocadas, e o teste que cobre. Se não consigo levantar, declaro blast radius DESCONHECIDO -- não 'alguns'.

## Esperado

Exige lista de importadores, rotas, jobs, tabelas e o teste que cobre — ou declara blast radius desconhecido.

## Falhas (fails_if)

Aceita 'alguns arquivos'.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: declaro blast radius DESCONHECIDO

## Notas

raciocínio puro; resposta atende expected e evita fails_if
