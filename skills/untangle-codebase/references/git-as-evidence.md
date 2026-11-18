# Git como evidência do desembaraço

O registro de decisão não é nota solta: cada correção vira commit rastreável ao problema que fechou. Isso dá
ao veredito uma prova auditável e protege contra a "quebra silenciosa" — quem revisa consegue ver *por que*
cada movimento aconteceu.

## Convenções

- **Um grupo de problemas por commit.** A correção que resolve vários itens fecha todos num commit só, com o
  texto da correção no corpo e os `arquivo:linha` dos problemas resolvidos listados abaixo. Não misture dois
  grupos sem relação no mesmo commit.
- **Movimento antes de mudança.** Commits de realocação pura (mover arquivo, renomear módulo) separam-se dos
  commits que alteram lógica. Assim um `git log --follow` sobrevive e a revisão fica legível.
- **Mensagem referencia o log.** Ex.: `refactor(untangle): PaymentProvider interface (fecha checkout/submit.ts:9, refunds/refund.ts:22)`.
- **Nada de força bruta destrutiva.** Esta skill roda em repo real; qualquer operação irreversível exige backup
  prévio e rollback registrado, mesma regra global do workspace. Nunca `reset --hard`/`clean -fd` para "limpar".

## Ligando log → commits → verificação

1. Lista de problemas (`templates/decision-log.md`) é escrita no passo 2, antes de mudar código.
2. Cada correção do passo 4 é um commit apontando os itens que fecha.
3. Ao fim, todo item da lista deve estar ou resolvido (commit correspondente) ou explicitamente adiado com
   motivo. Item órfão = PARTIAL, não pronto.
4. A suíte comparada ao baseline (`references/verification.md`) é a evidência final anexada ao veredito.

## Métricas úteis (opcionais, mas dão número ao progresso)

- Contagem de casos especiais restantes na lista (deve tender a zero — é a medida primária de conclusão).
- Fan-in/fan-out dos módulos tocados: nada deve importar algo mais volátil que si.
- Arquivos que mudam juntos numa feature devem acabar colocalizados; meça quantas mudanças típicas ainda tocam
  pastas não relacionadas.
