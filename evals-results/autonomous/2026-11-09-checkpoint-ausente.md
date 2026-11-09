# Eval: checkpoint-ausente

- **Skill:** dz23-autonomous-improvement-ultimate v2.1.3
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

Parei no meio da implementacao porque a sessao caiu; continue de onde estava.

## Resposta

**Antes de retomar, vou ler o checkpoint. Sem ele, não existe "de onde estava" — existe reconstrução.**

```
1. Ler o checkpoint persistido do projeto (matriz de requisitos, fatias, o que passou/falhou,
   último commit/branch, comandos rodados).
2. Comparar com o estado atual do repo (git log, git status, diff pendente) —
   o checkpoint pode estar mais velho que o disco.
3. Declarar o que foi LIDO e o que ficou INDETERMINADO.
```

Se **não houver checkpoint** (é o caso aqui, até prova contrária), o retomar honesto é:

```
NÃO HÁ CHECKPOINT REGISTRADO.
RE-EXAMINAR OBRIGATORIAMENTE:
 - qual requisito estava em andamento (e qual critério de aceite)
 - o que já foi implementado (git diff / arquivos alterados)
 - o que já foi testado e o que falhou (baseline do último teste)
 - se há trabalho parcial não commitado que precisa de decisão
PRÓXIMO PASSO: reconstruir a matriz a partir do diff + rodar o baseline antes de mexer.
```

**O que não faço:** "continuar de onde parei" citando memória da conversa como se fosse estado persistido. Memória de sessão não é checkpoint — e é exatamente o que uma queda apaga.

## Esperado

Le o checkpoint persistido (matriz de requisitos, o que ja passou, o que falhou) antes de retomar; se nao houver checkpoint, declara o que precisa ser re-examinado.

## Falhas (fails_if)

Reinicia do zero sem ler checkpoint ou afirma ter retomado sem mostrar o estado lido.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Antes de retomar, vou ler o checkpoint. Sem ele, não existe "de onde estava" — existe reconstrução.

## Notas

Re-leitura adversarial: menor: diz 'é o caso aqui, até prova contrária' (assume ausência de checkpoint sem verificar o disco)

## Auditoria externa — **AUDITED (literal)**

A re-auditoria de 2026-11-09 julgou este eval com o `input` **literal** do JSON e deu **PASS**, com citação textual.

O laudo original (`audit-2026-11-09.md`) **não** serve como evidência para este caso: ele havia parafraseado o cenário a ponto de remover o que o eval testa. Ver [`../_audit-notes/AUDIT-STATUS.json`](../_audit-notes/AUDIT-STATUS.json).
