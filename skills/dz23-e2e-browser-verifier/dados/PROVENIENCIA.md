# Proveniência — dados/ (acervo de E2E/Playwright)

- **Fonte:** ECC (`affaan-m/ECC`), skill `e2e-testing` (padrões Playwright). Licença **MIT** declarada
  no frontmatter da skill e lida no `LICENSE` da raiz do ECC.
- **O que é:** 3 datasets (16 registros) — `flaky-causas-e-correcao.csv` (race/rede/animação/espera
  fixa → correção), `seletores-e-esperas.csv` (data-testid, auto-wait locator, nada de waitForTimeout,
  POM), `verificar-fluxo-critico.csv` (pular em produção, preview antes de confirmar, esperar API 200,
  estados, multi-tenant). Extraídos das seções da SKILL.md de origem, com `origem_arquivo`/`origem_secao`.
- **Consulta:** `scripts/consulta-e2e.py` (subcomando PT: flaky/race, seletor/testid, fluxo/producao,
  busca; **matcher normaliza acento**) + `scripts/prova-consulta-e2e.py` no gate.
