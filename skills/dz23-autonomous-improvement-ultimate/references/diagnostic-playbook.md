# Playbook de diagnóstico e revisão adversarial

1. **Reproduzir:** isolar entrada, ambiente, versão e resultado esperado vs observado.
2. **Diferenciar:** comparar baseline, commits, configurações, dependências, rede, banco e permissões.
3. **Localizar:** rastrear chamadas e estados; coletar logs redigidos; evitar exposição de tokens.
4. **Hipótese falsificável:** definir teste que distingue causa de coincidência.
5. **Correção:** pequena e estrutural; teste de regressão antes/depois quando viável.
6. **Ataque:** inputs malformados, campos vazios, permissões insuficientes, tenants distintos, concorrência, retries, timeouts, falha de rede, refresh de página, acessibilidade e responsividade.
7. **Verificação:** teste focal, adjacentes, suíte relevante, build e smoke.
8. **Estagnação:** 3 falhas da mesma hipótese -> abandonar hipótese, bisect/instrumentar/inspecionar contratos; se dependência externa, BLOCKED_BY_EXTERNAL_DEPENDENCY.

Evite criar bugs novos com 'melhorias' não solicitadas. Riscos não reproduzidos devem ser marcados como hipótese, não defeito confirmado.
