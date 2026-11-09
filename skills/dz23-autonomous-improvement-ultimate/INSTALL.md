# Instalação — DZ23 Autonomous Improvement Ultimate

1. Extraia a pasta `dz23-autonomous-improvement-ultimate` no diretório de skills reconhecido pelo seu DeepSeek Harness (o caminho varia por instalação).
2. Confirme que o loader reconhece `SKILL.md` e carrega as referências quando solicitadas.
3. No `/goal`, instrua o agente a carregar `dz23-autonomous-improvement-ultimate` e, em frontend, `dz23-ultimate-pro-max`.
4. Faça um teste controlado: introduza um bug reproduzível em branch de teste, rode o goal e confirme baseline, teste falhando, correção, reteste, checkpoint e relatório com evidências.
5. Se o harness não suporta skills nativamente, configure leitura explícita do SKILL.md. Se não possui retomada automática, a skill não cria esse recurso.

Exemplo:
```text
/goal
Carregue dz23-autonomous-improvement-ultimate. Objetivo: corrigir defeitos reproduzíveis no escopo definido e validar cada requisito. Em UI, carregue também dz23-ultimate-pro-max. Preserve mudanças existentes; faça checkpoints e reporte evidências reais. Não execute ações destrutivas sem autorização.
```
