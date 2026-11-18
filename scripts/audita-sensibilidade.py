"""Audita os VERIFICADORES com a regra da rodada 43: cada um sabe ficar vermelho?

prova-verificadores.py cobre os flags --check. Este script cobre o resto: para cada verificador do
gate, injetar uma violacao no dominio que ele enuncia e exigir exit != 0. Um verificador que so
sabe dizer OK quando esta verde e uma afirmativa decorada -- foi assim que check-links, check-licenses
e check-copies aprovavam arvore vazia, e que build.py --check nao comparava nada.

Nasce da regra da rodada 43: verificar o verde nao basta, e preciso verificar que o verde saberia
ficar vermelho. Aplicada aos verificadores do gate, nao apenas as alegacoes do CHANGELOG.

Duas das primeiras execucoes acusaram verificadores ocos que nao existiam. Eu apaguei o LICENSE da
raiz -- que o check-licenses nem olha, pois ele percorre mcp/ e bundle/ -- e reescrevi
'Total pendente 99' quando o ROADMAP traz a forma de tabela '**Total pendente** | **99**'. As
violacoes simplesmente nao casavam com nada. Um verificador aprovado por violacao imaginaria e tao
inutil quanto um oco: por isso cada mutacao abaixo precisa produzir diferenca real, e um caso sem
mutacao eficaz e reportado como nao medido, nunca como OK.

Tudo em copia temporaria; o repo nunca e tocado.
"""
import json
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
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def base_completa() -> pathlib.Path:
    """Copia o repo sem artefatos pesados, preservando o que os verificadores leem."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    keep = ("scripts", "skills", "docs", "external", "cli", "prompts", "evals-results",
            "audit-results", "audit-package", ".github", "bundle", "mcp", "dados-design")
    for n in keep:
        p = RAIZ / n
        if not p.is_dir():
            continue
        shutil.copytree(p, tmp / n, symlinks=False,
                        ignore=shutil.ignore_patterns("node_modules", "__pycache__"))
    for f in ("README.md", "ROADMAP.md", "CHANGELOG.md", "CONTRIBUTING.md", "INDEX.md",
              "arsenal.json", "LICENSE", "SECURITY.md", "CODE_OF_CONDUCT.md", "VERSION",
              ".gitattributes", ".gitignore", "evals.schema.json"):
        if (RAIZ / f).is_file():
            shutil.copy2(RAIZ / f, tmp / f)
    return tmp


def _impressao(base: pathlib.Path) -> str:
    """Assinatura por CONTEUDO SEMANTICO dos arquivos da copia.

    Dois detalhes que custaram uma guarda ineficaz cada:

    1. Não usar tamanho+mtime: uma violação imaginária faz `write_text(texto)` com o texto
       inalterado, o arquivo é reescrito, o mtime muda e a comparação diria "mudou algo".
    2. Não hashear bytes crus: `Path.write_text` aplica newline universal, então reescrever um
       arquivo que no disco tem CRLF converte tudo para LF -- os bytes mudam (medido: 15345 para
       15559 num ROADMAP com 214 linhas) sem nenhuma alteração pretendida. A assinatura precisa
       ignorar exatamente essa diferença, como já acontece em todo o resto do arsenal (EOL nunca
       é divergência de conteúdo -- ver audit-zips e build.py --check). Por isso o hash é feito
       sobre o texto com quebras de linha normalizadas.
    """
    import hashlib
    partes = []
    for f in sorted(base.rglob("*")):
        if not f.is_file() or "__pycache__" in f.parts:
            continue
        try:
            bruto = f.read_bytes()
        except OSError:
            continue
        try:
            texto = bruto.decode("utf-8")
        except UnicodeDecodeError:
            digest = hashlib.sha256(bruto).hexdigest()[:16]      # binario: bytes mesmo
        else:
            digest = hashlib.sha256(
                texto.replace("\r\n", "\n").encode("utf-8")).hexdigest()[:16]
        partes.append(f"{f.relative_to(base)}:{digest}")
    return "|".join(partes)


def roda(base: pathlib.Path, *args, cwd=None):
    p = subprocess.run([PY, *map(str, args)], capture_output=True, cwd=str(cwd or base),
                       timeout=600)
    out = (p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")).strip()
    return p.returncode, out


def _viola_pendente(base: pathlib.Path) -> None:
    """Troca o valor REAL de 'Total pendente' por outro, sem assumir qual ele é.

    A versão anterior gravava o dígito 99 no regex, e na rodada seguinte à execução do primeiro
    eval de postgres o número passou a ser 98 -- a substituição não casou, nenhum arquivo mudou,
    e a guarda anti-violação-imaginária reportou 'medição vazia'. O bug era da lente, não do
    verificador: violação com valor fixo vence o tempo uma vez e apodrece depois. Ler o valor
    atual e escrever um diferente é o que torna a prova durável.
    """
    alvo = base / "ROADMAP.md"
    texto = alvo.read_text(encoding="utf-8")
    m = re.search(r"(\*\*Total pendente\*\*\s*\|\s*\*\*)(\d+)(\*\*)", texto)
    if not m:
        raise AssertionError("ROADMAP sem célula 'Total pendente' para violar")
    atual = int(m.group(2))
    novo = atual - 1 if atual > 1 else atual + 7
    alvo.write_text(texto[:m.start()] + m.group(1) + str(novo) + m.group(3)
                    + texto[m.end():], encoding="utf-8")


CASOS = {
    "check-structure": ("scripts/check-structure.py", lambda b: (
        (b / "skills/dz23-postgres-prod-preflight/VERSION").write_text("9.9.9\n", encoding="utf-8"))),
    "check-copies": ("scripts/check-copies.py", lambda b: (
        b / "skills/dz23-e2e-browser-verifier/scripts/skill_validator.py").write_bytes(
        (b / "skills/dz23-e2e-browser-verifier/scripts/skill_validator.py").read_bytes()
        + b"\n# drift\n")),
    "check-numbers": ("scripts/check-numbers.py", lambda b: (
        b / "README.md").write_text((b / "README.md").read_text(encoding="utf-8").replace(
        "Coleção de 15 skills", "Coleção de 7 skills"), encoding="utf-8")),
    "check-licenses": ("scripts/check-licenses.py", lambda b: [
        # A licenca do REPOSITORIO (LICENSE na raiz) nao e o que ele confere: as linhas 141-160
        # percorrem componentes em mcp/ e bundle/. Apagar a raiz, como eu fiz na primeira
        # versao desta auditoria, nao viola nada -- e um verificador aprovado por violacao
        # imaginaria e exatamente o tipo de erro que esta sessao vem caçando.
        (p.rename(str(p) + "_bak") or True)
        for p in (b / "bundle/dz23-dsh-agency/LICENSE",
                  b / "mcp/dz23-subagents-universal-mcp/LICENSE") if p.is_file()]),
    "check-links": ("scripts/check-links.py .", lambda b: (
        b / "README.md").write_bytes(b"Veja [x](docs/nao-existe-zz.md).\n"
                                     + (b / "README.md").read_bytes())),
    "check-docs-runnable": ("scripts/check-docs-runnable.py", lambda b: (
        b / "CONTRIBUTING.md").write_bytes(b"\n```bash\npython scripts/zz-inexistente.py\n```\n"
                                           + (b / "CONTRIBUTING.md").read_bytes())),
    "check-eval-results": ("scripts/check-eval-results.py", lambda b: _viola_pendente(b)),
    "checa-ancoras": ("scripts/checa-ancoras.py", lambda b: (
        b / "CHANGELOG.md").write_text(re.sub(r"(?m)^(## \[)(\d+\.\d+\.\d+)(\])",
                                              r"\g<1>0.0.1\g<3>",
                                              (b / "CHANGELOG.md").read_text(encoding="utf-8"),
                                              count=1), encoding="utf-8")),
    # Injecao literal fixa ("| 1.1.1 | Explora") apontava para a versao que a cartographer carregava
    # quando este caso foi escrito; o bump 1.1.1 -> 1.2.0 tornou o re.sub um no-op e o auditador
    # reportou SETUP!/medicao vazia -- corretamente, porque nada mudou conteudo. Agora a violacao
    # localiza a linha pelo nome da skill e troca a versao que ela de fato tem, entao sobrevive a
    # qualquer bump futuro em vez de quebrar no proximo.
    "gera-indice-skills": ("scripts/gera-indice-skills.py --check", lambda b: (
        _violar_indice_cartografo(b))),
}


def _violar_indice_cartografo(base):
    p = base / "skills/README.md"
    texto = p.read_text(encoding="utf-8")
    m = re.search(r"(?m)^\| \[codebase-cartographer\]\([^\)]*\) \| (\d+\.\d+\.\d+) \|", texto)
    if not m:
        raise AssertionError("linha da cartographer nao encontrada no indice")
    p.write_text(texto.replace(m.group(0), m.group(0).replace(m.group(1), "0.0.1"), 1),
                 encoding="utf-8")

print("=== cada verificador sabe ficar vermelho? ===")
ocos, falhas_setup = [], []
for nome, (cmd, mut) in CASOS.items():
    base = base_completa()
    try:
        rc_ok, _ = roda(base, *cmd.split())
        if rc_ok != 0:
            falhas_setup.append(f"{nome}: baseline ja vermelho na copia (exit {rc_ok})")
            print(f"  PULADO  {nome:<22} baseline vermelho na copia")
            continue
        antes = _impressao(base)
        try:
            mut(base)
        except Exception as exc:  # noqa: BLE001
            falhas_setup.append(f"{nome}: nao consegui aplicar a violacao ({type(exc).__name__})")
            print(f"  SETUP!  {nome:<22} {type(exc).__name__}")
            continue
        if _impressao(base) == antes:
            # Violacao imaginaria: nenhum arquivo mudou CONTEUDO, entao um exit 0 do verificador
            # nao diz nada sobre ele. Foi assim que duas execucoes desta auditoria acusaram
            # verificadores ocos inexistentes -- apaguei um LICENSE que o check-licenses nem le e
            # reescrevi um texto que o ROADMAP guarda em formato de tabela.
            falhas_setup.append(f"{nome}: a violacao nao alterou conteudo algum (medicao vazia)")
            print(f"  SETUP!  {nome:<22} violacao sem efeito")
            continue
        rc_bad, s = roda(base, *cmd.split())
        if rc_bad == 0:
            ocos.append(nome)
            print(f"  OCO     {nome:<22} aprovou a violacao :: {s.splitlines()[-1][:80] if s else ''}")
        else:
            motivo = [l.strip()[:88] for l in s.splitlines() if l.strip()][-1:]
            print(f"  OK      {nome:<22} reprova :: {(motivo[0] if motivo else '')}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

print("\n" + "=" * 62)
if ocos or falhas_setup:
    if ocos:
        print(f"{len(ocos)} verificador(es) OCO(S): {ocos}")
    if falhas_setup:
        print(f"{len(falhas_setup)} caso(s) nao medidos:")
        for f in falhas_setup:
            print("   -", f)
    sys.exit(1)
print("todos os verificadores sabem ficar vermelhos no dominio que enunciam")
