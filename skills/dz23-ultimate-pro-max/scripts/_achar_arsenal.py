"""_achar_arsenal.py — encontrado do checkout do arsenal a partir de uma skill.

Copiado para scripts/ de cada skill pelo install-all, porque a skill instalada em
~/.agents/skills precisa localizar o repo (que pode estar em outro disco) para rodar as
checagens comuns. Contar níveis de diretório falha nesse caso: `parents[3]` a partir da
instalação aponta para ~/.agents, que não tem o validador compartilhado.
"""
from __future__ import annotations

import os
from pathlib import Path


def localizar_arsenal(comeco: Path) -> Path | None:
    """Retorna a raiz do checkout do arsenal, ou None se não for localizável.

    Ordem: subir a árvore procurando o par scripts/skill_validator.py + skills/; depois
    o ponteiro `.dz23-arsenal`; depois a variável DZ23_ARSENAL.
    """
    resolvido = comeco.resolve()
    vistos: set[str] = set()
    for base in [resolvido, *resolvido.parents]:
        chave = str(base).lower()
        if chave in vistos:
            continue
        vistos.add(chave)
        if (base / "scripts" / "skill_validator.py").is_file() and (base / "skills").is_dir():
            return base

    for base in [resolvido, *resolvido.parents]:
        marcador = base / ".dz23-arsenal"
        if marcador.is_file():
            alvo = marcador.read_text(encoding="utf-8-sig").strip()
            if alvo and (Path(alvo) / "scripts" / "skill_validator.py").is_file():
                return Path(alvo)

    env = os.environ.get("DZ23_ARSENAL")
    if env and (Path(env) / "scripts" / "skill_validator.py").is_file():
        return Path(env)
    return None


def importar_validador_comum(aqui: Path):
    """Devolve a função validar_comum, ou None se o arsenal não estiver acessível."""
    import sys
    arsenal = localizar_arsenal(aqui)
    if arsenal is None:
        return None
    pasta = str(arsenal / "scripts")
    if pasta not in sys.path:
        sys.path.insert(0, pasta)
    try:
        from skill_validator import validar_comum  # type: ignore
    except ImportError:
        return None
    return validar_comum
