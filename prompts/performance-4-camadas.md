Atue como um Arquiteto de Software Sênior e Especialista em Performance e Escalabilidade de Sistemas. 

Eu estou desenvolvendo uma aplicação moderna e quero garantir que ela seja extremamente rápida, resiliente e proporcione uma experiência de usuário impecável, sem lentidão ou perda de conversão. 

Analise o projeto atual e gere um plano cirúrgico de otimização de performance dividido exatamente nas 4 camadas abaixo. Para cada item, forneça: o problema que ele evita, como implementar na prática e a diretriz técnica recomendada:

---

### 1. FRONTEND & INTERFACE (UX & Renderização)
* **Skeleton Loaders:** Implementar telas de carregamento fluídas para evitar layout shift e percepção de travamento.
* **Otimização de Mídia:** Servir imagens e assets estáticos obrigatoriamente em formatos modernos (WebP ou AVIF), com lazy loading em elementos fora da viewport.
* **Code Splitting & Bundling:** Dividir o JavaScript por página/rota e carregar scripts de terceiros de forma assíncrona ou tardia.
* **Virtualização de Listas:** Aplicar virtualização (ex: tanstack-virtual) em listas longas ou tabelas densas para não estourar o DOM.
* **Otimização de Input:** Aplicar debounce e throttle rigorosos em barras de busca, inputs e autocompletes.
* **Fontes & Estáticos:** Hospedar fontes localmente limitando pesos/variações e configurar cache agressivo de estáticos no navegador.
* **Resiliência Mobile:** Otimizar e testar a fluidez considerando cenários de rede móvel instável e latência alta.

### 2. COMUNICAÇÃO & REDE (APIs & Fluxos)
* **Prevenção de Duplicidade:** Eliminar chamadas de API duplicadas em tempo de montagem ou re-renderização (usando requisições em paralelo com Promise.all quando independentes).
* **Streaming & Otimização de IA:** Transmitir respostas de IA token por token (se aplicável) e atualizar a UI de forma otimista sem bloquear o usuário esperando o servidor.
* **Timeouts & Resiliência:** Configurar timeouts rígidos em todas as APIs externas e de terceiros.
* **Paginação Eficiente:** Garantir paginação ou cursor-based pagination em todas as listagens pesadas de dados.

### 3. BACKEND & BANCO DE DADOS (Arquitetura)
* **Prevenção de N+1:** Auditar e corrigir consultas N+1 no ORM/banco de dados.
* **Indexação Estratégica:** Criar índices compostos e otimizados para as consultas e filtros mais comuns.
* **Camada de Cache (Redis):** Estruturar cache em memória (Redis) para dados altamente consultados ou de leitura frequente.
* **Filas para Processamento Assalariado:** Descarregar tarefas pesadas, lentas ou de background para workers em filas dedicadas.

### 4. INFRAESTRUTURA & DEPLOY (DevOps & Observabilidade)
* **CDN & Distribuição de Ativos:** Servir arquivos estáticos e assets através de uma CDN global.
* **Compressão de Tráfego:** Ativar compressão avançada (Brotli ou GZIP) no servidor/proxy reverso.
* **Proximidade Geográfica:** Alinhar a infraestrutura do servidor o mais próximo possível do banco de dados principal.
* **Balanceamento de Carga:** Distribuir o tráfego de forma eficiente entre múltiplas instâncias da aplicação.
* **Monitoramento & RUM:** Rastrear requisições lentas via OpenTelemetry e monitorar a velocidade real dos usuários (Real User Monitoring).

---

**Formato da resposta:** Seja direto, técnico e acionável. Não traga explicações óbvias; traga as diretrizes exatas de como aplicar isso no código ou na arquitetura do projeto atual.
