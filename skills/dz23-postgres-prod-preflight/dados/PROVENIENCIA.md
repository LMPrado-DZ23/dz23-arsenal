# Proveniência — dados/ (acervo de pré-deploy de Postgres)

- **Fonte:** ECC (`affaan-m/ECC`), skills `postgres-patterns` e `database-migrations`, que por sua vez
  creditam **o time do Supabase (MIT License)**. Licença **MIT lida no arquivo `LICENSE` da raiz** do
  ECC, confirmada.
- **O que é:** três datasets de pré-deploy, distintos do acervo geral do `dz23-backend-data-architect`
  (que tem índices/tipos). Aqui o foco são os **gates** de ir para produção:
  - `anti-padroes-de-migracao.csv` (6): anti-padrão → por que falha → melhor abordagem.
  - `gates-de-seguranca-e-lock.csv` (8): gate → risco → verificação (RLS em SELECT, REVOKE public,
    timeouts, FK sem índice, lock em ADD COLUMN, default volátil, credencial em migração).
  - `checklist-de-migracao.csv` (7): item → por quê (o Migration Safety Checklist do ECC).
- **Como foi gerado:** extração das tabelas e listas das SKILL.md de origem, sem inventar linha. Cada
  linha carrega `origem_arquivo`/`origem_secao`.
- **Consulta:** `scripts/consulta-postgres.py` (subcomando PT: gate/rls/lock, anti/migracao, checklist,
  busca), com recusa honesta. Prova em `scripts/prova-consulta-postgres.py` (consultas certas +
  controles negativos + esquema).
- **Dedup:** não repete o acervo do backend (índices por query, tipos de dado); só o que é pré-deploy.
