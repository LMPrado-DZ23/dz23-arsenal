# Eval: crc-ignored

- **Skill:** dz23-reverse-engineer-anything v1.1.2
- **Data:** 2026-11-09
- **Método:** execucao piloto (sessao de agente com a skill carregada)
- **Veredito:** **PASS**

## Cenário

Payload de uImage extraído sem verificar ih_dcrc.

## Resposta

**Pare antes de analisar esse payload. Integridade não verificada = análise contaminada.**

Extração de uImage sem conferir `ih_dcrc` produz um arquivo que pode estar truncado, corrompido ou adulterado — e a partir daí todo achado é sobre um binário que talvez nunca tenha existido no dispositivo. Neste toolkit o CRC é verificado **por padrão**, e a falha dele é **achado**, não detalhe.

```
ALVO:      payload de uImage (arquivo não identificado)
INTEGRIDADE: NÃO VERIFICADA → análise suspensa
ESTADO:    NOT_TESTED
```

## Os dois CRCs do uImage, e o que cada um prova

| Campo | O que cobre | O que a falha significa |
|---|---|---|
| `ih_hcrc` (header CRC) | os 64 bytes de cabeçalho, com o próprio campo zerado | header corrompido na gravação/transferência; metadados (`ih_load`, `ih_ep`, `ih_size`) não são confiáveis |
| `ih_dcrc` (data CRC) | o payload inteiro declarado em `ih_size` | payload truncado, corrompido ou **modificado**; extrair isso é analisar artefato inválido |

## O que eu rodo antes de qualquer extração

```bash
python scripts/re_toolkit.py uimage kernel.img --extract kernel.bin
```

Saída esperada (caso válido):

```
uImage   : kernel.img (1164 bytes, sha256 d9f81714…)
arch/os  : ARM / Linux  tipo: kernel  compressão: none
CRC hdr  : 0x45191e7d vs calculado 0x45191e7d -> OK
CRC data : 0x6dda7b67 vs calculado 0x6dda7b67 -> OK
extraído : kernel.bin (1100 bytes, descomprimido=False)
```

Exit code `0` = header e data OK. Exit code `1` = falha de integridade (o script continua e reporta, mas o
veredito é reprovado).

## Quando o CRC falha, o que vai para o relatório

Falha de `ih_dcrc` é **achado de primeira classe**, não erro de ferramenta:

```
Achado: integridade do payload uImage não confere
Arquivo: kernel.img  sha256=…  tamanho=…  
Declarado: ih_dcrc=0x6dda7b67  ih_size=1100
Calculado: 0x41c9…  (tamanho presente: 1088)
Diagnóstico: payload 12 bytes mais curto que o declarado — extração/transferência truncada
Confiança: OBSERVADO
Consequência: qualquer análise do payload é NOT_TESTED até obter dump íntegro
```

Três leituras possíveis, e elas **não** são a mesma coisa:
1. **Truncamento** no dump → reextrair o arquivo do dispositivo.
2. **Corrupção** de transferência (FTP ASCII, cartão ruim) → repetir com verificação de hash ponta a ponta.
3. **Modificação deliberada** (patch, backdoor) → aí o achado é de segurança, não de integridade, e muda a
   conclusão do relatório.

## Só depois disso

1. CRC OK → extrair com offset e hash, e registrar `payload_sha256` no ledger.
2. `compression` diferente de `none` → descomprimir e **verificar o novo hash** antes de analisar.
3. Payload extraído entra na triagem normal (`triage`, `elf`, `strings` com offset).

## O que eu não faço

- Não analiso payload de uImage com CRC pendente, nem "só um `strings` para dar uma olhada".
- Não declaro o arquivo "inválido" sem comparar com um segundo dump — truncamento de transferência é a
  causa mais comum, e culpar o firmware por isso é erro de diagnóstico.

## Esperado

Verifica o CRC/hash declarado e registra resultado; extração que falha integridade é achado.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Pare antes de analisar esse payload. Integridade nao verificada = analise contaminada.

## Notas

Piloto. Skill exige ih_hcrc + ih_dcrc antes de extrair, trata falha de CRC como achado de primeira classe e nomeia 3 diagnosticos (truncamento/corrupcao/modificacao).
