# DSH — Integrações (opcional)

A agência DSH é **autossuficiente**: os 5 passos do [quickstart](DSH_QUICKSTART.md) a põem pra rodar só com os prompts e os scripts de verificação. **Nenhuma ferramenta externa é necessária.** Este documento é para quem quer encaixá-la em ferramentas de delegação, qualidade e execução — as camadas se empilham, não competem.

- **`dz23-subagents` (MCP)** — infraestrutura: delega os pods a modelos reais (`swarm_run`, `delegate`, `consensus`) e guarda a missão (`memory_checkpoint`). Os subagentes devolvem texto; o harness aplica, testa e verifica.
- **agência DSH** (esta biblioteca) — quem faz, com que fronteira, sob que impacto (T0–T3) e com que revisão (81).
- **`enterprise-product-builder`** (skill) — o padrão de qualidade do pod de produto: níveis L1–L4, fases, gates de segurança/acessibilidade/privacidade/performance e templates.
- **`super-autonomous-mission-loop`** (skill) — o motor que conduz a missão até o done com evidência: checkpoint, anti-loop, recuperação e conclusão em duas fases com três auditores.

Os conceitos se correspondem — é a mesma coisa com o nome de cada camada:

| Agência DSH | super-autonomous-mission-loop | dz23-subagents | enterprise-product-builder |
|---|---|---|---|
| Diretor monta o pod | ciclo recuperar → … → liberar | `swarm_run` com papéis | — |
| Pod (especialistas por demanda) | delegação de tarefa delimitada | papéis architect/backend/frontend/security/qa | pods por fase |
| Decision log (T2/T3, divergências) | checkpoint de estado da missão | `memory_checkpoint` | — |
| Impacto T3 → confirmação | `AWAITING_APPROVAL` | — | rigor L3/L4 |
| 81 Revisor Independente | um dos três auditores finais | `consensus` (não substitui gate) | três revisões antes do release |
| Contrato de interface (núcleo) | especificação + gates | contrato da delegação | contrato de API / feature-spec |
| check_sizes / check_consistency | gates de qualidade | — | gates do loop |

Cada ferramenta externa é um projeto à parte (skill ou MCP); consulte a documentação de cada uma para instalá-la. A regra transversal — resposta de IA é proposta, evidência é o que o harness executa — está nas regras de operação do [documento canônico](DSH_COMPLETE_SPECIALIST_AGENCY.md), porque vale com ou sem essas ferramentas.

## Usar os perfis via dz23-subagents (injeção de prompt)

O dz23 **não registra papéis novos**: o `role` de `delegate`/`swarm_run` é um enum fixo (`worker, architect, backend, frontend, security, qa, devops, reviewer`) e o `config/agents.example.json` é só referência (o runtime não o carrega). Então a adaptação não é "cadastrar os 83 perfis como papéis" — é **injeção de prompt**:

1. Monte o `prompt` = núcleo universal + o bloco do perfil DSH + a tarefa concreta.
2. Escolha o `role`-enum mais próximo — ele só roteia o modelo; o comportamento vem do prompt injetado:

| role-enum | perfis DSH |
|---|---|
| architect | 01, 02, 03, 21, 47 |
| backend | 04, 07, 08, 09, 22, 63 |
| frontend | 05, 06, 27–32, 82 |
| security | 16, 17, 18, 19, 52, 61 |
| qa | 13, 15, 56 |
| devops | 10, 11, 12, 14, 20, 23, 62 |
| reviewer | 24, 26, 42, 58, 81 |
| worker | os demais (marketing, finanças, ciência, setoriais 65–80, 83 e trading 84–87) |

3. Reúse o mesmo `project_id`/`mission_id`; passe `workspace`/`context` quando precisar de evidência.
4. Para saída estruturada (ex.: achados do 81), use `output_schema`.
5. A resposta é **proposta em texto**: o harness aplica, testa e verifica — nenhuma revisão de IA substitui um gate (regra de operação 9).

Um gerador (mantido fora desta biblioteca) materializa esses prompts e o `rolemap.json` a partir dos catálogos, para quem for programar a integração.
