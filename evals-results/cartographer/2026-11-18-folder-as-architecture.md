# Eval: folder-as-architecture

- **Skill:** dz23-codebase-cartographer v1.2.0
- **Data:** 2026-11-18
- **Método:** auto (autoavaliação na mesma sessão — viés do autor)
- **Veredito:** **PASS**

## Cenário

Mapa descreve camadas apenas pelos nomes das pastas.

## Resposta

Nome de pasta não é arquitetura. Levanto o grafo real de imports e aponto onde a intenção diverge -- ex.: um controller importando o ORM direto, pulando a camada de serviço. A pasta é a intenção; os imports são o que o código faz.

## Esperado

Levanta o grafo real de imports e mostra onde a intenção diverge (ex.: controller importando ORM direto).

## Falhas (fails_if)

Repete a estrutura de pastas como arquitetura.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Levanto o grafo real de imports

## Notas

raciocínio puro; resposta atende expected e evita fails_if
