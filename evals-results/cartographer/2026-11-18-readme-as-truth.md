# Eval: readme-as-truth

- **Skill:** dz23-codebase-cartographer v1.2.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

README diz 'Next.js + Postgres', manifest mostra Express + SQLite.

## Resposta

README diz Next.js+Postgres, o manifest diz Express+SQLite. Sigo o manifest (o que o código realmente usa) e registro a divergência como achado: a documentação está mentindo.

## Esperado

Segue o manifest e registra a divergência como achado de documentação mentindo.

## Falhas (fails_if)

Descreve a stack do README.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Sigo o manifest

## Notas

raciocínio puro; resposta atende expected e evita fails_if
