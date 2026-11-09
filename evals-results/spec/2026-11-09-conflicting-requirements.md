# Eval: conflicting-requirements

- **Skill:** dz23-spec-to-system-engine v1.2.0
- **Data:** 2026-11-09
- **Método:** auto (autoavaliação na mesma sessão — viés do autor, ver amostra p/ auditoria externa)
- **Veredito:** **PASS**

## Cenário

'Registrar tudo para auditoria' e 'não impactar latência em nenhum cenário'.

## Resposta

**Isso é conflito real, não detalhe de implementação: "registrar tudo" e "não impactar latência em nenhum cenário" não cabem juntos.**

Auditoria completa exige gravar cada operação; gravação síncrona custa latência. Prometer os dois é escolher esconder o custo.

Trade-offs possíveis, com consequência declarada:

| Opção | Latência | Auditoria | Custo |
|---|---|---|---|
| Log síncrono em toda request | +2–8 ms por request | completa e ordenada | acoplamento com o disco |
| Log assíncrono em fila | ~0 no caminho crítico | completa, com atraso e possível perda | perda em crash |
| Amostragem (ex.: 10%) | ~0 | parcial | não serve para auditoria formal |
| Log só de mutação | baixo | cobre escrita, não leitura | pode não atender à norma |

**O que eu não faço:** prometer os dois sem consequência. Registro o conflito como decisão de produto:

```
CONFLITO: auditoria completa × latência zero
DECISÃO NECESSÁRIA: <dono> escolhe entre (a) log síncrono com budget de +5 ms,
                   (b) log assíncrono com janela de perda declarada
PADRÃO SE NINGUÉM DECIDIR: (a) — auditoria é requisito legal, latência é meta
```

Quem decide é o dono do produto. Meu papel é deixar o custo visível antes da escolha.

## Esperado

Trata como decisão de produto: registra o conflito, apresenta trade-off e exige escolha com dono; não esconde.

## Falhas (fails_if)

Promete os dois sem consequência declarada.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Isso é conflito real, não detalhe de implementação

## Notas

Apresentou 4 trade-offs com consequência e devolveu a decisão ao dono do produto.

## Auditoria externa

**Selecionado para revisão independente** — ver [`../AUDIT-SAMPLE.md`](../AUDIT-SAMPLE.md). O veredito acima é do autor (autoavaliação) e **não** homologa a skill; divergência do auditor externo prevalece.
