# Resultado da auditoria da amostra — Rodada 2

> **Aviso de independência (importante):** esta auditoria foi feita pelo **mesmo agente** que produziu as
> respostas. Não é auditoria independente no sentido estrito. O que foi feito: releitura adversarial dos 5
> registros **como se fosse outro leitor**, procurando defeito em vez de confirmar acerto. Serve como
> segunda passada; **não** substitui um revisor que nunca viu a sessão.

Data: 2026-11-09 · Método: leitura de `input`, `expected`, `fails_if` e resposta registrada; nenhum outro
registro de `evals-results/` foi consultado durante o julgamento.

## Vereditos

| # | Eval | Registrado (autor) | Auditoria | Divergência |
|---|---|---|---|---|
| 1 | `conflicting-requirements` | PASS | **PASS** | — |
| 2 | `circular-dependency` | PASS | **PASS** | — |
| 3 | `risky-integration-last` | PASS | **PASS** | — |
| 4 | `contract-breaking-change` | PASS | **PASS** | — |
| 5 | `float-for-money` | PASS | **PARTIAL** | ⚠️ **sim** |

**Resultado: 4 PASS, 1 PARTIAL, 0 FAIL.** O `float-for-money` foi rebaixado e o registro atualizado.

## Julgamento detalhado

### 1. `conflicting-requirements` — PASS

`expected`: *"Trata como decisão de produto: registra o conflito, apresenta trade-off e exige escolha com
dono; não esconde."*

| Cláusula | Atendida | Trecho |
|---|---|---|
| registra o conflito | ✅ | *"Isso é conflito real, não detalhe de implementação"* |
| apresenta trade-off | ✅ | tabela com 4 opções e consequência de cada |
| exige escolha com dono | ✅ | *"DECISÃO NECESSÁRIA: \<dono\> escolhe entre (a)… (b)…"* |
| não esconde | ✅ | *"O que eu não faço: prometer os dois sem consequência"* |

`fails_if` (*"Promete os dois sem consequência declarada"*): **não violado** — o custo é declarado em cada
linha da tabela.

**Defeitos que o autor deixou passar:**
- **D-1 (menor):** a resposta inclui *"PADRÃO SE NINGUÉM DECIDIR: (a)"*. Um padrão pré-declarado permite ao
  dono **não decidir** — o que enfraquece "exige escolha com dono". Se o padrão existe, ele deveria vir com
  prazo ("se não houver decisão até \<data\>, vale (a)") e com registro de quem foi silente.
- **D-2 (menor):** *"auditoria é requisito legal"* é inferência não marcada. O input diz "registrar tudo
  **para auditoria**", não que exista obrigação legal. A skill exige separar observado de inferido.

### 2. `circular-dependency` — PASS

`expected`: *"Detecta o ciclo, quebra a dependência ou funde as fatias; explica por que o plano atual é
impossível."*

| Cláusula | Atendida | Trecho |
|---|---|---|
| detecta o ciclo | ✅ | *"Ciclo detectado: SL-02 → SL-03 → SL-02"* |
| explica a impossibilidade | ✅ | *"não existe ordem que satisfaça as duas"* |
| quebra ou funde | ✅ | 3 saídas: fundir, quebrar por contrato, stub |

`fails_if` (*"Não percebe ou 'resolve' com paralelismo"*): **não violado** — recusa explicitamente.

**Defeitos:** nenhum. É o registro mais limpo dos cinco.

### 3. `risky-integration-last` — PASS

`expected`: *"Reordena: a primeira fatia ataca a integração mais arriscada (descobrir caro cedo), ou exige
spike antes."*

Atende as duas metades: reordena **e** exige spike com pergunta específica e critério de evidência.
`fails_if` (*"Mantém o risco no fim do cronograma"*): **não violado**.

**Defeito:**
- **D-3:** *"SL-01: spike da integração (**2 dias**)"* — número único, sem premissa, exatamente o
  anti-pattern que **outro eval da mesma skill** condena (`single-number-estimate`: *"Troca por intervalo
  com premissas"*).

  **Correção de escopo do achado:** a regra **já existe** na skill — `SKILL.md` L55: *"Estimativa é
  intervalo com premissas; número único sem premissa é ficção"*, e L36 repete no passo PLANEJAR. Portanto
  **não é lacuna de regra**: é lapso da resposta. Não há o que corrigir na skill; o registro fica como
  evidência de que a skill tem a regra e a resposta não a aplicou.

### 4. `contract-breaking-change` — PASS

`expected`: *"Recusa aplicar direto; propõe aditivo (responder os dois campos), deprecação anunciada, janela
e instrumentação de uso antes de remover."*

Quatro de quatro: recusa ✅ · ambos os campos ✅ · deprecação + anúncio ✅ · instrumentação por versão de app
antes de remover ✅. `fails_if` (*"Aplica a renomeação em um passo e declara pronto"*): **não violado**.

**Defeito:**
- **D-4:** *"manter por 1 release como campo nulo? **NÃO** — campo nulo quebra mais que ausente"* é afirmação
  apresentada como fato, sem evidência — e é discutível: para cliente tipado, `null` declarado costuma ser
  mais seguro que campo ausente (que quebra validação de schema). A skill exige separar observado de
  inferido; aqui virou regra sem prova.

### 5. `float-for-money` — **PARTIAL** (divergência)

`expected`: *"Rejeita; troca por inteiro em centavos ou numeric com moeda; explica `0.1+0.2 ≠ 0.3` **e o
erro de arredondamento fiscal**."*

| Cláusula | Atendida | Evidência |
|---|---|---|
| rejeita float | ✅ | *"`FLOAT` para dinheiro é erro de exatidão, não de estilo"* |
| troca por inteiro/numeric | ✅ | `amount_cents BIGINT` + `currency` |
| explica `0.1+0.2 ≠ 0.3` | ✅ | *"`0.1 + 0.2 = 0.30000000000000004`"* |
| **erro de arredondamento fiscal** | ⚠️ **parcial** | *"arredondamento definido e testado (half-up, por linha ou por total — decidir e documentar)"* — define **como** arredondar, não explica **a consequência fiscal** (divergência entre valor da linha e total apurado, impacto em nota/apuração) |

`fails_if` (*"Aceita float ou sugere apenas 'arredondar no final'"*): **não violado** — rejeita `toFixed`
explicitamente.

Por que **PARTIAL** e não PASS: o `expected` lista o arredondamento fiscal como item próprio, e a resposta
cobre o mecanismo sem o efeito. Um terço do valor do eval está em fazer o leitor ver **por que** o contador
não fecha — e isso não está lá.

## Defeito de infraestrutura encontrado na auditoria

**Os registros não continham `fails_if`.** O template do `record-eval.py` gravava cenário, resposta,
esperado, avaliação e notas — mas **não** a seção de falha. Consequência prática: para julgar a segunda
dimensão o auditor precisava abrir o `evals.json`, contradizendo a própria instrução da amostra
(*"julgue por input, expected, fails_if e pela resposta"*).

**Corrigido nesta rodada:**
- `record-eval.py`: template agora inclui `## Falhas (fails_if)`, preenchido do `evals.json`.
- Backfill aplicado aos **25 registros** existentes.

## O que esta auditoria NÃO prova

- Não prova independência: mesmo autor.
- Não cobre os outros 10 registros da Rodada 2.
- Não cobre os 103 evals sem resultado.
- A divergência encontrada (1 de 5) **não** permite extrapolar taxa de erro para os outros 10 — 20% nesta
  amostra é indício, não medida.

## Recomendação

1. Os 4 PASS continuam **não homologados** até revisão por outro agente (Claude, sessão nova).
2. `float-for-money` foi rebaixado e o registro corrigido — ver o arquivo.
3. **D-3** é o defeito mais instrutivo: a regra *"estimativa é intervalo"* **já está escrita** na skill e a
   resposta a violou. Prova que ter a regra não garante aplicá-la — e que eval de um caso não pega violação
   de regra vizinha. Um eval que cruze "spike" com "estimativa" pegaria; hoje não existe.
