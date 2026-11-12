# phone-agent-harness — agentes que usam o telefone como runtime

`https://github.com/topics/phone-agent-harness` é um **tópico** do GitHub, não um projeto. Dois repositórios
estão listados nele, com naturezas opostas:

| Repo | Linguagem | O que faz | Instalável em Windows? |
|---|---|---|---|
| [`azizdaurov/pat-phone-agent-tool`](https://github.com/azizdaurov/pat-phone-agent-tool) | Python | o agente **liga e atende** pelo seu telefone, via Bluetooth; expõe o MCP `pat-phone` (`place_call`, `get_call`, `end_call`) | **sim**, com hardware e drivers |
| [`kellyvv/PhoneClaw`](https://github.com/kellyvv/PhoneClaw) | Swift | transforma o telefone em runtime de agente **on-device** | **não** — app iOS |

## Gap que preenche

Todas as skills DZ23 vivem no terminal. Um agente que **fala ao telefone** muda o alcance: cobrança de
fornecedor, confirmação de agendamento, verificação de identidade — tarefas em que o canal é voz, não HTTP.

## `pat-phone-agent-tool` — o que instalar

```powershell
git clone https://github.com/azizdaurov/pat-phone-agent-tool.git
cd pat-phone-agent-tool
# script do arsenal: cria venv e registra o MCP (não instala drivers)
pwsh -File install-pat-mcp.ps1 -DryRun
pwsh -File install-pat-mcp.ps1
# drivers + helper .NET + pareamento (setup oficial, muda o sistema)
powershell -ExecutionPolicy Bypass -File setup.ps1
```

### Requisitos duros (declarados pelo projeto)

- **Windows 11 x64** — não funciona em ARM nem em macOS.
- Telefone **pareado por Bluetooth**.
- **VB-CABLE + Voicemeeter** (drivers de áudio) e o helper `iphonecall` (.NET).
- ~4 GB de disco (modelos de fala).
- Claude Code instalado para o fluxo original (o MCP funciona com qualquer harness MCP).

### Por que o MCP não vem registrado por padrão

Sem telefone e drivers, o servidor **sobe mas toda chamada falha**. Registrar isso em todos os harnesses
poluiria o tool list com 3 ferramentas quebradas. O script deixa tudo pronto e o registro é um flag de
distância — mas só faz sentido depois do `setup.ps1`.

### Cuidados

- `setup.ps1` **instala driver de áudio no sistema** e liga o Developer Mode. Não é reversível "sem custo":
  faça quando puder reiniciar e testar áudio.
- Toda chamada do produto abre com uma linha fixa dizendo que é assistente de IA — não remova.
- Números reais ficam na máquina; o modelo vê nome ou placeholder.
- Gravar chamada tem implicação legal em várias jurisdições: informe o interlocutor (o produto já faz).

## `PhoneClaw` — por que não instalar

App Swift/iOS: roda **no telefone**, não no PC. Para usar em Windows seria preciso macOS + Xcode + conta de
desenvolvedor e instalá-lo no aparelho. Fora do escopo deste ambiente.

## Status neste arsenal

| Item | Estado |
|---|---|
| `pat-phone-agent-tool` clonado | ✅ |
| `install-pat-mcp.ps1` (venv + registro) | ✅ pronto, com `-DryRun` |
| Drivers de áudio / pareamento | ❌ pendente do dono |
| MCP `pat-phone` registrado | ❌ de propósito, até o hardware existir |
| Chamada telefônica de teste | ❌ `BLOCKED_BY_EXTERNAL_DEPENDENCY` |
| `PhoneClaw` | ❌ não aplicável (iOS) |
