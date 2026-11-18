# Revisão de interface web — <arquivo ou padrão>

Data: <AAAA-MM-DD> · Arquivos: <lista> · Regras aplicadas: 104 (Vercel WIG, MIT)

## Achados (formato `arquivo:linha`)

> Conciso e de alto sinal: sacrifique gramática por brevidade. Uma linha por achado, com a categoria
> e a regra violada.

| arquivo:linha | categoria | regra violada | correção |
|---|---|---|---|
| `src/Button.tsx:12` | Accessibility | botão só-ícone sem `aria-label` | adicionar `aria-label="Fechar"` |
| `src/Modal.tsx:40` | Focus States | foco não fica preso no modal aberto | trap de foco + retorno ao gatilho ao fechar |
| `src/Card.tsx:8` | Anti-patterns | `<div onClick>` para ação | trocar por `<button>` |

## Por categoria (cobertura da revisão)

Marque as categorias efetivamente checadas (consulte com `python scripts/consulta-web.py categoria <PT>`):

- [ ] Acessibilidade  [ ] Foco  [ ] Formulários  [ ] Animação  [ ] Tipografia  [ ] Conteúdo
- [ ] Imagens  [ ] Performance  [ ] Navegação  [ ] Toque  [ ] Layout/Safe-area  [ ] Dark mode
- [ ] i18n  [ ] Hidratação  [ ] Hover  [ ] Copy  [ ] Anti-padrões

## Veredito

- Total de achados: <N> · Bloqueadores (acessibilidade/anti-padrão): <N>
- Estado: **PASS** (sem violação) / **PARTIAL** (achados listados) — a revisão não altera o código,
  só reporta; correção é passo seguinte.
