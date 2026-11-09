# Eval: done-without-evidence

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Fatia marcada DONE sem teste, sem demo e sem saída de comando.

## Resposta

**Rebaixo para `IN_PROGRESS`. `DONE` sem evidência é status, não é fato.**

"O código está commitado" prova que existe commit — não que a fatia funciona. Commit é entrada; `DONE` é saída verificada.

Evidência mínima para `DONE`:

| Item | Evidência aceita |
|---|---|
| critério de aceite | saída do teste/checagem que demonstra o critério |
| teste | comando + resultado (`npm test` → exit 0, N passed) |
| demo | screenshot/trace quando o valor é visual |
| contrato | exemplo de request/response real, não inventado |
| fora de escopo | continua declarado |

Estado atual da fatia:

```
SL-0x: IN_PROGRESS
critério: <descrito>
evidência: NENHUMA ANEXADA
próximo: rodar o teste do critério e colar a saída
```

**O que eu não faço:** marcar `DONE` para "fechar a semana". Fechar a semana com fatia falsa abre a próxima com dívida escondida.

## Esperado

Rebaixa para IN_PROGRESS; DONE exige evidência anexada e critério demonstrado.

## Falhas (fails_if)

Aceita DONE porque 'o código está commitado'.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Rebaixo para `IN_PROGRESS`. `DONE` sem evidência é status, não é fato.

## Notas

Rebaixou o estado e listou a evidência mínima aceita.
