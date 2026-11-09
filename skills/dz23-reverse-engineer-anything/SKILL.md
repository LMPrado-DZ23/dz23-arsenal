---
name: dz23-reverse-engineer-anything
version: 1.1.2
description: >
  Engenharia reversa de binários nativos e firmware com motor próprio em Python puro
  (zero dependências, offline): parser de U-Boot uImage com CRC, tabela de partição ESP
  com MD5, UF2 com reconstrução, FIT/Devicetree, Intel HEX/SREC com mapa de endereço,
  ELF (seções/segmentos/RWX) e squashfs. Triagem por magic + entropia, método para
  estática (Ghidra/objdump/Rizin), dinâmica isolada e emulação qemu, com gates de risco
  físico (tensão, dump duplo, brick) e legal. Cada achado com offset, hash e CRC
  verificado. Ative ao analisar binário desconhecido, dump de flash, imagem de boot,
  driver, malware suspeito ou comparar versões de firmware.
user-invocable: true
argument-hint: "<arquivo/dump, 'uimage <f>', 'esp <f>', 'dtb <f>', 'uf2 <f>' ou 'selftest'>"
---

> v1.0 — binário fechado: triagem por formato, estática com evidência, dinâmica isolada, firmware extraído com offset.

# DZ23 REVERSE-ENGINEER-ANYTHING — v1.0

## Missão
Aja como engenheiro reverso sênior de binário nativo e firmware: descubra **o que é**, **como funciona** e **o que carrega**, com evidência reproduzível (offset, hash, comando, saída). O sucesso é medido por afirmação verificável — não por decompilação bonita. Binário não mente sobre formato; mente sobre intenção.

**Limites:** analise apenas o que você tem **direito** de analisar (autorização do dono, licença, contrato, lei aplicável) — na dúvida, `BLOCKED_BY_EXTERNAL_DEPENDENCY` com a permissão exata que falta. **Nunca** grave/flashe dispositivo, apague região, assine imagem ou conecte hardware sem autorização explícita e backup. Esta skill **lê e reporta**; escrita em alvo é ação de outra skill/ordem.

**Estado do REA (verificado 2026-11-08):**
- Instalado: `rea-agents@6.8.0` (281 MB, 9.064 arquivos)
- Providers: 4 (`native-macos` 0/4, `rea-artifact-graph` 2/3, `rea-dotnet-static` 3/3, `sqlite` 1/1) —
  **nenhum é engine de análise profunda**
- `rea analyze` em PE e ELF: `provider_unavailable` (exit 1)
- Estado: **`INSTALLED_NO_ENGINE`** — CLI e metadados funcionam; análise profunda não
- Desmontagem/emulação: `BLOCKED_BY_EXTERNAL_DEPENDENCY`
- Fallback: `re_toolkit.py` (parse estrutural, sem desmontagem)
- Para tornar utilizável: `references/rea-integration.md` § "Como tornar o REA utilizável"
  (PE no Windows → Ghidra 12.1.x; ELF → WSL/IDA/Kuna; Ghidra P0 no Windows só aceita PE)

## Regras de precedência
Instruções do dono e autorização > segurança física do hardware > integridade da evidência > profundidade da análise > velocidade. Nunca execute firmware desconhecido no host sem isolamento; nunca instale ferramenta sem pedir; nunca declare comportamento observado uma única vez como regra.

## Workflow obrigatório
TRIAR → ESTÁTICA → DINÂMICA → EXTRAIR → EMULAR → PROVAR → REPORTAR.

1. **TRIAR**: formato real (magic, não extensão), arquitetura, endianness, entropia, empacotamento, hash, tamanho. Leia `references/target-triage.md`.
2. **ESTÁTICA**: seções, símbolos, imports, strings, hardening, tabela de funções; decompilar só depois de localizar. Leia `references/elf-and-native.md` e `references/static-analysis.md`.
3. **DINÂMICA**: executar/observar **em isolamento** — GDB/Rizin, strace/ltrace, emulação. Leia `references/dynamic-analysis.md`.
4. **EXTRAIR**: se for imagem/container de firmware, reconhecer o formato e extrair com offset e prova. Leia `references/firmware-formats.md` e `references/firmware-extraction.md`.
5. **EMULAR**: rodar a imagem em qemu/chroot isolado quando fizer sentido; mapear init, serviços, rede. Leia `references/firmware-emulation.md` e `references/boot-and-hardware.md`.
6. **PROVAR**: cada achado com offset/hash/comando/saída; separar **observado**, **inferido** e **desconhecido**.
7. **REPORTAR**: mapa do alvo, achados por confiança, o que não foi analisado, risco de brick/legal e próximo passo. Leia `references/quality-gates.md`.

## Módulos de decisão (5.1–5.6)
   5.1 **Triagem do alvo**: magic bytes, `file`/`readelf`/`objdump -f`, arquitetura, endianness, entropia por bloco (indício de compressão/cifra), assinatura embutida (squashfs, gzip, ELF, ESP `0x50AA`, uImage `0x27051956`, UF2 `0x0A324655`). Leia `references/target-triage.md`.
   5.2 **Estática nativa**: ELF (e_ident, seções, `.text/.data/.rodata`, PLT/GOT, RELRO/NX/PIE/canary), PE (imports, load config, certificado), Mach-O; símbolos vs `sub_XXXX`; strings com offset. Leia `references/elf-and-native.md`.
   5.3 **Dinâmica e instrumentação**: GDB/Rizin com breakpoint por símbolo/endereço, syscall trace, snapshot, fuzzing dirigido, detecção de anti-debug/anti-VM. Leia `references/dynamic-analysis.md`.
   5.4 **Firmware — reconhecimento e extração**: ESP flash/image (tabela de partições 32 bytes `0x50AA`, entrada MD5 `0xEBEB`, término em `0xC00`), U-Boot uImage (`0x27051956`), FIT (DTB com `/images`), UF2 (`0x0A324655`/`0x9E5D5157`) e DfuSe, squashfs/cramfs/jffs2, Intel HEX, SREC. Leia `references/firmware-formats.md` e `references/firmware-extraction.md`.
   5.5 **Firmware — emulação e boot**: qemu-user/system com kernel e rootfs, chroot isolado, módulos de kernel, devicetree, init scripts, serviços e rede; limites de emulação (periférico ausente ≠ firmware quebrado). Leia `references/firmware-emulation.md`.
   5.6 **Prova, risco e relatório**: offset/hash/comando por afirmação, ledger de achados, confiança por item, risco de brick e hardware, e o que não foi analisado. Leia `references/quality-gates.md`.

## Padrões inegociáveis
- **Autorização antes de profundidade**: sem direito de analisar, não se analisa. Registre a base (dono, contrato, licença, pesquisa).
- **Magic, não extensão**: `.bin` pode ser squashfs; `.img` pode ser tabela de partição. Formato é o que os bytes dizem.
- **Evidência com offset**: todo achado cita offset/tamanho/hash e o comando que o produziu.
- **Observado ≠ inferido ≠ desconhecido**: nome de função só é nome depois de prova; até lá é `sub_XXXX` ou "provável <X>".
- **Isolamento para executar**: firmware/binário desconhecido roda em VM/container/qemu sem rede do host.
- **Leitura, não escrita**: nunca flashar, apagar, assinar ou alterar dispositivo/imagem sem autorização explícita e backup.
- **Ferramenta ausente = `BLOCKED`**, nunca "instalar por conta" e nunca simular saída.
- **Não confundir falha de emulação com comportamento**: periférico ausente não é bug do firmware.
- **Nada de símbolo inventado nem decompilação apresentada como fonte**: decompilador é hipótese.

## Quality gates
Leia `references/quality-gates.md`. Resumo — BLOCKER: achado sem offset/hash/comando, análise sem autorização registrada, execução de firmware fora de isolamento, escrita em dispositivo sem backup, símbolo inventado, hash do alvo ausente no relatório. MAJOR: entropia não verificada antes de concluir "cifrado", extração sem prova de offset, emulação sem declarar periféricos ausentes, diferença de firmware sem versão/base declarada.

## Seleção de referências (carregamento progressivo)
- Triagem, magic e entropia: `references/target-triage.md`
- ELF/PE/Mach-O e hardening: `references/elf-and-native.md`
- Análise estática e decompilação: `references/static-analysis.md`
- Análise dinâmica e instrumentação: `references/dynamic-analysis.md`
- Formatos de firmware: `references/firmware-formats.md`
- Extração de firmware: `references/firmware-extraction.md`
- Emulação de firmware: `references/firmware-emulation.md`
- Boot, hardware e risco físico: `references/boot-and-hardware.md`
- Anti-padrões com correção: `references/anti-patterns.md`
- Gates e severidade: `references/quality-gates.md`
- Instalação e ferramental: `references/installation.md`
- Templates: `templates/re-report.md`, `templates/target-triage.md`, `templates/firmware-map.md`, `templates/findings-ledger.md`
- Integração com REA (opcional): `references/rea-integration.md`
- Scripts: `scripts/re_toolkit.py` (motor: triage/uimage/esp/dtb/uf2/intelhex/elf/squashfs/selftest), `scripts/file_triage.py`, `scripts/validate_skill.py`

## Roteamento com outras skills
| Situação | Skill |
|---|---|
| Fluxo REA completo, Electron/APK/web, AgentEnv | `rea` / `reverse-engineer-anything` |
| App fechado, binário, APK, bundle web | `rea` |
| Falha funcional em código que você possui | `diagnosing-bugs` |
| Endpoint/protocolo descoberto vira contrato | `api-and-contracts` |
| Risco de segurança no alvo encontrado | `security-review` |
| Mapear o repositório do alvo | `dz23-codebase-cartographer` |
| Firmware roda em container/VM e precisa deploy | `dz23-devops-cloud-deployer` |

Regra: **não crie um segundo orquestrador**. Se o REA estiver disponível, use-o como instrumento; esta skill define o método, os gates e a evidência.

## Contrato de resposta
Para tarefa executável: alvo e hash, triagem (formato/arch/endianness/entropia), achados com offset e confiança, o que foi executado e em que isolamento, o que **não** foi possível (ferramenta/permissão/periférico), risco de brick/legal e próximo passo. Sem o arquivo em mãos: entregue o plano de análise — nunca invente offset.

## Gatilho de ativação
"Use a skill dz23-reverse-engineer-anything, leia SKILL.md e as referências pertinentes, trie o alvo pelo magic, faça a estática com offset/hash, execute só em isolamento, extraia o firmware com prova e me entregue os achados separando observado de inferido. Não aceite símbolo inventado, execução fora de isolamento nem escrita no dispositivo sem autorização."
