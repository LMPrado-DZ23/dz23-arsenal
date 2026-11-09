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
└── evals/evals.json    # cenários: id, input, expected, fails_if
```

## Regra de ouro: evidência ou silêncio

Nenhuma contribuição declara `PASS` sem comando e saída. O que não foi exercitado é `NOT_TESTED` — e
`NOT_TESTED` é uma resposta aceitável. Alegar sucesso não testado, não.

## Licença

Ao contribuir você concorda em licenciar sua contribuição sob MIT (ver `LICENSE`).
