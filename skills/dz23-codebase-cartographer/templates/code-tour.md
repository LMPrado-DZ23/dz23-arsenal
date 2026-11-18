---
tipo: template
agente: dsh
projeto: dz23-arsenal
data: 2026-11-18
tags: [code-tour, contexto, onboarding, cartografia]
---

# Template de code tour (`<nome>.tour`)

Artefato opcional da `dz23-codebase-cartographer`. Serve para explicar código a alguém que não é você,
caminhando por arquivos reais em ordem causal — não listando diretórios.

## Quando fazer (e quando não)

Antes de escrever qualquer linha, consulte o acervo incorporado:

```bash
python scripts/consulta-codebase.py quando-nao <o que o pedido parece ser>
python scripts/consulta-codebase.py profundidade <formato do pedido>
```

| Situação | Decisão |
|---|---|
| Pergunta pontual que se responde em chat | **não** faça `.tour` — responda direto |
| Pedido de documentação em prosa | use `documentation-lookup` ou edite os docs do repo |
| Tarefa de implementação/refatoração | implemente; tour não é entregável aqui |
| Onboarding amplo sem caminho específico | `codebase-onboarding`, não um tour único |
| Explicar como uma feature funciona / revisar PR / achar causa raiz | **faça** o tour |

A segunda consulta diz a persona do leitor e quantos passos ele suporta. Não ignore o número: tour com
passos demais para um leitor rápido é o antipadrão mais comum.

## Estrutura obrigatória

Cabeçalho com escopo e commit, depois passos numerados. Cada passo: arquivo real + o que olhar + por que
vem agora.

```markdown
# Tour: <nome do fluxo>

Commit: <sha> · Escopo: <o que este tour NÃO cobre> · Leitor: <persona> · Passos: <N>

## 1. <título curto orientando o leitor>
Arquivo: `caminho/real/arquivo.ext:LINHA`
Olhe: <função/classe/trecho específico>
Por que aqui: <conexão causal com o próximo passo>
Opcional: `outro/arquivo.ext` (leitura secundária)

## 2. ...
```

Regras inegociáveis, cada uma contra um antipadrão medido no acervo:

| Antipadrão | Correção aplicada neste template |
|---|---|
| Flat file listing | Todo passo tem "Por que aqui" ligando ao seguinte — é narrativa de dependência, não índice |
| Generic descriptions | Nomeie o caminho concreto do código; proibido "a camada de serviço cuida disso" |
| Guessed anchors | Verifique arquivo e linha antes de publicar (ver Validação abaixo) |
| Too many steps for a quick tour | O número vem da consulta de profundidade, não do entusiasmo |
| First step is content-only | O passo 1 ancora num arquivo real, nunca só texto solto |
| Persona mismatch | Declare o leitor no cabeçalho e escreva para ele |

## Âncoras: como verificar antes de entregar

Todo `arquivo:linha` precisa existir no commit declarado. Cheque mecânico, não visual:

```bash
# arquivo existe?
test -f "<arquivo>" || echo "ANCORA QUEBRADA: <arquivo>"
# linha existe? (o arquivo tem pelo menos N linhas?)
[ "$(wc -l < "<arquivo>")" -ge <N> ] || echo "LINHA FORA DO ARQUIVO: <arquivo>:<N>"
```

Ou, em lote sobre o próprio `.tour`:

```bash
grep -oE '`[^`]+:[0-9]+`' <nome>.tour | tr -d '`' | while IFS=: read -r f l; do
  [ -f "$f" ] && [ "$(wc -l < "$f")" -ge "$l" ] || echo "QUEBRA: $f:$l"
done
```

Âncora quebrada é pior que ausência de âncora: o leitor vai até lá, não acha nada, e passa a duvidar do
restante do tour.

## Freshness

Tour envelhece mais rápido que doc comum, porque aponta linha. Registre o commit no cabeçalho e o gatilho
de revalidação (ex.: "revalidar quando `src/billing/**` mudar"). Tour velho engana mais que tour ausente.

## Checklist de entrega

- [ ] `quando-nao` consultado e o caso justifica um `.tour`
- [ ] persona declarada e contagem de passos dentro do intervalo consultado
- [ ] passo 1 ancora em arquivo real
- [ ] todo `arquivo:linha` verificado por comando (saída colada na evidência)
- [ ] nenhum passo é descrição genérica — todos nomeiam caminho e padrão concreto
- [ ] commit e gatilho de revalidação no cabeçalho
