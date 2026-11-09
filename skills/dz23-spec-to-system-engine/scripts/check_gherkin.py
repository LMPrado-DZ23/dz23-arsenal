#!/usr/bin/env python3
"""Verifica estrutura de arquivo .feature (Gherkin).

Sem dependência externa: parser por regex conservador. Se
`gherkin-official` estiver instalado, use-o para validação completa
(`pip install gherkin-official` — opcional, não obrigatório).

Uso:
    python scripts/check_gherkin.py <arquivo.feature> [mais.feature ...]

Exit 0 = válido · 1 = estrutura inválida · 2 = input inválido
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

TAGS = re.compile(r"^\s*@[\w.\-:]+")
COMMENT = re.compile(r"^\s*#")
FEATURE = re.compile(r"^\s*Feature:")
BACKGROUND = re.compile(r"^\s*Background:")
SCENARIO = re.compile(r"^\s*Scenario( Outline)?:")
EXAMPLES = re.compile(r"^\s*Examples:")
STEP = re.compile(r"^\s*(Given|When|Then|And|But|\*)\s+\S")
STEP_KEYWORD = re.compile(r"^\s*(Given|When|Then|And|But|\*)\s+")
ORDER = {"Given": 0, "When": 1, "Then": 2}


def check(path: Path) -> list[str]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    useful = [l for l in lines if l.strip() and not COMMENT.match(l) and not TAGS.match(l)]
    if not useful:
        return [f"{path.name}: arquivo vazio"]
    if not FEATURE.match(useful[0]):
        errors.append(f"{path.name}: primeira linha útil deve ser 'Feature:'")

    in_block = False          # dentro de Background ou Scenario
    is_background = False
    in_outline = False
    outline_has_examples = True
    outline_line = 0
    steps_in_block = 0
    last_phase = -1
    scenarios = 0

    def close_block(end_line: int) -> None:
        nonlocal steps_in_block, in_outline, outline_has_examples, outline_line
        if in_block and not is_background and steps_in_block == 0:
            errors.append(f"{path.name}:{end_line}: cenário sem nenhum step")
        if in_outline and not outline_has_examples:
            errors.append(f"{path.name}:{outline_line}: 'Scenario Outline' sem 'Examples:'")

    for idx, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or COMMENT.match(raw) or TAGS.match(raw):
            continue

        if BACKGROUND.match(raw):
            close_block(idx)
            in_block, is_background, in_outline = True, True, False
            steps_in_block, last_phase = 0, -1
            continue

        if SCENARIO.match(raw):
            close_block(idx)
            scenarios += 1
            in_block, is_background = True, False
            in_outline = bool(SCENARIO.match(raw).group(1))
            outline_has_examples = not in_outline
            outline_line = idx
            steps_in_block, last_phase = 0, -1
            continue

        if EXAMPLES.match(raw):
            if not in_outline:
                errors.append(f"{path.name}:{idx}: 'Examples:' fora de 'Scenario Outline'")
            outline_has_examples = True
            continue

        m = STEP.match(raw)
        if m:
            if not in_block:
                errors.append(f"{path.name}:{idx}: step fora de 'Scenario'/'Background'")
                continue
            steps_in_block += 1
            keyword = STEP_KEYWORD.match(raw).group(1)
            if keyword in ORDER and not is_background:
                phase = ORDER[keyword]
                if phase < last_phase:
                    errors.append(f"{path.name}:{idx}: ordem inválida ({keyword} depois de Then)")
                last_phase = max(last_phase, phase)
            continue

        if raw.startswith("|"):
            continue  # tabela de dados / Examples

        # descrição livre multi-linha (indentada) é permitida
        if re.match(r"^\s{2,}\S", raw):
            continue

    close_block(len(lines))

    if scenarios == 0:
        errors.append(f"{path.name}: nenhum 'Scenario' encontrado")

    return errors


def main(argv: list[str]) -> int:
    if not argv:
        print("INVALID uso: check_gherkin.py <arquivo.feature> [...]", file=sys.stderr)
        return 2

    failed = 0
    for arg in argv:
        path = Path(arg)
        if not path.is_file():
            print(f"INVALID arquivo não encontrado: {path}", file=sys.stderr)
            failed = 2
            continue
        if path.suffix != ".feature":
            print(f"INVALID não é .feature: {path}", file=sys.stderr)
            failed = 2
            continue
        errors = check(path)
        if errors:
            failed = 1
            for err in errors:
                print(f"INVALID {err}")
        else:
            print(f"GHERKIN_VALID {path}")

    if failed:
        return failed
    print("GHERKIN_CHECK=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
