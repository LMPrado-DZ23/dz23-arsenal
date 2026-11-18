---
name: prune-tests
version: 1.0.0
description: >
  Poda todo teste que não guarda comportamento. Uma suíte cheia de testes que não falham numa
  regressão (ou que falham sem regressão) custa manutenção e dá falsa confiança: o agente confia num
  verde que não prova nada. Diagnóstico por dependência: mantenha um teste só se ele depende do
  comportamento intencional — muda quando o comportamento muda, falha quando ele regride. Poda o que
  depende do passado (afirma que código removido continua removido), do nada (nenhuma mudança no código
  o faz falhar) ou da implementação (muda junto com o código mesmo sem mudança de comportamento). Onde
  um desses também cobre comportamento de que algo depende, reescreve contra o comportamento. Use antes
  de confiar numa suíte, ao herdar testes alheios, ou junto da untangle-codebase num refactor profundo.
  Não é aumentar cobertura nem caçar flaky — é remover teste que não tem razão própria de existir.
user-invocable: true
argument-hint: "[caminho opcional para focar]"
metadata:
  origin: Caldo (caldoai/skills), MIT lida no arquivo LICENSE da raiz do repositório (Copyright 2026 Maze)
  license: MIT
  source-file: skills/prune-tests/SKILL.md
  method: internalizado e adaptado ao rito do arsenal (eval executável, referências, gate), não copiado byte a byte
---

# prune-tests

Poda todo teste que não guarda comportamento. Trate isto como objetivo, não como sugestão.

## Por que fazer isso

- **Verde honesto:** um teste que não falha numa regressão dá confiança que não existe.
- **Manutenção mais barata:** teste preso à implementação quebra a cada refactor legítimo e vira imposto.
- **Sinal limpo:** quando cada teste restante só falha numa regressão, um vermelho significa algo.

## O que podar (três famílias)

A pergunta única: *este teste depende do comportamento intencional?* Mantenha só se sim. Poda quem
depende de:

- **O passado** — afirma que código removido continua removido. Trazê-lo de volta seria uma decisão,
  não uma regressão. Ex.: "a feature X foi removida" ou "o módulo saiu do caminho antigo".
- **O nada** — nenhuma mudança no código o faz falhar, logo não tem razão própria de mudar. Ex.: testa
  o navegador (um `<button>` renderiza, um clique dispara); mocka a unidade sob teste e afirma o que o
  mock devolve; afirma o que o sistema de tipos já garante.
- **A implementação** — muda sempre que o código muda, mesmo sem mudança de comportamento. Ex.: o valor
  esperado deriva da mesma lógica do código (resultado errado ainda passa); afirma estado privado,
  ordem interna de chamadas ou qual helper foi invocado.

Taxonomia completa com exemplos em `references/taxonomia-do-que-podar.md`.

## Como podar (o detalhe mora nas referências)

1. **Mapeie de que cada teste depende**, sem apagar nada ainda. Método em `references/method.md`.
2. **Pode.** Delete todo teste não ancorado em comportamento intencional. Onde um também cobre
   comportamento de que algo depende, **reescreva contra esse comportamento** em vez de deletar.
3. **Delete o código de produção que só existia para os testes removidos** (helpers de teste, resets).

## Regras inegociáveis

- **Não reduza cobertura de comportamento real.** Antes de deletar, prove que outro teste guarda o
  mesmo comportamento, ou reescreva. Deletar um teste que era a única rede de um comportamento é
  regressão silenciosa. Ver `references/verification.md`.
- **Mapa primeiro, poda depois.** Nada de deletar durante o passo 1.
- **Git como evidência.** Cada poda vira commit rastreável à razão (passado/nada/implementação ou
  duplicata); o registro é o artefato, não nota solta. Ver `references/git-as-evidence.md`.
- **Suíte verde antes e depois**, com a mesma cobertura de comportamento — menos os testes que não
  guardavam nada.

## Estados de evidência

| Estado | Critério |
|---|---|
| PASS | testes podados, suíte verde, e cada removido justificado por uma das famílias |
| NOT_TESTED | poda feita mas a suíte não foi rodada para comprovar que nada de comportamento caiu |
| PARTIAL | restam testes suspeitos sem decisão (podar / reescrever / manter) |

## Veredito

Pronto quando: todo teste restante está ancorado em comportamento intencional; cada um falharia numa
regressão e só nela; nenhum teste afirma código que não existe mais; nenhum par guarda o mesmo
comportamento; nenhum código de produção existe só para teste. Caso contrário, declare PARTIAL com a
lista restante.

## Roteamento com outras skills

- Num refactor profundo que também reorganiza dependências: `untangle-codebase` (mesma filosofia,
  escopo maior); prune-tests é a parte "só testes".
- Para gerar ou fortalecer testes de comportamento que faltam: `tdd` / a skill de testes do stack.
- Verificação E2E do comportamento preservado: `dz23-e2e-browser-verifier`.
