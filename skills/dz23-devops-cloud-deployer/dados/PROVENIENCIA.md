# Proveniência — dados/ (acervo de deploy/cloud)

- **Fonte:** ECC (`affaan-m/ECC`), skill `deployment-patterns`. Licença **MIT lida no `LICENSE` da
  raiz** do ECC.
- **O que é:** 3 datasets (43 registros), complementando o que o `SKILL.md` já traz (fases, segredos,
  padrões inegociáveis):
  - `estrategias-de-deploy.csv` (3): estratégia → prós → contras → quando usar (Rolling/Blue-Green/Canary).
  - `docker-boas-praticas.csv` (12): FAZ/EVITA de Docker.
  - `checklist-producao.csv` (28): categoria → item (Aplicação/Infra/Monitoração/Segurança/Operações +
    Rollback).
- **Geração:** extração das tabelas/listas da SKILL.md de origem, com `origem_arquivo`/`origem_secao`.
- **Consulta:** `scripts/consulta-devops.py` (subcomando PT: estrategia/canary, docker/container,
  checklist/rollback/seguranca, busca) + `scripts/prova-consulta-devops.py` no gate.
