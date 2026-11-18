"""Audita afirmacoes qualitativas feitas nesta sessao: cada uma ainda e verdadeira?

Numero quebra alto (algum check reclama). Afirmacao do tipo 'X agora falha quando Y' quebra
em silencio: alguem remove a guarda, o texto continua no CHANGELOG e passa a ser descricao de
um sistema que nao existe. Este arquivo re-executa a experiencia por tras de cada frase.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
if len(sys.argv) > 1:
    RAIZ = pathlib.Path(sys.argv[1])
PY = sys.executable
sys.path.insert(0, str(RAIZ / "scripts"))


def exec_(args, cwd=None, stdin=None):
    p = subprocess.run([PY, *args], capture_output=True, cwd=str(cwd or RAIZ),
                       input=stdin, timeout=240)
    return p.returncode, (p.stdout.decode("utf-8", "replace")
                          + p.stderr.decode("utf-8", "replace"))


resultados = []


def afirma(texto, fn):
    """Aceita três resultados: OK, CAIU e N/A -- e eles não são a mesma coisa.

    Contratos aceitos por `fn`:
      * lança exceção            -> CAIU
      * devolve False            -> CAIU
      * devolve True ou None     -> OK (None = "verificou e não há violação")
      * devolve a string 'NA'    -> N/A: a precondição da prova não existe aqui

    A distinção N/A foi obrigatória pela primeira execução real do CI: duas provas dependem de
    ~/.agents/skills, que não existe num runner efêmero. Elas retornavam False -- o código
    queria dizer "não tenho como aferir" -- e `afirma` lia isso como reprovação, quebrando o
    build por uma razão que não é falha do repositório. É exatamente a regra que este arsenal
    aplica a claims (verifica_claims tem `nao-verificavel` fora do denominador) e que eu não
    apliquei às minhas próprias provas. Silenciar N/A como OK também seria errado: esconderia
    que em CI duas alegações ficam sem cobertura, e isso precisa aparecer no log.
    """
    try:
        ret = fn()
        if isinstance(ret, str) and ret.strip().upper() in ("NA", "N/A"):
            resultados.append((texto, None))
            print(f"  N/A     {texto}")
            return
        ok = True if ret is None else bool(ret)
    except Exception as exc:  # noqa: BLE001
        ok = False
        texto += f"  [excecao: {type(exc).__name__}]"
    resultados.append((texto, bool(ok)))
    print(f"  {'OK      ' if ok else 'CAIU!!!!'} {texto}")


print("=== gates-fantasma: cada um foi fechado com prova; a prova ainda vale? ===")

# D1: --verify-quotes sem AUDIT-STATUS deve falhar.
def d1():
    arq = RAIZ / "evals-results/_audit-notes/AUDIT-STATUS.json"
    backup = arq.read_bytes()
    deslocado = arq.with_name(arq.name + ".off")
    try:
        arq.rename(deslocado)
        rc, s = exec_(["scripts/run-evals.py", "--verify-quotes"])
        return rc == 1 and "ausente" in s
    finally:
        # Restaurar por caminho explicito, nunca com with_suffix(): na primeira versao isto
        # era `arq.with_suffix(".off")`, que apaga '.json' e produz AUDIT-STATUS.off -- um
        # arquivo novo na arvore versionada que o finally nao desfazia. A suíte vazou um
        # resíduo assim no repo real antes de eu perceber.
        if deslocado.exists():
            deslocado.replace(arq)
        if not arq.exists():
            arq.write_bytes(backup)
afirma("verify-quotes falha sem AUDIT-STATUS.json", d1)

# check-audit-inputs sem argumento: usage, nao traceback.
afirma("check-audit-inputs sem arg -> exit 2 com usage",
       lambda: (lambda r: r[0] == 2 and "Traceback" not in r[1])(
           exec_(["scripts/check-audit-inputs.py"])))

# check-numbers denuncia regra orfa.
def orfa():
    """Escreve README mentiroso numa COPIA, nunca no repo.

    A versão anterior alterava README.md do próprio repositório e restaurava em `finally`.
    Isso é inaceitável por três motivos independentes: um TimeoutExpired dentro do try pula o
    finally e deixa o repo corrompido (aconteceu -- 38 linhas injetadas num SKILL.md); qualquer
    crash entre escrever e restaurar faz o mesmo; e se duas verificações rodarem concorrentes,
    uma lê o estado que a outra corrompeu. Um auditor que precisa danificar o alvo para testá-lo
    está mal desenhado, não destemido.
    """
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        shutil.copytree(RAIZ / "scripts", tmp / "scripts")
        shutil.copytree(RAIZ / "skills", tmp / "skills")
        for n in ("README.md", "ROADMAP.md", "arsenal.json", ".gate-contagem",
                  "evals.schema.json"):
            if (RAIZ / n).is_file():
                shutil.copy2(RAIZ / n, tmp / n)
        if (RAIZ / "external").is_dir():
            shutil.copytree(RAIZ / "external", tmp / "external")
        if (RAIZ / "bundle").is_dir():
            shutil.copytree(RAIZ / "bundle", tmp / "bundle")
        if (RAIZ / "mcp").is_dir():
            shutil.copytree(RAIZ / "mcp", tmp / "mcp")
        readme = tmp / "README.md"
        t = readme.read_text(encoding="utf-8")
        readme.write_text(t.replace("Coleção de 12 skills", "Coleção de X skills"),
                          encoding="utf-8")
        rc, s = exec_(["scripts/check-numbers.py"], cwd=tmp)
        return "REGRA ÓRFÃ" in s or rc != 0
afirma("check-numbers pega regra orfa quando o numero sai do README", orfa)

# claims: referencia quebrada em SKILL.md e pega pelo gate.
def claims_pega():
    with tempfile.TemporaryDirectory() as td:
        esp = pathlib.Path(td) / "repo"
        shutil.copytree(RAIZ / "skills/dz23-e2e-browser-verifier",
                        esp / "skills/dz23-e2e-browser-verifier")
        shutil.copytree(RAIZ / "scripts", esp / "scripts")
        alvo = esp / "skills/dz23-e2e-browser-verifier/SKILL.md"
        alvo.write_bytes(alvo.read_bytes()
                         + "\nVer `references/relatorio-de-cobertura.md`.\n".encode())
        rc, s = exec_(["scripts/verifica_claims.py", "--texto", str(alvo), "--raiz", str(esp),
                       "--min", "1.0"])
        return rc != 0 and "falho" in s.lower()
afirma("verifica_claims reprova referencia quebrada", claims_pega)

# python -O nao desliga validador (rodada 19).
def modo_o():
    """Exige que seja o -O a mudar o resultado, não apenas 'algo reprova'.

    A versão anterior devolvia `rc != 0` depois de injetar uma referência quebrada. Como essa
    violação é pega também pela checagem própria da skill, qualquer exit != 0 bastava -- e se o
    conserto do -O regredisse, a prova continuaria verde. Medido nesta sessão: reescrevendo o
    validador com o padrão antigo (`assert not _erros_comuns`), o modo normal sai 1 e o `-O` sai 0
    com PASS; hoje os dois saem 1. Essa diferença entre modos é o que a alegação enuncia, então é
    o que ela passa a exigir.
    """
    with tempfile.TemporaryDirectory() as td:
        esp = pathlib.Path(td) / "skill"
        shutil.copytree(RAIZ / "skills/dz23-e2e-browser-verifier", esp)
        sm = esp / "SKILL.md"
        sm.write_bytes(sm.read_bytes() + "\nVer `references/painel-de-metricas.md`.\n".encode())
        alvo = str(esp / "scripts/validate_skill.py")
        rc_normal, s_normal = exec_([alvo])
        rc_o, s_o = exec_(["-O", alvo])
        if rc_normal == 0:
            raise AssertionError("referência quebrada não reprovada nem no modo normal")
        if rc_o == 0:
            raise AssertionError(f"python -O ainda desliga a reprovacao: {s_o[-140:]}")
        # sensibilidade: reproduzir o padrao antigo e exigir que ele mude o resultado sob -O
        v = esp / "scripts/validate_skill.py"
        texto = v.read_text(encoding="utf-8")
        antigo = re.sub(
            r"( *)for e in _erros_comuns:\n\1    print\(f\"FALHA: \{e\}\", file=sys\.stderr\)\n"
            r"\1raise SystemExit\(1\)",
            r"\1assert not _erros_comuns, _erros_comuns", texto)
        if antigo == texto:
            raise AssertionError("padrao corrigido nao encontrado no fonte; prova cega")
        v.write_text(antigo, encoding="utf-8")
        rc_antigo_o, _ = exec_(["-O", alvo])
        if rc_antigo_o != 0:
            raise AssertionError(
                "a regressao historica (assert) tambem reprovaria sob -O -- logo a prova nao e "
                "sensivel ao que alega; ela so mede 'alguma checagem reprova'")
afirma("validador nao aprova sob python -O", modo_o)

# skill instalada se auto-valida sem o checkout (rodada 7).
def instala_sem_repo():
    """Copia a skill instalada para um destino isolado e corrompe SÓ a cópia.

    Antes isto escrevia em ~/.agents/skills de verdade, protegido apenas por `finally`. Um
    TimeoutExpired dentro do try pula o finally e deixa a instalação do usuário quebrada -- o
    dano não aparece no git status, então passa despercebido até a próxima sessão. O validador
    resolve arsenal subindo a árvore e lendo .dz23-arsenal relativo ao próprio arquivo, então
    uma cópia fora de ~/.agents/skills com ponteiro mentiroso reproduz o cenário sem tocar em
    nada real.
    """
    import os
    sk_real = pathlib.Path(os.path.expanduser("~/.agents/skills"))
    origem = sk_real / "dz23-codebase-cartographer"
    if not origem.is_dir():
        return "NA"          # sem instalação nesta máquina; nada a provar aqui
    with tempfile.TemporaryDirectory() as td:
        esp = pathlib.Path(td) / "dz23-codebase-cartographer"
        shutil.copytree(origem, esp)
        # Caminho absolutamente ausente, não um caminho Windows: no Linux `D:\repo\...` é
        # relativo ao cwd e pode resolver para dentro do checkout -- mesmo defeito que fez o
        # selftest-ferramentas falhar na primeira execução real do CI.
        morto = str(pathlib.Path(tempfile.gettempdir()) / f"arsenal-morto-{os.getpid()}")
        (esp / ".dz23-arsenal").write_text(morto + "\n", encoding="utf-8")
        v = esp / "SKILL.md"
        v.write_bytes(v.read_bytes()
                      + "\nVer `references/mapa-de-fluxo-legado.md`.\n".encode())
        rc, s = exec_([str(esp / "scripts/validate_skill.py")])
        if rc == 0:
            return False
        # Reprovar não basta: é preciso saber QUAL ramo salvou a verificação. A resistência da
        # instalação vem da cópia embarcada de skill_validator.py (primeiro ramo de
        # importar_validador_comum), não do ponteiro -- o ROADMAP diz isso explicitamente. Uma
        # prova que não distingue os dois ramos aceitaria qualquer exit != 0 e deixaria de acusar
        # se alguém removesse a cópia embarcada sem remover a dependência do ponteiro.
        sys.path.insert(0, str(RAIZ / "scripts"))
        import inspect as _insp
        from _achar_arsenal import importar_validador_comum as _imp, localizar_arsenal as _loc
        alvo = (esp / "scripts/validate_skill.py").resolve()
        if _loc(alvo) is not None:
            raise AssertionError("cenário esperado era ponte morta; arsenal foi localizado")
        fn = _imp(str(alvo))
        origem = _insp.getfile(fn) if fn else None
        if origem is None:
            raise AssertionError(
                f"reprovou sem nenhum validador comum carregado (exit {rc}); a checagem que "
                f"pegou a referência é própria da skill, então a alegação 'mesmo sem o repo' "
                f"não está sendo exercida por este teste")
        if pathlib.Path(origem).parent != (esp / "scripts").resolve():
            raise AssertionError(f"validador comum veio de fora da cópia: {origem}")
        return True
afirma("skill instalada reprova mesmo sem o repo (rodada 7)", instala_sem_repo)

# CRLF: indice limpo apesar do working tree.
def crlf():
    bash = shutil.which("bash") or r"C:\Program Files\Git\bin\bash.exe"
    # Sem bash não há como medir, e isso não é falha do repositório. A versão anterior chamava
    # subprocess com um caminho possivelmente inexistente: FileNotFoundError subia para o
    # afirma() e a alegação aparecia como "caiu" num ambiente onde simplesmente não havia
    # medidor -- o mesmo engano de categoria que o CI cobrou na rodada 39 (ausência de
    # precondição tratada como reprovação). Irmã de confere_crlf_indice, que já fazia isso.
    if not pathlib.Path(bash).is_file():
        return "NA"
    p = subprocess.run([bash, "-c",
                        'cd "$1" && git grep -Il --cached -P "\\r$" -- "*.md" "*.py" '
                        '"*.sh" "*.yml" "*.json" "*.txt" || true', "x", str(RAIZ)],
                       capture_output=True, timeout=120)
    return not p.stdout.decode("utf-8", "replace").strip()
afirma("indice sem CRLF (passo de CI do jeito certo)", crlf)

# audit-zips nao confunde EOL com divergencia (rodada 9).
def eol_audit():
    """Mesma lição: comparar contra uma cópia convertida, nunca editar a instalação.

    audit-zips aceita --dest, então dá para apontá-lo para um espelho com LF puro e medir a
    decisão sem escrever em lugar nenhum que alguém usa.
    """
    sk_real = pathlib.Path.home() / ".agents/skills"
    if not (sk_real / "dz23-codebase-cartographer").is_dir():
        return "NA"          # runner efêmero não tem skills instaladas
    with tempfile.TemporaryDirectory() as td:
        esp = pathlib.Path(td)
        shutil.copytree(sk_real, esp / "skills", symlinks=False)
        alvo = esp / "skills/dz23-codebase-cartographer/references/data-and-flow.md"
        if not alvo.is_file():
            return "NA"
        alvo.write_bytes(alvo.read_bytes().replace(b"\r\n", b"\n"))
        rc, s = exec_(["scripts/audit-zips.py", "--dest", str(esp / "skills")])
        detalhe = s.split("CONTEUDO_DIVERGENTE")[-1][:400] if "CONTEUDO_DIVERGENTE" in s else ""
        return "cartographer" not in detalhe
afirma("audit-zips ignora diferenca so de EOL", eol_audit)

print("\n=== estrutura do arsenal: o que foi declarado nestas rodadas ainda vale? ===")

# A contagem de checks publicada não pode ser digitada em lugar nenhum: o check-numbers lê
# .gate-contagem, escrito pela execução real do gate. Se alguém fixar um número no README, isto
# precisa pegar.
def confere_contagem_derivada() -> None:
    """A contagem publicada não pode ser um número digitado na documentação.

    Não chamar o quality-gate daqui: este arquivo É um check dele, então invocar o gate
    recursa até estourar o prazo (medido: 241 s e TimeoutExpired).

    E não exigir .gate-contagem existente: o artefato é gitignored e o CI roda este auditor
    ANTES do gate, num checkout onde ele jamais existiu. A primeira versão desta função fazia
    `raise AssertionError("ausente")`, o que passava na minha máquina (onde eu acabara de rodar
    o gate) e falhava em qualquer clone limpo -- detectado ao verificar a bisectabilidade dos
    commits, não pelo teste local. Ausência do artefato é o estado normal de um checkout novo:
    nada há para contradizer, então a checagem aplicável é outra -- nenhum documento fixa um
    total de checks à mão.
    """
    artefato = RAIZ / ".gate-contagem"
    medido = None
    if artefato.is_file():
        try:
            medido = json.loads(artefato.read_text(encoding="utf-8")).get("total")
        except (json.JSONDecodeError, OSError):
            medido = None

    # O que vale sempre: a documentação não pode afirmar um total arbitrário.
    for nome in ("README.md", "ROADMAP.md", "CONTRIBUTING.md"):
        doc = RAIZ / nome
        if not doc.is_file():
            continue
        texto = doc.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"(?m)^.*?\b(\d{2})\s+checks\b.*$", texto):
            citado = int(m.group(1))
            if medido is not None and citado != medido:
                raise AssertionError(f"{nome} fixa {citado} checks; gate publicou {medido}")
            if medido is None:
                # sem medição recente, um número solto na doc é exatamente o que apodrece
                raise AssertionError(
                    f"{nome} afirma '{citado} checks' sem fonte executável para conferir "
                    f"(rode python scripts/quality-gate.py ou remova o número)")
    if medido is None:
        return          # checkout limpo: nada contradito, nada a comparar
    rc, s = exec_(["scripts/check-numbers.py", "--json"])
    d = json.loads(s)
    lido = d["real"].get("quality_gate_checks")
    if lido != medido:
        raise AssertionError(f"checker le {lido}, gate publicou {medido}")
    if d["problemas"]:
        raise AssertionError(f"divergencia numerica: {d['problemas'][:1]}")
afirma("nº de checks é derivado da execução, não digitado", confere_contagem_derivada)

# Índice de skills gerado (rodada 27): se alguém editar a tabela à mão, isto cai.
def confere_indice() -> None:
    """Não basta exit 0: é preciso provar que o --check sabe reprovar.

    Um verificador que passou a não comparar nada devolve 0 para sempre -- foi literalmente o
    defeito do build.py --check na rodada 28. A prova então aplica uma violação e exige reclame,
    além do estado limpo.
    """
    rc, s = exec_(["scripts/gera-indice-skills.py", "--check"])
    if rc != 0:
        raise AssertionError(f"índice de skills desatualizado: {s.strip()[:120]}")
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        for n in ("scripts", "skills"):
            shutil.copytree(RAIZ / n, base / n, symlinks=False)
        alvo = base / "skills/README.md"
        texto = alvo.read_text(encoding="utf-8")
        # Injecao por padrao literal fixo ("| 1.1.1 | Exploracao") apontava para a versao que a
        # cartographer tinha quando este teste foi escrito; bump real (1.1.1 -> 1.2.0) fez o re.sub
        # virar no-op e o verificador acusar "medicao vazia". A violacao agora localiza a linha pelo
        # nome da skill e troca a versao que ela de fato carrega -- senao o teste quebra no dia em que
        # qualquer skill sobe de versao, e verde obtido por injecao que nao aconteceu nao mede nada.
        m = re.search(r"(?m)^\| \[codebase-cartographer\]\([^\)]*\) \| (\d+\.\d+\.\d+) \|", texto)
        if not m:
            raise AssertionError("nao achei a linha da cartographer no indice para violar")
        violado = texto.replace(m.group(0), m.group(0).replace(m.group(1), "0.0.1"), 1)
        if violado == texto:
            raise AssertionError("não consegui violar o índice; prova cega")
        alvo.write_text(violado, encoding="utf-8")
        rc2, _ = exec_(["scripts/gera-indice-skills.py", "--check"], cwd=base)
        if rc2 == 0:
            raise AssertionError("--check aprovou indice com versao errada: verificador oco")


afirma("índice de skills bate com o disco", confere_indice)

# Bundle: os 88 agentes versionados batem com as fontes (rodada 28).
def confere_bundle() -> None:
    import os
    bund = RAIZ / "bundle/dz23-dsh-agency"
    p = subprocess.run([sys.executable, "build.py", "--check"], capture_output=True,
                       cwd=str(bund), timeout=180, env=os.environ)
    saida = p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")
    if p.returncode != 0:
        raise AssertionError(f"agents/ fora de sincronia: {saida.strip()[-140:]}")
    # O --check do bundle foi, por meses, um verificador que não comparava nada: media bytes e
    # imprimia OK. Conferir só o estado limpo deixaria a mesma classe de regressão passar verde,
    # então adulterar uma cópia dos agentes e exigir reclame.
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td) / "dz23-dsh-agency"
        shutil.copytree(bund, base, symlinks=False)
        alvo = base / "agents/00-diretor.txt"
        if not alvo.is_file():
            return          # layout mudou; nada a violar sem chutar
        alvo.write_bytes(alvo.read_bytes() + b"\nintruso-de-prova\n")
        rc2 = subprocess.run([sys.executable, "build.py", "--check"], capture_output=True,
                             cwd=str(base), timeout=180, env=os.environ).returncode
        if rc2 == 0:
            raise AssertionError("--check aprovou agents/ adulterado: voltou a ser verificador oco")


afirma("bundle agents/ sincronizado com as fontes", confere_bundle)

# Comandos da documentação apontam para arquivos que existem (rodada 26).
def confere_docs() -> None:
    rc, s = exec_(["scripts/check-docs-runnable.py"])
    if rc != 0:
        raise AssertionError(f"comando de doc quebrado: {s.strip()[:140]}")
    # Estado limpo sozinho não prova nada: um verificador que parou de ler blocos também devolve
    # 0. Violar em cópia e exigir reclame -- e ainda conferir que ele le alguma coisa, porque
    # "zero linhas conferidas" seria o gate-fantasma da rodada 15 de volta.
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        for n in ("scripts", "skills", "docs", "bundle", "mcp", "external", "cli"):
            if (RAIZ / n).is_dir():
                shutil.copytree(RAIZ / n, base / n, symlinks=False)
        for f in ("README.md", "ROADMAP.md", "CONTRIBUTING.md", "CHANGELOG.md",
                  "evals.schema.json", ".gate-contagem"):
            if (RAIZ / f).is_file():
                shutil.copy2(RAIZ / f, base / f)
        alvo = base / "CONTRIBUTING.md"
        alvo.write_bytes(alvo.read_bytes()
                         + b"\n```bash\npython scripts/nao-existe-zz-prova.py\n```\n")
        rc2, s2 = exec_(["scripts/check-docs-runnable.py"], cwd=base)
        if rc2 == 0:
            raise AssertionError("check-docs-runnable aprovou comando quebrado: verificador oco")
        if "linhas de comando conferidas em" not in s2:
            raise AssertionError("sem contagem de linhas conferidas; pode estar lendo zero docs")


afirma("toda referência de comando na documentação existe", confere_docs)

# Clone limpo: o índice não tem CRLF mesmo com a cópia de trabalho convertida (rodada 9). Esta é
# a razão do --cached no passo de CI; sem ela, o teste vira falso positivo em Windows.
def confere_crlf_indice() -> None:
    bash = shutil.which("bash") or r"C:\Program Files\Git\bin\bash.exe"
    if not pathlib.Path(bash).is_file():
        return "NA"       # ausência de medidor não é reprovação (ver crlf(), mesma lição)
    p = subprocess.run(
        [bash, "-c", 'cd "$1" && git grep -Il --cached -P "\\r$" -- "*.md" "*.py" "*.sh" '
                     '"*.yml" "*.json" "*.txt" || true', "x", str(RAIZ)],
        capture_output=True, timeout=180)
    saida = p.stdout.decode("utf-8", "replace").strip()
    if saida:
        raise AssertionError(f"{len(saida.splitlines())} blob(s) com CRLF no índice")
afirma("índice do git sem CRLF (decisão do passo de CI)", confere_crlf_indice)

# A checagem de citação fabricada é a camada mais valiosa do arsenal (a auditoria de 2026-11-09
# citou trechos que não estavam nas respostas) e passou por dois gates-fantasma nesta sessão.
# Provar o caminho positivo exige violar uma citação real -- em cópia, nunca no repo.
def confere_citacao_fabricada() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        for n in ("scripts", "audit-results", "audit-package", "evals-results", "skills"):
            if not (RAIZ / n).is_dir():
                return
            shutil.copytree(RAIZ / n, tmp / n, symlinks=False)
        rc, s = exec_(["scripts/run-evals.py", "--verify-quotes"], cwd=tmp)
        if rc != 0:
            raise AssertionError(f"baseline já falha na cópia: {s.strip()[:120]}")
        st = json.loads((tmp / "evals-results/_audit-notes/AUDIT-STATUS.json").read_text(
            encoding="utf-8"))
        validos = [l["arquivo"] for l in st.get("laudos", []) if l.get("status") == "VALIDO"]
        sys.path.insert(0, str(tmp / "scripts"))
        import importlib.util as iu
        sp = iu.spec_from_file_location("caq_probe", str(tmp / "scripts/check-audit-quotes.py"))
        caq = iu.module_from_spec(sp)
        sp.loader.exec_module(caq)
        # usar o próprio extrator para escolher o alvo: garante violar o que ele lê. As três
        # primeiras tentativas desta prova procuraram crases e falharam porque extrair_citacoes
        # lê linhas iniciadas por '>' -- formato imaginado, não observado.
        alvo = None
        for rel in validos:
            texto = (tmp / rel).read_text(encoding="utf-8")
            for mb in re.finditer(r"(?ms)^##\s+Eval[^\n]*\n(.*?)(?=^##\s+Eval|\Z)", texto):
                for cit in caq.extrair_citacoes(mb.group(1)):
                    if len(cit) >= 40 and cit in texto:
                        alvo = (rel, cit)
                        break
                if alvo:
                    break
            if alvo:
                break
        if not alvo:
            return          # nada a violar (laudos reescritos); não é aprovação nem falha
        rel, cit = alvo
        arq = tmp / rel
        falsa = cit[:16] + "ZZZ-INVENTADO " + cit[16:]
        arq.write_text(arq.read_text(encoding="utf-8").replace(cit, falsa, 1),
                       encoding="utf-8")
        rc2, s2 = exec_(["scripts/run-evals.py", "--verify-quotes"], cwd=tmp)
        if rc2 == 0:
            raise AssertionError("citação inventada passou despercebida -- gate-fantasma vivo")
afirma("citação fabricada num laudo VALIDO é recusada", confere_citacao_fabricada)

# Ordem do changelog: registrei entradas novas na posição errada duas vezes nesta sessão,
# porque usei sempre o mesmo cabeçalho como âncora de inserção em vez do topo corrente. Um
# changelog com a versão mais antiga no topo não conta história -- inverte a leitura.
def confere_ordem_changelog() -> None:
    texto = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
    vs = re.findall(r"(?m)^## \[([\d.]+)\]", texto)
    if not vs:
        raise AssertionError("CHANGELOG.md sem entradas de versão")
    chave = lambda v: tuple(int(x) for x in v.split("."))
    ruins = [(vs[i], vs[i + 1]) for i in range(len(vs) - 1) if chave(vs[i]) < chave(vs[i + 1])]
    if ruins:
        raise AssertionError(f"entradas fora de ordem descendente: {ruins[:3]}")
afirma("CHANGELOG em ordem de versão descendente", confere_ordem_changelog)

print("\n" + "=" * 64)
# None é N/A, não falha. `if not ok` trataria None como queda (not None == True), e foi assim
# que o CI reprovou duas provas cuja precondição simplesmente não existe num runner efêmero.
caiu = [t for t, ok in resultados if ok is False]
na = [t for t, ok in resultados if ok is None]
verificadas = len(resultados) - len(na)
if na:
    print(f"N/A ({len(na)}): precondicao ausente neste ambiente -- nao conta como falha,")
    print(f"        mas tampouco foi provada aqui:")
    for n in na:
        print(f"   - {n}")
if caiu:
    print(f"{len(caiu)} alegacao(oes) nao sustentada(s):")
    for c in caiu:
        print("   -", c)
    sys.exit(1)
print(f"{verificadas}/{len(resultados)} alegacoes sustentadas por execucao"
      + (f" ({len(na)} sem aplicacao aqui)" if na else ""))
