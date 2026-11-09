# Consolidação das cinco fontes

- **Gemini**: baseline, priorização de segurança e dados, testes determinísticos, anti-estagnação após 3 hipóteses e checkpoint a cada 5 ciclos.
- **Claude**: precedência do /goal, estados explícitos, matriz de aceite, revisão adversarial e formato de relatório detalhado.
- **Manus**: checagem de ferramentas disponíveis, proteção de alterações, contratos de aceite, risco de produção e retomada sem poluir o repositório.
- **DeepSeek**: arquivo recebido contém somente o trecho final de ativação e separação de PASS/FAIL/NOT_RUN/BLOCKED; não foi possível recuperar conteúdo anterior a partir desse arquivo.
- **ChatGPT**: integração com skills especializadas, critérios de parada, controle de escopo, testes por camada e checkpoints.

## Conflitos reconciliados
- Não usar “zero erros” como prova absoluta; exigir gates verificáveis.
- Não exigir dark mode, E2E ou deploy em todo projeto indiscriminadamente: aplicar por contexto e justificar N/A.
- Não criar loops sem limite nem afirmar execução 24/7 sem runtime real.
- Não confundir bloqueio externo com necessidade de aprovação ou limite de sessão.
- `HIGH` aberto impede VERIFIED_COMPLETE; itens MEDIUM/LOW exigem aceite explícito ou pendência documentada.
