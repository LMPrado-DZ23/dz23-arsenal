# TARGET TRIAGE — <alvo>

> `sha256sum <alvo>`: ______________________ · tamanho: __________ · data: __________
> AUTORIZAÇÃO: ______________________________________

## Magic (literal)
```
offset 0x00000000: <bytes>   -> <formato>
offset 0x0000____: <bytes>   -> <assinatura secundária>
```

## Cabeçalho
| Campo | Valor | Fonte |
|---|---|---|
| Formato | | magic |
| Arquitetura | | `readelf -h` / strings de toolchain |
| Endianness | | |
| Entry point | | |
| Tipo (EXEC/DYN/REL) | | |

## Entropia por bloco (4 KiB)
| Offset | Entropia (bits/byte) | Interpretação |
|---|---|---|
| 0x00000000 | | |
| 0x00001000 | | |

Fronteiras detectadas (transição brusca): `<offsets>`

## Empacotamento
- [ ] UPX (`upx -l`)
- [ ] packer genérico (`.text` alta entropia + imports mínimos)
- [ ] nenhum observado

## Plataforma (indício por string)
| String | Indício |
|---|---|

## Strings relevantes (primeiras 20 com offset)
```
0x________  <string>
```

## Decisão
- [ ] **Estática** (ELF/PE normal)
- [ ] **Extração** (container de firmware)
- [ ] **Emulação** (imagem completa)
- [ ] **BLOCKED** — motivo: <ferramenta/permissão/cifra>

## Não verificado
- <item> — como verificar: <comando>
