# Eval: finding-without-offset

- **Skill:** dz23-reverse-engineer-anything v1.1.2
- **Data:** 2026-11-09
- **Método:** execucao piloto (sessao de agente com a skill carregada)
- **Veredito:** **PASS**

## Cenário

'Há uma chave privada embutida no firmware.'

## Resposta

**Isso não é um achado. É uma hipótese sem localização.**

"Chave privada embutida" é uma afirmação que precisa de três coisas para valer: **offset** (onde está), **hash do arquivo** (de qual binário estamos falando) e **comando** (como você chegou lá). Sem os três, o estado é `NOT_TESTED` — não `PASS`.

```
ACHADO:      "chave privada embutida"
ARQUIVO:     não identificado
HASH:        não informado
OFFSET:      não informado
COMANDO:     não informado
ESTADO:      NOT_TESTED
```

## Por que eu não aceito a afirmação

Três coisas diferentes produzem esse texto, e cada uma leva a uma conclusão oposta:

| O que foi visto | O que realmente é | Como distinguir |
|---|---|---|
| bloco de bytes com `-----BEGIN` e muito espaço em branco | **chave privada em claro** (vazamento real) | `strings -a -t x firmware.bin \| grep -n "BEGIN.*PRIVATE KEY"` |
| dado aleatório de 32/64 bytes com entropia alta | **pode ser** chave, ou IV, ou hash, ou salt | extrair o bloco e rodar `openssl pkey -inform DER -in bloco.der -noout` |
| PEM cifrado (`BEGIN ENCRYPTED PRIVATE KEY`) | chave presente **mas protegida** | o cabeçalho diz; sem a passphrase não há uso |

Nenhuma dessas leituras se resolve por inspeção visual. Resolve-se com offset e comando.

## O que eu exijo para transformar isso em achado

```bash
# 1. localizar com offset (o -t x imprime o deslocamento em hex)
strings -a -t x target.bin | grep -Ei "BEGIN (RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY"

# 2. extrair o bloco exato a partir do offset encontrado
dd if=target.bin of=bloco.pem bs=1 skip=$((0xOFFSET)) count=2048

# 3. provar que é chave válida (e se está protegida)
openssl pkey -in bloco.pem -noout -text 2>&1 | head -5
openssl pkey -in bloco.pem -inpass pass:xxx -noout 2>&1 | head -3   # se cifrada

# 4. registrar hash do alvo e do bloco extraído
sha256sum target.bin bloco.pem
python scripts/re_toolkit.py triage target.bin
```

**Critério de aceite:** a linha do relatório precisa ficar assim —

```
Achado: chave privada RSA 2048 em claro
Arquivo: target.bin  sha256=9f2c…a71e
Offset: 0x0004b8c0 (2.048 bytes)
Comando: strings -a -t x target.bin | grep "BEGIN RSA PRIVATE KEY"
Prova: openssl pkey -in bloco.pem -noout -text → "Private-Key: (2048 bit)"
Confiança: OBSERVADO
```

Se a chave for cifrada, o achado muda: "chave privada **protegida por passphrase**" — e a conclusão de
segurança é outra. Dizer "chave exposta" nos dois casos é erro de análise, não de redação.

## Se você tiver só a suspeita

Aceito a suspeita e classifico como `NOT_TESTED`, com a hipótese registrada e o próximo comando nomeado. O
que não aceito é ela entrar no relatório como fato.

## Esperado

Exige offset, hash do arquivo e comando que localizou; sem isso o achado é NOT_TESTED.

## Avaliação

- Aderência ao expected: sim
- Defeitos encontrados: nenhum
- Trecho literal: Isso nao e um achado. E uma hipotese sem localizacao.

## Notas

Piloto. Skill exigiu offset+hash+comando e rebaixou a afirmacao para NOT_TESTED; incluiu como distinguir chave em claro de chave cifrada por comando.
