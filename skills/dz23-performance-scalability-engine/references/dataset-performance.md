# Acervo de priorização de performance (dados-performance/)

Índice de **uso**. Origem, licença e verificação em `dados-performance/PROVENIENCIA.md` e no registro
geral `dados-design/VENDOR.md`. Este arquivo responde uma pergunta: **quando consultar em vez de
improvisar.**

## O problema que este acervo resolve

Performance tem ordem, e agente erra a ordem com frequência alta: ataca re-render (prioridade 5) quando
o gargalo é um `await` seguido de outro `await` independente (prioridade 1), ou mexe em micro-otimização
de JavaScript (7) com bundle de primeiro load estourado (2). O custo do erro não é só ineficiência — é
publicar "otimizei" sem o gargalo ter se movido.

Duas tabelas atacam isso: **prioridade por categoria** (por onde começar) e **métrica → categoria** (o
sintoma medido aponta o tipo de regra que mexe nele).

## Como consultar

```bash
python scripts/consulta-performance.py listar
python scripts/consulta-performance.py prioridade cascata     # -> Eliminating Waterfalls, CRITICAL
python scripts/consulta-performance.py prioridade peso        # -> Bundle Size Optimization, CRITICAL
python scripts/consulta-performance.py metrica lcp            # -> Waterfalls, Bundle Size, Resource Hints
python scripts/consulta-performance.py metrica "pulo de layout"   # -> CLS -> Rendering
python scripts/consulta-performance.py categoria bundle       # -> prefixo `bundle-`, prioridade 2
```

Português funciona por mapa fechado termo-a-termo (`cascata`→Waterfalls, `ssr`→Server-Side Performance,
`travamento`→TBT). Se a palavra não está no mapa nem na tabela, a resposta é **"sem correspondência"**
mais a lista de valores disponíveis — nunca uma aproximação.

## Quando usar no método

- **Chegou "está lento" sem medição** → `metrica <o que o usuário descreve>` para saber quais categorias
  costumam mover aquela métrica; depois meça antes de tocar. Nunca parta de categoria: parta do número.
- **Você já mediu e tem vários candidatos** → `listar` e ataque pela coluna `priority` descendente. A
  tabela existe para impedir exatamente a escolha por facilidade.
- **Escrevendo regra/checklist de revisão** → a coluna `prefix` dá o namespace das regras por categoria
  (`async-`, `bundle-`, `rerender-`), útil para rotular achados de forma estável entre sessões.
- **Fechando otimização** → confirme que a métrica alvo melhorou pela mesma tabela: se você atacou
  `rendering` e o problema era LCP, a consulta mostra que LCP depende primeiro de waterfalls e bundle.

## Limite honesto

São **13 linhas**: 8 categorias priorizadas e 5 métricas. É um mapa de *ordem de ataque*, não um corpo
de conhecimento de performance — as regras específicas de cada categoria continuam em
`references/measurement-first.md` e nas camadas do `SKILL.md`. Prioridades são de terceiros (ECC, MIT),
derivadas de prática com React/Next em ambiente Vercel; podem não ser as suas. Uma medição sua vale mais
que qualquer linha daqui — o acervo serve para escolher **por onde começar**, não para concluir.

Fora deste escopo: backend/banco (use `consulta-backend.py`), design e acessibilidade de interface
(`consulta-design.py`).
