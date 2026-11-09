# Context brief e orçamento de leitura

## O problema
Despejar 3.000 linhas de código no contexto do próximo agente não é transferir conhecimento — é transferir custo. Brief bom é **índice com ponteiros**, não resumo.

## Regra do orçamento
Declare o teto antes de escrever:
```
ORÇAMENTO: ≤ 120 linhas / ≤ 8 arquivos citados
```
Estourou: corte para os ponteiros essenciais. Brief que não cabe não será lido inteiro — será ignorado.

## Anatomia do brief
```markdown
# CONTEXT BRIEF — <repo> @ <sha curto> — <data>

## Pergunta
<mudar X? avaliar impacto? onboarding?>

## 30 segundos
<3–5 linhas: o que é o sistema, stack real, onde começa>

## Onde mexer
- <arquivo:linha> — <por que é ali>
- <arquivo:linha> — <o que já existe>

## O que NÃO tocar
- <arquivo:linha> — <motivo, risco>

## Como validar
- `<comando>` — <o que prova>
- <área sem teste> → validação manual em <tela/fluxo>

## Convenções que valem aqui
- <regra> — exemplo em <arquivo:linha>

## Armadilhas
- <armadilha> — evidência em <arquivo:linha>

## Lacunas conhecidas
- <o que eu não verifiquei> — como verificar
```

## Princípios
1. **Ponteiro > conteúdo.** "A lógica está em `src/services/order.ts:88-140`" vale mais que colar o trecho.
2. **Ordenar por utilidade**, não por estrutura de pasta.
3. **Dizer o que não foi verificado** — lacuna declarada é mais útil que lacuna escondida.
4. **Zero adjetivo.** "Código confuso" não ajuda; "função de 240 linhas em `x.ts:12`" ajuda.
5. **Atualizável em 1 minuto**: se revalidar o brief custa mais que refazer, ele morre.

## O que não entra no brief
- Histórico de commit completo.
- Lista de todas as dependências.
- Arquitetura ideal que o repo não tem.
- Opinião sobre estilo (isso é de outra skill).

## Quando o brief é grande de verdade
Se o sistema é grande e a pergunta é ampla, produza **brief raiz + briefs por módulo**, e o raiz aponta para os outros. Nunca um documento de 400 linhas: ninguém lê e ele apodrece.

## Saída
`context-brief.md` dentro do orçamento declarado, com ponteiros, lacunas e comando de validação.
