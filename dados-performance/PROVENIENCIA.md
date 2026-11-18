# Proveniência de `dados-performance/`

## Fonte e licença

- **Projeto:** ECC (`affaan-m/everything-claude-code` v2.2.3), baixado como `ECC-main.zip`.
- **Licença:** MIT — lida no arquivo `LICENSE` da raiz do repositório (1.071 caracteres, texto MIT
  completo). Não é a alegação de um README: existe arquivo para ler. Critério e caso concreto discutido
  em `dados-backend/PROVENIENCIA.md` e na decisão do vault
  `20-Decisoes/2026-11-18-dz23-arsenal-licenca-so-no-arquivo-license.md`.
- **Skill-fonte:** `skills/react-performance/SKILL.md`, seções `Priority Index` e
  `Lighthouse / Web Vitals Mapping`.

## Por que esta fonte e não a Vercel

O plano de consolidação nomeava `vercel-labs/agent-skills` (`react-best-practices`) como fonte deste
acervo, listada como MIT. Verificado antes de copiar: **não existe arquivo `LICENSE`** no repositório —
nem na raiz, nem em subpasta, nem dentro de `skills/react-best-practices/`; a API do GitHub devolve
`license: null`; o `package.json` não declara licença; o README tem uma seção `## License` com a palavra
"MIT" sozinha, sem texto, sem aviso de copyright, sem ano. Isso é "o README alega", não "a licença foi
lida". Como o arsenal é público e redistribui conteúdo, a ambiguidade foi resolvida pela regra do
projeto: material permissivo **com arquivo** entra; material sem arquivo não entra.

A ECC `react-performance` cobre o mesmo terreno prioritário — as 8 categorias com prioridade e o mapa de
métricas Web Vitals — com licença verificável. O restante das regras detalhadas da Vercel continua como
referência externa em `external/vercel-react-best-practices.md`, onde pode ser consultado sem que
estejamos redistribuindo o texto.

## Como foi gerado

Mesmo extrator de `dados-backend/`: localiza blocos de tabela markdown com separador `|---|`, captura
cabeçalho e linhas sob a seção nomeada, escreve um CSV por tabela e anexa `origem_arquivo` /
`origem_secao` a cada registro. Só tabelas de decisão foram extraídas; a narrativa da skill-fonte (que é
a maior parte dos ~17 KB) não virou dado — ela já existe coberta pelas camadas 5.2–5.5 do `SKILL.md`
desta skill, e copiá-la criaria segunda fonte de verdade para o mesmo domínio.

| Arquivo | Linhas | Seção na fonte |
|---|---|---|
| `prioridade-por-categoria.csv` | 8 | Priority Index |
| `metrica-para-categoria.csv` | 5 | Lighthouse / Web Vitals Mapping |

## Verificação

- **Fidelidade célula por célula:** as **42 células** de conteúdo dos dois CSVs foram conferidas contra a
  tabela na fonte (comparação normalizada de crase, negrito e espaço). Zero divergências.
- **Consultor com prova no gate:** `scripts/prova-consulta-performance.py` executa 9 consultas legítimas,
  **os 41 termos do mapa PT→EN um a um**, 3 controles negativos e a validação de esquema. Verde, e
  detecta defeito quando injetado (sinônimo morto plantado → exit 1, apontando chave e valor).
- A exaustão do mapa não é burocracia: encontrou um termo (`vital`) apontando para dataset errado, e a
  primeira versão tinha quatro entradas no radical ("waterfall" contra "Waterfalls") que nunca casavam
  nada — invisíveis à prova que testasse só os termos escolhidos para ela.

## Limites do acervo

Ordem de ataque derivada de prática alheia com React/Next em ambiente Vercel. Não substitui medição
própria: serve para escolher por onde começar, não para concluir que algo está otimizado.
