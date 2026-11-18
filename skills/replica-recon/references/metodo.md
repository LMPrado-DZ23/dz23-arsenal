# Método — do app ao mapa de recon

## Passo 1 — escopo

Pergunte três coisas (ou proponha e peça um sim):
1. **Qual app, qual plataforma** (web, iOS, Android, desktop).
2. **Qual fatia.** "Todo o Notion" não é projeto. "Páginas, blocos e compartilhamento do Notion" é.
   Default: o core loop — o fluxo que os usuários pagam.
3. **Para quem** — negócio do usuário, um nicho, um produto para vender.

## Passo 2 — fontes (URL em toda linha)

Monte a tabela de fontes antes de qualquer análise, em ordem de valor. Detalhe em `fontes.md`.

## Passo 3 — inventário de telas

Uma linha por tela, IDs estáveis `S01, S02…` (todo outro arquivo referencia por ID):
`ID | tela | rota/como chegar | propósito | componentes-chave | estados vistos`.
**Estados importam:** vazio, carregando, cheio, erro, permissão negada, mobile. Um estado vazio que
você não registrou é um estado vazio que você não vai construir.

## Passo 4 — fluxos

`F01, F02…` cada um um objetivo e as telas que percorre, com cliques do caminho feliz e casos de borda:
```
F01 Convidado agenda uma reunião
    S07 página de agendamento -> S08 escolher horário -> S09 formulário -> S10 confirmado
    cliques do caminho feliz: 4
    borda: sem horários na semana, fuso diferente, horário tomado enquanto preenchia
```
A contagem de cliques do caminho feliz vira o número a bater no clone.

## Passo 5 — componentes

Toda parte de UI repetida (botão, input, date picker, modal, tabela, toast, nav): nome, variantes,
estados, telas que usam. Vira a lista de componentes do design.

## Passo 6 — modelo de dados inferido

Entidades, campos e relações, cada uma com **evidência** e **confiança**:
```
Agendamento  id, tipo_evento_id, inicio, fim, nome_convidado, email_convidado,
             status (confirmado | cancelado | remarcado), respostas (json)
             evidência: campos do form S09, confirmação S10, artigo "Cancelar agendamento"
             confiança: alta
```
Marque chute como chute. O planejamento de schema (spec/backend) transforma isto em schema real.

## Passo 7 — matriz de features

`replica/features.csv` (feature, área, prioridade, original, clone, notas). Prioridade =
must/should/could. `clone` começa `no` em toda linha e é preenchido durante a construção.

## Passo 8 — o que não dá para clonar

Honestamente, como linhas `skip` com motivo: conteúdo licenciado (catálogo de música, banco de
imagens), a rede e seus usuários, dados do app, deals de parceiro, hardware, licença regulada (banco,
saúde). "Clonar qualquer app" é as features e o fluxo, não o que o app possui.

## Passo 9 — dimensione

Telas, fluxos, entidades e as partes difíceis (realtime, sync, pagamento, integração de calendário/
e-mail, offline). Dê um tamanho: S (um fim de semana), M (semanas), L (um trimestre), XL (reescope).
Sem promessa de clone perfeito.
