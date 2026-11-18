# Proveniência — dados/ (acervo de gates de qualidade)

> **falhas-de-agente.csv** (6 linhas) vem da skill `agent-introspection-debugging` do ECC (MIT): os 6 modos de falha de agente (loop/tool-calls, contexto estourado, ECONNREFUSED, 429, arquivo sumido, hipotese errada) com causa provavel e o que checar. Cada linha cita `ECC agent-introspection-debugging/SKILL.md`.

- **Fonte:** **ORIGINAL (DZ23)** — destilado da própria `references/quality-gates.md` da skill. Nada
  externo; é o conhecimento que a skill já tinha, tornado consultável.
- **O que é:** 2 datasets (19 registros):
  - `gates-de-qualidade.csv` (13): área → evidência mínima para PASS → casos de risco (git/baseline,
    lint, unit, integração, E2E, build, auth/security, multitenancy, banco, UI, a11y, performance, operação).
  - `verificacao-por-componente.csv` (6): componente → o que verificar (botão, formulário, menu, modal,
    tabela, API).
- **Geração:** parse da tabela e da lista de `quality-gates.md`, com `origem_arquivo`/`origem_secao`.
- **Consulta:** `scripts/consulta-autonomous.py` (subcomando PT: gate/area/qualidade, componente/ui,
  busca; matcher normaliza acento) + `scripts/prova-consulta-autonomous.py` no gate.
