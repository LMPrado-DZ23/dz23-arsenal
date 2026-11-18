# Mapa de recon: {{app}} ({{plataforma}})

Fatia: {{a fatia sendo clonada}}
Para: {{para quem é o clone}}
Data: {{AAAA-MM-DD}}

## Fontes

| # | fonte | URL | notas |
| --- | --- | --- | --- |
| 1 | central de ajuda | | |

## Core loop

{{uma frase: a coisa que os usuários pagam}}

## Telas

| ID | tela | rota / como chegar | propósito | componentes-chave | estados vistos |
| --- | --- | --- | --- | --- | --- |
| S01 | | | | | vazio, cheio, erro |

## Fluxos

```
F01 {{objetivo}}
    S01 -> S02 -> S03
    cliques do caminho feliz: {{n}}
    borda: {{casos}}
```

## Componentes

| componente | variantes | estados | usado em |
| --- | --- | --- | --- |
| Botão | primário, secundário, ghost, perigo | default, hover, foco, desabilitado, carregando | todas |

## Modelo de dados inferido

```
{{Entidade}}  {{campos}}
              evidência: {{IDs de tela, artigos de ajuda}}
              confiança: alta | média | chute
```

Relações: {{Usuário 1-n TipoEvento, TipoEvento 1-n Agendamento, …}}

## Matriz de features

Ver `features.csv`. Must: {{n}}, should: {{n}}, could: {{n}}, skip: {{n}}.

## Fora de escopo (não dá ou não se deve clonar)

- {{conteúdo licenciado, a rede, deals de parceiro, …}}

## Tamanho

Telas {{n}}, fluxos {{n}}, entidades {{n}}. Partes difíceis: {{lista}}. Tamanho: {{S|M|L|XL}}.
