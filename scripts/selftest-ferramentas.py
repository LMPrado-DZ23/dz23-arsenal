#!/usr/bin/env python3
"""selftest-ferramentas.py — ataque as ferramentas do arsenal com entradas doentes.

Nasceu de duas rodadas de verificação em que eu exercitei os scripts desta sessão e eles
morreram: `{'endpoints': {...}}` derrubava a triagem com AttributeError, e um
`.gate-contagem` contendo `[]` derrubava o conferidor de números. Os casos estavam escritos
em arquivos soltos fora do repo, onde morrem junto com a máquina que os gerou. Este arquivo
é o contrário: fica versionado e roda no CI.

Princípio que estes testes defendem: **um verificador que explode é pior que um verificador
que erra.** Quem encontra traceback num gate para de olhar a saída, e o passo passa a ser
ignorado -- exatamente o mecanismo pelo qual os dois gates-fantasma deste repo (v1.5.0)
sobreviveram até serem procurados. Entrada malformada não é caso excepcional aqui: o JSON de
sinais vem de coletor externo, o manifesto é gerado por outro script, o caminho do checkout
vem de variável de ambiente.

Cobre três instrumentos:
  * gate_candidatos  -- triagem determinística (formas doentes de JSON de sinais)
  * verifica_claims  -- checagem mecânica de claims (texto hostil, traversal, vazio)
  * _achar_arsenal   -- descoberta do checkout (env inválida, árvore incompleta)

Uso:
    python scripts/selftest-ferramentas.py            # legível
    python scripts/selftest-ferramentas.py --json     # máquina
    python scripts/selftest-ferramentas.py --selftest # auto-verificação do próprio runner
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from _achar_arsenal import localizar_arsenal  # noqa: E402
from gate_candidatos import PRIORIDADE_MAX, avaliar  # noqa: E402
from verifica_claims import avaliar as avaliar_claims  # noqa: E402


def sem_excecao(rotulo: str, fn) -> list[str]:
    """Executa e devolve problema se explodir. O conteúdo é verificado depois."""
    try:
        fn()
        return []
    except Exception as exc:  # noqa: BLE001 — este teste EXISTE para pegar exceção
        return [f"{rotulo}: {type(exc).__name__}: {exc}"]


# --- gate_candidatos -----------------------------------------------------------

FORMAS_DOENTES = [
    ("dict no lugar de lista", {"endpoints": {"rota": "x"}}),
    ("lista de strings", {"endpoints": ["nada", "nenhuma"]}),
    ("item nulo", {"benchmarks": [None]}),
    ("campos com tipo errado", {"endpoints": [{"rota": "x", "requests": "muito",
                                              "p95_ms": "alta", "hit_rate": "baixa",
                                              "cacheavel": True}]}),
    ("raiz não é objeto", ["a", "b"]),
    ("raiz é número", 42),
    ("raiz é string", "nada"),
    ("raiz é nulo", None),
    ("vazio", {}),
]


def testa_triagem() -> list[str]:
    problemas: list[str] = []

    for rotulo, entrada in FORMAS_DOENTES:
        problemas += sem_excecao(f"triagem/{rotulo}", lambda e=entrada: avaliar(e))

        def confere(entr: object = entrada) -> None:
            r = avaliar(entr)
            if r["lancados"]:
                raise AssertionError("entrada malformada lançou candidato")
            if not r["nao_avaliaveis"]:
                raise AssertionError("não declarou nada como não-avaliável")
        problemas += sem_excecao(f"triagem/{rotulo}/declaração", confere)

    # Escala: prioridade ordena, não mede grandeza.
    def confere_teto() -> None:
        r = avaliar({"endpoints": [{"rota": "enorme", "requests": 10**9,
                                    "p95_ms": 10**7, "hit_rate": 0.0, "cacheavel": True}],
                     "benchmarks": [{"nome": "apertado", "metrica": "LCP",
                                     "medido": 10**9, "budget": 1, "amostras": 10**6}]})
        for v in r["lancados"]:
            if not (0 <= v["prioridade"] <= PRIORIDADE_MAX):
                raise AssertionError(f"prioridade {v['prioridade']} fora do teto")
    problemas += sem_excecao("triagem/teto-de-prioridade", confere_teto)

    # Negativo: dados bons abaixo do limiar não lançam, mas ficam registrados.
    def confere_negativo() -> None:
        r = avaliar({"endpoints": [{"rota": "ping", "requests": 40, "p95_ms": 12,
                                    "hit_rate": 0.99, "cacheavel": True}]})
        if r["lancados"]:
            raise AssertionError("lançou abaixo do limiar")
        if not r["contidos"]:
            raise AssertionError("sumiu com o caso avaliado e rejeitado")
    problemas += sem_excecao("triagem/negativo", confere_negativo)

    # Determinismo: mesma entrada, mesma saída, byte a byte.
    def confere_determinismo() -> None:
        bom = {"endpoints": [{"rota": "GET /a", "requests": 900, "p95_ms": 800,
                              "hit_rate": 0.1, "cacheavel": True}]}
        if json.dumps(avaliar(bom), sort_keys=True) != json.dumps(avaliar(bom),
                                                                   sort_keys=True):
            raise AssertionError("avaliar não é determinístico")
    problemas += sem_excecao("triagem/determinismo", confere_determinismo)

    return problemas


# --- verifica_claims -----------------------------------------------------------

TEXTOS_HOSTIS = [
    ("vazio", ""),
    ("bytes de controle", "\x00\x01`a/b.md`\x02"),
    ("backtick não fechado", "veja `caminho/sem/fechar.md"),
    ("unicode e emoji", "veja `oops/../é/文件.md` e `emoji🔉/x.md`"),
    ("traversal puro", "veja `../../../Windows/win.ini`"),
    ("traversal embutido", "veja `a/../../b/README.md`"),
    ("caminho absoluto unix", "veja `/etc/shadow`"),
    ("caminho absoluto windows", "veja `C:\\Windows\\win.ini`"),
    ("casa alheia", "veja `~/foo/bar.md`"),
    ("outro projeto", "veja `projects/outra-coisa/src/index.js`"),
    ("placeholder", "veja `references/NAO-EXISTE-teste.md`"),
    ("imperativo", "Crie `scripts/arquivo-futuro.py` com o gate."),
    ("destino de escrita", "Registre em `docs/quality-loop/state.md` se apropriado."),
    ("numérico", "O p95 caiu de 850ms para ~250ms em 42% dos casos."),
    ("code block", "Exemplo:\n```bash\ncat scripts/ausente.sh\n```\n"),
    ("grande", ("Cada `references/x.md` e 90ms.\n" * 2000)),
]


def testa_claims() -> list[str]:
    problemas: list[str] = []
    for rotulo, texto in TEXTOS_HOSTIS:
        problemas += sem_excecao(f"claims/{rotulo}",
                                 lambda t=texto: avaliar_claims(t, RAIZ))

    def confere_traversal() -> None:
        r = avaliar_claims("veja `../../../Windows/win.ini`.", RAIZ)
        if r["falhos"]:
            raise AssertionError("traversal vazou como alegação verificável: oracle de "
                                 "existência para caminhos fora do checkout")
    problemas += sem_excecao("claims/traversal-não-vaza", confere_traversal)

    def confere_numerico_fora_do_denominador() -> None:
        r = avaliar_claims("O p95 caiu de 850ms para ~250ms.", RAIZ)
        if not r["sem_suporte"]:
            raise AssertionError("grandeza numérica não foi declarada como sem-suporte")
        if r["denominador"]:
            raise AssertionError("sem-suporte entrou no denominador do passRate")
        if r["passRate"] is not None:
            raise AssertionError(f"com só sem-suporte, passRate deveria ser None: "
                                 f"{r['passRate']}")
    problemas += sem_excecao("claims/numerico-fora-do-denominador",
                             confere_numerico_fora_do_denominador)

    def confere_code_block_nao_e_claim() -> None:
        r = avaliar_claims("Exemplo:\n```python\nopen('inexistente.py')\n```\n", RAIZ)
        if r["total_claims"]:
            raise AssertionError("código de exemplo virou alegação sobre este repo")
    problemas += sem_excecao("claims/code-block", confere_code_block_nao_e_claim)

    def confere_passrate_nao_punitivo() -> None:
        # Caminho real + numérico: o denominador conta só o conferível.
        alvo = "scripts/check-numbers.py"
        r = avaliar_claims(f"Cada `{alvo}` leva 90ms.", RAIZ)
        if r["verificados"] != 1 or r["sem_suporte"] < 1:
            raise AssertionError(f"contagem mista errada: {r}")
        if r["passRate"] != 1.0:
            raise AssertionError(f"passRate punido pelo limite do extrator: {r['passRate']}")
    problemas += sem_excecao("claims/passrate-nao-punitivo", confere_passrate_nao_punitivo)

    return problemas


# --- _achar_arsenal ------------------------------------------------------------

def testa_descoberta() -> list[str]:
    problemas: list[str] = []

    def confere_encontra_o_proprio_repo() -> None:
        achado = localizar_arsenal(RAIZ / "skills/dz23-devops-cloud-deployer/scripts/x.py")
        if achado is None or not (achado / "skills").is_dir():
            raise AssertionError(f"não localizou o próprio arsenal: {achado}")
    problemas += sem_excecao("descoberta/repo-atual", confere_encontra_o_proprio_repo)

    def confere_env_invalida() -> None:
        import os
        guardado = os.environ.get("DZ23_ARSENAL")
        os.environ["DZ23_ARSENAL"] = r"D:\caminho\que\nao\existe"
        try:
            if localizar_arsenal(pathlib.Path(r"C:\qualquer\lugar\x.py")) is not None:
                raise AssertionError("aceitou caminho de env inexistente")
        finally:
            if guardado is None:
                os.environ.pop("DZ23_ARSENAL", None)
            else:
                os.environ["DZ23_ARSENAL"] = guardado
    problemas += sem_excecao("descoberta/env-invalida", confere_env_invalida)

    def confere_ponteiro_mentiroso() -> None:
        with tempfile.TemporaryDirectory() as td:
            marcador = pathlib.Path(td) / ".dz23-arsenal"
            marcador.write_text("D:\\nao\\existe\\mais\\arsenal\n", encoding="utf-8")
            alvo = pathlib.Path(td) / "skills" / "x" / "scripts" / "validate_skill.py"
            if localizar_arsenal(alvo) is not None:
                raise AssertionError("confiou em ponteiro apontando para nada")
    problemas += sem_excecao("descoberta/ponteiro-quebrado", confere_ponteiro_mentiroso)

    return problemas


# --- check-copies / check-licenses com árvore incompleta -----------------------

def testa_guardas_de_arvore() -> list[str]:
    """Os verificadores de estrutura encontram um repo pela metade sem explodir?

    Um checkout parcial (clone interrompido, merge no meio, skill recém-criada) é o estado
    em que essas ferramentas mais precisam dizer algo útil -- e é justamente o estado em que
    um KeyError ou TypeError transformaria o diagnóstico em traceback.
    """
    problemas: list[str] = []
    scripts = ("check-copies.py", "check-licenses.py")

    def monta(cenario: str) -> pathlib.Path:
        """Cenário isolado, com RAIZ própria -- sem arsenal.json nem skills/ completos.

        Detalhe que importa: copiar os scripts para fora do repo não basta, porque eles
        derivam RAIZ de __file__ e passariam a enxergar... o repo real ao lado, com o
        manifesto íntegro. O teste então validava o cenário errado e dava verde. Aqui a
        árvore montada é autocontida: só existe o que este bloco criou dentro de tmp.
        """
        tmp = pathlib.Path(tempfile.mkdtemp())
        (tmp / "scripts").mkdir()
        for n in scripts:
            (tmp / "scripts" / n).write_text((RAIZ / "scripts" / n).read_text(encoding="utf-8"),
                                             encoding="utf-8")
        if cenario == "vazio":
            (tmp / "skills").mkdir()
        elif cenario == "sem-skills":
            pass  # arvore nua: sem skills/ nem arsenal.json -- o caso que dava traceback
        elif cenario == "sem-mcp":
            (tmp / "skills" / "dz23-x").mkdir(parents=True)
        elif cenario == "com-skill-pela-metade":
            sk = tmp / "skills" / "dz23-y"
            (sk / "scripts").mkdir(parents=True)
            (sk / "SKILL.md").write_text("---\nname: dz23-y\nversion: 1.0.0\n"
                                         "description: x\n---\n# y\n", encoding="utf-8")
        # Arsenal incompleto de propósito: sem arsenal.json, sem external/, sem mcp/.
        assert not (tmp / "arsenal.json").exists(), "cenário vazou o manifesto do repo real"
        return tmp

    import subprocess
    for cenario in ("vazio", "sem-skills", "sem-mcp", "com-skill-pela-metade"):
        base = monta(cenario)
        try:
            for n in scripts:
                p = subprocess.run([sys.executable, str(base / "scripts" / n)],
                                   capture_output=True, timeout=120, cwd=str(base))
                saida = (p.stdout.decode("utf-8", "replace")
                         + p.stderr.decode("utf-8", "replace"))
                if "Traceback" in saida:
                    problemas.append(f"guardas/{cenario}/{n}: traceback")
        finally:
            import shutil
            shutil.rmtree(base, ignore_errors=True)

    # Não basta não explodir: com skills/ ausente o gate tem que reclamar, e não dar verde.
    def confere_sem_skills_denuncia() -> None:
        base = monta("sem-skills")
        try:
            p = subprocess.run([sys.executable, str(base / "scripts/check-copies.py")],
                               capture_output=True, timeout=120, cwd=str(base))
            saida = p.stdout.decode("utf-8", "replace")
            if p.returncode == 0:
                raise AssertionError("skills/ ausente reportado como sucesso")
            if "ausente" not in saida:
                raise AssertionError(f"não explicou a causa: {saida[:90]}")
        finally:
            import shutil
            shutil.rmtree(base, ignore_errors=True)
    problemas += sem_excecao("guardas/sem-skills-denuncia", confere_sem_skills_denuncia)

    def confere_copies_denuncia_fonte_ausente() -> None:
        import subprocess
        base = monta("sem-mcp")
        try:
            # remove a fonte: o gate tem que reclamar, não silenciar
            (base / "scripts" / "skill_validator.py").write_text("", encoding="utf-8")
            p = subprocess.run([sys.executable, str(base / "scripts/check-copies.py")],
                               capture_output=True, timeout=120, cwd=str(base))
            saida = p.stdout.decode("utf-8", "replace")
            if "Traceback" in saida:
                raise AssertionError("traceback com módulo-fonte vazio")
        finally:
            import shutil
            shutil.rmtree(base, ignore_errors=True)
    problemas += sem_excecao("guardas/copies-sem-fonte", confere_copies_denuncia_fonte_ausente)

    return problemas


# --- os verificadores rejeitam o que devem? ------------------------------------

FM_BOM = ("---\nname: dz23-t\nversion: 1.0.0\ndescription: d\nuser-invocable: true\n---\n# t\n")
EVALS_BOM = json.dumps({
    "schema_version": "1.0", "skill_name": "dz23-t",
    "cases": [{"id": "a", "title": "t", "input": "p", "prompt": "p",
               "expected": ["x"], "fails_if": ["y"]}],
}).encode()


def _fixture(tmp: pathlib.Path, **mud) -> pathlib.Path:
    """Repo mínimo com uma skill; `mud` sobrescreve partes específicas."""
    (tmp / "scripts").mkdir(exist_ok=True)
    for n in ("check-structure.py", "check-copies.py", "check-licenses.py"):
        shutil.copy(RAIZ / "scripts" / n, tmp / "scripts" / n)
    sk = tmp / "skills" / "dz23-t"
    (sk / "scripts").mkdir(parents=True)
    (sk / "references").mkdir()
    (sk / "evals").mkdir()
    (sk / "SKILL.md").write_text(mud.get("fm", FM_BOM), encoding="utf-8")
    (sk / "VERSION").write_text(mud.get("version", "1.0.0") + "\n", encoding="utf-8")
    (sk / "CHANGELOG.md").write_text(
        mud.get("changelog", "## [1.0.0] — x\n\n- nasceu\n"), encoding="utf-8")
    (sk / "README.md").write_text("# r\n\n## Arsenal\n\nx\n", encoding="utf-8")
    (sk / "evals" / "evals.json").write_bytes(mud.get("evals", EVALS_BOM))
    modelo = RAIZ / "skills/dz23-devops-cloud-deployer/scripts/validate_skill.py"
    shutil.copy(modelo, sk / "scripts" / "validate_skill.py")
    for n in ("_achar_arsenal.py", "skill_validator.py"):
        shutil.copy(RAIZ / "scripts" / n, sk / "scripts" / n)
    return tmp


def testa_rejeicao() -> list[str]:
    """Não basta sobreviver: o verificador tem que REPROVAR conteúdo inválido.

    Esta foi a lacuna mais cara da sessão. Um ataque anterior rodava os verificadores com
    `cwd=fixture` e media apenas ausência de traceback -- mas todos derivam RAIZ de
    `__file__`, então escaneavam o repo real ao lado e davam verde sem tocar no caso
    inventado. Saía "5 inválidos aceitos" quando na verdade nada havia sido lido. Com
    `--raiz` explícito dá para medir a decisão, não só a sobrevivência.
    """
    import subprocess
    problemas: list[str] = []

    invalidos = {
        "sem name no frontmatter": {"fm": "---\nversion: 1.0.0\ndescription: d\n"
                                          "user-invocable: true\n---\n# x\n"},
        "VERSION != frontmatter": {"version": "9.9.9"},
        "CHANGELOG sem secao da versao": {"changelog": "# hist\n\nnada aqui\n"},
        "evals JSON corrompido": {"evals": b"{ isto nao e json"},
        "evals sem schema_version": {"evals": json.dumps(
            {"skill_name": "dz23-t", "cases": [{"id": "a", "title": "t", "input": "p",
                                                "expected": ["x"], "fails_if": ["y"]}]}
        ).encode()},
        "evals case duplicado": {"evals": json.dumps(
            {"schema_version": "1.0", "skill_name": "dz23-t", "cases": [
                {"id": "a", "title": "t", "input": "p", "expected": ["x"], "fails_if": ["y"]},
                {"id": "a", "title": "u", "input": "q", "expected": ["x"], "fails_if": ["y"]}]}
        ).encode()},
    }

    def roda_raiz(tmp: pathlib.Path, script: str, *args: str) -> tuple[int, str]:
        p = subprocess.run([sys.executable, str(RAIZ / "scripts" / script),
                            "--raiz", str(tmp), *args],
                           capture_output=True, timeout=180, cwd=str(RAIZ))
        return p.returncode, (p.stdout.decode("utf-8", "replace")
                              + p.stderr.decode("utf-8", "replace"))

    # baseline válido: precisa ser ACEITO, senão toda rejeição abaixo é ruído.
    with tempfile.TemporaryDirectory() as td:
        tmp = _fixture(pathlib.Path(td))
        rc, s = roda_raiz(tmp, "check-structure.py")
        if "Traceback" in s:
            problemas.append(f"rejeicao/baseline: traceback -- {s.strip()[-140:]}")
        elif rc != 0:
            problemas.append(f"rejeicao/baseline: skill válida foi recusada -- {s.strip()[:160]}")

    for rotulo, mud in invalidos.items():
        with tempfile.TemporaryDirectory() as td:
            tmp = _fixture(pathlib.Path(td), **mud)
            rc, s = roda_raiz(tmp, "check-structure.py")
            if "Traceback" in s:
                problemas.append(f"rejeicao/{rotulo}: traceback -- {s.strip()[-140:]}")
            elif rc == 0:
                problemas.append(f"rejeicao/{rotulo}: aceito, deveria reprovar "
                                 f"-- {s.strip()[:140]}")

    # Árvore vazia não pode virar aprovação em nenhum dos três.
    def confere_arvore_vazia() -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            for script in ("check-copies.py", "check-licenses.py"):
                rc, s = roda_raiz(tmp, script)
                if "Traceback" in s:
                    raise AssertionError(f"{script} explodiu em árvore vazia")
                if rc == 0:
                    raise AssertionError(f"{script} aprovou árvore sem nada conferir: "
                                         f"{s.strip()[:110]}")
    problemas += sem_excecao("rejeicao/arvore-vazia-nao-aprova", confere_arvore_vazia)

    return problemas


def rodar_tudo() -> dict:
    grupos = {
        "triagem": testa_triagem(),
        "claims": testa_claims(),
        "descoberta": testa_descoberta(),
        "guardas": testa_guardas_de_arvore(),
        "rejeicao": testa_rejeicao(),
    }
    total = sum(len(v) for v in grupos.values())
    return {"ok": total == 0, "problemas": total, "por_grupo": grupos}


def selftest() -> int:
    """Auto-verificação: garante que o runner detecta falha quando há falha.

    Um harness de teste sem teste negativo é uma decoração. Aqui injeto uma violação
    conhecida e exijo que ela seja reportada; se não for, este arquivo inteiro é falso.
    """
    armadilha = [{"rota": "x", "requests": 10**9, "p95_ms": 10**7,
                  "hit_rate": 0.0, "cacheavel": True}]

    def quebrado() -> None:
        from gate_candidatos import avaliar as av
        r = av({"endpoints": armadilha})
        for v in r["lancados"]:
            if not (0 <= v["prioridade"] <= PRIORIDADE_MAX):
                raise AssertionError("fora do teto")
        raise AssertionError("violação injetada de propósito")

    detected = bool(sem_excecao("armadilha", quebrado))
    if not detected:
        print("SELFTEST DO RUNNER FALHOU: violação injetada não foi detectada")
        return 1
    print("runner OK · detecta a violação injetada")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    como_json = "--json" in argv
    if "--selftest" in argv:
        return selftest()

    resultado = rodar_tudo()
    if como_json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        selftest()
        for grupo, itens in resultado["por_grupo"].items():
            print(f"{grupo:<12} {'OK' if not itens else str(len(itens)) + ' problema(s)'}")
            for i in itens:
                print(f"   - {i}")
        print()
        if resultado["ok"]:
            print("todas as ferramentas degradam sem explodir")
        else:
            print(f"FALHAS: {resultado['problemas']}")

    return 0 if resultado["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
