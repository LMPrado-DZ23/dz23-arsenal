# Quality gates — evidência reprodutível ou nada

| Gate | PASS quando | Evidência mínima |
|---|---|---|
| Autorização | base do direito de analisar registrada | dono/contrato/licença citados |
| Identidade | hash e tamanho do alvo no relatório | `sha256sum` |
| Triagem | formato por magic, arch, endianness, entropia | `xxd` + saída de entropia |
| Estática | achados com offset/endereço | `readelf`/`objdump`/`rizin` |
| Dinâmica | execução em isolamento **com prova** | `ip a` + connect falhando |
| Extração | artefato com offset, tamanho e hash | log de extração |
| Integridade | CRC/hash declarado verificado | saída da verificação |
| Emulação | limites declarados (periférico ausente) | log de boot + o que não subiu |
| Hardware | nenhuma escrita sem backup/autorização | autorização + hash duplo |
| Relatório | observado ≠ inferido ≠ não analisado | seções separadas |

**Estados:** `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`, `BLOCKED_BY_EXTERNAL_DEPENDENCY`.

## Severidade

**BLOCKER:**
- Análise sem autorização registrada.
- Achado sem offset/hash/comando.
- Execução de firmware/binário desconhecido fora de isolamento (ou isolamento não comprovado).
- Escrita em dispositivo sem backup verificado e autorização.
- Símbolo/função nomeada sem cadeia de evidência.
- Hash do alvo ausente do relatório.
- Payload cifrado apresentado como analisado.

**MAJOR:**
- Entropia não verificada antes de concluir "cifrado".
- Extração sem offset/prova (ex.: `dd` do arquivo inteiro).
- CRC/hash declarado não verificado.
- Emulação sem declarar periféricos ausentes.
- Comparação de versões sem base/commit declarado.
- Cobertura não declarada (`NOT_ANALYZED` ausente).

**MINOR:**
- Nome de ferramenta sem versão.
- Offset em decimal em vez de hexadecimal.
- Falta de nota de ambiente na dinâmica.

## Checklist final
- [ ] Autorização/base legal registrada.
- [ ] Hash e tamanho do alvo.
- [ ] Formato, arquitetura e endianness por magic.
- [ ] Entropia medida (com interpretação).
- [ ] Achados com offset/endereço e comando.
- [ ] Dinâmica em isolamento comprovado (quando houve).
- [ ] Extração com offset/tamanho/hash por artefato.
- [ ] CRC/assinatura verificados (ou declarados como não verificáveis).
- [ ] Emulação com limites declarados (quando houve).
- [ ] Observado / inferido / não analisado separados.
- [ ] Risco físico e legal declarados.
- [ ] O que não foi analisado, e por quê.
