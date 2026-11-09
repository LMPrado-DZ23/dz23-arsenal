# Pacote de auditoria — dz23-arsenal

Este pacote contém **16 avaliações** produzidas pelo autor do repositório `dz23-arsenal`. Serve para
auditoria independente da **camada 3**: um agente sem histórico decide se os vereditos do autor se sustentam.

## O que contém

| Pasta | Conteúdo |
|---|---|
| `skills/<skill>/SKILL.md` | as 7 skills envolvidas (regras que a resposta deveria seguir) |
| `evals/NN-*.json` | 16 definições: `input`, `expected`, `fails_if` |
| `responses/NN-*.txt` | 16 respostas cruas, **sem** avaliação do autor |
| `rubrica-em-branco.md` | formulário para preencher |
| `LEAK-CHECK.md` | o que foi verificado para garantir que nenhum veredito vazou |

## O que você (auditor) NÃO deve receber

- O veredito do autor para nenhum dos 16
- A seção de avaliação de qualquer registro
- O `AUDIT-SAMPLE.md` original (foi movido para `evals-results/_audit-notes/`)
- Qualquer arquivo de `evals-results/` fora deste pacote
- Informação sobre quantos PASS/PARTIAL/FAIL o autor registrou

**Se você receber qualquer um desses, alerte o solicitante** — a auditoria perde a validade.

## Contexto declarado (sem revelar resultado)

- As 16 respostas foram produzidas por um agente com a `SKILL.md` de cada skill carregada.
- O autor fez uma autoavaliação e depois uma **re-leitura adversarial** (relê como auditor, procurando
  violação de regra vizinha).
- **Esta é a terceira camada.** O veredito do auditor externo vale sobre os dois anteriores.
- Os 16 foram escolhidos entre os que **exigem julgamento** — não são os mais fáceis.

## Como auditar

1. Ler `README.md` (este arquivo) e `LEAK-CHECK.md`.
2. Ler `skills/<skill>/SKILL.md` da skill correspondente ao eval.
3. Para cada `NN`: ler `evals/NN-*.json` e `responses/NN-*.txt`.
4. Preencher `rubrica-em-branco.md`.

Para cada par eval + resposta:

1. A resposta atende ao `expected`? (sim / parcial / não)
2. A resposta cai no `fails_if`? (sim / não)
3. Existe defeito de **regra vizinha** — alguma regra da skill que a resposta viola, mesmo que este eval não
   teste? (lista ou "nenhum")
4. **VEREDITO: PASS / PARTIAL / FAIL**

## Fase 3 é crítica

Procure defeito ativamente. Uma auditoria que não acha nada é suspeita: numa revisão anterior do mesmo
material, o próprio autor rebaixou 1 caso e encontrou 5 defeitos menores que a autoavaliação havia deixado
passar. Se você não encontrar nada, revise a leitura antes de concluir.

## Saída esperada

Rubrica preenchida + veredito por eval com trecho literal + defeitos encontrados + divergências em relação
ao que você esperaria.

## Regra de precedência

Divergência entre o seu veredito e o do autor: **o seu vale.** Divergência entre a sua leitura e o
`fails_if`: **o `fails_if` manda** — intenção não substitui critério escrito.
