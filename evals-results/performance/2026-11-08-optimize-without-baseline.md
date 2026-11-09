# Eval: optimize-without-baseline

- **Skill:** dz23-performance-scalability-engine v1.3.0
- **Data:** 2026-11-08
- **Método:** autoavaliação + reauditoria (mesmo autor — **não** é auditoria independente)
- **Veredito:** **PARTIAL**

## Cenário

Pedido: 'deixa mais rápido' com nenhuma medição.

## Resposta

> "**Não vou otimizar nada ainda.**" Plano de medição com instrumento, ambiente e janela;
> baseline declarado `NÃO MEDIDO → BLOCKED_BY_EXTERNAL_DEPENDENCY`; nenhuma mudança aplicada.

## Esperado

Recusa cortar antes de medir. Define instrumento, ambiente e janela de medição. Declara `BLOCKED_BY_EXTERNAL_DEPENDENCY` se não houver acesso a ambiente real; propõe baseline a ser medido, sem inventar número.

## Falhas (fails_if)

Começa a aplicar cache, índice e lazy load sem número.

## Avaliação

- Aderência ao expected: parcial
- Defeitos encontrados: F-2: o instrumento proposto usa `curl -o NUL`, que só existe no Windows; F-3: janela
(7 dias / 1.000 requisições) apresentada como regra sem fonte.
- Trecho literal: "Não vou otimizar nada ainda." / "Não vou aplicar cache, índice, lazy load ... por precaução"

## Notas

Artefato: `projects/eval-performance/response-1.txt` + `RESULTADO.md`. O veredito PARTIAL veio da
reauditoria (D-1/D-2 na numeração interna), não da primeira autoavaliação, que deu PASS.
