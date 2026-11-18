# Marca: {{seu nome}}

Ângulo (de replica/fixes.md): {{posicionamento}}

## Nome

Finalistas e checagens (marque "a rodar" ou o resultado + data; nunca "disponível" sem rodar):

| nome | marca US | marca EU | domínio | App Store/Play | handles | web |
|---|---|---|---|---|---|---|
| {{nome}} | a rodar | a rodar | a rodar | a rodar | a rodar | a rodar |

Escolhido: **{{nome}}** — porque {{razão ligada ao ângulo}}.

## Paleta

Primária de família diferente da do original ({{deles}} → {{sua}}). Zero falha AA.

| papel | cor |
|---|---|
| primária | {{#hex}} |
| superfície | {{#hex}} |
| texto | {{#hex}} |

## Brief de logo

- Ideia (uma linha): {{…}}
- Tipo: wordmark / símbolo+wordmark / monograma
- Funciona a 16px e 1024px. Entregáveis: SVG, ícone 1024 sem transparência, favicon, social 1200×630.
- Não pode parecer o do original: {{o que evitar}}.

## Voz

Três palavras: {{x (não y)}}, {{…}}, {{…}}. Faz/evita: {{5 pares}}.
Strings reescritas: {{cadastro, vazio, botão, confirmação, erro}} — nenhuma ecoando o original.

## Sweep

`python scripts/sweep.py . --config replica/brand.json` → **clean** (nenhuma sobra do original).
