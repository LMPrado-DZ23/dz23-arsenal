# App Store Compliance — auditoria pré-submissão para App Store e Google Play

**Autor:** Mirza Iqbal (mjmirza)
**Repo:** https://github.com/mjmirza/app-store-compliance
**Licença:** **ORA 2.3** (`LicenseRef-OpenRoots-ORA-2.3`) — lida em `LICENSE` + `NOTICE`. **Não é OSI.**
**Versão instalada:** 2.5.3 · **Estado nesta máquina:** skill instalada em 2026-11-26 (4 harnesses)

## A licença primeiro, porque ela muda a decisão

O repositório é *source-available*, não aberto:

| Tier | Termo |
|---|---|
| Root | grátis e incondicional até **US$ 20 mi** de receita anual, e para **qualquer indivíduo**, ONG, escola ou órgão público, em qualquer tamanho |
| Canopy | acima do limite, **0,5%** do que excede, teto de US$ 250 mil/ano |
| Compute | **treinar IA com esta obra exige licença separada** em todos os tiers |

Consequência para este arsenal (MIT): **`REFERENCIA`, nunca `INCORPORAR`**. Nada do conteúdo é
copiado para o repositório; o que fica aqui é o ponteiro, o estado da instalação e os cuidados.
Para uso pessoal nesta máquina, o tier Root cobre.

## O que entrega

Uma auditoria de conformidade **antes** do upload, contra as Apple App Store Review Guidelines e as
Google Play Developer Program Policies, com plano de correção por severidade. Números que o próprio
projeto publica: **125 padrões de rejeição** documentados, **117 prazos regulatórios** rastreados
(EU AI Act, DSA, COPPA, leis de idade), Privacy Manifest e Data safety.

| Peça | O que é |
|---|---|
| `agent-os/skill/SKILL.md` | a skill (10 KB): quando rodar, o que varrer, como classificar |
| `agent-os/hooks/app-store-compliance-guard.sh` | guard de 161 KB que roda **antes de cada comando de shell** e bloqueia (exit 2) um `submit` de app com risco conhecido |
| `docs/` (30+ arquivos) | Apple, Google Play, acessibilidade, segurança mobile, privacidade, regulatório 2026, checklist |
| `data/*.json` | padrões de rejeição, prazos regulatórios, registro de rulings, receitas de detecção |
| `scripts/*.py` | auditores reais: `release-audit.py`, `metadata-audit.py`, `validate-privacy-manifest.py`, monitores de política |
| `evals/gold-cases.json` | casos de ouro para medir a skill |

## Instalação — o que funcionou, e o que não

O instalador oficial é **bash**. Nesta máquina `bash` resolve para `C:\WINDOWS\system32\bash.exe`,
que é o launcher do WSL, e o WSL padrão aqui é `docker-desktop` — que **não tem `/bin/bash`**:

```
$ bash scripts/install.sh --dry-run
<3>WSL ERROR: CreateProcessCommon: execvpe(/bin/bash) failed: No such file or directory
```

Caminho que funciona: **Git Bash** explicitamente.

```powershell
$env:ASC_UNAME='MINGW64_NT-10.0'      # faz o instalador usar o matcher Bash|PowerShell (Windows)
& 'C:\Program Files\Git\bin\bash.exe' scripts/install.sh install
```

Saída real (exit 0):

```
  ok    files copied
  ok    hook added to settings.json (a backup sits next to it)
  ok    guard present at ~/.claude/hooks/app-store-compliance-guard.sh
  ok    version 2.5.3
  ok    skill payload complete at ~/.claude/skills/app-store-compliance
  ok    slash command /app-store-audit installed
  ok    guard blocks a sample app with known rejection risks
  ok    the registered hook command blocks a submit command
  ok    the registered hook command stays silent on an ordinary command
  ok    the registered hook command blocks a submit command run through PowerShell
  note  python3 not found. The guard still runs; deadline list and privacy manifest validator are skipped.
```

O instalador **prova a si mesmo**: bloqueia um app de amostra com risco conhecido, fica silencioso
num comando comum, e testa o caminho pelo PowerShell.

## Onde ficou em cada harness

| Harness | Caminho | Como |
|---|---|---|
| Claude Code | `~/.claude/skills/app-store-compliance` | instalador oficial (skill + `/app-store-audit` + hook) |
| DeepSeek Harness | `~/.agents/skills/app-store-compliance` | junction para a cópia do Claude |
| Codex CLI | `~/.codex/skills/app-store-compliance` | junction (Codex também lê `~/.agents/skills`) |
| Qwen Code | `~/.qwen/skills/app-store-compliance` | junction |

Hook registrado em `~/.claude/settings.json` para `Write|Edit|MultiEdit`? Não: para **Bash e
PowerShell**, `PreToolUse`, com backup do settings ao lado do arquivo.

## Limitações medidas nesta máquina

- **`python3` no Git Bash apontava para o atalho da Microsoft Store** (`python3 --version` respondia
  *"Python was not found"*), então o guard rodava com o **checklist de prazos regulatórios e o
  validador de Privacy Manifest desligados** — justamente as partes de 2026 (EU AI Act, DSA).
  Corrigido com um shim de uma linha em `~/bin/python3` (`exec python "$@"`), que vem antes do atalho
  no PATH do Git Bash. Depois disso o `doctor` deixa de emitir o aviso e o `deadline-checker.py` roda.
- O guard é **bash**; se o Claude Code rodar uma ferramenta fora de Bash/PowerShell, o matcher não pega.
- `omnibridge`/outros MCP não têm relação com isto — são camadas independentes.

## Uso

```
/app-store-audit                 # no Claude Code
bash ~/.claude/hooks/app-store-compliance-guard.sh /caminho/do/app   # auditoria direta
python3 scripts/release-audit.py ...   # scripts avulsos (precisa de python3 no PATH do bash)
```

## Cuidados

- **O que este repositório guarda é ficha + link, não o pacote.** São 6 KB de texto próprio (o que a
  ferramenta faz, o que foi instalado, o que falhou aqui) apontando para o repositório oficial — nenhum
  arquivo do projeto original é versionado, e nenhum trecho longo é citado. Isso é indexação, não
  redistribuição.
- **A restrição da ORA vale para o conteúdo do pacote:** copiar os arquivos dele para outro repositório,
  ou usá-lo para **treinar modelo**, exige licença; acima de US$ 20 mi de receita anual há royalty de
  0,5%. Para uso pessoal nesta máquina, o tier Root cobre.
- **O guard intercepta todo comando de shell** no Claude Code. É o custo de ter a proteção; ele foi
  desenhado para sair 0 em comando comum (verificado no install), mas é uma peça a mais no caminho.
- **Atualização**: `git -C <clone> pull` e repetir o instalador; o `uninstall` remove tudo o que ele
  adicionou (guarda a lista do que criou).

## Rollback

```powershell
$env:ASC_UNAME='MINGW64_NT-10.0'
& 'C:\Program Files\Git\bin\bash.exe' <clone>/scripts/install.sh uninstall
# e apague as três junctions em ~/.agents/skills, ~/.codex/skills e ~/.qwen/skills
```
