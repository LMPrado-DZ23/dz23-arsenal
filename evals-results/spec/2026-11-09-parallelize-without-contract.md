# Eval: parallelize-without-contract

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

Dois agentes começam API e UI no mesmo dia, sem contrato escrito.

## Resposta

**Paralelizar API e UI no mesmo dia sem contrato escrito é retrabalho agendado — bloqueio o paralelo.**

Dois agentes partindo juntos vão inventar dois payloads, dois formatos de erro e duas noções de timeout. O encontro acontece no dia da integração, quando o custo de mudar já é alto.

Contrato mínimo antes de liberar o paralelo:

```
ENDPOINT: GET /orders?cursor=<c>&status=<s>
RESPOSTA 200: { items: [{id, amount_cents, status, created_at}], next_cursor: string|null }
ERROS: 400 (cursor inválido) · 401/403 · 429 (Retry-After) · 500 (corpo {code,message})
TIMEOUT: 3 s no cliente; 2 s no servidor
PAGINAÇÃO: cursor opaco, limite máx 100
VERSÃO: v1 — campo novo só aditivo
DONO: backend define o schema · consumidor: UI
```

**O que eu não aceito:** "começa e a gente ajusta depois". Ajuste de contrato depois = duas implementações alteradas + testes refeitos.

Com o contrato assinado, o paralelo é seguro e eu libero — com mock do contrato do lado da UI.

## Esperado

Bloqueia o paralelo até fechar contrato (payload, erro, timeout, versão) e define dono/consumidor.

## Falhas (fails_if)

Aceita o paralelo e sugere 'ajustar depois'.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Paralelizar API e UI no mesmo dia sem contrato escrito é retrabalho agendado — bloqueio o paralelo.

## Notas

Bloqueou o paralelo e entregou contrato mínimo com erros, timeout e dono.
