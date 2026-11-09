# Análise dinâmica e instrumentação

## Regra de ouro
Binário/firmware desconhecido **não roda no host**. Use VM descartável, container sem rede, ou qemu. Se não há isolamento, o estado é `BLOCKED_BY_EXTERNAL_DEPENDENCY` — não "só um testezinho".

## GDB (nativo, com símbolo ou sem)
```bash
gdb -q ./alvo
(gdb) set pagination off
(gdb) info functions            # nomes quando há símbolo
(gdb) break *0x401234           # por endereço quando não há
(gdb) run arg1
(gdb) info registers
(gdb) x/16xb $rsp
(gdb) x/s 0x402010              # string no endereço
```
Sem fonte: `disassemble /r` mostra bytes + instrução (prova para o relatório).

## Rizin como depurador (native debug)
```bash
rizin -d -q -c 'db 0x401234; dc; dr; pd 10' alvo
rizin -q -c 'aaa; db sym.main; dc; dso' alvo    # dso = step over
```

## Syscalls e arquivos
```bash
strace -f -e trace=openat,connect,execve ./alvo 2>&1 | head -40
ltrace -f -e 'malloc+free+strcmp' ./alvo 2>&1 | head
```
Em Windows: Process Monitor (ProcMon) ou ETW; em container, `strace` funciona igual.

Syscall de rede (`connect`) sem DNS resolvido é ouro para achar C2/config de servidor.

## Isolamento mínimo
```bash
# container sem rede, read-only, sem capabilities
docker run --rm -it --network=none --read-only --cap-drop=ALL \
  -v "$PWD/alvo:/alvo:ro" debian:trixie-slim /alvo
# VM: qemu com user-mode networking e sem compartilhamento de host
```
Confirme com `ip a` dentro do container e com um `connect` falhando — evidência de que o isolamento existe.

## Anti-debug / anti-VM (reconhecer e contornar com honestidade)
| Técnica | Sinal | Contorno |
|---|---|---|
| `ptrace(PTRACE_TRACEME)` | retorno −1 sob debugger | patch do retorno ou `set follow-fork` |
| `prctl(PR_SET_DUMPABLE)` | falha de attach | hook |
| `rdtsc` timing | saltos por tempo | breakpoint condicional |
| `/proc/self/status` TracerPid | leitura e comparação | fake do arquivo no chroot |
| CPUID/hypervisor bit | detecção de VM | ajustar qemu `-cpu` |
| Debugger check antes de `main` | `.init_array` | breakpoint no construtor |

Contornar anti-debug é análise, **não** ataque: registre o que foi alterado e por quê.

## Fuzzing dirigido
- Um alvo por vez, com corpus pequeno e válido (senão você fuzz de nada).
- AFL++/libFuzzer com instrumentação; sem fonte, use qemu-mode (mais lento, ainda útil).
- Critério de parada declarado (tempo, execuções, crash único). Crash reproduzido com input salvo é evidência.

## Instrumentação de runtime
- `LD_PRELOAD` para interceptar `strcmp`/`open` sem patch de binário — registre o `.so` usado.
- Frida para app empacotado/JS; no nativo, hook em função exportada ou por offset (com ASLR desligado: `setarch -R`).
- eBPF (bpftrace) para observar kernel/`openat` sem parar o processo.

## Limites da dinâmica
- Um caminho observado **não** prova todos os caminhos. Diga "observado neste input".
- Comportamento com rede real pode diferir em isolamento — declare o ambiente.
- Tempo de execução curto esconde rotina de persistência (que roda depois). Use janela declarada.

## Saída
Comandos executados, ambiente de isolamento (com prova), o que foi observado (syscalls, memória, rede), patche/anti-debug contornado e o que **não** se observou.
