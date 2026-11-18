# Limitações — dz23-arsenal

Retrato honesto. O arsenal **não** é universal nem "superior a tudo"; é forte em governança e
densidade de verificadores, e limitado onde a prova exige infra, hardware, juízo independente ou
adoção externa. Superioridade só é declarada com benchmark comparável e evidência — nunca por volume.

## Capacidade comprovada vs. instrução forte

- Os vereditos de eval são **Camada 1** (autoavaliação do autor), agora **reproduzíveis** por replay
  determinístico em 8 casos. Isso prova reprodutibilidade e discriminação do grader — **não** juízo
  independente. **Camada 3** (juiz externo, conjunto separado, controle de viés) é `NOT_TESTED`.
- "Instalada ≠ exercitada": uma ferramenta no PATH não é capacidade comprovada até ser exercitada
  nesta sessão. `verify-cli` mede o que existe; o estado real é declarado por skill.

## Ferramentas necessárias e não garantidas

Docker, Postgres, navegador/Playwright, Ghidra/jadx/apktool, binwalk/qemu, Lighthouse/k6, Node para
os MCP. Sem elas, as skills correspondentes declaram `BLOCKED_BY_EXTERNAL_DEPENDENCY`, não `PASS`.

## Formatos e domínios

- **Eng. reversa:** suporta ELF/PE/Mach-O e vários firmwares via toolkit + REA; **não** executa
  APK/DEX, iOS assinado, WASM, kernels ou pcap sem as ferramentas específicas (a skill descreve, a
  execução exige a tool).
- **Domínios ausentes (sem skill dedicada):** mobile, dados/ciência, e SAST/DAST/SBOM dedicado de
  aplicação (o SBOM atual é da cadeia do próprio repo, não um scanner de alvo).

## Hardware, sandbox e legal

- **Hardware:** UART/JTAG/SPI exigem bancada física + autorização — `BLOCKED` por definição aqui.
- **Sandbox:** malware e binário desconhecido só em VM/container sem rede; não executo no host.
- **Autorização:** eng. reversa, pentest (pentagi) e clone (replica, clean-room) exigem direito/escopo
  declarado; sem isso a skill recusa. Nunca review falsa (FTC), nunca nome do original na loja.

## Segurança e segredos

- Nunca grava segredo/credencial/PII (gate `secrets` + Gitleaks no histórico). Deploy, pentest e
  pagamento exigem credencial do dono — a skill **pede antes**, não deduz.
- Supply-chain: SBOM das **deps diretas declaradas** (este repo não versiona lockfile por política);
  a árvore resolvida + integrity é artefato de CI, não do SBOM committado.

## Integrações externas

OpenHands, LangGraph, Ollama, LiteLLM, vLLM, SWE-agent, Semantic Kernel, Pydantic AI, MCP
Inspector/Registry, OpenBot: hoje **apenas catalogados** (URL + licença `a-verificar`). **Não há
adaptador testado** — ficam `BLOCKED` até fontes + requisito + teste. OpenBot nunca com
`danger-full-access` automático.

## Produto e ecossistema

- **0 adoção externa, 0 validação independente** registrada. Densidade de verificadores (109 checks,
  CI 2 SO) é mensurável e é a força real; adoção, interop padronizada e escala de comunidade são
  pontos fracos e **não** se resolvem com commit.

## Custo e ação irreversível

Chamadas pagas, geração de mídia e deploy não disparam sem pedido. Deletar produção, pagar/mover
dinheiro, publicar e mudar credencial exigem revisão humana. Nunca automático: pagamento, envio em
massa, destruição irreversível, review falsa.
