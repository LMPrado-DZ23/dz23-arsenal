# Resultados de execução de evals

Histórico **versionado** de evals executados de verdade. Um arquivo por execução:
`<skill-curto>/<data>-<eval-id>.md`.

## Por que existe

`evals/evals.json` é a **especificação** do comportamento esperado. Este diretório é a **prova** de que
alguém executou o cenário e julgou o resultado. Sem arquivo aqui, o eval é `NOT_TESTED` — não importa
quantos cenários existam.

## Como registrar

```bash
# manual, com a resposta em arquivo
python scripts/record-eval.py \
  --skill dz23-devops-cloud-deployer \
  --eval-id secret-in-image \
  --verdict PASS \
  --response-file /tmp/resposta.txt \
  --method "execucao real com Docker" \
  --notes "build + docker history --no-trunc"
```

## Regras

1. **Veredito só com evidência.** `PASS` exige trecho literal da resposta e/ou saída de comando.
2. **`NOT_RECOVERED` é resposta válida** quando o artefato da execução não existe mais. Não reconstrua de
   memória.
3. **`BLOCKED` não é falha**: é eval que exige dependência ausente (Ghidra, cluster). Declare a dependência.
4. Um arquivo por execução — reexecução cria arquivo novo com a data do dia, preservando o histórico.

## Estado

Ver `python scripts/run-evals.py --report` e a seção "Status de evals" no `ROADMAP.md`.
