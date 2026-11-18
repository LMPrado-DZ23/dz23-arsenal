# Registro de decisão (decision log)

Artefato central desta skill. Duas metades: a **lista de problemas** (passo 2, antes de mudar qualquer coisa)
e as **correções** escritas *acima* dos problemas que resolvem (passo 3). Uma correção cobre vários problemas;
problemas órfãos ao fim significam PARTIAL.

## Formato

```md
## Problemas (todos os lugares onde "mudam juntos?" está errado)

- `caminho/arquivo.ext:LINHA` <descrição concreta do vínculo ou caso especial>
- ...

## Correções (cada uma acima dos problemas que resolve)

- <a única mudança estrutural>. 
  - `caminho/arquivo.ext:LINHA` <problema 1 que ela fecha>
  - `caminho/arquivo.ext:LINHA` <problema 2 que ela fecha>
```

## Exemplo preenchido

### Lista de problemas

```md
- `ui/LogoutDialog.tsx:30` espera 100ms depois de fechar e torce para o input conseguir foco até lá.
- `ui/Toolbar.tsx:40` e `ui/Menu.tsx:22` chamam as mesmas ações, cada uma checando por conta quando estão desabilitadas.
- `checkout/submit.ts:9` depende diretamente de `payments/stripe.ts`.
- `shortcuts/keymap.ts:18` tem um switch com um case por ação, separado da lista do menu.
- `ui/CommandPalette.tsx:55` mantém sua própria lista de ações, e falta as mais novas.
- `ui/SettingsDialog.tsx:61` seta um global `skipRefocus` para impedir que o diálogo de logout abra foco no input.
- `history/undo.ts:30` tem um caso especial para toda ação que pode ser desfeita.
- `refunds/refund.ts:22` embrulha cada chamada Stripe em `if (order.provider === "paypal")`.
- Todo handler de ação precisa chamar `track()` na mão, e alguns não chamam.
- `ui/Toolbar.test.tsx` e `ui/Menu.test.tsx` testam as mesmas ações separadamente.
```

### Com as correções

```md
- Fazer o `Dialog` genérico devolver o foco a quem o tinha antes de abrir, para o wait e a flag irem embora.
  - `ui/LogoutDialog.tsx:30` espera 100ms depois de fechar e torce pelo foco.
  - `ui/SettingsDialog.tsx:61` seta o global `skipRefocus`.
- Definir interface `PaymentProvider` implementada por Stripe e PayPal, para checkout e refunds deixarem de saber qual usam.
  - `checkout/submit.ts:9` depende diretamente de `payments/stripe.ts`.
  - `refunds/refund.ts:22` embrulha tudo em `if (order.provider === "paypal")`.
- Tornar toda ação do usuário um comando com nome, handler e undo, para toolbar, menu, atalhos, paleta e histórico rodarem de uma única lista.
  - `ui/Toolbar.tsx:40` e `ui/Menu.tsx:22` checam desabilitação cada um por si.
  - `shortcuts/keymap.ts:18` tem switch paralelo à lista do menu.
  - `ui/CommandPalette.tsx:55` mantém lista própria, desatualizada.
  - `history/undo.ts:30` tem caso especial por ação desfazível.
  - Todo handler chama `track()` na mão.
  - `ui/Toolbar.test.tsx` e `ui/Menu.test.tsx` testam as mesmas ações separados.
```

Note: três correções fecharam dez problemas. Cada uma é uma mudança estrutural, não um remendo local — é
assim que se distingue redesenhar de consertar caso por caso.
