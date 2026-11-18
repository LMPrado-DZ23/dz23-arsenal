# Proveniência — dados/ (acervo de engenharia reversa)

- **Fonte:** **ORIGINAL (DZ23)** — destilado das próprias referências da skill
  (`references/anti-patterns.md` e a seção "Seleção de referências" do `SKILL.md`). Nada externo foi
  copiado; é o conhecimento que a skill já tinha, agora **consultável**.
- **O que é:** 2 datasets (49 registros):
  - `anti-padroes.csv` (38): fase → anti-padrão → por que dói → correção (autorização, identificação,
    estática, dinâmica, firmware, emulação, hardware, relatório).
  - `selecao-de-referencia.csv` (11): situação → qual `references/*.md` carregar (carregamento progressivo).
- **Geração:** parse do `anti-patterns.md` (itens `sintoma → por que → correção`), com
  `origem_arquivo`/`origem_secao`.
- **Consulta:** `scripts/consulta-reverse.py` (subcomando PT: anti/antipadrao/fase, referencia/ref,
  busca; matcher normaliza acento) + `scripts/prova-consulta-reverse.py` no gate.
