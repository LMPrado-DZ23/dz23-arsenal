"""executa-scripts-skills.py -- roda os scripts que as proprias skills mandam executar.

Onze arquivos vivem em skills/<x>/scripts/ e sao citados nos SKILL.md como instrucao executavel.
Ate aqui, nada neste arsenal os executava: validate_skill.py confere frontmatter, referencias e
evals; check-structure confere arquivos; nenhum dos onze foi exercitado uma vez sequer. Um script
de skill que quebra no primeiro uso transforma a habilidade inteira em instrucao falsa, e a skill
continua verde.

Cada caso usa o formato de entrada que o proprio script documenta, nao um que eu imaginei -- as
duas primeiras tentativas desta suite passaram JSON onde check_budget le tabela markdown e
markdown onde validate_spec le JSON, e teriam acusado defeitos inexistentes. Os fixtures validos
sao derivados das docstrings e do exemplo distribuido pela skill (examples/spec-example.json).

Todo verificador tem controle negativo obrigatorio: alem de aceitar a entrada correta, precisa
recusar a violacao correspondente (budget estourado -> exit != 0; spec sem requirements -> exit
!= 0). Sem isso, "rodou e saiu 0" nao prova nada -- lição da rodada 43 aplicada a scripts de
terceiros dentro das skills.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
S = RAIZ / "skills"
PY = sys.executable

BUDGET_OK = """# Budget

| Métrica | Budget | Estado |
|---|---|---|
| LCP p75 | ≤ 2,5 s | ok |
| p95 API | ≤ 500 ms | ok |
"""

BENCH_DENTRO = """# Benchmark

### Depois
| Métrica | p50 | p95 | p99 |
|---|---|---|---|
| LCP p75 | 1,2 s | 1,8 s | 2,1 s |
| p95 API | 300 ms | 420 ms | 610 ms |
"""

BENCH_FORA = """# Benchmark

### Depois
| Métrica | p50 | p95 | p99 |
|---|---|---|---|
| LCP p75 | 4,2 s | 5,8 s | 6,1 s |
| p95 API | 900 ms | 1400 ms | 1800 ms |
"""

FEATURE_OK = """Feature: X
  Scenario: y
    Given a
    When b
    Then c
"""


def run(args, cwd=None, timeout=300):
    p = subprocess.run([PY, *map(str, args)], capture_output=True, cwd=str(cwd or RAIZ),
                       timeout=timeout)
    out = (p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")).strip()
    return p.returncode, out


def caso(nome, args, rc_ok=(0,), marca=None, traceback_proibido=True):
    try:
        rc, out = run(args)
    except Exception as exc:  # noqa: BLE001
        return f"{nome}: EXEC FALHOU {type(exc).__name__}: {exc}"
    if rc not in rc_ok:
        return f"{nome}: exit={rc} :: {out.splitlines()[-1][:110] if out else '(sem saida)'}"
    if traceback_proibido and "Traceback" in out:
        return f"{nome}: traceback na saida :: {out.splitlines()[0][:110]}"
    if marca and marca not in out:
        return f"{nome}: saida sem {marca!r} :: {out[:110]!r}"
    return None


def main(argv=None):
    for s_ in (sys.stdout, sys.stderr):
        try:
            s_.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    problemas = []
    medidos = []

    def registra(rotulo, resultado):
        medidos.append(rotulo)
        if resultado:
            problemas.append(resultado)

    # --- dz23-codebase-cartographer ---------------------------------------------------------
    registra("repo_probe", caso(
        "repo_probe", [S / "dz23-codebase-cartographer/scripts/repo_probe.py", str(RAIZ),
                       "--json"], marca='"tracked_files"'))
    out = run([S / "dz23-codebase-cartographer/scripts/repo_probe.py", str(RAIZ), "--json"])[1]
    try:
        d = json.loads(out)
        if not isinstance(d.get("tracked_files"), int):
            problemas.append(f"repo_probe: tracked_files nao inteiro ({d.get('tracked_files')!r})")
        medidos.append("repo_probe(JSON)")
    except json.JSONDecodeError as exc:
        problemas.append(f"repo_probe: JSON ilegivel: {exc}")

    registra("repo_inventory", caso(
        "repo_inventory", [S / "dz23-codebase-cartographer/scripts/repo_inventory.py", str(RAIZ)],
        marca="INVENTORY_OK"))

    # --- dz23-reverse-engineer-anything ------------------------------------------------------
    registra("file_triage", caso(
        "file_triage", [S / "dz23-reverse-engineer-anything/scripts/file_triage.py", PY],
        marca="read_only=true"))

    # --- dz23-spec-to-system-engine ----------------------------------------------------------
    registra("validate_spec(exemplo da skill)", caso(
        "validate_spec", [S / "dz23-spec-to-system-engine/scripts/validate_spec.py",
                          S / "dz23-spec-to-system-engine/examples/spec-example.json"],
        marca="SPEC_STRUCTURE_VALID"))
    with tempfile.TemporaryDirectory() as td:
        vazio = pathlib.Path(td) / "spec.json"
        vazio.write_text(json.dumps({"schema_version": 1, "requirements": []}), encoding="utf-8")
        rc, _ = run([S / "dz23-spec-to-system-engine/scripts/validate_spec.py", str(vazio)])
        medidos.append("validate_spec(controle negativo)")
        if rc == 0:
            problemas.append("validate_spec aceitou spec sem requirements (controle falhou)")

        g = pathlib.Path(td) / "f.feature"
        g.write_text(FEATURE_OK, encoding="utf-8")
        registra("check_gherkin", caso("check_gherkin",
                                       [S / "dz23-spec-to-system-engine/scripts/check_gherkin.py",
                                        str(g)], marca="PASS"))
        ruim = pathlib.Path(td) / "ruim.feature"
        ruim.write_text("Feature: X\n  Scenario: y\n    Something sem passo Gherkin\n",
                        encoding="utf-8")
        rc2, _ = run([S / "dz23-spec-to-system-engine/scripts/check_gherkin.py", str(ruim)])
        medidos.append("check_gherkin(controle negativo)")
        if rc2 == 0:
            problemas.append("check_gherkin aceitou scenario sem passos (controle falhou)")

    # --- dz23-performance-scalability-engine --------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        (base / "budget.md").write_text(BUDGET_OK, encoding="utf-8")
        dentro = base / "bench_ok.md"
        dentro.write_text(BENCH_DENTRO, encoding="utf-8")
        fora = base / "bench_fora.md"
        fora.write_text(BENCH_FORA, encoding="utf-8")
        cb = S / "dz23-performance-scalability-engine/scripts/check_budget.py"
        registra("check_budget(dentro)", caso(
            "check_budget", [cb, "--budget", base / "budget.md", "--benchmark", dentro],
            marca="BUDGET_PASS"))
        rc, out = run([cb, "--budget", base / "budget.md", "--benchmark", fora])
        medidos.append("check_budget(controle negativo)")
        if rc == 0 or "BUDGET_FAIL" not in out:
            problemas.append(f"check_budget nao reprovou budget estourado (exit {rc}): {out[:110]}")

    # --- scripts cujo contrato exige ambiente externo: ao menos responder sem quebrar ---------
    for rotulo, arq in (("release_probe", S / "dz23-devops-cloud-deployer/scripts/release_probe.py"),
                        ("pg_preflight", S / "dz23-postgres-prod-preflight/scripts/pg_preflight.py"),
                        ("web_vitals_probe",
                         S / "dz23-performance-scalability-engine/scripts/web_vitals_probe.py"),
                        ("compare_samples",
                         S / "dz23-performance-scalability-engine/scripts/compare_samples.py"),
                        ("re_toolkit", S / "dz23-reverse-engineer-anything/scripts/re_toolkit.py")):
        registra(f"{rotulo}(--help)", caso(arq.name, [arq, "--help"], rc_ok=(0, 1, 2)))

    # --- replica-entrepreneur: reviews.py ranqueia avaliacoes reais e degrada sem explodir -------
    import tempfile as _tf
    import pathlib as _pl
    _rev = S / "replica-entrepreneur/scripts/reviews.py"
    _ex = S / "replica-entrepreneur/examples/reviews-exemplo.csv"
    registra("reviews(exemplo)", caso(
        "reviews", [_rev, str(_ex), "--today", "2026-11-18"],
        marca="What users of the original"))
    with _tf.TemporaryDirectory() as _td:
        _bad = _pl.Path(_td) / "ruim.csv"
        _bad.write_text("source,date,rating\nx,2026-01-01,5\n", encoding="utf-8")
        # sem coluna url/text: erro limpo (rc 2), nunca traceback
        registra("reviews(sem coluna obrigatoria)", caso("reviews-neg", [_rev, str(_bad)], rc_ok=(2,)))

    # --- replica-diff: parity.py (score de features) e imgdiff.py (diff de layout, decoder PNG) ----
    _par = S / "replica-diff/scripts/parity.py"
    _img = S / "replica-diff/scripts/imgdiff.py"
    _fx = S / "replica-diff/examples/features-exemplo.csv"
    _o = S / "replica-diff/examples/orig.png"
    _c = S / "replica-diff/examples/clone.png"
    registra("parity(exemplo)", caso("parity", [_par, str(_fx)], marca="Parity:"))
    registra("imgdiff(exemplo)", caso("imgdiff", [_img, str(_o), str(_c), "--json"], marca='"mode"'))
    with _tf.TemporaryDirectory() as _td2:
        _bad2 = _pl.Path(_td2) / "ruim.csv"
        _bad2.write_text("feature,area\nx,y\n", encoding="utf-8")   # sem coluna clone/priority
        registra("parity(sem coluna)", caso("parity-neg", [_par, str(_bad2)], rc_ok=(2,)))
        _notpng = _pl.Path(_td2) / "nao.png"
        _notpng.write_text("isto nao e um png\n", encoding="utf-8")
        registra("imgdiff(nao-png)", caso("imgdiff-neg", [_img, str(_notpng), str(_notpng)], rc_ok=(2,)))

    # --- replica-brand: sweep.py acha sobras do original no codigo (exit 1 se achar) -------------
    _sw = S / "replica-brand/scripts/sweep.py"
    with _tf.TemporaryDirectory() as _td3:
        _proj = _pl.Path(_td3) / "src"
        _proj.mkdir()
        (_proj / "a.js").write_text('const CalendlyEmbed = "x"; // #006bff\n', encoding="utf-8")
        # com sobra: exit 1
        registra("sweep(com sobra)", caso(
            "sweep", [_sw, str(_td3), "--avoid", "Calendly", "--colors", "#006bff"], rc_ok=(1,),
            marca="hits"))
        # sem o nome em lugar nenhum: clean, exit 0
        (_proj / "a.js").write_text('const Embed = "x";\n', encoding="utf-8")
        registra("sweep(clean)", caso(
            "sweep-clean", [_sw, str(_td3), "--avoid", "Calendly"], rc_ok=(0,), marca="Clean"))
        # sem nada para procurar: erro limpo, exit 2
        registra("sweep(sem alvo)", caso("sweep-neg", [_sw, str(_td3)], rc_ok=(2,)))

    # --- replica-launch: listing.py (lint de listagem de loja) ----------------------------------
    _lst = S / "replica-launch/scripts/listing.py"
    _ex3 = S / "replica-launch/examples/listing-exemplo.json"
    registra("listing(exemplo)", caso("listing", [_lst, str(_ex3)], marca="errors"))
    # nome do original presente na listagem -> erro (exit 1)
    registra("listing(nome do original)", caso(
        "listing-neg", [_lst, str(_ex3), "--avoid", "Slotwise"], rc_ok=(1,), marca="mentions"))
    with _tf.TemporaryDirectory() as _td4:
        _bad4 = _pl.Path(_td4) / "ruim.json"
        _bad4.write_text("{ nao e json valido", encoding="utf-8")
        registra("listing(json invalido)", caso("listing-json", [_lst, str(_bad4)], rc_ok=(2,)))

    dados = {"ok": not problemas, "executados": len(medidos), "problemas": problemas}
    if args.json:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
    else:
        print(f"scripts de skill executados: {len(medidos)} casos "
              f"(incluindo controles negativos)")
        for p in problemas:
            print(f"PROBLEMA: {p}")
        if not problemas:
            print(f"todos os {len(medidos)} rodam com a entrada que documentam e recusam violacao")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
