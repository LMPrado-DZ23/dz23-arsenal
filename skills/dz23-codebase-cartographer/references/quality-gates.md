# Quality gates — mapa verificável ou nada

| Gate | PASS quando | Evidência mínima |
|---|---|---|
| Pergunta | o mapa responde a uma pergunta declarada | seção "Pergunta" |
| Cabeçalho | repo, commit, branch, data | bloco no topo |
| Inventário | stack real, entry points, build, testes | manifest + Dockerfile + CI |
| Grafo | dependências do caminho crítico com ponteiros | `arquivo:linha` |
| Dados | fonte da verdade × cópias; escritor/leitor | tabela |
| Convenções | padrão com exemplo real | 1 exemplo por regra |
| Risco | zonas classificadas + blast radius | lista de importadores |
| Brief | dentro do orçamento, com "não tocar" e validação | `context-brief.md` |
| Honestidade | observado × inferido × não verificado | marcação por seção |

**Estados:** `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`, `BLOCKED_BY_EXTERNAL_DEPENDENCY` (sem acesso ao repo/banco).

## Severidade

**BLOCKER (não entrega o mapa):**
- Afirmação estrutural sem `arquivo:linha`.
- Mapa sem commit SHA ou data.
- Arquitetura inventada (módulo descrito que não existe).
- "Li tudo" sem amostragem declarada.
- Brief acima do orçamento declarado.
- Zona de risco do núcleo (dinheiro/auth/migração) ausente quando o repo tem.

**MAJOR (entrega com ressalva):**
- Ciclo ou dependência sem verificação.
- Fluxo de dado sem entrada ou saída.
- Hot spot sem evidência de churn/complexidade.
- Convenção afirmada sem exemplo.
- Brief sem comando de validação.
- Área sem teste não mencionada.

**MINOR:**
- Inventário de pasta sem propósito declarado.
- Seção vazia sem nota de ausência.
- Falta de nível de confiança em seção secundária.

## Checklist final
- [ ] Pergunta do mapa escrita.
- [ ] Cabeçalho com repo, commit, branch, data.
- [ ] Stack verificada contra manifest (não contra README).
- [ ] Entry points e comando de run identificados.
- [ ] Grafo do caminho crítico com ponteiros.
- [ ] Fonte da verdade × cópias mapeadas.
- [ ] Convenções com exemplo e arquivo.
- [ ] Zonas de risco classificadas com evidência.
- [ ] Blast radius respondido (importadores, rotas, jobs, tabelas, teste).
- [ ] `context-brief.md` dentro do orçamento, com "não tocar" e validação.
- [ ] Lacunas declaradas (o que não foi verificado).
