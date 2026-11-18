"""_tracks.py — fonte única do mapa skill ↔ pasta de registros.

Existiam três cópias deste dicionário (run-evals.py, check-eval-results.py,
record-eval.py). Quando `dz23-postgres-prod-preflight` entrou no arsenal, nenhuma foi
atualizada: `record-eval.py` criava a pasta com o nome longo e `check-eval-results.py`
rejeitava como "pasta não mapeada" — um beco sem saída que travava justamente a skill
com 0 de 13 evals executados.

Agora o mapa é derivado do disco. Uma skill nova entra sozinha, no momento em que o
diretório aparece em `skills/`.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = RAIZ / "skills"

# Apelidos fixos, por legibilidade dos caminhos em evals-results/. Qualquer skill sem
# entrada aqui recebe um apelido derivado do nome, de forma determinística.
APELIDOS = {
    "dz23-autonomous-improvement-ultimate": "autonomous",
    "dz23-backend-data-architect": "backend",
    "dz23-codebase-cartographer": "cartographer",
    "dz23-devops-cloud-deployer": "devops",
    "dz23-e2e-browser-verifier": "e2e",
    "dz23-performance-scalability-engine": "performance",
    "dz23-postgres-prod-preflight": "postgres",
    "dz23-reverse-engineer-anything": "reverse-engineer",
    "dz23-spec-to-system-engine": "spec",
    "dz23-ultimate-pro-max": "ultimate-pro-max",
}


def _apelido(name: str) -> str:
    if name in APELIDOS:
        return APELIDOS[name]
    # Fallback determinístico: tira o prefixo dz23- e encurta. Não precisa ser bonito,
    # precisa ser estável — o apelido vira nome de pasta versionado.
    base = re.sub(r"^dz23-", "", name)
    return base[:24]


@lru_cache(maxsize=1)
def skills_no_disco() -> tuple[str, ...]:
    return tuple(sorted(p.name for p in SKILLS.iterdir() if p.is_dir()))


@lru_cache(maxsize=1)
def para_apelido() -> dict[str, str]:
    """skill completa → apelido de pasta."""
    return {name: _apelido(name) for name in skills_no_disco()}


@lru_cache(maxsize=1)
def para_skill() -> dict[str, str]:
    """apelido de pasta → skill completa (inverso de `para_apelido`)."""
    return {v: k for k, v in para_apelido().items()}


if __name__ == "__main__":  # smoke test rápido
    pa, ps = para_apelido(), para_skill()
    assert len(pa) == len(ps), "mapas não são inversos um do outro"
    for skill, cur in pa.items():
        assert ps[cur] == skill, f"round-trip falhou em {skill}"
    print(f"{len(pa)} skills mapeadas:")
    for skill, cur in sorted(pa.items()):
        print(f"  {skill:<42} {cur}")
