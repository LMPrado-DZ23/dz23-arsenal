---
name: web-design-guidelines
version: 1.0.0
description: >
  Revisa código de UI contra as Web Interface Guidelines (104 regras em 17 categorias: acessibilidade,
  foco, formulários, animação, tipografia, performance, dark mode, i18n, hidratação, anti-padrões e
  mais). O conhecimento vive DENTRO da skill (dados/ + referência), não numa URL remota: revisa offline,
  sem WebFetch, sem depender de terceiro a cada uso. Saída concisa em `arquivo:linha`, alto sinal.
  Use ao pedir "revise minha UI", "audite acessibilidade", "cheque o site contra boas práticas", antes
  de abrir PR de frontend, ou junto da dz23-ultimate-pro-max (que desenha a UI; esta confere a UI pronta).
  Não é lint de estilo nem reescrita — é auditoria de conformidade com as regras, reportando achados.
user-invocable: true
argument-hint: "<arquivo ou padrão para revisar>"
metadata:
  origin: >
    Regras de vercel-labs/web-interface-guidelines (command.md), MIT lida no arquivo LICENSE da raiz
    (Copyright 2025 Vercel Labs). A skill fina vercel-labs/agent-skills NAO foi usada: sem licenca
    (license:null) e dependia de WebFetch remoto.
  license: MIT
  source-file: skills/web-design-guidelines/references/web-interface-guidelines.md
  method: regras internalizadas e consultáveis offline; adaptado ao rito do arsenal (acervo, consultor, eval, gate)
---

# web-design-guidelines

Revise o código de UI indicado contra as Web Interface Guidelines. Reporte achados; não reescreva.

## Por que fazer isso

- **Autonomia:** as 104 regras vivem no acervo da skill — a revisão roda offline, sem buscar de URL.
- **Acessibilidade e anti-padrões pegos cedo:** botão só-ícone sem `aria-label`, `<div onClick>`,
  foco que não fica preso num modal — tudo flagrado antes do PR, não depois.
- **Sinal alto:** saída em `arquivo:linha`, concisa, uma linha por achado.

## Como revisar

1. **Pegue os arquivos** (o argumento, ou pergunte qual padrão revisar).
2. **Leia o acervo da categoria relevante** antes de afirmar violação:
   `python scripts/consulta-web.py categoria <PT>` (ex.: `acessibilidade`, `formulario`, `animacao`,
   `dark`, `antipadroes`) ou `python scripts/consulta-web.py busca <termo>`. Lista completa em
   `references/web-interface-guidelines.md`.
3. **Cheque cada arquivo contra as regras**, categoria por categoria.
4. **Reporte em `arquivo:linha`** — categoria, regra violada, correção. Modelo em
   `templates/relatorio-revisao.md`.

## O acervo consultável

`dados/regras-por-categoria.csv` — 104 regras, cada uma com `categoria` e `origem_secao`. Consulte, não
decore: `python scripts/consulta-web.py listar` mostra as 17 categorias e os termos PT. O consultor
casa por palavra inteira e responde **"sem correspondência"** quando não há — nunca aproxima.

## Regras inegociáveis

- **Afirmação de violação cita a regra do acervo**, não opinião. Se a regra não está nas 104, não é
  achado desta skill — diga que é recomendação sua, separada.
- **Revisão não altera código.** Esta skill reporta; a correção é passo seguinte (ou outra skill).
- **`arquivo:linha` real.** Um achado sem localização verificável é ruído.
- **Offline.** Não busque as regras de URL remota em tempo de execução; o acervo interno é a fonte.

## Estados de evidência

| Estado | Critério |
|---|---|
| PASS | arquivos revisados, nenhuma violação das 104 regras encontrada |
| PARTIAL | achados listados em `arquivo:linha`, cada um citando a regra |
| NOT_TESTED | pediram revisão mas os arquivos não foram lidos/aplicadas as regras |

## Veredito

Pronto quando: todo arquivo pedido foi lido; cada achado tem `arquivo:linha` + categoria + regra do
acervo + correção; nenhuma violação foi afirmada sem regra que a sustente. Sem achados → PASS; com
achados → PARTIAL com a lista.

## Roteamento com outras skills

- Desenhar/implementar a UI (não revisar): `dz23-ultimate-pro-max` (consome o acervo de design).
- Regras de performance React/Next com priorização: `dz23-performance-scalability-engine`.
- Verificar o comportamento da UI ponta a ponta: `dz23-e2e-browser-verifier`.
