"""gate_candidatos.py — triagem determinística ANTES de investigar.

Técnica absorvida de vercel-labs/agent-skills (`skills/vercel-optimize/lib/gates/*.mjs`,
lido 2026-11-17). O princípio: a decisão de "isto merece investigação" não pode ser
julgamento de LLM. É uma função pura sobre sinais já coletados, que devolve o mesmo
resultado byte-idêntico para a mesma entrada, com o threshold escrito como expressão —
não como "parece lento".

O arsenal tinha baseline e veredito DEPOIS do trabalho (master-engineer, autonomous),
mas nada filtrando ANTES do primeiro passo. Consequência observável: um `/goal` de
melhoria começa varrendo o que é chamativo, não o que é gargalo.

Cada gate devolve `lançado` ou `contido` com o motivo numérico. Um candidato contido não
desaparece: vai para a lista "considerado e não agiu, por quê", que é o que impede o
relatório de parecer omitente (outra peça roubada do mesmo pacote).

Uso:
    python scripts/gate_candidatos.py --sinais sinais.json          # legível
    python scripts/gate_candidatos.py --sinais sinais.json --json   # máquina
    python scripts/gate_candidatos.py --selftest                    # controle + negativo

Formato de sinais.json (só o que o gate olha; ausente = não avaliável, nunca "zero"):
{
  "endpoints": [
    {"rota": "GET /pedidos", "requests": 1200, "p95_ms": 900, "hit_rate": 0.2,
     "cacheavel": true}
  ],
  "benchmarks": [
    {"nome": "home", "metrica": "LCP", "medido": 3400, "budget": 2500, "amostras": 20}
  ],
  "tabelas": [
    {"nome": "pedidos", "linhas": 4_000_000, "sem_indice_em": ["cliente_id"],
     "consultas_por_min": 800}
  ]
}
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Mudou um threshold? Sobe a versão. Sem isso, dois relatórios com números diferentes
# não dizem se o código mudou ou se os dados mudaram.
GATE_VERSION = "1.0.0"

MAX_CANDIDATOS = 6


@dataclass
class Veredicto:
    id: str
    gate: str
    lancado: bool
    prioridade: int          # maior = mais urgente
    motivo: str              # a comparação numérica que decidiu
    evidencia: dict = field(default_factory=dict)


def _falta(valor) -> bool:
    """Ausência não é zero. Tratar sinal faltante como 0 lançaria gate por ignorância."""
    return valor is None


# --- gates ---------------------------------------------------------------------

def gate_rota_quente_sem_cache(ep: dict) -> Veredicto | None:
    """Rota cara, frequente e cacheável. Threshold como expressão, não adjetivo."""
    r, p95, hr, cache = (ep.get("requests"), ep.get("p95_ms"),
                         ep.get("hit_rate"), ep.get("cacheavel"))
    if any(_falta(x) for x in (r, p95, hr)) or not cache:
        return None
    lancado = r > 500 and p95 > 400 and hr < 0.5
    return Veredicto(
        id=f"rota:{ep.get('rota', '?')}", gate="rota-quente-sem-cache", lancado=lancado,
        prioridade=min(r // 100, 50) + (p95 // 100),
        motivo=(f"requests={r} (>500) e p95={p95}ms (>400) e hit_rate={hr} (<0.5) "
                f"e cacheavel=true"),
        evidencia={"rota": ep.get("rota"), "requests": r, "p95_ms": p95, "hit_rate": hr},
    )


def gate_budget_estourado(b: dict) -> Veredicto | None:
    """Métrica de front acima do budget com amostra suficiente para acreditar."""
    medido, budget, n = b.get("medido"), b.get("budget"), b.get("amostras")
    if any(_falta(x) for x in (medido, budget, n)):
        return None
    if n < 10:
        return Veredicto(id=f"bench:{b.get('nome', '?')}:{b.get('metrica', '?')}",
                         gate="budget-estourado", lancado=False, prioridade=0,
                         motivo=f"amostras={n} (<10): sem base para afirmar desvio",
                         evidencia=b)
    estouro = (medido - budget) / budget if budget else 0
    lancado = estouro >= 0.20
    return Veredicto(
        id=f"bench:{b.get('nome', '?')}:{b.get('metrica', '?')}", gate="budget-estourado",
        lancado=lancado, prioridade=int(estouro * 100),
        motivo=f"{b.get('metrica')}={medido} vs budget={budget} ({estouro:+.0%}) "
               f"em {n} amostras; limiar 20%",
        evidencia=b)


def gate_tabela_grande_sem_indice(t: dict) -> Veredicto | None:
    """Tabela grande, consultada muito e sem índice na coluna usada no filtro."""
    linhas, sem_idx, qpm = t.get("linhas"), t.get("sem_indice_em"), t.get("consultas_por_min")
    if _falta(linhas) or _falta(qpm) or not sem_idx:
        return None
    lancado = linhas > 1_000_000 and qpm > 100
    return Veredicto(
        id=f"tabela:{t.get('nome', '?')}", gate="tabela-grande-sem-indice",
        lancado=lancado, prioridade=min(qpm // 50, 40) + min(linhas // 1_000_000, 20),
        motivo=f"linhas={linhas} (>1M) e consultas={qpm}/min (>100) e sem índice em "
               f"{list(sem_idx)}",
        evidencia=t)


GATES = {
    "rota-quente-sem-cache": ("endpoints", gate_rota_quente_sem_cache),
    "budget-estourado": ("benchmarks", gate_budget_estourado),
    "tabela-grande-sem-indice": ("tabelas", gate_tabela_grande_sem_indice),
}


def avaliar(sinais: dict) -> dict:
    """Roda todos os gates sobre os sinais. Função pura: mesma entrada, mesma saída."""
    lancados: list[Veredicto] = []
    contidos: list[Veredicto] = []
    nao_avaliaveis: list[str] = []

    for nome, (chave, fn) in GATES.items():
        itens = sinais.get(chave)
        if itens is None:
            nao_avaliaveis.append(f"{nome}: sinal '{chave}' ausente — gate não avaliado")
            continue
        for item in itens:
            v = fn(item)
            if v is None:
                nao_avaliaveis.append(f"{nome}: item sem campos suficientes — não avaliado")
            elif v.lancado:
                lancados.append(v)
            else:
                contidos.append(v)

    lancados.sort(key=lambda v: (-v.prioridade, v.id))
    escolhidos = lancados[:MAX_CANDIDATOS]
    adiados = lancados[MAX_CANDIDATOS:]

    return {
        "gate_version": GATE_VERSION,
        "lancados": [asdict(v) for v in escolhidos],
        "adiados_por_limite": [asdict(v) for v in adiados],
        "contidos": [asdict(v) for v in contidos],
        "nao_avaliaveis": nao_avaliaveis,
        "resumo": (f"{len(escolhidos)} lançado(s), {len(adiados)} adiado(s) por limite de "
                   f"{MAX_CANDIDATOS}, {len(contidos)} contido(s), "
                   f"{len(nao_avaliaveis)} não avaliável(is)"),
    }


# --- auto-teste: controle positivo E negativo -----------------------------------
def selftest() -> int:
    falhas: list[str] = []

    def espera(cond: bool, msg: str):
        if not cond:
            falhas.append(msg)

    bons = {
        "endpoints": [{"rota": "GET /pedidos", "requests": 1200, "p95_ms": 900,
                       "hit_rate": 0.2, "cacheavel": True}],
        "benchmarks": [{"nome": "home", "metrica": "LCP", "medido": 3400,
                        "budget": 2500, "amostras": 20}],
        "tabelas": [{"nome": "pedidos", "linhas": 4_000_000,
                     "sem_indice_em": ["cliente_id"], "consultas_por_min": 800}],
    }
    r = avaliar(bons)
    espera(len(r["lancados"]) == 3, f"controle positivo: esperava 3 lançados, veio {len(r['lancados'])}")

    # Negativo: mesmos dados abaixo do limiar NÃO podem lançar.
    maus = {
        "endpoints": [{"rota": "GET /ping", "requests": 40, "p95_ms": 12,
                       "hit_rate": 0.99, "cacheavel": True}],
        "benchmarks": [{"nome": "home", "metrica": "LCP", "medido": 2400,
                        "budget": 2500, "amostras": 30}],
        "tabelas": [{"nome": "config", "linhas": 12, "sem_indice_em": ["k"],
                     "consultas_por_min": 3}],
    }
    rn = avaliar(maus)
    espera(not rn["lancados"], "controle negativo: lançou algo que não devia")
    espera(len(rn["contidos"]) == 3, "controle negativo: deveria registrar 3 contidos")

    # Ausência de sinal não vira zero nem lançamento silencioso.
    rv = avaliar({})
    espera(len(rv["nao_avaliaveis"]) == 3, "sinaus ausentes deveriam marcar não-avaliável")
    espera(not rv["lancados"], "sem dados não pode lançar")

    # Determinismo: mesma entrada, saída idêntica.
    espera(json.dumps(avaliar(bons), sort_keys=True) == json.dumps(avaliar(bons), sort_keys=True),
           "gate não é determinístico")

    # Amostra pequena segura o lançamento (Goodhart guard).
    rp = avaliar({"benchmarks": [{"nome": "x", "metrica": "INP", "medido": 9000,
                                  "budget": 200, "amostras": 3}]})
    espera(not rp["lancados"], "3 amostras não deveriam lançar")

    if falhas:
        print("SELFTEST FALHOU:")
        for f in falhas:
            print("  -", f)
        return 1
    print(f"selftest OK · gate_version {GATE_VERSION} · "
          f"positivo/negativo/vazio/determinismo/amostra-pobre")
    return 0


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--sinais", help="JSON com os sinais coletados")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.sinais:
        print("use --sinais <arquivo.json> ou --selftest", file=sys.stderr)
        return 2

    caminho = Path(args.sinais)
    if not caminho.is_file():
        print(f"FALHA: {caminho} não existe", file=sys.stderr)
        return 2
    try:
        sinais = json.loads(caminho.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        print(f"FALHA: {caminho} ilegível: {exc}", file=sys.stderr)
        return 2

    resultado = avaliar(sinais)

    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return 0

    print(f"# Triagem de candidatos (gates {GATE_VERSION})\n")
    print(f"{resultado['resumo']}\n")
    if resultado["lancados"]:
        print("## Investigar (nesta ordem)\n")
        for i, v in enumerate(resultado["lancados"], 1):
            print(f"{i}. `{v['id']}` [{v['gate']}] prioridade {v['prioridade']}")
            print(f"   {v['motivo']}")
    if resultado["adiados_por_limite"]:
        print("\n## Adiados pelo limite de atenção\n")
        for v in resultado["adiados_por_limite"]:
            print(f"- `{v['id']}` [{v['gate']}] prioridade {v['prioridade']}")
    if resultado["contidos"]:
        print("\n## Considerado e não agiu, por quê\n")
        for v in resultado["contidos"]:
            print(f"- `{v['id']}` [{v['gate']}]: {v['motivo']}")
    if resultado["nao_avaliaveis"]:
        print("\n## Não avaliável (falta sinal — não é 'sem problema')\n")
        for n in resultado["nao_avaliaveis"]:
            print(f"- {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
