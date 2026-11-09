#!/usr/bin/env python3
"""Acrescenta a secao 'Arsenal' aos README.md das skills, sem remover conteudo original.

Uso: python add_arsenal_readme.py <repo-root>
"""
from __future__ import annotations

import sys
from pathlib import Path

SECOES = {
    "dz23-autonomous-improvement-ultimate": {
        "versao": "2.1",
        "categoria": "orchestration",
        "complexidade": "advanced",
        "quando": [
            "Qualquer `/goal` de engenharia com critério de aceite medível.",
            "Tarefa longa que precisa sobreviver a interrupção (checkpoint persistido).",
            "Correção de bug com causa raiz não óbvia.",
            "Refactor com risco de regressão que exige baseline + reteste.",
        ],
        "nao": [
            "Pergunta rápida ou ajuste de 1 linha — o ritual custa mais que o trabalho.",
            "Sem critério de aceite medível: o ciclo não tem fim.",
            "Junto com outro orquestrador — só um conduz.",
            "Como ferramenta de operação em produção: ela orquestra mudança de código.",
        ],
        "cli": "`git`, `python` (3.10+) e o que a skill de domínio chamada exigir.",
        "gates": [
            "Matriz de requisitos com critério verificável, evidência e estado.",
            "Baseline registrado antes de mexer (o que já falhava).",
            "Veredito explícito: `PASS` / `PARTIAL` / `FAIL` / `NOT_TESTED` / `BLOCKED_BY_EXTERNAL_DEPENDENCY`.",
            "Checkpoint retomável a cada rodada, com o que **não** foi testado declarado.",
        ],
        "integra": "Chama todas as outras skills. É a única que orquestra; as demais decidem dentro do próprio domínio.",
    },
    "dz23-backend-data-architect": {
        "versao": "1.0.1",
        "categoria": "backend",
        "complexidade": "advanced",
        "quando": [
            "Criar ou alterar serviço, endpoint, schema, tabela, índice ou migração.",
            "Definir contrato de API entre times.",
            "Diagnosticar N+1, query lenta ou escrita travada por índice.",
            "Garantir isolamento de tenant em dado multi-tenant.",
        ],
        "nao": [
            "Ajuste de UI sem impacto em dados (use `dz23-ultimate-pro-max`).",
            "Deploy, container ou IaC (use `dz23-devops-cloud-deployer`).",
            "Migração em produção sem possibilidade de teste: declare `BLOCKED` antes de improvisar.",
        ],
        "cli": "`git`, `python` (obrigatórias) · `docker`, `sqlite3`, `psql` (recomendadas — sem `psql`, o `EXPLAIN` fica `BLOCKED`).",
        "gates": [
            "Contrato documentado antes da implementação (formato, erros, paginação, idempotência).",
            "Migração com caminho de reversão declarado.",
            "Índice justificado por `EXPLAIN` — índice por precaução é bloqueio.",
            "Prova de isolamento de tenant em toda query multi-tenant.",
        ],
        "integra": "Recebe spec de `dz23-spec-to-system-engine` e mapa de `dz23-codebase-cartographer`; entrega imagem/pipeline para `dz23-devops-cloud-deployer`; recebe gargalo de `dz23-performance-scalability-engine`.",
    },
    "dz23-codebase-cartographer": {
        "versao": "1.1.0",
        "categoria": "exploration",
        "complexidade": "intermediate",
        "quando": [
            "Entrar em repositório desconhecido (onboarding, primeiro dia).",
            "Antes de refactor em código legado.",
            "Avaliar impacto de mudança em módulo com muitas dependências.",
            "Quando o repo é grande demais para o agente ler inteiro.",
        ],
        "nao": [
            "Repo de 3 arquivos: ler direto é mais rápido.",
            "Quando o mapa já está atualizado.",
            "Análise de artefato compilado sem fonte (use `dz23-reverse-engineer-anything`).",
        ],
        "cli": "`git`, `rg`, `python` (obrigatórias) · `jq` (recomendada) · `graphlint` (opcional, grafo de dependência).",
        "gates": [
            "Toda afirmação com `arquivo:linha` ou comando executado.",
            "Zonas de risco declaradas: hot path, código sem teste, dependência circular.",
            "`EVIDENCE_LEDGER` separando verificado de `NOT_TESTED`.",
            "Handoff pronto: o brief é entrada para outra skill, não relatório de vaidade.",
        ],
        "integra": "Alimenta `dz23-backend-data-architect` e `dz23-ultimate-pro-max` com contexto; precede qualquer mudança em legado; recebe dossiê de `dz23-reverse-engineer-anything`.",
    },
    "dz23-devops-cloud-deployer": {
        "versao": "1.2.1",
        "categoria": "devops",
        "complexidade": "advanced",
        "quando": [
            "Containerizar aplicação (imagem mínima, reproduzível, sem root).",
            "Montar ou corrigir pipeline de CI/CD com gates.",
            "Provisionar ambiente e preparar rollback ensaiado.",
            "DevSecOps: scan de imagem, dependência e segredo.",
        ],
        "nao": [
            "Deploy em produção sem autorização explícita — a skill exige, não assume.",
            "Projeto que não tem deploy (biblioteca local).",
            "Otimização de latência (use `dz23-performance-scalability-engine`).",
        ],
        "cli": "`docker`, `git`, `trivy` (obrigatórias) · `kubectl`, `helm`, `terraform`, `hadolint`, `gitleaks` (recomendadas — sem elas, parte do fluxo fica `BLOCKED`).",
        "gates": [
            "Build reprodutível: pin por digest, sem `latest`.",
            "Gate de scan sem CRITICAL/HIGH aberto.",
            "Rollback ensaiado, não prometido.",
            "Observabilidade mínima: SLO, painel, trace, smoke pós-deploy.",
        ],
        "integra": "Recebe imagem/pipeline de `dz23-backend-data-architect`; entrega ambiente para `dz23-e2e-browser-verifier`; recebe gargalo de infra de `dz23-performance-scalability-engine`.",
    },
    "dz23-e2e-browser-verifier": {
        "versao": "1.1.0",
        "categoria": "testing",
        "complexidade": "intermediate",
        "quando": [
            "Verificar fluxo crítico de UI em browser real (cross-browser).",
            "Provar que uma correção de interface funciona, com evidência visual.",
            "Auditar acessibilidade (axe + WCAG 2.2 AA).",
            "Capturar trace/vídeo de um bug intermitente.",
        ],
        "nao": [
            "Fluxo sem UI (teste de API puro).",
            "Quando não há ambiente no ar: declare `BLOCKED`, não simule browser.",
            "Como substituto de teste unitário.",
        ],
        "cli": "`node`, `npx`, `playwright` (obrigatórias) · `rg` (recomendada).",
        "gates": [
            "Todo teste com seletor estável (role/label), nunca coordenada.",
            "Artefato salvo: screenshot, trace ou vídeo por execução.",
            "Veredito `PASS` exige execução; `NOT_TESTED` quando não rodou.",
            "Flaky declarado como flaky, não como instabilidade do produto.",
        ],
        "integra": "Recebe ambiente de `dz23-devops-cloud-deployer` e build de `dz23-ultimate-pro-max`; fecha o ciclo de release.",
    },
    "dz23-performance-scalability-engine": {
        "versao": "1.3.0",
        "categoria": "performance",
        "complexidade": "advanced",
        "quando": [
            "Investigar lentidão com medição real (LCP/INP, p50/p95/p99).",
            "Preparar sistema para pico de tráfego.",
            "Reduzir custo de infra com evidência.",
            "Corrigir N+1, índice ausente, bundle grande — sempre com prova.",
        ],
        "nao": [
            "Antes de existir baseline: a skill bloqueia otimização sem número.",
            "Micro-otimização antes de localizar o gargalo.",
            "Como checklist de boas práticas aplicada em tudo.",
        ],
        "cli": "`python`, `curl` (obrigatórias) · `lighthouse`, `k6`, `psql` (recomendadas — sem elas, load test e `EXPLAIN` ficam `BLOCKED`).",
        "gates": [
            "Baseline medido com volume e percentil (nunca média).",
            "Budget declarado **antes** da mudança.",
            "Uma camada por vez, uma mudança por vez.",
            "Antes/depois com o mesmo instrumento, mesmo dado e mesmo ambiente.",
        ],
        "integra": "Localiza o gargalo e delega: frontend → `dz23-ultimate-pro-max`, backend/banco → `dz23-backend-data-architect`, infra → `dz23-devops-cloud-deployer`.",
    },
    "dz23-reverse-engineer-anything": {
        "versao": "1.1.1",
        "categoria": "exploration",
        "complexidade": "advanced",
        "quando": [
            "Analisar binário desconhecido (ELF/PE/Mach-O) sem fonte.",
            "Firmware, dump de flash, imagem de boot (ESP, uImage, UF2, Intel HEX, DTB).",
            "Recuperar protocolo de dispositivo ou comparar versões de firmware.",
            "CTF, auditoria de artefato fechado.",
        ],
        "nao": [
            "Código-fonte disponível: use `dz23-codebase-cartographer`.",
            "Análise sem autorização legal do dono do artefato.",
            "Desmontagem/emulação sem REA instalado: declare `NOT_TESTED`, não simule saída.",
        ],
        "cli": "`python` (obrigatória) · `objdump`, `readelf`, `strings` (recomendadas) · `ghidra`, `qemu`, REA (opcionais — habilitam desmontagem e emulação).",
        "gates": [
            "Toda afirmação com offset e hash do artefato.",
            "CRC/MD5/checksum verificados quando o formato tem integridade.",
            "Risco físico declarado antes de tocar hardware (tensão, dump duplo, brick, OTP).",
            "Autorização explícita antes de instalar REA (~1,2 GB, 42 deps).",
        ],
        "integra": "Entrega dossiê para `dz23-codebase-cartographer`; usa REA quando disponível (ver `references/rea-integration.md`).",
    },
    "dz23-spec-to-system-engine": {
        "versao": "1.2.0",
        "categoria": "orchestration",
        "complexidade": "intermediate",
        "quando": [
            "Transformar pedido, ideia ou documento em especificação executável.",
            "Quebrar épico em fatias verticais entregáveis.",
            "Definir critério de aceite verificável antes de implementar.",
            "Reconciliar o plano com o que foi realmente entregue.",
        ],
        "nao": [
            "Implementar — ela especifica; quem constrói é a skill de domínio.",
            "Tarefa de 5 minutos com requisito óbvio.",
            "Quando não há ninguém para validar a spec com o solicitante.",
        ],
        "cli": "`git` (obrigatória) · `python` (recomendada, para validadores).",
        "gates": [
            "Todo requisito com critério de aceite verificável e rastreabilidade REQ → fatia → teste.",
            "Contrato de interface acordado antes de paralelizar trabalho.",
            "Dependências e caminho crítico declarados.",
            "O que está fora de escopo é explícito.",
        ],
        "integra": "Alimenta `dz23-backend-data-architect` e `dz23-ultimate-pro-max`; é orquestrada por `dz23-autonomous-improvement-ultimate`.",
    },
    "dz23-ultimate-pro-max": {
        "versao": "2.1",
        "categoria": "frontend",
        "complexidade": "advanced",
        "quando": [
            "Criar ou redesenhar interface com identidade própria (não template).",
            "Revisar UI/UX: hierarquia, tipografia, cor, motion, estados.",
            "Definir ou corrigir design system e tokens.",
            "Auditar acessibilidade e performance de render.",
        ],
        "nao": [
            "Backend, banco ou contrato de API (`dz23-backend-data-architect`).",
            "Deploy ou infra (`dz23-devops-cloud-deployer`).",
            "Quando não há requisito visual nem usuário definido: primeiro a spec.",
        ],
        "cli": "`node`, `npx` (obrigatórias) · `playwright`, `lighthouse` (recomendadas para verificação visual e de performance).",
        "gates": [
            "Direção de arte declarada antes do primeiro componente.",
            "Estados completos: loading, vazio, erro, sucesso, permissão negada.",
            "Contraste e foco de teclado verificados, não presumidos.",
            "Verificação visual com screenshot antes de declarar pronto.",
        ],
        "integra": "Recebe requisitos de `dz23-spec-to-system-engine`; recebe gargalo de render de `dz23-performance-scalability-engine`; entrega build para `dz23-e2e-browser-verifier`.",
    },
}


def bloco(skill: str, dados: dict) -> str:
    linhas = [
        "",
        "---",
        "",
        "## Arsenal — resumo operacional",
        "",
        f"**Versão real (VERSION/frontmatter):** {dados['versao']} · "
        f"**Categoria:** {dados['categoria']} · **Complexidade:** {dados['complexidade']}",
        "",
        "### Quando usar",
        "",
    ]
    linhas += [f"- {x}" for x in dados["quando"]]
    linhas += ["", "### Quando NÃO usar", ""]
    linhas += [f"- {x}" for x in dados["nao"]]
    linhas += ["", "### Instalação", "", "```bash",
               "# Já incluída no install-all. Manual:",
               f"cp -r skills/{skill} ~/.agents/skills/{skill}",
               "```", "", "### Uso", "", "```bash",
               f"/{skill}",
               "",
               f"# ou por descrição — o agente carrega sozinho (ver SKILL.md)",
               "```", "", "### Pré-requisitos de CLI", "", dados["cli"],
               "", "### Evidência / Quality gates", ""]
    linhas += [f"- {x}" for x in dados["gates"]]
    linhas += ["", "### Integração com outras skills", "", dados["integra"],
               "", "### Versão e changelog", "",
               "Ver [`CHANGELOG.md`](CHANGELOG.md) (desta skill) e o histórico do arsenal em "
               "[`../../CHANGELOG.md`](../../CHANGELOG.md).", ""]
    return "\n".join(linhas)


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    raiz = Path(argv[0] if argv else ".")
    if not raiz.is_dir():
        print(f"INVALID raiz inexistente: {raiz}", file=sys.stderr)
        return 2

    feito = 0
    for skill, dados in SECOES.items():
        alvo = raiz / "skills" / skill / "README.md"
        if not alvo.is_file():
            print(f"FALTA: {alvo}", file=sys.stderr)
            continue
        texto = alvo.read_text(encoding="utf-8")
        if "## Arsenal — resumo operacional" in texto:
            print(f"SKIP (já tem seção): {skill}")
            continue
        novo = texto.rstrip("\n") + "\n" + bloco(skill, dados)
        alvo.write_text(novo, encoding="utf-8", newline="\n")
        print(f"OK: {skill} (+{len(bloco(skill, dados).splitlines())} linhas)")
        feito += 1

    print(f"\n{feito} README(s) atualizados; conteúdo original preservado (só append).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
