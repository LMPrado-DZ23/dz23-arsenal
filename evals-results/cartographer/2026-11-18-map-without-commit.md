# Eval: map-without-commit

- **Skill:** dz23-codebase-cartographer v1.2.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Mapa do repositório entregue sem SHA nem data de leitura.

## Resposta

Recuso entregar sem o cabeçalho: repo, commit (SHA), branch e data de leitura são BLOCKER. Sem o SHA ninguém sabe contra qual estado o mapa vale, e ele deixa de ser reutilizável no primeiro commit.

## Esperado

Recusa entregar: cabeçalho com repo, commit, branch e data é BLOCKER; sem isso o mapa não é reutilizável.

## Falhas (fails_if)

Entrega o mapa assim mesmo.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: repo, commit (SHA), branch e data de leitura são BLOCKER

## Notas

raciocínio puro; resposta atende expected e evita fails_if
