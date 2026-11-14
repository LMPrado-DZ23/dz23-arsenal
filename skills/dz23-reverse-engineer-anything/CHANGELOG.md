# Changelog — dz23-reverse-engineer-anything

## [1.1.3] — 2026-11-14

### Corrigido
- `references/rea-integration.md` e `SKILL.md`: o estado **`INSTALLED_NO_ENGINE`** ficou obsoleto.
  Nesta máquina, Ghidra **12.1.4** e jadx **0.7.1** estão instalados **e configurados**
  (`GHIDRA_INSTALL_DIR`, `REA_JADX_MCP_JAR`), mais apktool 3.0.3, adb 37.0.1, WABT 1.0.42 e
  unblob 26.6.4. Estado passa a **`AVAILABLE`** para nativo, APK, wasm e Android.
  O que continua ausente: `ida`, `kuna`, `jeb`, `hopper`.
- Distinção que faltava nas versões anteriores: **instalado ≠ configurado**. Em 2026-11-08 o REA
  estava instalado e *sem* env de provider; a CLI sobe sem engine mesmo com o binário no disco.
  Registrar o estado pelo binário, e não pela config do processo, produziu dois diagnósticos errados
  em sequência (1.1.1 e 1.1.2). A verificação agora exige `rea doctor` **com a env do processo**.
- `references/rea-integration.md`: seção "Como tornar o REA utilizável" vira "Como iniciar o REA",
  com o bootstrap único (`tools/rea-env.ps1` / `tools/rea-env.sh`) e o gate de autorização mantido.

### Prova registrada
- `procedure_pseudo_code` devolveu `void entry(void)` real de um PE x86-64.
- `inspect_android_package`: 20.990 classes, 1.842 recursos, 45 componentes de um APK.
- `inspect_wasm_artifact`: WABT 1.0.42, `validation: valid`, export `add (i32,i32)->i32`.
- `adb`: `emulator-5554` listado.

### Lição (terceira da mesma família)
"Instalado ≠ disponível ≠ funcional" agora tem um quarto membro: **configurado no processo**.
Binário no disco com servidor MCP sem env é exatamente o caso que engana os dois lados.

## [1.1.2] — 2026-11-08

### Corrigido
- `references/rea-integration.md`: **duas** afirmações erradas corrigidas em sequência:
  1. **"REA não instalado"** — falso. `Get-Command rea` + `rea --version` mostram `rea-agents@6.8.0`
     instalado (281 MB, 9.064 arquivos).
  2. **"REA disponível"** — falso. `rea analyze` retorna `provider_unavailable` para **PE e ELF**; nenhum
     dos 4 providers é engine de análise profunda.

  Estado real: **`INSTALLED_NO_ENGINE`** — CLI funciona, análise profunda `BLOCKED`.
- Tamanho corrigido: 1,2 GB (estimativa) → **281 MB (medido)**.
- Adicionado: seção de verificação (`rea --version`, `rea capabilities`, `rea analyze`) antes de declarar
  `AVAILABLE`.
- Adicionado: tabela de como tornar o REA utilizável (Ghidra/IDA/Kuna por plataforma).
- Adicionado: limitação conhecida — Windows Ghidra P0 aceita apenas PE e raw 6502; para ELF usar
  WSL/IDA/Kuna.
- `SKILL.md`: nota de estado `INSTALLED_NO_ENGINE` + fallback `re_toolkit.py`.
- Documentado: `rea doctor` avisa "skill identity stale" apontando `reverse-engineer-anything` (skill
  interna do REA) — **esperado, não é bug desta skill**.

### Lição (dupla)
"Verificar antes de afirmar" falhou **duas vezes** na mesma skill:
1. Assumi "não instalado" sem rodar `Get-Command rea`.
2. Quase assumi "AVAILABLE" sem rodar `rea analyze` — a verificação funcional da Fase 0 evitou o segundo
   erro.

O padrão DZ23 exige: estado verificado é `INSTALLED_NO_ENGINE`, não "não instalado" nem "AVAILABLE".
**Instalado ≠ funcional ≠ disponível.**

## [1.1.1] — 2026-11-08

Doc-only. Nenhum código alterado (`re_toolkit.py` e `file_triage.py` intactos); itens 1 e 3 (desmontador,
squashfs) continuam para a v1.2.0.

### Adicionado
- `references/rea-integration.md`: guia completo de instalação do REA — link oficial, comandos, gate de
  autorização obrigatório, tabela de fallback sem REA, versão mínima testada (6.8.0) e regra de segurança
  ao rodar o MCP.
- `SKILL.md`: nota de que o REA é **opcional**, com o custo da instalação (1,2 GB, 42 deps, Node ≥ 20) e
  ponteiro para o guia.
- `README.md`: seção "REA (opcional, recomendado para análise profunda)" com os 4 passos.

### Corrigido
- **Gap identificado:** a v1.1.0 citava o REA mas não guiava a instalação — um agente ficava sabendo que
  o REA existe e não sabia onde baixar, como configurar nem que precisava de autorização.

### Verificação de fatos (não copiados de suposição)
- `https://github.com/morluto/rea` → **HTTP 200**.
- `gh repo view morluto/rea` → licença **MIT**.
- `package.json` da fonte extraída → versão **6.8.0**.
- SHA-256 de `rea-main.zip` → `a6ad9946390fb1f00d2cb7d503845cf48a1502694c9783241d493a3571a5b815`.
- Tamanho: **estimado** ~1,2 GB com `node_modules` (não medido — o REA não foi instalado); medidos
  89,2 MB (fonte extraída) e 27,1 MB (zip). O número estimado está rotulado como estimativa no guia.

## [1.1.0] — 2026-11-08

**De documento de método para motor executável.** A v1.0.0 descrevia formatos; não os lia. Esta versão
adiciona parser real, em Python puro (stdlib), offline, com verificação de integridade.

### Adicionado
- `scripts/re_toolkit.py` — motor com 8 subcomandos:
  - `triage` — magic, arquitetura (ELF), entropia por bloco, strings, sha256
  - `uimage` — header U-Boot, **CRC do header e do payload verificados**, extração com descompressão
  - `esp` — tabela de partição ESP (entradas de 32 B, magic `0x50AA`), **MD5 verificado**
  - `dtb` — FDT/FIT: nós, propriedades, `/images`, nós `hash`/`signature`
  - `uf2` — blocos (magic início/fim), reconstrução por `targetAddr`, detecção de buraco
  - `intelhex` — Intel HEX e SREC com **checksum verificado**, mapa de endereço, detecção de gap
  - `elf` — classe, machine, entry, PIE, seções, segmentos, **detecção de segmento RWX**
  - `squashfs` — superblock (metadados; não extrai — declara `BLOCKED` sem `unsquashfs`)
  - `selftest` — gera fixtures válidas e verifica cada parser (15 checagens)
- Saída `--json` em todos os subcomandos, com `read_only=true` e `executed_target=false`.
- Exit codes: `0` ok · `1` falha de integridade (CRC/MD5/buraco) · `2` input inválido.

### Corrigido
- Description do frontmatter prometia extração/emulação que a skill não executava (era só texto).

### Validação real (não simulada)
- `python scripts/re_toolkit.py selftest` → **SELFTEST 15/15 PASS**, exit 0.
- Fixtures geradas e reabertas pela CLI: uImage (CRC header `0x45191e7d` e data `0x6dda7b67` **OK**),
  ESP (3 partições `factory`/`nvs`/`spiffs`, MD5 **OK**), UF2 (3 blocos, 972 B reconstruídos, 0 buracos),
  Intel HEX (32 B escritos, 240 B de gap detectado), DTB (`model=Test Board`, `/images/kernel@1`,
  `comp=none`).
- **ELF real** (busybox musl extraído de `alpine:latest` via Docker, 804.616 B): ELF64 x86-64, `DYN`,
  entry `0x6ed1`, 24 seções, 12 segmentos, **0 RWX**, `.note.gnu.build-id` e `.text` (624.560 B) lidos.

### Bugs encontrados e corrigidos durante a validação (o selftest pegou)
1. `uImage`: fixture gravava `dcrc=0` — o teste estava errado, não o parser. Fixture passou a calcular o CRC.
2. `SREC`: parser gravava o registro **S0** (header/metadata) como se fosse dado de memória → 16 B virava 17.
3. `ESP`: valor do magic estava byte-swapped (`0xAA50` em vez de `0x50AA`) no parser e na fixture.
4. `FDT`: propriedade de 4 bytes ASCII (`"none"`) era exibida como `0x6e6f6e65`; agora tenta string primeiro.

## [1.0.0] — 2026-11-08

Primeira versão. Engenharia reversa de **binários nativos e firmware** com evidência.

Base factual: documentação técnica do REA (`rea-main`, 8.198 entradas, extraída em
`projects/dz23-reverse-engineer-anything/_rea-source/`, fora do zip) — formatos de firmware
(ESP flash/image, U-Boot uImage, FIT, UF2/DfuSe, devicetree, kernel modules, ELF notes) e postura de
ferramental ("REA chama objdump/GDB/Rizin fornecidos pelo usuário; não instala").

- `SKILL.md`: missão com limites (autorização, isolamento, read-only no alvo), workflow em 7 etapas
  (TRIAR → ESTÁTICA → DINÂMICA → EXTRAIR → EMULAR → PROVAR → REPORTAR) e módulos 5.1–5.6.
- 11 references: triagem, ELF/PE/Mach-O, estática/decompilação, dinâmica, formatos de firmware,
  extração, emulação, boot/hardware, anti-padrões (38), quality gates, instalação.
- 4 templates: `re-report.md`, `target-triage.md`, `firmware-map.md`, `findings-ledger.md`.
- 2 scripts: `file_triage.py` (magic/entropia/strings, read-only) e `validate_skill.py`.
- 15 cenários de avaliação em `evals/evals.json` (schema 1).
- Padrões inegociáveis: autorização antes da profundidade, magic em vez de extensão, achado com
  offset/hash, observado ≠ inferido ≠ desconhecido, isolamento para executar, leitura sem escrita no
  alvo, ferramenta ausente = `BLOCKED`, nunca símbolo inventado.

### Validação do script
`file_triage.py` exercitado em arquivos reais nesta máquina:
`rea-main.zip` (27.123.908 B, `50 4b 03 04`, detectado como ZIP, entropia média 7,93 bits/byte — 64/64
blocos acima de 7,5) e `ls.exe` do Git para Windows (149.479 B, `4d 5a`, detectado como PE, entropia
5,465). Também validado: JSON (`--json`) e caminho inexistente (exit 2).
Limitação conhecida: `strings` usa janela de 8 caracteres e não extrai UTF-16 (comum em PE da Microsoft).
