# Amostra para auditoria externa

**5 de 15** registros da Rodada 2 foram separados para revisão por outro agente (Claude, em sessão nova, sem o histórico desta).

## Por que essa amostra existe

Os 15 registros desta rodada têm `method: auto` — o mesmo agente produziu a resposta e julgou. A rodada anterior da skill de performance mostrou o tamanho do problema: a autoavaliação deu 3/3 PASS e a reauditoria encontrou **5 defeitos**, três deles que o autor não viu na primeira releitura.

Por isso: **auto-avaliação não homologa**. Estes 5 vão para auditoria externa.

## Como auditar

1. Abrir a sessão nova, carregar a skill correspondente.
2. Ler o arquivo de registro e o `evals/evals.json` da skill.
3. Responder ao `input` **sem** olhar o registro.
4. Comparar a própria resposta com `expected` e `fails_if`.
5. Emitir veredito. Divergência do meu veredito → o do auditor vale.

## Os 5 selecionados

| # | Registro | Veredito do autor | Por que foi escolhido |
|---|---|---|---|
| 1 | [`spec/2026-11-09-conflicting-requirements.md`](spec/2026-11-09-conflicting-requirements.md) | PASS | Conflito real com decisão de produto — testa se a skill devolve a escolha ao dono em vez de prometer os dois. |
| 2 | [`spec/2026-11-09-circular-dependency.md`](spec/2026-11-09-circular-dependency.md) | PASS | Ciclo em plano — testa se a skill reconhece impossibilidade em vez de 'resolver com paralelismo'. |
| 3 | [`spec/2026-11-09-risky-integration-last.md`](spec/2026-11-09-risky-integration-last.md) | PASS | Reordenação por risco — testa se a skill exige spike com pergunta específica, não exploração aberta. |
| 4 | [`backend/2026-11-09-contract-breaking-change.md`](backend/2026-11-09-contract-breaking-change.md) | PASS | Compatibilidade de contrato — testa se a skill exige aditivo + instrumentação antes de remover campo. |
| 5 | [`backend/2026-11-09-float-for-money.md`](backend/2026-11-09-float-for-money.md) | PASS | Exatidão monetária — testa se a skill troca float por inteiro e recusa formatar para 'resolver'. |

## Critério de escolha

Não escolhi os mais fáceis. Peguei os que **exigem julgamento**: conflito sem resposta óbvia, impossibilidade estrutural, reordenação por risco, compatibilidade de contrato publicado e exatidão monetária. Se a skill estivesse errada, seria nesses que o erro apareceria.

## O que o auditor deve marcar se o meu PASS estiver errado

- Resposta que caiu em `fails_if` → **FAIL** (o `fails_if` manda, não a intenção).
- Resposta que satisfez `expected` parcialmente → **PARTIAL**, com a lacuna nomeada.
- Registro sem trecho literal que sustente o veredito → **FAIL** (o trecho é obrigatório).
