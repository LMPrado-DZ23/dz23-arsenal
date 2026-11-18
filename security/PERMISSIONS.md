# Permissões das skills — dz23-arsenal

> **Gerado** por `scripts/gera-permissoes.py` de `security/permissoes.json`. Não edite à mão — o gate (`permissoes:indice`) reprova divergência.

Regra 7 do mandato: toda skill que executa comando, altera arquivo, usa navegador, acessa rede ou controla o computador declara permissões, riscos, entradas, saídas, dry-run, rollback e necessidade de aprovação. **18** skills declaradas; o verificador exige uma por skill existente.

Permissões possíveis: `shell` · `filesystem-read` · `filesystem-write` · `network` · `browser` · `database` · `deploy` · `computer-control` · `none`.

## dz23-autonomous-improvement-ultimate

- **Permissões:** shell, filesystem-read, filesystem-write
- **Riscos:** orquestra outras skills; pode disparar ações de qualquer uma delas (deploy, DB, rede)
- **Entradas:** objetivo /goal, critério de aceite, estado/checkpoint
- **Saídas:** mudanças de código, evidências, backlog, checkpoint retomável
- **Dry-run:** plano antes de executar; não aplica mudança sem passar pelos quality-gates
- **Rollback:** git revert do commit da iteração; checkpoint permite retomar estado anterior
- **Aprovação:** antes de qualquer ação destrutiva, deploy ou custo externo disparado por uma sub-skill

## dz23-backend-data-architect

- **Permissões:** shell, filesystem-read, filesystem-write, database, network
- **Riscos:** projeta e pode rodar migrations; altera schema; acessa APIs
- **Entradas:** requisitos de backend/dados, schema atual, contratos
- **Saídas:** modelos, migrations, contratos OpenAPI, código de API
- **Dry-run:** migration em banco local/efêmero; plano de schema antes de aplicar
- **Rollback:** migration reversível (down); git revert do código
- **Aprovação:** OBRIGATÓRIA antes de migration em banco real/produção ou mudança de contrato público

## dz23-codebase-cartographer

- **Permissões:** shell, filesystem-read
- **Riscos:** baixo -- leitura e mapeamento; não altera código
- **Entradas:** caminho do repositório a mapear
- **Saídas:** mapa de dependências, tour de código, pontos de impacto (consulta)
- **Dry-run:** n/a -- somente leitura por natureza
- **Rollback:** n/a -- não escreve
- **Aprovação:** nenhuma (análise read-only)

## dz23-devops-cloud-deployer

- **Permissões:** shell, filesystem-read, filesystem-write, network, deploy, computer-control
- **Riscos:** ALTO -- build, deploy, infra cloud; pode afetar produção e gerar custo
- **Entradas:** alvo de deploy, credenciais (do dono), estratégia
- **Saídas:** artefatos de build, recursos de infra, deploy
- **Dry-run:** terraform plan / --dry-run; build sem push; ambiente de staging primeiro
- **Rollback:** rollback de deploy, destroy do recurso provisionado, git revert do IaC
- **Aprovação:** OBRIGATÓRIA antes de deploy, provisionamento com custo ou qualquer ação em produção

## dz23-e2e-browser-verifier

- **Permissões:** shell, filesystem-read, filesystem-write, browser, network
- **Riscos:** medio -- dirige navegador real e pode submeter formulários no alvo
- **Entradas:** URL-alvo ou fluxo a testar; credenciais de teste quando aplicável
- **Saídas:** screenshots, vídeo, trace, relatório PASS/PARTIAL/FAIL/BLOCKED
- **Dry-run:** rodar contra ambiente de teste/local; nunca contra produção sem aprovação
- **Rollback:** n/a para o teste; dados de teste criados devem ser limpos
- **Aprovação:** antes de testar contra produção ou usar credenciais reais

## dz23-performance-scalability-engine

- **Permissões:** shell, filesystem-read, filesystem-write, network, browser
- **Riscos:** medio -- teste de carga pode degradar um alvo compartilhado
- **Entradas:** alvo a medir, budget de performance
- **Saídas:** medições (Lighthouse/k6), relatório antes/depois, recomendações
- **Dry-run:** medir em baixa concorrência primeiro; alvo local/staging
- **Rollback:** n/a para medição; reverter otimizações por git revert
- **Aprovação:** antes de teste de carga contra alvo compartilhado ou de produção

## dz23-postgres-prod-preflight

- **Permissões:** shell, filesystem-read, filesystem-write, database
- **Riscos:** medio -- inspeciona banco; é advisory, mas habilita migrations de risco
- **Entradas:** migration/alteração proposta, conexão de banco (preflight)
- **Saídas:** veredito de segurança/lock, anti-padrões, checklist
- **Dry-run:** preflight é read-only sobre o banco; não aplica a migration
- **Rollback:** n/a -- não altera; a migration que habilita precisa de plano de rollback próprio
- **Aprovação:** a migration aprovada no preflight exige aprovação antes de rodar em produção

## dz23-reverse-engineer-anything

- **Permissões:** shell, filesystem-read, filesystem-write, computer-control
- **Riscos:** medio -- executa ferramentas de RE sobre binários; binário desconhecido só em sandbox
- **Entradas:** binário/artefato autorizado a analisar
- **Saídas:** pseudocódigo, mapa de chamadas, contrato de API reconstruído, evidência
- **Dry-run:** análise estática antes de dinâmica; binário desconhecido em VM/container sem rede
- **Rollback:** n/a -- não modifica o alvo; artefatos de análise são descartáveis
- **Aprovação:** exige autorização/escopo declarado (RE defensiva); recusa sem direito

## dz23-spec-to-system-engine

- **Permissões:** shell, filesystem-read, filesystem-write
- **Riscos:** medio -- gera estrutura de sistema; pode sobrescrever arquivos
- **Entradas:** especificação/requisitos
- **Saídas:** scaffolding de sistema, ADRs, contratos, testes
- **Dry-run:** plano de arquivos antes de gerar; não sobrescreve sem confirmar
- **Rollback:** git revert do scaffolding gerado
- **Aprovação:** antes de sobrescrever arquivos existentes ou scaffolding destrutivo

## dz23-ultimate-pro-max

- **Permissões:** shell, filesystem-read, filesystem-write, browser
- **Riscos:** baixo-medio -- altera UI/frontend; usa navegador para QA visual
- **Entradas:** requisito de interface, design de referência
- **Saídas:** código de UI, screenshots de QA visual, relatório
- **Dry-run:** preview local; screenshots antes de commitar
- **Rollback:** git revert das mudanças de UI
- **Aprovação:** nenhuma para dev local; aprovação antes de publicar

## prune-tests

- **Permissões:** shell, filesystem-read, filesystem-write
- **Riscos:** ALTO -- remove testes; adaptada para NUNCA remover sem baseline e aprovação
- **Entradas:** suíte de testes, baseline de execução
- **Saídas:** lista de candidatos a remoção com justificativa; remoção só após aprovação
- **Dry-run:** lista os candidatos primeiro, sem apagar nada
- **Rollback:** git revert da remoção; a suíte estava versionada
- **Aprovação:** OBRIGATÓRIA antes de remover qualquer teste; nunca remove para ficar verde

## replica-brand

- **Permissões:** shell, filesystem-read, filesystem-write, network
- **Riscos:** medio -- coleta identidade de marca da web; respeitar ToS e clean-room
- **Entradas:** URL/produto de referência
- **Saídas:** brand kit destilado (cores, tipografia, tom)
- **Dry-run:** coletar sem reusar ativos protegidos; clean-room
- **Rollback:** n/a -- produz artefato novo
- **Aprovação:** respeitar direitos; nunca clonar marca registrada nem usar nome do original

## replica-diff

- **Permissões:** shell, filesystem-read, filesystem-write
- **Riscos:** baixo -- compara features/versões
- **Entradas:** duas versões/produtos a comparar
- **Saídas:** diff de features, lacunas
- **Dry-run:** n/a -- análise
- **Rollback:** n/a -- produz artefato novo
- **Aprovação:** nenhuma

## replica-entrepreneur

- **Permissões:** shell, filesystem-read, filesystem-write
- **Riscos:** baixo -- análise de viabilidade/negócio
- **Entradas:** ideia/produto de referência
- **Saídas:** análise de oportunidade, plano
- **Dry-run:** n/a -- análise
- **Rollback:** n/a -- produz artefato novo
- **Aprovação:** nenhuma

## replica-launch

- **Permissões:** shell, filesystem-read, filesystem-write
- **Riscos:** medio -- produz material de lançamento/listing
- **Entradas:** produto a lançar, mercado-alvo
- **Saídas:** listing, material de lançamento
- **Dry-run:** gerar rascunho; não publicar
- **Rollback:** n/a -- artefato novo
- **Aprovação:** antes de publicar; nunca usar o nome do original na loja (regra anti-FTC)

## replica-recon

- **Permissões:** shell, filesystem-read, filesystem-write, network
- **Riscos:** medio -- reconhecimento de produto via web/scraping
- **Entradas:** alvo de recon (URL/produto)
- **Saídas:** mapa de features, superfície do produto
- **Dry-run:** coletar respeitando ToS; sem autenticar no alvo
- **Rollback:** n/a -- produz artefato novo
- **Aprovação:** respeitar ToS/robots; autorização quando o alvo exigir

## untangle-codebase

- **Permissões:** shell, filesystem-read, filesystem-write
- **Riscos:** ALTO -- reorganiza dependências de um codebase inteiro
- **Entradas:** repositório a desembaraçar, baseline de testes
- **Saídas:** diagnóstico estrutural, redesenho aplicado preservando comportamento
- **Dry-run:** diagnóstico (mapa de 'muda junto?') antes de qualquer edição
- **Rollback:** git revert; exige baseline verde antes e depois
- **Aprovação:** antes de aplicar o redesenho; preserva comportamento intencional

## web-design-guidelines

- **Permissões:** filesystem-read
- **Riscos:** baixo -- acervo de regras consultável, read-only
- **Entradas:** categoria/termo de consulta
- **Saídas:** regras de design/acessibilidade/performance que casam a consulta
- **Dry-run:** n/a -- somente leitura por natureza
- **Rollback:** n/a -- não escreve
- **Aprovação:** nenhuma (consulta read-only)

