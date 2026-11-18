---
name: untangle-codebase
version: 1.0.0
description: >
  Desembaraça um codebase inteiro num passe só, para que agentes que trabalham nele leiam menos por
  mudança, quebrem menos sem perceber e depurem mais rápido. Diagnóstico estrutural por "estas peças
  mudam juntas?": cataloga casos especiais, elos ocultos, elos desnecessários e sobra; redesenha dos
  primeiros princípios (uma correção atrás de vários problemas, não cada caso isolado); aplica e repete
  até não restar nada que valha corrigir, preservando o comportamento intencional. Use quando um repo está
  difícil de mudar, espalhado por camadas, cheio de wrappers e flags pontuais, ou antes de delegar trabalho
  pesado a agentes que gastam tokens procurando onde mexer. Não é revisão de estilo nem caçada de bug
  isolado — é reorganização de dependência e coesão.
user-invocable: true
argument-hint: "[área ou preocupação opcional para focar]"
metadata:
  origin: Caldo (caldoai/skills), MIT lida no arquivo LICENSE da raiz do repositório (Copyright 2026 Maze)
  license: MIT
  source-file: skills/untangle-codebase/SKILL.md
  method: internalizado e adaptado ao rito do arsenal (eval executável, referências, gate), não copiado byte a byte
---

# untangle-codebase

Comece um refactor profundo deste codebase e leve até o fim. Trate isto como objetivo, não como sugestão.

## Por que fazer isso

- **Saída melhor:** agentes escrevem melhor código num codebase bem estruturado.
- **Mudanças mais baratas e rápidas:** agente gasta menos token procurando e mais no problema.
- **Menos quebra silenciosa:** agente quebra menos sem perceber.
- **Depuração mais rápida:** agente acha causa raiz mais rápido.

O método completo, em cinco passos, está em `references/method.md`. O formato do registro de decisão
(problemas + a correção que resolve vários de uma vez) está em `templates/decision-log.md`. Antes de
catalogar, consulte a taxonomia das quatro famílias de defeito em `references/defect-taxonomy.md`.

## Resumo do fluxo (o detalhe mora nas referências)

1. **Pergunte** quais extras entram além do desembaraço: remover comentários que só repetem o código;
   remover/consertar testes que não pegam bug real. Liste as duas opções com a descrição exata e faça só o
   que o usuário escolher.
2. **Catalogue todos os problemas, sem mudar nada ainda.** A pergunta única: *estas peças deveriam mudar
   juntas?* Há três formas de errar — elo oculto, elo desnecessário, sobra — mais os casos especiais.
3. **Redesenhe dos primeiros princípios.** Procure a *uma* correção atrás de vários problemas; não conserte
   caso por caso. Escreva cada correção acima dos problemas que ela resolve.
4. **Aplique tudo da lista.** Remova os casos especiais que o redesenho torna desnecessários; mantenha os
   que o sistema ainda precisa. Se escolheu Testes, faça-os por último (são a rede de regressão).
5. **Confira e repita até terminar.** Subagentes procuram casos especiais/elos/sobra. Pare quando não resta
   nada que valha corrigir — quantos casos especiais sobram é a melhor medida de quão perto você chegou.

## Regras inegociáveis

- **Não altere comportamento intencional.** O veredito final exige teste provando que o comportamento é o
  mesmo de quando começou, exceto bugs que o refactor corrigiu. Ver `references/verification.md`.
- **Lista primeiro, mudança depois.** Nada de editar durante o passo 2. Um diff sem lista de problemas é
  refatoração por gosto, não por evidência.
- **Uma correção por grupo de problemas.** Se sua "correção" resolve um único item e parece cosmética, é
  provavelmente o erro de consertar casos especiais isolados (anti-padrão central desta skill).
- **Git como evidência.** Cada fix vira commit rastreável ao problema que fechou; o registro de decisão é o
  artefato, não nota solta. Ver `references/git-as-evidence.md`.

## Estados de evidência

| Estado | Critério |
|---|---|
| PASS | mudança aplicada, suíte verde, e o problema correspondente saiu da lista |
| NOT_TESTED | reorganização feita mas comportamento não foi comprovado por teste |
| PARTIAL | lista tem itens sem correção mapeada |

## Veredito

Pronto quando: poucos casos especiais restam; uma mudança típica cai num lugar só; todo import é razoável e
nada importa algo mais volátil que si; subagentes não acham mais nada que valha corrigir; comportamento
intencional comprovadamente igual. Caso contrário, declare PARTIAL com a lista restante.

## Roteamento com outras skills

- Mapear o grafo de dependências atual antes de decidir por onde começar: `dz23-codebase-cartographer`.
- Decidir se uma peça deve virar módulo profundo (interface estável sobre implementação volátil): vocabulário
  em `codebase-design`.
- Podar apenas testes, sem tocar em produção: use `prune-tests` (escopo menor, mesma filosofia).
- Registrar decisões estruturais como ADR: `dz23-spec-to-system-engine`.
