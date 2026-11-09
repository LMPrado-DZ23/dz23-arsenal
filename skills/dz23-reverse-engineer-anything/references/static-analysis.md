# Análise estática e decompilação

## Ordem
1. **Localizar** (strings, imports, símbolos, xrefs) → 2. **Desmontar** a região → 3. **Decompilar** (hipótese) → 4. **Confirmar** com a dinâmica.

Decompilador é **hipótese de alto valor**, não fonte. Toda afirmação tirada do decompilador precisa de âncora: instrução, constante ou syscall.

## Ghidra headless (sem GUI, reprodutível)
```bash
# projeto temporário + import + análise automática
$GHIDRA/support/analyzeHeadless.sh /tmp/ghidra proj -import alvo \
  -postScript ExportFunctions.java -scriptPath scripts -deleteProject
```
- Script de exportação mínima (ex.: listar funções com endereço e tamanho) torna o resultado **auditável**.
- Use `-processor` quando a detecção falhar (ARMv7, MIPS BE, RISCV).
- Rode em cópia do arquivo, nunca no original; gere o projeto em diretório descartável.

## Rizin / radare2 (rápido, scriptável)
```bash
rizin -q -c 'aaa; afl; izz~password; pdf @ sym.main' alvo
rizin -q -c 'aaa; axt @ 0x401234; pdf @ 0x4012a0' alvo     # xrefs + função
rizin -q -c 'iI; iS; ii' alvo                               # info, seções, imports
```
`aaa` (análise completa) é caro; em binário grande, analise por região (`af @ addr`) depois de achar a função por string/xref.

## Localizar por string (o atalho que funciona)
```bash
strings -t x -n 6 alvo | grep -iE 'error|fail|password|token|/api/|http' | head -30
# -t x dá o offset: é a evidência que você vai citar
```
Depois: xref da string → função que a usa → `pdf`/`decompile` → confirmação.

## Funções de biblioteca sem símbolo
Reconheça por padrão de código (FLIRT/signature quando houver):
```bash
# Rizin: aplicar assinaturas se disponíveis
rizin -q -c 'zfc libc.sig; aaa; afl~strcpy' alvo
```
Sem assinatura: compare o prólogo com a implementação conhecida da ABI (ex.: `strlen` com loop de 4 bytes é inconfundível).

## Fluxo de controle e dados
| Pergunta | Como responder |
|---|---|
| quem chama esta função | `axt @ <addr>` (Rizin), xrefs no Ghidra |
| quais constantes usa | `pdf` e grep de `0x` |
| tabela de despacho (switch) | `jmp [rax*4+0x...]` → dump da tabela com `pxw` |
| struct layout | leitura de offsets `[rdi+0x18]` somada ao tamanho alocado |
| string cifrada em `.rodata` | entropia do bloco + rotina de decifra referenciada |

## Binários grandes: estratégia
- Não analise tudo. Ache **3 a 5 funções** que respondem à pergunta do dono (ex.: "como valida licença?").
- Marque o resto como `NOT_ANALYZED` no relatório — cobertura parcial declarada é honesta e útil.
- Em firmware com 500 binários, priorize: init scripts, serviço exposto na rede, binário que fala com o hardware.

## Anti-análise estática (reconhecer)
- String ofuscada (XOR/RC4 em `.rodata`) → procure rotina com laço curto e chave imediata.
- Fluxo achatado (state machine com `switch` enorme) → mapeie os estados, não o grafo.
- Chamada indireta por tabela calculada → resolva a tabela estaticamente quando possível.
- `.init_array` com verificação → a checagem roda **antes** de `main`; procure lá.

## Saída
Lista de funções analisadas com endereço, hipótese de papel, âncora de evidência (instrução/string/constante) e o que ficou sem análise.
