# Plano de fatias — <projeto>

## Regra
Toda fatia entrega **valor verificável de ponta a ponta**. Camada técnica é passo interno, não fatia.

| ID | Fatia (valor entregue) | REQs | Depende de | Dono | Tamanho | DoD | Estado |
|---|---|---|---|---|---|---|---|
| SL-01 | | REQ-001 | — | | 2–4 d | | TODO |
| SL-02 | | | SL-01 | | | | TODO |

## Definição de pronto (vale para todas)
- [ ] critério de aceite do(s) REQ demonstrado
- [ ] teste verde e citado
- [ ] erro/vazio tratados
- [ ] permissão/tenant verificado quando aplicável
- [ ] log/métrica do caminho novo
- [ ] rollback/flag quando o risco pede

## Dependências e caminho crítico
```
SL-01 → SL-02 → SL-04 → SL-07   (caminho crítico)
SL-03 e SL-05 em paralelo após SL-01
```
- Caminho crítico: <cadeia>
- Duração do caminho crítico: <intervalo + premissa>
- Paralelizável (fora do caminho): <lista>

## Contratos necessários
| Fronteira | Contrato | Dono | Consumidor | Status |
|---|---|---|---|---|

## Capacidade e buffer
- Pessoas × dias disponíveis:
- Reserva (20%):
- Buffer de integração (no fim do caminho crítico):

## Marcos
| Marco | Conteúdo | Data alvo | Critério |
|---|---|---|---|
| MVP | | | |
| Release | | | |

## Riscos do plano
| Risco | Impacto no caminho crítico | Ação |
|---|---|---|
