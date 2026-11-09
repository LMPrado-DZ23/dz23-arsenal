# Design system e componentes

## Auditoria antes de importar biblioteca
Identifique componentes existentes, tokens, estilos, CSS reset, versões React/Vue/Svelte, build, licenças, suporte teclado e bundle. shadcn/ui é referência/código-fonte adaptável, não uma dependência para copiar cegamente. Só incorporar componentes se stack e arquitetura justificarem.

## Contratos
Button: action real, pending, disabled, feedback e foco.
Input: label, descrição, validação, erro e autocomplete.
Dialog: foco inicial, trap, Escape, retorno de foco e confirmação quando destrutivo.
Table: dados reais, ordenação/filtro/paginação reais se exibidos, estado vazio, overflow controlado e mobile.
Sidebar: rota ativa, grupos, expansão, busca, permissões e preferências persistentes.
Toast: feedback verdadeiro e acessível; não substituir erro contextual.
Skeleton: transitório e com término; nunca placeholder permanente.
Charts: fonte, período, unidade, ausência de dados e estado de erro explícitos.

## Sem duplicação
Reutilize componentes de domínio, hooks e stores. Uma nova interface pode mudar a apresentação, não criar uma segunda fonte de verdade. Evite tokens ad hoc, componentes gigantes e CSS global com colisões.

## Check de revisão
Sem botões falsos; todos os estados relevantes; sem perda de teclado; sem regressão de bundle injustificada; sem import de pacotes desnecessários.
