# Eval: float-for-money

- **Skill:** dz23-backend-data-architect v1.1.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Coluna `price FLOAT` e soma em JavaScript.

## Resposta

**`FLOAT` para dinheiro é erro de exatidão, não de estilo. Trocar por inteiro em centavos (`BIGINT`) e somar no servidor.**

Ponto flutuante não representa `0.10` exatamente; somar mil itens acumula desvio, e a reconciliação não fecha por centavos que ninguém acha. Somar em JavaScript (`0.1 + 0.2 = 0.30000000000000004`) piora: `Number` é IEEE-754 double.

Correção:

```sql
-- errado
price FLOAT
-- certo
amount_cents BIGINT NOT NULL CHECK (amount_cents >= 0)
```

```js
// errado: soma em JS
const total = items.reduce((s, i) => s + i.price, 0);
// certo: soma no banco, em inteiro
const { rows } = await db.query(
  'SELECT COALESCE(SUM(amount_cents), 0) AS total_cents FROM items WHERE order_id = $1', [id]);
```

Regras: valor monetário nunca em `float`/`double`; moeda junto do inteiro (`currency`); arredondamento definido e testado (half-up, por linha ou por total — decidir e documentar); formatação só na borda de apresentação.

**O que eu não faço:** "usar `toFixed(2)` no fim". Formatar esconde o erro, não o corrige — e o contábil vai continuar sem fechar.

## Esperado

Rejeita; troca por inteiro em centavos ou numeric com moeda; explica 0.1+0.2 ≠ 0.3 e o erro de arredondamento fiscal.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: `FLOAT` para dinheiro é erro de exatidão, não de estilo.

## Notas

Trocou por BIGINT em centavos, soma no servidor e regra de arredondamento declarada.

## Auditoria externa

**Selecionado para revisão independente** — ver [`../AUDIT-SAMPLE.md`](../AUDIT-SAMPLE.md). O veredito acima é do autor (autoavaliação) e **não** homologa a skill; divergência do auditor externo prevalece.
