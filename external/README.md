# Skills externas recomendadas

**Treze** projetos mantidos por outras organizações que **complementam** as 10 skills DZ23. Nenhum deles
está redistribuído aqui — cada arquivo documenta o repositório oficial, o gap que preenche e os cuidados.

Nove são **skills**; quatro são **plataformas** (PentAGI, Modern Web Guidance, Astryx, phone-agent-harness).

## Índice

| Skill | Autor | Gap que preenche |
|---|---|---|
| [Superpowers](superpowers.md) | obra | processo de SDLC completo (brainstorm → spec → plan → TDD → review) |
| [UI UX Pro Max](ui-ux-pro-max.md) | nextlevelbuilder | **design intelligence por segmento e stack** (paleta, tipografia, estados) |
| [REA](rea.md) | morluto | engenharia reversa com motor real (Ghidra, IDA, Kuna) |
| [Cloudflare Security Audit](cloudflare-security-audit.md) | cloudflare | auditoria de segurança de **source** |
| [Anthropic Skills](anthropic-skills.md) | anthropic | geração de Office (pdf/docx/xlsx/pptx) e meta-skills |
| [Vercel React Best Practices](vercel-react-best-practices.md) | vercel-labs | performance React/Next específica |
| [Supabase Postgres Best Practices](supabase-postgres-best-practices.md) | supabase | Postgres/Supabase específico |
| [Playwright MCP](playwright-mcp.md) | microsoft | automação de browser via MCP |
| [Terraform AWS VPC](terraform-aws-vpc.md) | terraform-aws-modules | módulo VPC AWS canônico |
| [PentAGI](pentagi.md) | VXControl | **executa** pentest autônomo (não só revisa) |
| [Modern Web Guidance](modern-web-guidance.md) | Chrome/Edge/Firefox/MDN | plataforma web **moderna** (209 guias) |
| [Astryx](astryx.md) | Meta | design system React 19 com CLI para agentes |
| [phone-agent-harness](phone-agent-harness.md) | comunidade | agente que **liga e atende** telefone |

## Como escolher

| Se você precisa… | Instale |
|---|---|
| de processo, não só de execução | Superpowers |
| de direção visual por segmento antes de codar UI | UI UX Pro Max |
| desmontar binário com pseudocódigo | REA |
| revisar segurança de código | Cloudflare Security Audit |
| gerar `.docx`/`.xlsx`/`.pdf` | Anthropic Skills |
| otimizar React/Next | Vercel React Best Practices |
| modelar Postgres/Supabase | Supabase Postgres Best Practices |
| automatizar browser via MCP | Playwright MCP |
| montar VPC na AWS | Terraform AWS VPC |
| executar pentest autorizado | PentAGI (ponte MCP em `mcp/pentagi-mcp`) |
| escrever UI com API web atual | Modern Web Guidance |
| app React 19 com biblioteca pronta | Astryx |
| agente que fala ao telefone | pat-phone-agent-tool (ver `phone-agent-harness.md`) |

## Regra de convivência

Skills externas e DZ23 **coexistem** em `~/.agents/skills/`. Não há conflito de namespace porque cada uma
tem nome próprio. O que não se deve fazer é instalar duas skills que reivindicam o mesmo comando.

## Aviso sobre números

Este repositório **não** publica contagem de estrelas, downloads ou "popularidade" das skills externas:
números assim mudam toda semana e, quando não verificados, viram desinformação. Para cada uma, consulte o
próprio repositório.

## Plataformas vs skills

`PentAGI`, `Modern Web Guidance`, `Astryx` e `phone-agent-harness` não são skills no sentido do arsenal:

| Projeto | Instala como | Descoberta |
|---|---|---|
| PentAGI | stack Docker + **ponte MCP** (`mcp/pentagi-mcp`) | ferramentas `pentagi_*` no harness |
| Modern Web Guidance | skill por agente (`~/.agents/skills`) | skill + CLI `npx modern-web-guidance` |
| Astryx | CLI global npm + skill | skill + `astryx docs/component/search` |
| phone-agent-harness | MCP `pat-phone` (Python) | ferramentas `place_call`/`get_call`/`end_call` |

Como registrar em cada harness: [`docs/harness-integration.md`](../docs/harness-integration.md).
