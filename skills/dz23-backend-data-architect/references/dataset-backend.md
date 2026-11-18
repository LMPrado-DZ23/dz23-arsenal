# Acervo de decisões de backend (dados-backend/)

Índice de **uso**. Origem, licença e verificação estão em `dados-backend/PROVENIENCIA.md` e no registro
geral `dados-design/VENDOR.md`. Este arquivo existe para responder uma pergunta só: **quando consultar
o acervo em vez de improvisar.**

## O que é

30 decisões tabuladas, extraídas das tabelas de decisão do ECC (MIT), cada linha com arquivo e seção
de origem embutidos na própria célula:

| Dataset | Registros | Responde |
|---|---|---|
| `indices-por-padrao-de-query.csv` | 6 | Que índice usar para tal forma de `WHERE` (B-tree, composta, GIN, BRIN) |
| `tipos-de-dado.csv` | 5 | Tipo correto por caso de uso — e o que evitar (`float` para dinheiro, `varchar(255)`) |
| `antipadroes-de-migracao.csv` | 6 | Anti-padrão de migração, por que falha e a abordagem melhor |
| `semantica-de-metodo-http.csv` | 5 | Método HTTP: seguro? idempotente? para quê |
| `estilo-de-api-quando-usar.csv` | 4 | Offset vs cursor por formato de dado |
| `faixas-de-rate-limit.csv` | 4 | Rate limit por tipo de chamador (anônimo → interno) |

## Como consultar

```bash
python scripts/consulta-backend.py listar
python scripts/consulta-backend.py tipo dinheiro
python scripts/consulta-backend.py indice "tempo de serie"
python scripts/consulta-backend.py migracao "editar migracao"
python scripts/consulta-backend.py http parcial
python scripts/consulta-backend.py api "scroll infinito"
python scripts/consulta-backend.py limite interno
```

Português funciona por mapa fechado termo-a-termo (`dinheiro`→Money, `interno`→Internal). Se a palavra
não está no mapa nem na tabela, a resposta é **"sem correspondência"** mais a lista de valores
disponíveis — nunca uma aproximação. Isso é deliberado: um acervo que responde a pergunta certa com a
linha errada engana mais que um acervo ausente, porque o agente passa a confiar no resultado.

## Quando consultar no método

- **Modelando tabela ou coluna** → `tipo <caso>` antes de escolher o tipo, e `indice <padrão de query>`
  ao criar índice. Custo de trocar tipo depois é migração com rewrite; custa zero perguntar agora.
- **Escrevendo migração** → `migracao <suspeita>` consulta a lista de anti-padrões. Combinar com
  `references/migrations-and-zero-downtime.md`, que tem o *como* (expand/contract, backfill convergente)
  e os executáveis autoverificáveis em `examples/`.
- **Desenhando endpoint** → `http <método>` para semântica de segurança/idempotência; `api <formato>`
  para paginação; `limite <tipo de chamador>` para expor rate limit coerente.
- **Revisando código alheio** → os seis datasets juntos funcionam como checklist: se alguma linha sua
  contradiz uma linha daqui, ou a fonte está desatualizada ou você tem motivo para documentar.

## Limite honesto

São 30 linhas, não um corpo de conhecimento — destiladas de tabelas de decisão de três skills do ECC.
O restante do valor daquelas fontes é narrativa, e foi para `references/` como texto, não como dado.
Não trate ausência de linha aqui como licença para inventar: o acervo cobre o que foi medido na fonte;
fora disso, decide-se pelo projeto, e se registra a decisão (ver `dz23-spec-to-system-engine` / ADR).

Material sem equivalente tabulado neste arsenal (padrões de API em geral, arquitetura de serviço,
observabilidade) continua em `references/` desta skill — consultável por leitura, não por comando.
