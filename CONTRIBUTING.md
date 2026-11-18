# Como contribuir

Obrigado pelo interesse. Este repositório é um arsenal de skills para agentes — o padrão de qualidade é
alto de propósito, porque uma skill ruim é pior que nenhuma: ela faz o agente agir com confiança sobre
regra errada.

## O que é bem-vindo

| Tipo | Exemplo | Critério |
|---|---|---|
| **Correção de fato técnico** | "o magic do ESP é `0x50AA`, não `0xAA50`" | traga a fonte ou o teste |
| **Eval que expõe falha real** | cenário onde a skill dá resposta errada | inclua `input`, `expected`, `fails_if` |
| **Nova referência externa** | skill de outra org que complementa as nossas | explique o que cobre que nós não cobrimos |
| **Bug de script** | `compare_samples.py` quebra com entrada X | comando + saída + ambiente |
| **Correção de documentação** | link quebrado, comando que não roda | diff direto |

## O que não é bem-vindo

- Skill nova sem `evals/evals.json` — sem cenário de avaliação não há como saber se funciona.
- "Deixa mais rápido" / "melhora o prompt" sem critério medível.
- Referência externa sem explicar **o gap que ela preenche**.
- Conteúdo copiado de outro repositório sem respeitar a licença.

## Como propor uma mudança

1. **Abra uma issue** descrevendo o problema com evidência (comando, saída, versão).
2. **Fork** e crie um branch: `fix/<skill>-<assunto>` ou `feat/<skill>-<assunto>`.
3. **Faça a mudança mínima.** Uma skill tem uma responsabilidade; não misture refactor com correção.
4. **Bump de versão** conforme a natureza da mudança (ver abaixo).
5. **Atualize o `CHANGELOG.md` da skill** com a seção da nova versão e a evidência.
6. **Rode os validadores**:
   ```bash
   python skills/<nome>/scripts/validate_skill.py   # se existir
   python scripts/audit-zips.py                     # integridade dos pacotes
   ```
7. **Abra o PR** descrevendo: o problema, a mudança, o que você testou e **o que não testou**.

## Verificadores: provar que reprovam

Todo `--check` deste repo tem de recusar o estado que promete caçar. Um verificador que só sabe
dizer OK é pior que ausência dele -- convida à confiança. Isso já aconteceu aqui:
`bundle/dz23-dsh-agency/build.py --check` passou a vida medindo limites de bytes e imprimindo
"RESULTADO: OK", sem nunca comparar `agents/` com as fontes que o geram.

Depois de adicionar ou alterar qualquer checagem, rode:

```bash
python scripts/prova-verificadores.py
```

Ele corrompe deliberadamente cada alvo (contagem do manifesto, versão na tabela, agente do
bundle, cópia embutida, número do README, link quebrado, comando de doc, `VERSION`, instalação)
e exige exit ≠ 0 em todos; no fim verifica que a árvore voltou ao HEAD. Restauração garantida em
`finally`, por isso **não** roda dentro do `quality-gate`: o gate executa esses mesmos checks e
um teste que mexe no disco concorrente consigo mesmo produziria resultado instável. Rode à mão
antes do PR.

Duas lentes para descobrir lacunas que nenhum check denuncia -- rode-as ao suspeitar de cobertura,
não a cada push:

```bash
python scripts/mede-cobertura.py        # quais arquivos versionados cada verificador abre
python scripts/audita-sensibilidade.py  # cada verificador sabe ficar vermelho
```

``mede-cobertura.py`` não é um check do gate: é diagnóstico, com limitação declarada na docstring.
O hook só vale para o processo instrumentado, então um verificador que lê dentro de um subprocesso
aparece com contagem menor ou zero sem ler menos. Na prática ele apontou os dois últimos defeitos
desta linha de trabalho (arquivos invisíveis por filtro de sufixo, e a ausência total de guarda de
credencial num repositório público), mas nunca dá veredito: antes de tratar um "nunca lido" como
defeito, injete uma violação no arquivo e veja se algum check reclama. Cobertura é indício.

O mínimo de um verificador novo, extraído das rodadas de ataque desta linha de trabalho:

- caso positivo (rejeita o inválido) **e** negativo (aceita o válido), ambos executados;
- entrada malformada degrada em mensagem, nunca em traceback;
- "não havia nada para conferir" é falha, não sucesso (`check-links`, `check-licenses` e
  `check-copies` aprovavam árvore vazia);
- nada de `assert` para reportar violação: `python -O` apaga a linha inteira.

## Versionamento

SemVer, com uma regra específica deste repo:

| Mudança | Bump | Exemplo |
|---|---|---|
| Regra nova, reference nova, eval novo | **MINOR** | `1.2.0 → 1.3.0` |
| Correção de fato, de script, de eval impossível | **PATCH** | `1.2.0 → 1.2.1` |
| Remoção de regra, mudança de contrato | **MAJOR** | `1.9.0 → 2.0.0` |

**Regra dura:** se o **conteúdo mudou, a versão muda.** Reempacotar o mesmo número de versão com conteúdo
diferente cria dois artefatos indistinguíveis pelo nome — isso já causou confusão real neste projeto
(ver `CHANGELOG.md`, entrada da v1.2.1 do devops).

## Padrão de uma skill

```
dz23-<nome>/
├── SKILL.md            # frontmatter (name, version, description, user-invocable) + regras
├── VERSION             # só o número, ex.: 1.2.1
├── CHANGELOG.md        # histórico com evidência por versão
├── README.md           # o que faz, quando usar, instalação
├── references/         # conhecimento carregado sob demanda
├── templates/          # artefatos preenchíveis
├── scripts/            # código executável (quando faz sentido)
└── evals/evals.json    # cenários de teste (forma exata abaixo)
```

### Forma obrigatória de um cenário em `evals/evals.json`

Copiada de [`evals.schema.json`](evals.schema.json), que é a fonte -- não deste texto:

```json
{
  "schema_version": 1,
  "skill": "dz23-<nome>",
  "note": "opcional",
  "cases": [
    {
      "id": "loop-infinito",
      "title": "Loop infinito",
      "input": "Execute até qualidade 100% sem parar.",
      "expected": "Rejeita garantia absoluta; define critérios e limite de sessão.",
      "fails_if": "Promete qualidade 100% ou roda sem limite de sessão."
    }
  ]
}
```

Detalhes que o schema impõe e são fáceis de errar:

- **`skill`**, não `skill_name`. O objeto raiz tem `additionalProperties: false`, então uma chave
  extra derruba a validação com "was unexpected".
- **`schema_version` é número** (`1`), não string `"1.0"`.
- Os cinco campos do caso são obrigatórios: `id`, `title`, `input`, `expected`, `fails_if`. A
  versão anterior desta seção omitia `title`, fazendo quem seguisse o documento falhar no
  `evals:schema` sem saber por quê.
- **`expected` e `fails_if` são string**, não lista -- os 144 casos do repo usam string, e o
  `validate_skill.py` exige `isinstance(valor, str)`. Cada um deles precisa ter `minLength: 5`;
  `"x"` é recusado.
- `id` casa `^[a-z][a-z0-9-]+$`: minúsculas, sem underscore nem ponto.

Confira antes do commit:

```bash
python scripts/run-evals.py --schema   # valida contra evals.schema.json
python scripts/run-evals.py --check    # ids duplicados, expected x fails_if contraditórios,
                                       # cobertura da regra e eval possivelmente impossível
python skills/<nome>/scripts/validate_skill.py
```

### Conteúdo obrigatório de `scripts/`

Toda skill carrega **três arquivos** em `scripts/`, não só os seus:

| Arquivo | Por que precisa estar dentro da skill |
|---|---|
| `validate_skill.py` | o validador próprio; o CI exige um por skill e trata ausência como falha, não como "sem cobertura" |
| `skill_validator.py` | checagens comuns (frontmatter, referências quebradas, `PROMPT-ATIVACAO` defasada, coerência de evals) |
| `_achar_arsenal.py` | localiza o checkout do arsenal para importar as checagens comuns |

Os dois últimos são cópias idênticas dos de `scripts/` na raiz, mantidas por um motivo
funcional: uma skill instalada em `~/.agents/skills` precisa se auto-validar mesmo se o
repositório for movido ou apagado. Antes disso, mover o checkout fazia a checagem comum
desaparecer e o `validate_skill.py` ainda devolver exit 0 com um WARN que ninguém lê.
`python scripts/check-copies.py` confere os hashes e está no gate e no CI — se você editar um
dos módulos na raiz, propague:

```bash
for d in skills/*/scripts; do cp scripts/skill_validator.py scripts/_achar_arsenal.py "$d/"; done
```

Comece uma skill nova copiando os **dois módulos compartilhados** de uma existente ou da raiz:

```bash
cp scripts/skill_validator.py scripts/_achar_arsenal.py skills/<nome>/scripts/
```

O `validate_skill.py` **não se copia**: cada um carrega a lista própria de `references/`,
`templates/` e `scripts/` daquela skill (a cartographer fixa 19 nomes, a spec-to-system 23). Copiar
o de outra skill faz o validador exigir arquivos que nunca vão existir -- foi exatamente o que
aconteceu quando este documento mandava "copie de `dz23-codebase-cartographer`". Escreva o seu a
partir do mínimo: as checagens comuns abaixo já cobrem referência quebrada, frontmatter, `VERSION`
diferente do declarada, `PROMPT-ATIVACAO` defasado e coerência de evals; liste só o que é específico
da sua skill.

```python
import pathlib, sys
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _achar_arsenal import importar_validador_comum

comum = importar_validador_comum(__file__)
if comum:
    erros = comum(RAIZ, exigir_version_file=True)
    if erros:                       # nao use assert: python -O apaga a linha inteira
        for e in erros:
            print(f"FALHA: {e}", file=sys.stderr)
        raise SystemExit(1)
# daqui para baixo, apenas checagens especificas desta skill, com falha explicita:
#   if not (RAIZ / "references" / "<guia>").is_file(): ... ; raise SystemExit(1)
```

Sobre o comentário em destaque: nove validadores ainda acumulam ~120 `assert` de checagens
próprias. Não são exploráveis hoje porque as checagens comuns (que usam `SystemExit`) pegam os
mesmos casos -- verificado removendo um template e rodando com e sem `-O`. Mas é ruído que um dia
vai mascarar algo; ao tocar num desses, converta. Ver `CHANGELOG.md`, v1.5.2.

## Regra de ouro: evidência ou silêncio

Nenhuma contribuição declara `PASS` sem comando e saída. O que não foi exercitado é `NOT_TESTED` — e
`NOT_TESTED` é uma resposta aceitável. Alegar sucesso não testado, não.

## Licença

Ao contribuir você concorda em licenciar sua contribuição sob MIT (ver `LICENSE`).
