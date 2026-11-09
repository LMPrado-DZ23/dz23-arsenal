# Superpowers

**Autor:** obra
**Repo:** https://github.com/obra/superpowers
**Licença:** verificar no repositório

## O que faz

Superpowers é um conjunto de skills que implementa o ciclo de vida de desenvolvimento completo dentro do
agente: brainstorm → spec → plano → TDD → debug → revisão → verificação. A diferença em relação a um
prompt de "faça um plano" é que cada etapa tem artefato e critério de saída.

É a referência mais próxima de "processo de engenharia" empacotado como skill, e influenciou o desenho do
`dz23-spec-to-system-engine` e do `dz23-autonomous-improvement-ultimate`.

## Por que usar em conjunto com DZ23

| Superpowers cobre | DZ23 cobre |
|---|---|
| processo de construção (plan → TDD → review) | gates de evidência por domínio |
| brainstorm e refino de ideia | spec executável com rastreabilidade REQ→TEST |
| ciclo de debug | loop autônomo com checkpoint e revisão adversarial |
| verificação pragmática | veredito `PASS/PARTIAL/FAIL/NOT_TESTED` explícito |

O encaixe natural: **Superpowers define o fluxo; DZ23 define o padrão de prova.** Quem já usa
`dz23-autonomous-improvement-ultimate` ganha com Superpowers a etapa de "como construir", que o loop DZ23
deliberadamente não define (ele orquestra, não implementa).

## Instalação

Como plugin (Claude Code):

```
/plugin install superpowers@claude-plugins-official
```

Manual:
```bash
git clone https://github.com/obra/superpowers.git
cp -r superpowers/* ~/.agents/skills/
```

## Exemplo de uso

```
"Quero adicionar autenticação por magic link. Usa o processo do Superpowers:
 brainstorm comigo, escreve a spec, quebra em plano, e só então implementa com TDD."
```

## Alternativas

- `dz23-spec-to-system-engine` — se você quer só a parte de especificação, com rastreabilidade formal.
- `superpowers` é mais amplo; as duas podem coexistir.

## Cuidados

- O pacote traz **muitas** skills de uma vez; instalar tudo polui o catálogo do agente. Instale o que for
  usar.
- Verifique a licença no repositório antes de uso comercial — este documento não a reproduz.
- Não publique contagem de estrelas: muda toda semana.
