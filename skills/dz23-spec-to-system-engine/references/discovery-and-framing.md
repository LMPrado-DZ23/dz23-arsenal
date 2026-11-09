# Enquadramento e escopo

## Antes da especificação
Especificação que começa pela solução já nasceu torta. Primeiro: qual problema, de quem, com que sintoma, qual o custo de não resolver.

## Enquadramento em 8 respostas
1. **Problema**: o que dói hoje, com evidência (relato, dado, ticket, perda).
2. **Atores**: quem usa, quem decide, quem é impactado e quem paga.
3. **Job to be done**: o que a pessoa tenta concluir — no verbo dela, não no nome da feature.
4. **Resultado esperado**: o que muda de observável quando funcionar.
5. **Restrições**: prazo, orçamento, stack, legado, regulação, contrato, time.
6. **Fora de escopo**: o que **não** entra, com motivo. Escrito.
7. **Riscos conhecidos**: o que pode inviabilizar (dado inexistente, integração instável, decisão política).
8. **Critério de sucesso do projeto**: como saberemos, em 30/90 dias, se valeu.

## Fora de escopo é entrega
Lista explícita evita o "achei que vinha junto". Formato:
```
FORA DE ESCOPO
- Importação de planilha legada — depende de contrato com fornecedor (Q2).
- App mobile — escopo separado, mesma API.
- Relatório customizável — v2; MVP entrega relatório fixo.
```

## Nível de confiança
Marque o enquadramento como:
- **Confirmado** — validado com quem pediu.
- **Assumido** — premissa explícita, precisa validação.
- **Desconhecido** — bloqueia decisão; vira spike ou pergunta.

Nunca trate premissa como requisito.

## Antipadrão de enquadramento
- "O usuário pediu X" sem saber por quê → risco de construir a solução errada com qualidade.
- Escopo que cresce por entusiasmo ("já que estamos aqui…").
- Prazo definido antes do escopo — inverte a ordem e garante corte no lugar errado.

## Triagem da entrada
| Tipo de entrada | Ação primária |
|---|---|
| PRD / documento | extrair objetivo, usuário-alvo, critério de sucesso, fora de escopo |
| User story solta | verificar `Como/Quero/Para que` e completar |
| Brief informal | aplicar as 5 perguntas obrigatórias |
| Ticket vago | reescrever como story + critérios antes de estimar |
| Wireframe / mockup | derivar fluxos, estados de UI e mensagens de erro |
| Spec técnica | mapear para contratos (API, schema, evento) |

Entrada puramente verbal (chat, e-mail, call) → declarar `ENTRADA_INFORMAL` e triar antes de decompor.

## As 5 perguntas obrigatórias
```
1. Quem usa?              (papel/persona concreta, não "o usuário")
2. Qual problema resolve? (dor ou ganho medível)
3. Como se sabe que está pronto? (critério em linguagem natural)
4. O que explicitamente NÃO está no escopo?
5. Qual a consequência de não entregar ou entregar errado?
```
Resposta "não sei" → registrar `AMBIGUIDADE-XXX` e **bloquear** a decomposição até resolver.

## Detector de ambiguidade
| Palavra proibida | Por quê | Substituto exigido |
|---|---|---|
| rápida, performática | sem métrica | p95 < X ms; throughput > Y req/s |
| simples, intuitiva | sem critério | máx. N cliques; N s de aprendizado |
| igual ao X | escopo implícito | listar as funcionalidades exatas do X |
| robusta, escalável | sem threshold | N usuários simultâneos; N req/s |
| fácil de manter | subjetivo | cobertura > X%; complexidade < Y |
| deve funcionar | tautologia | cenário feliz + 3 cenários de erro |

## Formato do registro de ambiguidade
```
AMBIGUIDADE-001 · campo: critério de sucesso do relatório
Pergunta: qual período e qual métrica definem "relatório útil"?
Bloqueia: decomposição (fase 4) e Gherkin (fase 5)
Dono de resolver: <product owner> · prazo: <data>
Status: aberta | resolvida (resposta + quem respondeu + data)
```
Spec aprovada com `AMBIGUIDADE` aberta é reprovada.

## Saída
Um parágrafo de problema + atores + resultado + restrições + fora de escopo + riscos + nível de confiança. Se não cabe em uma página, o problema ainda não está entendido.
