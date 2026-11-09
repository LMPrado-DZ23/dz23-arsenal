# Changelog — Agência de especialistas DSH

## [1.0.0] — 2026-11-08

Primeira versão consolidada e distribuível.

### Adicionado
- `VERSION` (1.0.0)
- `build.py` — gera `agents/` com 88 arquivos prontos para colar no
  campo `agent-instructions`; modos `--check`, `--list`, `--stdout NN`
- `agents/` pré-gerado (00-diretor + 01..87)
- `CHANGELOG.md` (este arquivo)

### Alterado
- `README.md`: navegação completa + versão declarada
- `DSH_COMPLETE_SPECIALIST_AGENCY.md`: nota anti-duplicação Diretor/01
  na seção Instalação
- `check_consistency.py`: flag `--strict` (aviso vira falha)
- `check_consistency.py`: REF_NAMED mais estrito (reduz falso-positivo)
- `DSH_SPECIALIST_AGENT_CATALOG*.md`: instrução "copie núcleo + perfil"
  consolidada em referência ao canônico (mantém parágrafo próprio, mas
  não repete o procedimento 3×)

### Corrigido
- Referências cruzadas validadas (C3)
- Links markdown resolvem (C4)
- Limite 65536 bytes verificado em todos os 88 agentes (C6+C7)

## [0.9.0] — anterior (não versionado)

Estado consolidado a partir de 5 fontes (Gemini, Claude, Manus, DeepSeek,
ChatGPT). Ver `COMPARISON.md`.
