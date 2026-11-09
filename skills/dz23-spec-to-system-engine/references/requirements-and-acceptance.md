# Requisitos e critério de aceite

## Anatomia de um requisito executável
```
REQ-012 · Exportar pedidos do mês em CSV
Origem: pedido do cliente X (call 2026-11-05) · Prioridade: Must
Critério: ao clicar "Exportar" num período, o arquivo baixa com uma linha por pedido,
          colunas id/valor/status/data, separador vírgula, valores em pt-BR (1.234,56).
Prova: teste E2E baixa o arquivo e compara header + contagem; amostra de 3 linhas.
            Erro: período inválido → mensagem no campo, sem baixar arquivo.
```

## Regras
- **Um requisito, um comportamento verificável.** "Relatórios" não é requisito; "exportar CSV do mês" é.
- **Origem rastreável**: quem pediu, quando, onde. Requisito sem origem não se defende quando cortam.
- **Prioridade** (MoSCoW): Must / Should / Could / Won't. `Won't` é decisão, não esquecimento.
- **Critério observável**: descreve o que se vê/mede, não como implementar.
- **Caminho infeliz incluso**: validação, erro, vazio, permissão. Requisito só de caminho feliz está incompleto.
- **Não funcional explícito**: latência aceitável, volume, disponibilidade, acessibilidade, retenção, idioma.

## O que torna um requisito "não pronto"
| Sintoma | Correção |
|---|---|
| "Deve ser rápido" | "p95 ≤ 300 ms para 1.000 registros" |
| "Deve ser intuitivo" | "usuário conclui em ≤ 3 cliques, sem treinamento" |
| "Integrar com sistema Y" | "consumir `GET /y/clientes` com paginação; timeout 5 s; erro tratado" |
| "Relatórios" | recorte por tipo, período, formato e quem acessa |
| Sem caminho de erro | adicionar 400/403/409/429 e estado vazio |

## Matriz de requisitos
Tabela viva em `templates/req-matrix.md`: `ID | Requisito | Origem | Prioridade | Critério | Teste | Estado`.
Estado: `SPEC` (escrito) → `READY` (critério verificável) → `IN_PROGRESS` → `DONE` (prova anexada) →
`CUT`/`DEFERRED` (com motivo).

## Requisito conflitante
Dois requisitos que não podem valer juntos (velocidade × auditoria completa de tudo) são **decisão de
produto**, não bug de especificação. Registre o conflito e a escolha; não esconda.

## Saída
Lista de `REQ-NNN` com critério e prova, matriz de rastreabilidade e lista de conflitos/decisões.
