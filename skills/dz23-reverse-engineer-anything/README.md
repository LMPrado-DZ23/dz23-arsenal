# DZ23 Reverse-Engineer-Anything v1.0.0

Skill de **engenharia reversa de binários nativos e firmware** com evidência, para DeepSeek Harness e
agentes compatíveis com `SKILL.md`.

Cobre o caminho completo: **triagem → estática → dinâmica → extração → emulação → prova → relatório**,
com uma regra que atravessa tudo: **cada achado carrega offset, hash e comando**.

## Conteúdo

| Arquivo | Para quê |
|---|---|
| `SKILL.md` | Missão e limites, workflow em 7 etapas, módulos 5.1–5.6 |
| `references/target-triage.md` | Magic bytes, entropia por bloco, arquitetura, packer |
| `references/elf-and-native.md` | ELF/PE/Mach-O, seções, hardening, símbolos |
| `references/static-analysis.md` | Ghidra headless, Rizin, xrefs, strings com offset |
| `references/dynamic-analysis.md` | GDB/Rizin, strace, isolamento comprovado, anti-debug |
| `references/firmware-formats.md` | ESP, uImage, FIT, UF2/DfuSe, devicetree, squashfs/UBI/HEX |
| `references/firmware-extraction.md` | Extratores, offset, integridade, o que procurar no rootfs |
| `references/firmware-emulation.md` | qemu-user/system, limites de emulação, pós-boot |
| `references/boot-and-hardware.md` | Cadeia de boot, UART/JTAG/SPI, risco de brick, legal |
| `references/anti-patterns.md` | 38 erros recorrentes com correção |
| `references/quality-gates.md` | Gates, severidade e checklist de 12 itens |
| `references/installation.md` | Ferramental por área e o que verificar antes de prometer |
| `templates/re-report.md` | Relatório final (triagem → achados → risco → lacunas) |
| `templates/target-triage.md` | Triagem de um alvo |
| `templates/firmware-map.md` | Mapa de flash, cadeia de boot, interfaces |
| `templates/findings-ledger.md` | Ledger de achados por confiança + cobertura |
| `scripts/re_toolkit.py` | **Motor**: triage, uimage (CRC), esp (MD5), dtb/FIT, uf2, intelhex/SREC, elf, squashfs, selftest |
| `scripts/file_triage.py` | Triagem read-only: magic, ELF arch, entropia, strings |
| `scripts/validate_skill.py` | Validador do pacote (inclui fatos de formato) |

## Escopo e limites

- **Autorização primeiro**: só se analisa o que se tem direito de analisar. Sem base, `BLOCKED`.
- **Read-only no alvo**: nunca flashar, apagar ou assinar sem autorização e backup verificado.
- **Isolamento**: firmware/binário desconhecido roda em VM/container/qemu — execução no host é proibida.
- **Não substitui** `rea`/`reverse-engineer-anything` (stack completa REA), `security-review`
  (vulnerabilidade) nem `diagnosing-bugs` (código que você possui).

## Uso

1. Instalar em `~/.agents/skills/` (`references/installation.md`).
2. Invocar por `/dz23-reverse-engineer-anything` ou por descrição ("trie este dump de flash").
3. Artefatos vão para `projects/<alvo>/re/`.

```bash
python scripts/re_toolkit.py selftest            # 15 checagens em fixtures válidas
python scripts/re_toolkit.py triage alvo.bin     # magic, arch, entropia, strings
python scripts/re_toolkit.py uimage kernel.img --extract kernel.bin
python scripts/re_toolkit.py esp flash.bin       # tabela de partição + MD5
python scripts/re_toolkit.py dtb image.itb       # FIT: imagens, hashes
python scripts/re_toolkit.py uf2 firmware.uf2 --extract firmware.bin
python scripts/re_toolkit.py intelhex fw.hex --out fw.bin
python scripts/re_toolkit.py elf binario         # seções, segmentos, RWX
python scripts/re_toolkit.py squashfs root.sqsh  # superblock (não extrai)
```

**Prompt de ativação:** [`PROMPT-ATIVACAO.txt`](PROMPT-ATIVACAO.txt).
**Avaliação:** `evals/evals.json` — 15 cenários (schema 1). Cenários não são testes executados.
**Versão:** [`VERSION`](VERSION) (1.0.0) · histórico em [`CHANGELOG.md`](CHANGELOG.md).

## Princípio

Formato é o que os bytes dizem. Nome de função é hipótese até a evidência. Executar sem isolar é
comprometer a bancada. Escrever no dispositivo sem backup é brick.
### REA (opcional, recomendado para análise profunda)

Esta skill funciona sem o REA, mas com o REA ganha desmontagem, emulação e UI. Para instalar:

1. **Autorizar** a instalação (~1,2 GB, 42 deps, Node ≥ 20) — a skill nunca instala silenciosamente
2. `git clone https://github.com/morluto/rea.git`
3. `cd rea && pnpm install`
4. Configurar o MCP no harness (`mcpServers` → `rea` → `node <path>/rea/dist/mcp-server.js`)

Versão mínima testada: **6.8.0** (MIT). Guia completo em
[`references/rea-integration.md`](references/rea-integration.md).

---

## Arsenal — resumo operacional

**Versão real (VERSION/frontmatter):** 1.1.1 · **Categoria:** exploration · **Complexidade:** advanced

### Quando usar

- Analisar binário desconhecido (ELF/PE/Mach-O) sem fonte.
- Firmware, dump de flash, imagem de boot (ESP, uImage, UF2, Intel HEX, DTB).
- Recuperar protocolo de dispositivo ou comparar versões de firmware.
- CTF, auditoria de artefato fechado.

### Quando NÃO usar

- Código-fonte disponível: use `dz23-codebase-cartographer`.
- Análise sem autorização legal do dono do artefato.
- Desmontagem/emulação sem REA instalado: declare `NOT_TESTED`, não simule saída.

### Instalação

```bash
# Já incluída no install-all. Manual:
cp -r skills/dz23-reverse-engineer-anything ~/.agents/skills/dz23-reverse-engineer-anything
```

### Uso

```bash
/dz23-reverse-engineer-anything

# ou por descrição — o agente carrega sozinho (ver SKILL.md)
```

### Pré-requisitos de CLI

`python` (obrigatória) · `objdump`, `readelf`, `strings` (recomendadas) · `ghidra`, `qemu`, REA (opcionais — habilitam desmontagem e emulação).

### Evidência / Quality gates

- Toda afirmação com offset e hash do artefato.
- CRC/MD5/checksum verificados quando o formato tem integridade.
- Risco físico declarado antes de tocar hardware (tensão, dump duplo, brick, OTP).
- Autorização explícita antes de instalar REA (~1,2 GB, 42 deps).

### Integração com outras skills

Entrega dossiê para `dz23-codebase-cartographer`; usa REA quando disponível (ver `references/rea-integration.md`).

### Versão e changelog

Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em [`../../CHANGELOG.md`](../../CHANGELOG.md).
