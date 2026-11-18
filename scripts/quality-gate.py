#!/usr/bin/env python3
"""quality-gate.py — roda todos os checks do arsenal. Um comando, um veredito.

Uso:
    python scripts/quality-gate.py            # relatório legível
    python scripts/quality-gate.py --json     # saída para CI
    python scripts/quality-gate.py --fix      # regenera manifesto/índice antes de checar

Exit: 0 = tudo passou · 1 = alguma falha · 2 = erro de ambiente
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def rodar(nome: str, cmd: list[str], cwd: Path | None = None) -> dict:
    try:
        p = subprocess.run(cmd, cwd=str(cwd or RAIZ), capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=300)
        saida = (p.stdout or "").strip().splitlines()
        erro = (p.stderr or "").strip().splitlines()
        return {
            "check": nome,
            "ok": p.returncode == 0,
            "exit": p.returncode,
            "resumo": saida[-1] if saida else (erro[-1] if erro else ""),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"check": nome, "ok": False, "exit": -1, "resumo": f"erro: {exc}"}


def validar_skills(py: str) -> list[dict]:
    """Roda o validate_skill.py de cada skill que tiver um.

    Skill sem validador NÃO é "passou": é cobertura ausente. Antes isto devolvia
    ok=True com "sem validate_skill.py (pulado)", então a skill mais importante do
    arsenal (a de loop autônomo) podia degradar silenciosamente sem quebrar o CI.
    """
    resultados = []
    for skill in sorted(p for p in (RAIZ / "skills").iterdir() if p.is_dir()):
        v = skill / "scripts" / "validate_skill.py"
        if not v.is_file():
            resultados.append({
                "check": f"validate:{skill.name}",
                "ok": False,
                "exit": 1,
                "resumo": "sem validate_skill.py — cobertura ausente, não é aprovação",
            })
            continue
        r = rodar(f"validate:{skill.name}", [py, str(v)])
        resultados.append(r)
    return resultados


def total_de_checks_gerado() -> int | None:
    """Última contagem real produzida pelo próprio gate, lida de .gate-contagem.

    O check-numbers precisa saber quantos checks existem para conferir a documentação, mas
    não pode chamar o gate (recursão: ele é um dos checks) nem parsear este fonte (um
    parser de Python por regex contou 24 contra 31 reais — silenciosamente errado). Então
    o gate publica o número quando roda, e o conferidor lê o que foi medido. Se o arquivo
    não existe, devolve None e a regra de contagem é pulada — ausência nunca vira 0.
    """
    arq = RAIZ / ".gate-contagem"
    if not arq.is_file():
        return None
    try:
        dados = json.loads(arq.read_text(encoding="utf-8"))
        n = dados.get("total")
        return int(n) if isinstance(n, int) and n > 0 else None
    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        return None


def publicar_contagem(total: int) -> None:
    try:
        (RAIZ / ".gate-contagem").write_text(
            json.dumps({"total": total}, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")
    except OSError:
        pass  # contagem é conveniência; falhar o gate por isso seria ridículo


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fix", action="store_true")
    args = ap.parse_args(argv)

    py = sys.executable
    resultados: list[dict] = []

    if args.fix:
        resultados.append(rodar("manifesto:gerar", [py, "scripts/build-manifest.py"]))

    resultados += validar_skills(py)
    resultados.append(rodar("manifesto:check", [py, "scripts/build-manifest.py", "--check"]))
    # O índice de skills (skills/README.md) era mantido à mão e apodreceu inteiro: as nove
    # linhas divergiam do disco e uma skill não tinha linha. Agora é gerado, e este check
    # garante que ninguém volta a editá-lo na mão.
    resultados.append(rodar("indice-skills:check",
                            [py, "scripts/gera-indice-skills.py", "--check"]))
    resultados.append(rodar("numeros", [py, "scripts/check-numbers.py"]))
    resultados.append(rodar("links", [py, "scripts/check-links.py", "."]))
    # Links apontam para arquivos; isto confere os COMANDOS que a documentação manda rodar.
    # Nasceu de criar uma skill seguindo só o CONTRIBUTING (rodada 25): o texto mandava copiar
    # um validador não-copiável e mostrava um evals.json que o schema rejeita. Nenhuma checagem
    # automatizada via isso, porque nenhuma delas é um humano lendo o guia.
    resultados.append(rodar("docs-executaveis", [py, "scripts/check-docs-runnable.py"]))
    # Registro estrutural: ordem do changelog, numeração das dívidas, versão corrente no topo
    # de cada skill. Existe porque duas edições minhas nesta sessão não casaram com o texto
    # alvo e ninguém percebeu -- editar por busca-e-substituição silenciosa sempre dá exit 0.
    resultados.append(rodar("ancoras", [py, "scripts/checa-ancoras.py"]))
    # Cada verificador do gate e forcado a reprovar uma violacao do proprio dominio. Sem isto,
    # um verificador que parou de comparar nada continua devolvendo 0 -- foi o build.py --check
    # da rodada 28, e aqui se descobriu que duas das minhas proprias violacoes eram imaginarias.
    resultados.append(rodar("verificadores-sensiveis", [py, "scripts/audita-sensibilidade.py"]))
    # Estado da instalação do usuário. Entra sem --strict de propósito: divergência de conteúdo
    # entre repo e ~/.agents/skills é defeito real e deve quebrar o gate, mas "nada instalado" é
    # a condição normal de um runner efêmero -- com --strict este check seria vermelho em todo CI
    # e alguém acabaria removendo o check inteiro. A distinção existe no próprio script: use
    # `python scripts/audit-zips.py --strict` ao instalar, para exigir presença.
    resultados.append(rodar("instalacao:conteudo", [py, "scripts/audit-zips.py"]))
    # Os SKILL.md mandam o agente executar onze scripts dentro de skills/<x>/scripts/. Ate a
    # rodada 46 nada neste arsenal os rodava -- validate_skill confere arquivos, nao comportamento.
    # Suite com entrada no formato que cada um documenta e controle negativo por verificador.
    resultados.append(rodar("skills:scripts-executados",
                            [py, "scripts/executa-scripts-skills.py"]))
    resultados.append(rodar("estrutura", [py, "scripts/check-structure.py"]))
    # Toda referência de cada skill tem de ser nomeada no SKILL.md -- o único texto que o agente
    # carrega ao ativar a habilidade. Um guia correto, versionado e invisível às instruções é
    # material morto: aconteceu com diagnostic-playbook.md e verificacao.md (rodada 47).
    resultados.append(rodar("skills:enderecamento", [py, "scripts/checa-enderecamento.py"]))
    resultados.append(rodar("gate:autoteste-enderecamento",
                            [py, "scripts/prova-enderecamento.py"]))
    # As skills embutem cópias de scripts/skill_validator.py e scripts/_achar_arsenal.py
    # para se auto-validarem fora do checkout. Duplicação intencional — mas só é segura
    # enquanto as cópias baterem com a fonte.
    resultados.append(rodar("copias", [py, "scripts/check-copies.py"]))
    resultados.append(rodar("licencas", [py, "scripts/check-licenses.py"]))
    # Catálogo de fontes externas (mandato: layer catalog/). O índice de ~35 fontes é
    # máquina-legível em catalog/catalog.json; licença só é "verificada" com o LICENSE lido e
    # sha256 no disco, as demais ficam "a-verificar" (catalogadas por URL, nada copiado). O
    # verificador cruza com external/ (sem doc órfão) e tem autoteste de controle negativo.
    resultados.append(rodar("catalogo:verifica", [py, "scripts/check-catalog.py"]))
    resultados.append(rodar("catalogo:indice", [py, "scripts/gera-catalog.py", "--check"]))
    resultados.append(rodar("catalogo:autoteste", [py, "scripts/check-catalog.py", "--selftest"]))
    # SBOM (mandato: layer supply-chain/). CycloneDX gerado dos lockfiles reais; cada biblioteca
    # com integrity sha512. O verificador reparseia os lockfiles por conta própria (independente
    # do gerador) e reprova drift; o gerador --check pega edição manual; autoteste é controle negativo.
    resultados.append(rodar("sbom:verifica", [py, "scripts/check-sbom.py"]))
    resultados.append(rodar("sbom:drift", [py, "scripts/gera-sbom.py", "--check"]))
    resultados.append(rodar("sbom:autoteste", [py, "scripts/check-sbom.py", "--selftest"]))
    # Permissões por skill (mandato, regra 7). Toda skill que executa/altera/usa rede ou navegador
    # declara permissões, riscos, entradas, saídas, dry-run, rollback e aprovação em
    # security/permissoes.json. O verificador exige uma declaração por skill existente (sem skill
    # sem declaração, sem declaração órfã); PERMISSIONS.md é gerado; autoteste é controle negativo.
    resultados.append(rodar("permissoes:verifica", [py, "scripts/check-permissoes.py"]))
    resultados.append(rodar("permissoes:indice", [py, "scripts/gera-permissoes.py", "--check"]))
    resultados.append(rodar("permissoes:autoteste", [py, "scripts/check-permissoes.py", "--selftest"]))
    # Instalador multiplataforma (mandato, layer install/). O autoteste exercita o ciclo inteiro
    # num diretório temporário: dry-run inócuo, install das 18 skills, manifesto coerente, log sem
    # segredo, idempotência, rollback preciso e no-op seguro. Offline por construção (só cópia).
    resultados.append(rodar("install:autoteste", [py, "scripts/dz23-install.py", "--selftest"]))
    # Harness de eval por replay (mandato P1; dívida nº 1). Torna vereditos de eval REPRODUZÍVEIS:
    # re-gradua a resposta registrada com um grader determinístico e exige que reproduza o veredito
    # E discrimine (resposta ruim sintética dá FAIL). Camada 1-reproduzível, não juízo independente
    # (Camada 3 segue NOT_TESTED, declarado em eval-harness/README.md).
    resultados.append(rodar("replay:executa", [py, "scripts/replay-eval.py"]))
    resultados.append(rodar("replay:verifica", [py, "scripts/check-replay.py"]))
    resultados.append(rodar("replay:autoteste", [py, "scripts/check-replay.py", "--selftest"]))
    # Fecha o furo achado na revisão (Qwen): skill incorporada (não dz23-*) com evals declarados não
    # pode ficar verde em silêncio. Exige evidência executada (dados/ ou replay) OU NOT_TESTED
    # declarado com motivo em eval-harness/cobertura-incorporadas.json. Não move o denominador 144.
    # untangle-codebase: acervo das 4 familias de defeito estrutural (taxonomia propria da skill),
    # agora consultavel offline -- fecha o item 3 da revisao para a skill que tinha taxonomia real.
    resultados.append(rodar("untangle:consulta", [py, "scripts/consulta-untangle.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-untangle",
                            [py, "scripts/prova-consulta-untangle.py"]))
    # prune-tests: acervo das familias de teste podavel (taxonomia propria). Classifica, nunca remove.
    resultados.append(rodar("prune:consulta", [py, "scripts/consulta-prune.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-prune",
                            [py, "scripts/prova-consulta-prune.py"]))
    resultados.append(rodar("cobertura:incorporadas", [py, "scripts/check-cobertura-incorporadas.py"]))
    resultados.append(rodar("cobertura:autoteste",
                            [py, "scripts/check-cobertura-incorporadas.py", "--selftest"]))
    # Documento era a única superfície sem verificador de conteúdo: existência e link eram
    # conferidos, mas texto corrompido passava. Nesta sessão eu mesmo injetei duas vezes resíduo
    # de ferramenta num .md (caractere CJK no meio do português e uma expressão Python inteira no
    # CHANGELOG) e cinco verificadores diferentes deram verde com o artefato plantado.
    resultados.append(rodar("docs-higiene", [py, "scripts/check-doc-hygiene.py"]))
    # Acervo de design incorporado em vendor/ so vale se for consultavel: dado sem meio de acesso
    # vira referencia morta, a classe que a rodada 47 achou. A prova cobre os dois lados -- resolve
    # em portugues e recusa chutar quando nao ha correspondencia.
    resultados.append(rodar("design:consulta", [py, "scripts/consulta-design.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-design",
                            [py, "scripts/prova-consulta-design.py"]))
    resultados.append(rodar("gate:autoteste-higiene", [py, "scripts/prova-higiene-doc.py"]))
    # Acervo de decisões de backend (ECC, MIT) e o consultor em português. Molde obrigatório do
    # plano de consolidação: dado dentro do repo + consulta + prova no gate. A prova cobre os dois
    # modos de falha medidos na construção: substring que aproxima a linha errada e fallback que
    # despeja a tabela inteira quando não sabe -- ambos passaram verdes antes de existir teste.
    resultados.append(rodar("backend:consulta", [py, "scripts/consulta-backend.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-backend",
                            [py, "scripts/prova-consulta-backend.py"]))
    # Acervo de priorizacao de performance (ECC, MIT com arquivo LICENSE). A prova exercita os 41
    # sinonimos do mapa um a um -- nao uma amostra -- porque quatro entradas no radical ("waterfall"
    # contra "Waterfalls") passaram batidas quando a teste so cobria os termos escolhidos para ela.
    resultados.append(rodar("performance:consulta", [py, "scripts/consulta-performance.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-performance",
                            [py, "scripts/prova-consulta-performance.py"]))
    # codebase e espec: as provas existiam desde que os acervos entraram, mas nao eram rodadas pelo
    # gate -- lacuna real. Sem isto, o consulta-espec de scripts/ do repo apontava o dado so por
    # ancestral e falhava rodando da raiz (verde no uso instalado, quebrado ao testar no checkout),
    # e nada denunciava. Agora os cinco consultores sao exercitados e provados aqui.
    resultados.append(rodar("codebase:consulta", [py, "scripts/consulta-codebase.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-codebase",
                            [py, "scripts/prova-consulta-codebase.py"]))
    resultados.append(rodar("espec:consulta", [py, "scripts/consulta-espec.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-espec",
                            [py, "scripts/prova-consulta-espec.py"]))
    # web-design-guidelines: regras internalizadas (Vercel WIG, MIT), consultaveis offline.
    resultados.append(rodar("web:consulta", [py, "scripts/consulta-web.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-web",
                            [py, "scripts/prova-consulta-web.py"]))
    # postgres-prod-preflight: acervo de pre-deploy (gates, anti-padroes de migracao, checklist).
    resultados.append(rodar("postgres:consulta", [py, "scripts/consulta-postgres.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-postgres",
                            [py, "scripts/prova-consulta-postgres.py"]))
    # devops-cloud-deployer: acervo de deploy/cloud (estrategias, docker, checklist de producao).
    resultados.append(rodar("devops:consulta", [py, "scripts/consulta-devops.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-devops",
                            [py, "scripts/prova-consulta-devops.py"]))
    # e2e-browser-verifier: acervo de E2E/Playwright (flaky, seletores/esperas, fluxo critico).
    resultados.append(rodar("e2e:consulta", [py, "scripts/consulta-e2e.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-e2e",
                            [py, "scripts/prova-consulta-e2e.py"]))
    # reverse-engineer-anything: acervo de RE (anti-padroes por fase, mapa de referencias).
    resultados.append(rodar("reverse:consulta", [py, "scripts/consulta-reverse.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-reverse",
                            [py, "scripts/prova-consulta-reverse.py"]))
    # autonomous-improvement-ultimate: acervo de gates de qualidade (evidencia por area, componente).
    resultados.append(rodar("autonomous:consulta", [py, "scripts/consulta-autonomous.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-autonomous",
                            [py, "scripts/prova-consulta-autonomous.py"]))
    # A skill que MANDA rodar um script tem de levar o script e o dado junto. Medido na rodada 58:
    # os tres consultores instruidos pelo SKILL.md viviam em scripts/ do repo, e `install-all` copia
    # apenas a pasta da skill -- a habilidade instalada em ~/.agents/skills/ mandava executar arquivo
    # inexistente. Verde no checkout porque la os dois caminhos existem; quebrado no uso real.
    resultados.append(rodar("skills:autocontencao", [py, "scripts/checa-autocontencao.py"]))
    resultados.append(rodar("gate:autoteste-copias-de-consultor",
                            [py, "scripts/prova-copias-de-consultor.py"]))
    # Todo comando `python scripts/consulta-*.py ...` que um SKILL.md ou reference promove e executado
    # aqui. Um agente copia o exemplo e roda; se a interface mudou e o documento nao, o resultado e uma
    # habilidade que instrui um comando quebrado -- verde em todos os outros checks. Achado real: assim
    # apareceu que `ux formulario --severidade alta` filtrava contra 'high' comparado a 'alta' e nunca
    # devolvia nada, e que dataset-design.md apresentava 14 arquivos dos quais o script lia 5.
    resultados.append(rodar("docs:exemplos-executaveis",
                            [py, "scripts/checa-exemplos-executaveis.py"]))
    # Acervo de code tour (ECC, MIT). A prova nao depende da fonte ECC estar nesta maquina -- ela e
    # verificada na geracao (44 celulas) e o hash de cada CSV fica registrado em dados/PROVENIENCIA.md,
    # entao a prova confere invariantes (contagem, origem preenchida, hash) em qualquer ambiente. Um
    # N/A silencioso quando a fonte falta deixaria o grupo sem dentes.
    resultados.append(rodar("codebase:consulta",
                            [py, "skills/dz23-codebase-cartographer/scripts/consulta-codebase.py",
                             "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-codebase",
                            [py, "scripts/prova-consulta-codebase.py"]))
    # Acervo de categorias de ADR (ECC architecture-decision-records, MIT). O hash de integridade aqui ja
    # nasce canonico (\r\n -> \n antes do sha256), porque no item anterior hashear bytes crus fez o CI
    # reprovar um checkout Linux cujo conteudo era identico ao disco Windows so por EOL. Ver a licao em
    # docs/quality-loop/state.md ("verde local != verde no runner").
    resultados.append(rodar("espec:consulta",
                            [py, "skills/dz23-spec-to-system-engine/scripts/consulta-espec.py", "listar"]))
    resultados.append(rodar("gate:autoteste-consulta-espec",
                            [py, "scripts/prova-consulta-espec.py"]))
    # Trilha C: a dz23-subagents-universal-mcp tem 293 testes proprios em node:test (zero dependencias), mas
    # ate aqui o gate do ARSENAL nunca os executava -- so pentagi-mcp tinha check. Cobertura ausente do tipo
    # que a rodada 46 achou nos scripts embutidos: o teste existia, ninguem o rodava no lugar certo. Rodar a
    # suite dela e mais honesto que escrever um selftest paralelo. Sem node no PATH declara NOT_TESTED (exit 0)
    # em vez de PASS silencioso; com node exige fail 0 E tests > 0 (runner que nao descobriu caso daria 0/0/ok).
    resultados.append(rodar("mcp:subagents-selftest", [py, "scripts/selftest-subagents-mcp.py"]))
    # Repositório PÚBLICO, e até esta rodada nenhum verificador abria um arquivo em busca de
    # credencial: colar um token GitHub válido em `.env.example` dava gate 46/46 verde. Os quatro
    # scripts que mencionam "segredo" no fonte falam de outra coisa (scan descrito em prosa, design
    # tokens, tokenização para comparar citações) -- nenhum abre um arquivo procurando credencial.
    # Padrão de emissor real, não entropia: ver docstring do check-secrets.
    resultados.append(rodar("secrets", [py, "scripts/check-secrets.py"]))
    # Bundle DSH: os três validadores próprios existiam mas nunca rodaram no gate nem no CI
    # (dívida 4 do ROADMAP). `agents/` é artefato gerado e versionado -- sem o build.py --check
    # real, divergir das fontes era invisível, e o flag antigo só media bytes.
    _bundleraiz = RAIZ / "bundle" / "dz23-dsh-agency"
    resultados.append(rodar("bundle:consistencia",
                            [py, str(_bundleraiz / "check_consistency.py")], cwd=_bundleraiz))
    resultados.append(rodar("bundle:tamanho",
                            [py, str(_bundleraiz / "check_sizes.py")], cwd=_bundleraiz))
    resultados.append(rodar("bundle:agents-sincronizados",
                            [py, str(_bundleraiz / "build.py"), "--check"], cwd=_bundleraiz))
    resultados.append(rodar("evals:coerencia", [py, "scripts/run-evals.py", "--check"]))
    # MCP PentAGI: serviço self-hosted que normalmente está fora. O selftest agora cobra
    # degradação acionável nesse caso, então roda em qualquer máquina -- antes exigia serviço
    # de pé e por isso nunca entrou no gate. Condicionado a node_modules existir: sem as
    # dependências instaladas não há como abrir o servidor, e isso é ausência de medidor,
    # não reprovação (mesma disciplina aplicada às alegações de CRLF).
    _pentagi = RAIZ / "mcp" / "pentagi-mcp"
    if (_pentagi / "node_modules").is_dir():
        resultados.append(rodar("mcp:pentagi-selftest", ["node", "scripts/selftest.js"],
                                cwd=_pentagi))
    resultados.append(rodar("evals:schema", [py, "scripts/run-evals.py", "--schema"]))
    resultados.append(rodar("evals:registros", [py, "scripts/check-eval-results.py"]))
    resultados.append(rodar("evals:citacoes", [py, "scripts/run-evals.py", "--verify-quotes"]))
    # Auto-testes dos instrumentos novos: se o verificador quebrar, o gate avisa antes de
    # alguém confiar num passRate errado.
    resultados.append(rodar("gate:autoteste", [py, "scripts/gate_candidatos.py", "--selftest"]))
    resultados.append(rodar("claims:autoteste", [py, "scripts/verifica_claims.py", "--selftest"]))
    # Ataque sistemático: entradas doentes contra triagem, claims e descoberta de arsenal.
    # Um verificador que explode num JSON malformado é pior que um que erra -- quem vê
    # traceback para de olhar a saída, e foi assim que os gates-fantasma sobreviveram aqui.
    resultados.append(rodar("ferramentas:ataque", [py, "scripts/selftest-ferramentas.py"]))
    # Re-executa a experiencia por tras de cada afirmacao feita nesta linha de trabalho.
    # Numero quebra alto (algum check reclama); frase do tipo 'X agora falha quando Y' apodrece
    # em silencio -- alguem remove a guarda, o texto continua no CHANGELOG e vira descricao de um
    # sistema que nao existe. Este check recusa essa deriva.
    resultados.append(rodar("alegacoes:reexecucao", [py, "scripts/audita-alegacoes.py"]))
    # Referências citadas nos SKILL.md têm de existir. Roda sobre as 10 skills; --min 1.0
    # transforma o script em veredito: sem ele ele é relatório e sai 0 mesmo achando caminho
    # quebrado, o que faria este check parecer mais forte do que é (observado ao injetar uma
    # referência inexistente -- o validate: pegou, o claims: saiu OK).
    for skill in sorted(p for p in (RAIZ / "skills").iterdir() if p.is_dir()):
        sm = skill / "SKILL.md"
        if sm.is_file():
            resultados.append(rodar(f"claims:{skill.name}",
                                    [py, "scripts/verifica_claims.py",
                                     "--texto", str(sm), "--raiz", str(RAIZ),
                                     "--min", "1.0"]))

    # Regressao de encoding: o gate tem de sobreviver a um locale cp1252 (o bug real
    # desta sessao -- captura de subprocesso sem encoding explicito quebrava tudo). A
    # prova roda o proprio gate sob PYTHONIOENCODING=cp1252; a flag ARSENAL_GATE_
    # ENCODING_SELFTEST quebra a recursao, entao a rodada interna pula esta linha.
    if os.environ.get("ARSENAL_GATE_ENCODING_SELFTEST") != "1":
        resultados.append(rodar("gate:autoteste-encoding-cp1252",
                                [py, "scripts/prova-encoding-gate.py"]))

    falhas = [r for r in resultados if not r["ok"]]
    publicar_contagem(len(resultados))
    if args.json:
        print(json.dumps({"ok": not falhas, "total": len(resultados),
                          "falhas": len(falhas), "checks": resultados}, indent=2, ensure_ascii=False))
        return 0 if not falhas else 1

    print("# Quality gate — dz23-arsenal\n")
    print(f"{'check':<42}{'resultado':<10}resumo")
    print("-" * 100)
    for r in resultados:
        marca = "OK" if r["ok"] else "FALHA"
        print(f"{r['check']:<42}{marca:<10}{r['resumo'][:52]}")
    print()
    print(f"{len(resultados) - len(falhas)}/{len(resultados)} checks passaram")
    if falhas:
        print("\nFALHAS:")
        for r in falhas:
            print(f"  - {r['check']}: {r['resumo']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
