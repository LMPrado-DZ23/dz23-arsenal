# OmniBridge MCP — um servidor MCP para todos os apps CAD, BIM e 3D

**Autor:** ayoubmep
**Repo:** https://github.com/ayoubmep/omnibridge-mcp
**Licença:** MIT (arquivo `LICENSE`, 1.080 B, e `license = "MIT"` no `pyproject.toml`)
**Versão instalada:** 0.1.0 · **Estado nesta máquina:** servidor MCP instalado e registrado nos 4
harnesses; bridge do Blender instalado, sem teste de app conectado

## O que faz

Um servidor MCP que conversa com **28 apps** de CAD/BIM/3D instalados na máquina, com **5 ferramentas
fixas** para todos eles. Em vez de centenas de ferramentas por app, ele dá ao modelo a capacidade de
rodar um **script curto dentro do app** mais um guia de como escrever esse script.

| Ferramenta | O que faz |
|---|---|
| `cad_apps` | lista os apps suportados e se estão alcançáveis agora |
| `cad_skill` | devolve o guia de script de um app: linguagem, nomes prontos, unidades, armadilhas |
| `cad_read` | roda script que **só inspeciona** o modelo |
| `cad_modify` | roda script que **altera** o modelo, como um passo de undo |
| `cad_screenshot` | imagem do viewport, para o modelo conferir o próprio trabalho |

Separar leitura de escrita é deliberado: o cliente MCP pode auto-aprovar a primeira e pedir
confirmação na segunda.

**Apps com bridge interna** (rodam script dentro): Blender, Rhino, 3ds Max, SketchUp, FreeCAD, Maya,
Cinema 4D, Houdini, Fusion, QGIS, Revit, Archicad.
**Apps por automação** (nada a instalar): AutoCAD (+ Civil 3D, Plant 3D, Map 3D, MEP), SOLIDWORKS,
BricsCAD/ZWCAD/GstarCAD/nanoCAD, Inventor, CATIA, Solid Edge, MicroStation, Navisworks, Tekla, ETABS,
SAP2000, Robot.

Status declarado pelo projeto: **testado** em AutoCAD 2024, Revit 2026, Archicad 29, SOLIDWORKS 2025,
Blender 5.2, Unreal 5.8. O resto é escrito contra a API documentada e **precisa do primeiro teste
real** — o próprio README diz isso.

## Por que usar junto do arsenal

O arsenal já tinha um MCP para Blender (`external/blender-mcp`, via `blender-mcp`/`mcp-for-blender`).
O OmniBridge não o substitui: ele cobre **o resto do estúdio** — CAD, BIM e as outras ferramentas de
DCC — com o mesmo desenho de ferramentas e um guia por app.

| Necessidade | Ferramenta |
|---|---|
| Blender com biblioteca de assets e geração 3D | `blender` MCP (já instalado) |
| **AutoCAD, Revit, Rhino, SketchUp, Fusion, Maya, Unreal** | **OmniBridge** |
| render, textura, pipeline de assets | skills `blender-*` do pack instalado |

## Instalação — o que funcionou

```powershell
uv tool install git+https://github.com/ayoubmep/omnibridge-mcp
# > Installed 1 executable: omnibridge   (exit 0)
```

Ficou em `C:\Users\lmpra\.local\bin\omnibridge.exe`. O `config` do próprio projeto imprime o
snippet certo por cliente:

```powershell
omnibridge config claude-code   # claude mcp add omnibridge -- "<caminho do omnibridge.EXE>"
omnibridge config codex         # [mcp_servers.omnibridge] command = "...omnibridge.EXE" args = []
```

Registro feito à mão nos quatro harnesses, com o caminho absoluto do `.EXE` (cliente aberto pela GUI
não herda `~/.local/bin` no PATH):

| Harness | Onde | Forma |
|---|---|---|
| DeepSeek Harness | `~/.dsh/profiles/desktop/cordis.patch.yml` → `mcp-manager.servers.omnibridge` | stdio |
| Claude Code | `~/.claude.json` → `mcpServers.omnibridge` | stdio |
| Codex CLI | `~/.codex/config.toml` → `[mcp_servers.omnibridge]` | stdio |
| Qwen Code | `~/.qwen/settings.json` → `mcpServers.omnibridge` | stdio |

Bridge do Blender (não é o mesmo add-on do `blender-mcp`; os dois convivem):

```powershell
omnibridge install blender
# [blender] installed in %APPDATA%\Blender Foundation\Blender\5.3\scripts\addons\omnibridge
# [blender] now enable it: Edit > Preferences > Add-ons > search 'OmniBridge' > tick.
```

## Prova de funcionamento (execução real, nesta máquina)

Handshake por stdio com `omnibridge serve`:

```
initialize -> {"name":"OmniBridge","version":""}
tools/list -> 5: cad_apps, cad_skill, cad_read, cad_modify, cad_screenshot
cad_apps  ok=true  -> 28 apps, todas "not running" (nenhum CAD aberto)
cad_skill(blender) ok=true -> guia devolvido (Python/bpy, nomes prontos, armadilhas)
```

E pelo harness, sem reiniciar o app: a ferramenta `mcp__omnibridge__cad_apps` respondeu `[]` com
`only_available=true` — vazio porque **nenhum app está aberto**, não porque falhou.

## Cuidados

- **Scripts não são sandbox.** Um `cad_modify` pode apagar geometria e escrever arquivo como o app
  pode. Trabalhe em cópia, salve antes, e mantenha a aprovação do cliente ligada em `cad_modify`.
- **Local por desenho**: as bridges escutam em `127.0.0.1` e exigem o token em `~/.omnibridge/token`.
  `omnibridge serve --transport http` **não tem login próprio** — só em rede confiável, com túnel
  autenticado, e desligue depois.
- **Dois add-ons no Blender**: `addon.py` (blender-mcp) e `omnibridge`. Portas diferentes, sem
  conflito, mas cada um precisa ser habilitado e conectado separadamente.
- **Status "untested" é declaração do autor**, não erro de instalação: em app não testado, o primeiro
  script pode falhar e é você quem descobre.

## Rollback

```powershell
uv tool uninstall omnibridge-mcp
omnibridge uninstall blender          # antes do uninstall do pacote
# remover a entrada `omnibridge` dos 4 arquivos de config (backups .bak-omnibridge-* ao lado)
```
