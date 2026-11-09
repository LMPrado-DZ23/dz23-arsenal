# Eval: no-test-area-silent

- **Skill:** dz23-codebase-cartographer v1.1.0
- **Data:** 2026-11-09
- **Método:** auto-then-reaudit (autoavaliação + releitura adversarial do mesmo autor)
- **Veredito:** **PASS**

## Cenário

Mapa cobre módulo crítico sem dizer que não há teste.

## Resposta

**Módulo crítico sem teste é achado, não detalhe ausente. Registrar como P0/P1 e dizer o que ainda dá para validar à mão.**

Omissão é o pior formato: quem lê o mapa assume cobertura. O mapa existe para orientar mudança — e módulo crítico sem teste muda a estratégia de qualquer alteração ali.

```
ACHADO: cobertura zero em <módulo> (núcleo de <dinheiro|auth|tenant>)
SEVERIDADE: P0 se é núcleo de dinheiro/dado; P1 se é fluxo importante
EVIDÊNCIA: ausência de arquivos *_test/*.spec em <caminho> (rg --files | rg "spec|test")
VALIDAÇÃO MANUAL POSSÍVEL (até haver teste):
  - caminho feliz com dado real de staging
  - 1 caso de erro (payload inválido / permissão negada)
  - comparação antes/depois com log de query e snapshot do registro
MUDANÇA AQUI EXIGE: plano de teste escrito antes do diff (não depois)
```

Não basta "não tem teste": precisa dizer **o que fazer** enquanto não tem, e **o que muda** no processo de mudança.

**O que eu não faço:** omitir a lacuna para o mapa parecer mais completo. Mapa que esconde buraco é pior que mapa incompleto.

## Esperado

Registra ausência de teste como achado P0/P1 e indica validação manual possível.

## Falhas (fails_if)

Omite a lacuna.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Módulo crítico sem teste é achado, não detalhe ausente.

## Notas

Re-leitura adversarial: nenhum
