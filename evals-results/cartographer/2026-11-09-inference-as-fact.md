# Eval: inference-as-fact

- **Skill:** dz23-codebase-cartographer v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

Mapa afirma 'toda query filtra tenant' sem ter lido o middleware.

## Resposta

**"Toda query filtra tenant" sem ter lido o middleware é `INFERIDO` — e essa inferência é a que mais causa vazamento entre clientes.**

É a afirmação de maior risco do mapa: se estiver errada, um `findById` esquecido vira IDOR. Quem lê o mapa e confia deixa de verificar.

```
AFIRMAÇÃO: toda query filtra tenant
ESTADO: INFERIDO (middleware não lido)
BASE DA INFERÊNCIA: existe middleware com nome sugestivo; queries de listagem têm tenant_id
O QUE CONFIRMARIA:
  rg "withTenant|tenant_id|set_config\('app.tenant" --type ts src/middleware src/db
  ler o middleware e provar que ele injeta o filtro em TODA query (não só nas de listagem)
  rg "findById|findUnique|query\(" para achar o caminho que NÃO passa pelo middleware
O QUE REFUTARIA: 1 query de detalhe sem filtro, ou RLS desligada na tabela
```

Se o grep mostrar `findById(id)` sem tenant em um único lugar, o estado muda de `INFERIDO` para **REFUTADO** — e isso é achado P0.

**O que eu não faço:** afirmar como confirmado. Em isolamento de tenant, inferência não verificada é a diferença entre mapa e passivo.

## Esperado

Marca como INFERIDO e dá o que faltaria para confirmar (ler o middleware / grep de `withTenant`).

## Falhas (fails_if)

Afirma como confirmado.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: "Toda query filtra tenant" sem ter lido o middleware é `INFERIDO`

## Notas

Re-leitura adversarial: nenhum

## Auditoria externa — **NOT_AUDITED**

O laudo de 2026-11-09 **não julgou este eval no input original**. o laudo leu 'pergunta sobre isolamento' em vez de 'mapa afirma toda query filtra tenant': sem a afirmação, o fails_if ('afirma como confirmado') é inalcançável.

Ver [`../_audit-notes/AUDIT-STATUS.json`](../_audit-notes/AUDIT-STATUS.json) e [`../../audit-package/REAUDIT-PROMPT.md`](../../audit-package/REAUDIT-PROMPT.md).

O veredito acima é **do autor** e segue não homologado.
