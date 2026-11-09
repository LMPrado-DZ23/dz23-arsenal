# Anti-padrões em engenharia reversa

Cada item: **sintoma** → **por que dói** → **correção**.

## Autorização e escopo
1. **Analisar sem direito** → risco legal e reputacional → registre a base (dono, contrato, licença) antes do primeiro comando.
2. **Escopo elástico** ("já que abri, vou ver tudo") → tempo queimado e exposição desnecessária → pergunta declarada, alvo declarado.
3. **Expor credencial encontrada** no relatório → vaza segredo e queima a divulgação responsável → cite só `arquivo:linha` e o tipo.
4. **Distribuir firmware proprietário** → violação de licença → compartilhe hash e achados, não o binário.

## Identificação
5. **Confiar na extensão** → `.bin` que é squashfs → magic bytes primeiro.
6. **Concluir "cifrado" por entropia alta sem testar** → pode ser compressão → tente descompressores e cite a entropia.
7. **`file` como prova** → libmagic erra em container de firmware → confirme com `xxd` no offset.
8. **Ignorar endianness** → ler header BE como LE gera tamanho absurdo → declare `Data: big/little` do ELF ou o magic.

## Estática
9. **Símbolo inventado** → `decrypt_password` sem prova vira fato falso → `sub_XXXX` até a cadeia de evidência.
10. **Decompilação como fonte** → apresentar código gerado como "o código" → hipótese com âncora em instrução.
11. **`objdump -d` linear em `.text` com dados** → lixo interpretado como código → siga fluxo de controle, não byte a byte.
12. **Analisar 500 funções sem pergunta** → mapa bonito e inútil → 3–5 funções que respondem à pergunta.
13. **Não declara cobertura** → leitor acha que tudo foi visto → `NOT_ANALYZED` explícito.
14. **Ignorar `.init_array`** → rotina roda antes de `main` e passa despercebida → cheque construtores.

## Dinâmica
15. **Rodar binário desconhecido no host** → compromete a máquina de análise → VM/container sem rede.
16. **"Isolei" sem provar** → confiança falsa → `ip a` + connect falhando como evidência.
17. **Um caminho observado virar regra** → generalização errada → "observado neste input, neste ambiente".
18. **Contornar anti-debug sem registrar** → resultado não reproduzível → documente patch/offset.
19. **Fuzzing sem corpus válido** → gasta tempo achando nada → corpus pequeno e válido + critério de parada.

## Firmware
20. **`dd` do arquivo inteiro como "o rootfs"** → inclui bootloader e padding → extraia por offset e tamanho do header.
21. **Ignorar CRC/hash declarado** → análise de payload corrompido → verifique `ih_dcrc`/`hash@1`/MD5 ESP e registre.
22. **Offset do squashfs errado por 1 byte** → "not a squashfs" → `grep -abo hsqs` no original.
23. **Montar imagem em loop no host** → exploit de filesystem → extraia em container com `debugfs`/`unsquashfs`.
24. **Executar script do rootfs no host** → execução arbitrária → só em emulação isolada.
25. **Seguir symlink absoluto da extração** → leitura fora do jail → trate como achado e não siga.
26. **Confundir assinado com cifrado** → achar que não dá para ler → assinado se lê; cifrado não.

## Emulação
27. **Classificar falha de periférico como bug do firmware** → conclusão errada → declare ausência de GPIO/SPI.
28. **Emular sem `-dtb`/`-M` correto** → boot silencioso e "firmware não funciona" → case com o `compatible` do devicetree.
29. **Rede `tap` sem necessidade** → firmware alcança a rede local → `user` mode por padrão.

## Hardware
30. **Conectar UART/JTAG sem conferir tensão** → queima o alvo → confirme 1.8 V vs 3.3 V.
31. **Um dump só** → corrupção silenciosa → duas leituras com hash igual.
32. **Dump com `0xFF`/`0x00` sustentado analisado como conteúdo** → conclusão fantasia → valide distribuição de bytes.
33. **Gravar em flash sem backup verificado** → brick irreversível → backup duplo + plano de recuperação + autorização.
34. **Ignorar secure boot/OTP** → tentativa de gravação que falha ou inutiliza → identifique a proteção antes.

## Relatório
35. **Achado sem offset/hash** → não reproduzível → toda afirmação com localização.
36. **Misturar observado com inferido** → leitor não sabe o que confiar → seção separada por confiança.
37. **Omitir ferramenta ausente** → parece que a análise foi completa → `BLOCKED` explícito com a ferramenta que falta.
38. **"Analisei tudo" sem amostragem declarada** → cobertura fictícia → declare o que ficou fora.

## Como usar
Percorra na revisão: **não se aplica / aplicado / pendente com risco**. Achado BLOCKER (ver `quality-gates.md`) impede entregar o relatório.
