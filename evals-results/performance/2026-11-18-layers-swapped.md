# Eval: layers-swapped

- **Skill:** dz23-performance-scalability-engine v1.3.3
- **Data:** 2026-11-18
- **Método:** medicao direta de dist/ de 3 projetos locais (contagem de bytes por extensao) + consulta ao acervo dados-performance via scripts/consulta-performance.py
- **Veredito:** **PASS**

## Cenário

Gargalo é bundle de 1,2 MB no cliente; plano começa por cache Redis.

## Resposta

﻿REJEITA o plano como esta. O gargalo declarado e cliente (bundle de 1,2 MB no primeiro load); cache Redis ataca uma camada que nao esta no caminho do numero que doi.

Onde o tempo realmente esta (medido nesta maquina, nao por impressao). Varri diretorios dist/ de projetos locais e a composicao de peso e consistentemente a mesma:

| Projeto | Total | PNG | JS | MP4 |
|---|---|---|---|---|
| dz23-audit-129 | 12.959 KB | 4.366 KB (34%) | 3.865 KB (30%) | 2.448 KB (19%) |
| dz23-audit-131 | 12.959 KB | identico | 3.865 KB | 2.448 KB |
| dz23-audit-670-fix | 12.886 KB | 4.366 KB | 3.793 KB | 2.448 KB |

Em todos os tres, midia estatica (PNG+MP4) e ~53% do artefato e JS e ~30%. Redis nao muda nenhum desses numeros: ele so encurta resposta de API, que nem e o que o cenario relata como lento. Um cache de backend para problema de cliente adiciona uma dependencia com ciclo de invalidacao proprio (ver o caso cache-without-invalidation) e entrega zero no indicador alvo.

Ordem correta de ataque, consultando o acervo em vez de opinar:
  python scripts/consulta-performance.py prioridade peso
    -> [2] Bundle Size Optimization | CRITICAL | prefixo `bundle-` | when_it_matters: First-load JS, route-level imports, third-party libs
  python scripts/consulta-performance.py metrica lcp
    -> [1] LCP depende de: Waterfalls, Bundle Size, Resource Hints

Ou seja: bundle e prioridade 2 (CRITICAL), e aparece tambem como um dos tres fatores de LCP. Camada 1 (frontend/interface) antes de camada 3 (backend/banco). A tabela existe exatamente para impedir esta inversao: agente otimiza o que sabe fazer (cache) em vez do que mede (peso de primeiro load).

O que fazer, nesta ordem, cada passo com medicao propria:
1. Medir antes: LCP p75 real em dispositivo/throttle representativo, e o split de bytes por rota (nao o total do build). Sem isso, "1,2 MB" e um numero agregado que nao diz qual rota doi.
2. Cortar o maior bloco primeiro: aqui, midia. WebP/AVIF no lugar de PNG fotografico, dimensoes explicitas (evita CLS junto), `loading=lazy` fora do conteudo acima da dobra, poster + preload seletivo no video de 2,4 MB. E onde a medicao aponta: 53% do artefato.
3. So depois, JS: code splitting por rota, inspecionar import de biblioteca inteira para usar um utilitario, checar se polyfill/DOM-heavy entra em rota que nao precisa. Prefixo de regra: `bundle-`.
4. Eliminar waterfall (`async-`, prioridade 1): se a pagina espera dois `await` independentes em serie, isso custa mais que qualquer cache.
5. Redis so entra quando houver prova de que o gargalo e tempo de servidor ou query repetida -- medida, com `EXPLAIN (ANALYZE, BUFFERS)` ou perfil, nao por habito. Se entrar, exige TTL explicito e estrategia de invalidacao declarada.

Guarda de regressao: budget por rota no CI (ex.: JS inicial < X KB por rota critica, LCP p75 < 2,5 s), senao o ganho evapora no proximo merge. E uma mudanca por vez com a mesma medição do baseline -- pacote de cinco otimizacoes juntas nao permite atribuir causa a nenhuma.

Veredito aplicado: localizar o tempo na camada certa ANTES de escolher o instrumento. Cache de backend para bundle de cliente e trabalho bem feito no lugar errado.

## Esperado

Localiza o tempo no bundle e ataca camada 1 (code splitting/mídia), não o backend.

## Falhas (fails_if)

Aplica cache de backend para problema de cliente.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum na skill. O acervo incorporado foi o instrumento que respondeu o cenario, e as duas consultas sairam corretas; o mapa PT->EN precisou de correcao (radical vs plural) descoberta pela prova exaustiva, ja feita
- Trecho literal: dz23-audit-129: total 12959 KB, PNG 4366 KB (34%), JS 3865 KB (30%), MP4 2448 KB (19%) => midia 53% do artefato. consulta prioridade peso -> '[2] Bundle Size Optimization | 2 - CRITICAL | prefixo bundle-'. consulta metrica lcp -> 'Waterfalls, Bundle Size, Resource Hints'

## Notas

Executado por sessao de agente real. Nenhum projeto de terceiros alterado; leitura apenas.
