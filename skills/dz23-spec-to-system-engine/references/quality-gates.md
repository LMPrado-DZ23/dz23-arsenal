# Quality gates — evidência, não promessa

| Gate | PASS quando | Evidência mínima |
|---|---|---|
| Enquadramento | problema, atores, resultado, restrições e fora de escopo escritos | documento de spec |
| Requisitos | todo `REQ` com origem, prioridade e critério verificável | matriz preenchida |
| Prova | todo `REQ` tem teste/comando/demo definido | coluna `Teste` preenchida |
| Decomposição | toda fatia entrega valor de ponta a ponta, com dono e DoD | plano de fatias |
| Contratos | toda fronteira paralela tem contrato com erro/timeout | contrato versionado |
| Riscos | risco alto com mitigação, dono e prazo; incerteza com spike | registro de risco |
| Plano | caminho crítico e ordem definidos; estimativa com premissa | plano + grafo |
| Rastreabilidade | `REQ → fatia → teste → evidência` sem órfão | matriz |
| Execução | `DONE` só com prova; desvio registrado | matriz + log de desvio |

**Estados:** `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`, `BLOCKED_BY_EXTERNAL_DEPENDENCY`. Especificação
entregue sem prova possível é `NOT_TESTED`, nunca `PASS`.

## Severidade

**BLOCKER (não entrega a spec):**
- Requisito sem critério verificável (não dá para provar).
- Fatia sem dono ou sem definição de pronto.
- Fronteira paralela sem contrato de interface.
- Requisito do usuário removido sem registro de `CUT` e aprovador.
- Dependência circular no plano.
- `DONE` declarado sem evidência.
- Escopo sem fora de escopo escrito em entrega com prazo.

**MAJOR (entrega com ressalva):**
- Estimativa sem premissa.
- Requisito não funcional ausente (latência, volume, a11y).
- Spike sem pergunta/prazo.
- Caminho crítico não identificado.
- Caminho de erro/permissão não especificado.
- Risco alto sem dono.

**MINOR (registra e segue):**
- Nome de fatia técnico em vez de valor.
- Matriz sem coluna de evidência.
- ADR de decisão reversível faltando (uma linha basta).

## Matriz de verificação por artefato
- **Spec**: problema, atores, resultado, restrições, fora de escopo, riscos, sucesso.
- **Requisitos**: unicidade do `REQ`, critério observável, prioridade, conflito identificado.
- **Fatias**: valor ponta a ponta, tamanho, dependência, DoD, rollback.
- **Contratos**: entrada/saída/erro/timeout/versionamento/dono.
- **Plano**: ordem, caminho crítico, capacidade, buffer, marcos.
- **Rastreabilidade**: nenhum `REQ` órfão, nenhuma fatia sem `REQ`, teste ligado a `REQ`.

## Checklist final
- [ ] Problema e resultado esperado escritos, com quem pediu.
- [ ] Fora de escopo explícito.
- [ ] Todo `REQ` com critério verificável e prova.
- [ ] Conflitos de requisito registrados com decisão.
- [ ] Fatias verticais com dono, tamanho e DoD.
- [ ] Contratos fechados nas fronteiras paralelas.
- [ ] Riscos com dono/prazo; spikes com pergunta.
- [ ] Caminho crítico e ordem definidos.
- [ ] Estimativas em intervalo com premissas.
- [ ] Matriz de rastreabilidade sem órfão.
- [ ] O que não foi definido está declarado.
