# Instalação no DeepSeek Harness

1. Descubra o diretório real de skills pelo loader/configuração do DeepSeek Harness. Não presuma `~/.agents/skills` ou qualquer caminho universal.
2. Extraia a pasta `dz23-ultimate-pro-max` inteira para esse diretório, preservando SKILL.md, references e scripts.
3. Reinicie/recarregue o catálogo; confirme descoberta pelo nome `dz23-ultimate-pro-max` e leitura efetiva de SKILL.md.
4. Se não houver descoberta automática, configure a instrução persistente: `Para UI/UX/frontend, leia integralmente <CAMINHO_REAL>/dz23-ultimate-pro-max/SKILL.md e as referências pertinentes antes de modificar código`.
5. Execute `python scripts/validate_skill.py` dentro da pasta para verificar integridade documental.
6. Faça uma tarefa-piloto de uma tela, exija direção visual, build, captura renderizada e evidências. A declaração do agente sozinha não comprova que carregou a skill.
7. Use o arquivo `PROMPT-ATIVACAO.txt` para ativação manual.

Esta skill não instala componentes shadcn nem modifica B-3PO automaticamente.
