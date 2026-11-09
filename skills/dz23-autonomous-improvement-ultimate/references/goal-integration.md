# Integração com /goal

## Entrada
Extraia do comando: resultado desejado, escopo, não escopo, repositório, ambiente, prazo/orçamento, riscos, permissões e critérios de aceite. Traduza expressões vagas como “10/10”, “sem erros” e “melhorar tudo” em fluxos e medições observáveis. Não interprete essas expressões como autorização para alterações destrutivas.

## Contrato mínimo
```markdown
# Acceptance
- Goal: ...
- In scope: ...
- Out of scope: ...
- Environment: ...
- Limits: session, cost, iterations (if provided)
| ID | Criterion | Evidence | Status |
|---|---|---|---|
| REQ-001 | ... | ... | NOT_RUN |
```

## Skills simultâneas
- Esta skill é **orquestradora de qualidade**, não substitui o `/goal` nem a skill especializada.
- Se UI/UX, carregar `dz23-ultimate-pro-max` para direção visual, screenshots, WCAG e responsividade.
- Se banco/infra, seguir procedimentos nativos e políticas do projeto; não inventar ferramentas.
- Um único backlog e um único checkpoint devem ser a fonte de verdade; evite dois agentes editando os mesmos arquivos simultaneamente.

## Retorno e término
O `/goal` permanece aberto até aceite verificado ou bloqueio/limite legítimo. O encerramento da sessão não equivale a conclusão. A skill não cria um serviço 24/7; continuidade real depende do harness/scheduler e de execução autorizada.
