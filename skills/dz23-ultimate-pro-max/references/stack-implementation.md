# Implementação por stack (Tailwind, shadcn/ui, React, Next, Vue, mobile)

Este documento cobre o que a direção de arte **não** cobre: como o design system vira código na stack real
sem perder token, estado e acessibilidade.

## 1. Tokens → configuração da stack

Três camadas, nunca uma só:

| Camada | Exemplo | Onde vive |
|---|---|---|
| **Primitiva** | `--blue-600: #2563eb` | tema / CSS variables |
| **Semântica** | `--color-action-primary` | tema, referenciando primitiva |
| **Componente** | `--button-bg` | componente, referenciando semântica |

Regra: componente **nunca** usa primitiva direto. Se usar, trocar de tema quebra a UI e ninguém descobre
até o cliente reclamar.

**Tailwind (v3/v4):** mapeie tokens semânticos no tema, não valores soltos no JSX.

```js
// tailwind.config.js (resumo)
theme: {
  extend: {
    colors: {
      action: { primary: "var(--color-action-primary)" },
      surface: { base: "var(--color-surface-base)" },
    },
    spacing: { 1: "4px", 2: "8px", 3: "12px", 4: "16px" }, // escala fixa, sem valor ad hoc
    fontFamily: { sans: ["var(--font-sans)", "system-ui"] },
  }
}
```

Proibido no JSX: `text-[#7c3aed]`, `p-[13px]`, `mt-[7px]`. Valor mágico é dívida de design.

## 2. shadcn/ui — adotar, não copiar cego

- shadcn/ui é **código-fonte adaptável**, não dependência de runtime: você incorpora o componente e passa a
  ser dono dele.
- Antes de incorporar: verifique stack, versão de React, política de acessibilidade e o que o componente
  **não** faz (loading, erro, permissão).
- Ao incorporar, ajuste ao token semântico do projeto — não deixe a paleta default do shadcn.
- Componente incorporado entra no inventário de componentes; não crie um segundo "botão do projeto".

## 3. Estados obrigatórios de cada componente interativo

| Estado | Como aparece | Como verificar |
|---|---|---|
| default | base | render inicial |
| hover | mudança sutil de fundo/elevação | mouse sobre |
| active/pressed | leve depressão | clique mantido |
| **focus-visible** | anel visível, 2px+, contraste ≥ 3:1 | **só teclado** (Tab), nunca `outline: none` sem substituto |
| disabled | opacidade + `cursor-not-allowed` + `aria-disabled` | interação bloqueada |
| loading | spinner/disabled + texto de progresso | ação dupla não dispara duas vezes |
| error | mensagem associada ao campo (`aria-describedby`) | leitor de tela anuncia |

`outline: none` sem alternativa é **BLOCKER** de acessibilidade, não detalhe estético.

## 4. Especificidades por stack

**React**
- Componente controlado por padrão; estado local só para UI efêmera.
- `key` estável (nunca índice em lista mutável).
- Evite `useEffect` para derivar estado — calcule no render.

**Next.js (App Router)**
- Server Component por padrão; `"use client"` só onde há estado/efeito/evento.
- Não passe função ou objeto não serializável de server para client.
- `next/image` para mídia, `next/font` para fonte (evita CLS e requisição externa).
- Fronteira server/client é decisão de arquitetura: mudar depois custa refactor.

**Vue / Nuxt**
- `v-for` com `:key` estável; props tipadas; `defineProps`/`defineEmits` explícitos.
- `useAsyncData`/`useFetch` no Nuxt em vez de fetch manual em `onMounted`.
- Scoped style ou token global — nunca CSS global que colide.

**React Native / Expo**
- `FlatList` obrigatória para lista longa (nunca `ScrollView` com 500 itens).
- `Pressable` com feedback (`android_ripple`, `opacity`).
- Safe area (`react-native-safe-area-context`) e teclado (`KeyboardAvoidingView`).
- Imagem com dimensão explícita para não pular layout.

**Flutter**
- `ListView.builder` para lista longa; `const` onde possível.
- `MediaQuery` + `LayoutBuilder` para responsivo real, não breakpoint fixo.
- `Semantics` explícito em widget customizado interativo (Flutter a11y é opt-in em parte dos casos).

## 5. Bugs visuais recorrentes (e a correção)

| Sintoma | Causa | Correção |
|---|---|---|
| Texto de badge/chip quebra em duas linhas | falta `nowrap` | `whitespace-nowrap` (Tailwind) / `white-space: nowrap` |
| Botão sem cursor de mão | `cursor` é `default` em `<button>` estilizado ou `div` clicável | `cursor-pointer`; melhor: usar `<button>` |
| Layout "pula" ao carregar | imagem/mídia sem dimensão | `width`/`height` ou `aspect-ratio` |
| Fonte muda de tamanho no carregamento | fonte externa tardia | fonte local + `font-display: swap` + preload |
| Animação ignora preferência do usuário | falta de guarda | `@media (prefers-reduced-motion: reduce) { animation: none }` |
| Texto sobre imagem ilegível | contraste variável | overlay com gradiente + verificação de contraste no pior caso |
| Modal "prende" o foco errado | sem focus trap e sem retorno de foco | trap + retorno ao gatilho no fechamento |
| Toaster cobre ação no mobile | posição fixa sem safe area | safe-area inset + z-index documentado |

## 6. Checklist antes de entregar para o `e2e-browser-verifier`

- [ ] tokens semânticos usados (nenhum hex/px mágico no JSX)
- [ ] todos os estados da tabela do §3 implementados
- [ ] foco visível por teclado em todo interativo
- [ ] contraste ≥ 4.5:1 (texto) e ≥ 3:1 (UI) verificado
- [ ] `prefers-reduced-motion` respeitado
- [ ] dimensão de mídia declarada (sem CLS)
- [ ] lista longa virtualizada ou paginada
- [ ] estados de vazio, erro e permissão negada desenhados
- [ ] nenhum componente duplicando outro do inventário

Este checklist **não** substitui o browser real: `dz23-e2e-browser-verifier` é quem prova.

## 7. Relação com o catálogo externo

Para **decidir** paleta, tipografia e estilo por segmento, use
`external/ui-ux-pro-max.md` (no repositório dz23-arsenal: https://github.com/LMPrado-DZ23/dz23-arsenal/blob/main/external/ui-ux-pro-max.md) (design intelligence por segmento e stack).
Este documento assume que a decisão visual já foi tomada e trata da **execução fiel** dela.
