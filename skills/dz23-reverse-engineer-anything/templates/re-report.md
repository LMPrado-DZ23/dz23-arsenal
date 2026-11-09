# RE-REPORT — <alvo>

> ALVO: `<path>` · SHA-256: `<hash>` · tamanho: `<bytes>` · data: `<AAAA-MM-DD>`
> AUTORIZAÇÃO: `<dono/contrato/licença>` · ANALISTA: `<agente>`

## 1. Triagem
| Item | Valor | Evidência |
|---|---|---|
| Formato (magic) | | `xxd -l 64` |
| Arquitetura | | `readelf -h` / inferência declarada |
| Endianness | | |
| Entropia (média por bloco) | | script/comando |
| Empacotamento | | |
| Plataforma (indício) | | strings |

## 2. Mapa
```
<árvore/boot chain: bootloader → kernel → rootfs → serviços>
```

## 3. Achados
| ID | Achado | Estado | Evidência (offset/hash/comando) |
|---|---|---|---|
| F-001 | | OBSERVADO / INFERIDO / DESCONHECIDO | |

## 4. O que foi executado
| Ação | Ambiente/isolamento | Resultado |
|---|---|---|
| | VM/container/qemu, sem rede | |

## 5. Extração (quando aplicável)
| Artefato | Offset | Tamanho | SHA-256 | Integridade |
|---|---|---|---|---|

## 6. Emulação (quando aplicável)
- Modo: qemu-user / qemu-system
- Subiu: <init, serviços, portas>
- **Não** subiu e por quê: <periférico ausente, NVRAM, anti-emulação>

## 7. Risco
- **Físico/brick**: <o que não se deve fazer neste alvo>
- **Legal**: <base da análise; o que não pode ser distribuído>
- **Segurança**: <achado que deve ser divulgado ao fabricante>

## 8. Lacunas
- <o que não foi analisado e por quê: ferramenta ausente, cifrado, escopo>

## 9. Próximo passo
1. <ação concreta>
