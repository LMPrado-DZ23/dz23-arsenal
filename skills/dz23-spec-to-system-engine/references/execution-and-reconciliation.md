# Execução e reconciliação

## O plano envelhece
Plano é hipótese. A cada fatia entregue, reconcilie: o que era previsto, o que aconteceu, o que muda.
Desvio **registrado** é gestão; desvio escondido é dívida.

## Ciclo de reconciliação (por fatia)
1. Estado real da fatia (`DONE` exige prova).
2. Matriz de requisitos atualizada.
3. Riscos revisados (algum caiu? surgiu novo?).
4. Caminho crítico recalculado — mudou?
5. Próxima fatia confirmada ou reordenada, com motivo.

## Desvio
```
DESVIO-02 · SL-04 (UI de export) atrasou 2 dias
Causa: contrato precisou de ajuste (campo `format`)
Impacto: caminho crítico +2d · buffer consumido 40%
Ação: SL-06 (relatório) movida para após o release; escopo do MVP mantido
```
Sem causa, impacto e ação, não é registro de desvio — é desculpa.

## Quando o escopo precisa cortar
Corte por **valor**, com o dono do produto, e registre em `CUT` com motivo. Nunca corte em silêncio um
requisito `Must`; nunca mantenha no plano algo que ninguém vai fazer.

## Handoff para execução
Antes de entregar para quem constrói (`templates/handoff.md`):
- fatia, `REQ` cobertos, contrato, DoD, dependência liberada, o que está fora;
- critério de aceite e como provar;
- risco conhecido e o que fazer se aparecer.

Handoff sem contrato e sem DoD não é handoff — é "vira-se".

## Após a entrega
- Requisito entregue sai de `READY` para `DONE` **com prova**.
- Requisito não entregue tem estado explícito (`DEFERRED`/`CUT`) e comunicação.
- Lição de estimativa: o intervalo errou por quê? Registre para calibrar o próximo.

## Saída
Matriz atualizada, desvios registrados, próximo passo definido e o que ficou fora com motivo.
