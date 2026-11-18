# Proveniência do material externo (`vendor/`)

Este arquivo registra **o que entrou de fora, de onde veio, sob qual licença e o que foi feito com
isso**. Não existe para burocracia: um repositório que incorpora código alheio sem rastreabilidade
perde o direito de relicenciar, não consegue responder a um pedido de remoção e quebra a própria
política que declara. Ver `docs/OSS_FUSION_POLICY.md` do projeto irmão e `external/` aqui.

## Regra operacional

| Situação | O que entra no arsenal |
|---|---|
| Licença permissiva identificada (MIT, Apache-2.0, ISC, BSD, CC0) | **Código ou dados copiados**, com aviso de origem ao lado |
| Licença ausente ou ambígua | **Nada.** Só a ideia, reimplementada do zero, registrada como `ORIGINAL` |
| Licença copyleft (GPL, AGPL, CC-BY-SA) | **Nada copiado.** Excluído explicitamente |

Nenhuma linha foi incorporada antes de a licença ser lida no arquivo `LICENSE`, não no que o README
alega. Foi assim que `osime-osint-investigation` (CC-BY-SA-4.0) ficou de fora na triagem inicial.

## Incorporado

### `dados-design/ui-ux-pro-max-data/` — 39 arquivos, ~3 MB
- **Origem:** skill `ui-ux-pro-max` (instalada em `~/.agents/skills/ui-ux-pro-max`).
- **Licença:** ISC, declarada no corpo da habilidade.
- **O que é:** base de conhecimento estruturada e consultável — 80 estilos de interface ativos,
  192 perfis de paleta e raciocínio por tipo de produto (`styles.csv`, `ui-reasoning.csv`,
  `products.csv`), 74 diretrizes de UX (`ux-guidelines.csv`), 105 ícones, 17 stacks, 25 tipos de
  gráfico, presets GSAP, e catálogo de fontes com a licença de cada família
  (`google-fonts.csv`, `google-font-licenses.json`: 1.934 famílias, quase todas OFL).
- **Como foi usado:** referência de consulta pela skill `dz23-ultimate-pro-max`. Os CSVs têm
  proveniência própria em `data-provenance.json`, apontando para W3C e GoogleChrome — dados
  verificados, não opinião gerada.
- **Modificações:** nenhuma. Cópia byte a byte dos `.csv`/`.json` de dados; scripts, testes e
  fixtures da skill de origem **não** foram trazidos.

## Avaliado e NÃO incorporado

| Fonte | Licença | Motivo |
|---|---|---|
| `ECC-main.zip` | MIT | 38 MB / 4.878 arquivos de skills e agentes de terceiros. Aproveitável como técnica, já destilada em `external/`. Copiar inteiro criaria duas fontes de verdade para a mesma orientação e apagaria a autoria das nossas. |
| `modern-web-guidance-src-main.zip` | Apache-2.0 | 38 MB, sendo 428 `.patch` e 329 `.html` de casos de teste upstream. A versão destilada já está instalada (`modern-web-guidance`, 210 arquivos/1,9 MB) e é o que as skills consomem. |
| `open-code-review-main.zip` | Apache-2.0 | Código Go de ferramenta externa, executável por CLI (`ocr`). Integrar por comando é mais honesto que duplicar 551 arquivos `.go`. |
| `ui-main.zip` | MIT | 30 MB de componentes React/Next (.tsx). São componentes de biblioteca alheia; o arsenal orienta *como* construir UI, não distribui catálogo de widgets. Usar via dependência quando um projeto específico precisar. |
| `astryx-main.zip` | MIT | 290 MB de design system com binários. Já disponível pelo comando `astryx` nesta máquina; a skill `astryx` instalada aponta para ele. |
| `rea-main.zip` | MIT (referência a GPLv3 em dependência) | Ferramenta já instalada e operada por MCP neste ambiente. |
| `osime-osint-investigation` | CC-BY-SA-4.0 | Copyleft de atribuição compartilhada: incorporar obrigaria relicenciar o arsenal. Excluído na triagem. |

## Pendente de decisão

Nada nesta pasta depende de decisão sua para continuar válido. Se algum dia o arsenal deixar de ser
MIT, revisar antes: `ui-ux-pro-max-data` (ISC, compatível com sublicenciamento).
