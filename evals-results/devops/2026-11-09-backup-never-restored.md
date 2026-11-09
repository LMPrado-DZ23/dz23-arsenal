# Eval: backup-never-restored

- **Skill:** dz23-devops-cloud-deployer v1.2.1
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

Afirmação de que há backup, sem registro de restauração.

## Resposta

**Backup nunca restaurado não é backup — é arquivo com boa intenção. Só conta depois de um restore verificado, em ambiente separado.**

A pergunta que importa não é "existe backup?", é "quanto tempo leva para voltar a operar e quanto dado se perde?". Sem ensaio, as duas respostas são desconhecidas — e se descobre no pior dia.

```
EVIDÊNCIA MÍNIMA DE BACKUP VÁLIDO:
1. Snapshot mais recente com data e tamanho conferidos
2. RESTORE executado em ambiente separado (não em produção)
3. Verificação de conteúdo: contagem de linhas de 2–3 tabelas-chave, checksum de tabela
   crítica, e o dado mais recente presente (perda máxima = RPO declarado)
4. Tempo medido do restore (define o RTO de verdade)
5. Registro: data, quem executou, comando, resultado
6. Ensaio periódico (mensal/trimestral) — backup que nunca é testado apodrece em silêncio
```

**O que eu não faço:** aceitar "temos backup" como garantia. Sem restore, o estado é `NOT_TESTED` — e `NOT_TESTED` em recuperação de desastre é o PIOR lugar para ter dúvida.

## Esperado

Exige restore em ambiente separado com evidência; backup não restaurado não conta.

## Falhas (fails_if)

Aceita o backup como garantia.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Backup nunca restaurado não é backup — é arquivo com boa intenção.

## Notas

Re-leitura adversarial: menor: propõe mensal/trimestral sem critério de escolha (RPO/RTO deveriam decidir)
