# Verificação de vazamento

## O que foi checado

| Checagem | Resultado |
|---|---|
| `**Veredito:**` (padrão do registro do autor) em qualquer arquivo | **0** |
| `## Avaliação` **preenchida** em `responses/` ou `evals/` | **0** |
| `Aderência ao expected` preenchida em `responses/` ou `evals/` | **0** |
| Verdict como resultado nas 16 respostas | **0** |

### Onde os termos aparecem e por quê (não é vazamento)

| Arquivo | Ocorrências | Natureza |
|---|---|---|
| `rubrica-em-branco.md` | 16 × `## Avaliação`, 16 × `Aderência ao expected` | **campos em branco** do formulário (`[sim / parcial / não]`), não preenchimento |
| `README.md` | 1 × `PASS / PARTIAL / FAIL` | **escala de veredito** que o auditor deve usar |
| `LEAK-CHECK.md` | este bloco | meta-documentação |

Nenhum arquivo do pacote contém o veredito que o autor atribuiu a qualquer dos 16 evals.

## As 4 ocorrências de termos de estado (todas legítimas)

O `grep` de `PASS|PARTIAL|FAIL` retorna 4 linhas no pacote. **Nenhuma é veredito do autor** — todas são
conteúdo da própria resposta, que fala sobre os estados previstos pela skill:

| Arquivo | Linha | Por que não é vazamento |
|---|---|---|
| `responses/12-autonomous-checkpoint-ausente.txt` | `PRÓXIMO PASSO: ...` | casa a substring **"PASS"O** (palavra "passo"), não um veredito |
| `responses/13-autonomous-blocked-secret.txt` | *"o relatório diz `PASS`"* | a resposta explica o que **não** faria: declarar `PASS` sobre mock |
| `responses/13-autonomous-blocked-secret.txt` | *"e `PASS` sobre ele"* | idem — regra da skill sobre mock permanente |
| `responses/21-ultimate-pro-max-prova-visual.txt` | *"o estado vira `PASS` (ou `FAIL`, com o defeito nomeado)"* | define quando o estado muda; não diz qual é o estado deste eval |

**Decisão:** manter as 4. Removê-las alteraria a evidência (a resposta foi escrita assim), o que é pior que a
ambiguidade do `grep`. O que importa — o veredito do autor — não está no pacote.

## O que foi removido na extração

- Título do registro (`# Eval: ...`) — poderia conter estado.
- Seções `## Avaliação`, `## Notas`, `## Auditoria externa`.
- Linhas iniciadas por `Veredito`, mesmo que aparecessem dentro da resposta.

## Verificação independente

```bash
grep -rn '\*\*Veredito:\*\*' audit-package/          # esperado: 0
grep -rn '## Avaliação' audit-package/                    # esperado: 0
grep -rn 'Aderência ao expected' audit-package/           # esperado: 0
```
