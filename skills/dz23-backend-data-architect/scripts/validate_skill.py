import sys
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
# --- checagens comuns do arsenal (scripts/skill_validator.py) ---------------
# Reunifica o que estava espalhado em dez copias divergentes: frontmatter, VERSION x
# frontmatter, PROMPT-ATIVACAO congelada, referencias quebradas, evals coerentes e
# nome de skill descontinuada em frontmatter vivo. As checagens especificas desta skill
# continuam abaixo.
_ARSENAL = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ARSENAL / "scripts"))
try:
    from skill_validator import validar_comum
except ImportError as exc:  # ambiente fora do repo (skill instalada sozinha)
    print(f"WARN: checagens comuns indisponiveis ({exc})")
    validar_comum = None
else:
    _erros_comuns = validar_comum(root)
    assert not _erros_comuns, "checagens comuns falharam:\n  - " + "\n  - ".join(_erros_comuns)

required = [
    'SKILL.md',
    'README.md',
    'CHANGELOG.md',
    'PROMPT-ATIVACAO.txt',
    'references/installation.md',
    'references/service-architecture.md',
    'references/data-modeling.md',
    'references/api-contracts.md',
    'references/migrations-and-zero-downtime.md',
    'references/security-and-tenancy.md',
    'references/performance-and-observability.md',
    'references/quality-gates.md',
    'references/anti-patterns.md',
    'templates/adr.md',
    'templates/contract-review.md',
]
missing = [x for x in required if not (root / x).is_file()]
assert not missing, 'Arquivos ausentes: ' + ', '.join(missing)

s = (root / 'SKILL.md').read_text(encoding='utf-8')
assert s.startswith('---\n'), 'SKILL.md sem frontmatter'
assert re.search(r'(?m)^name: dz23-backend-data-architect$', s), 'name do frontmatter incorreto'
assert re.search(r'(?m)^version: \d+\.\d+\.\d+$', s), 'version ausente ou inválida'
assert re.search(r'(?m)^description: .+', s), 'description ausente'

for f in root.rglob('*.md'):
    assert f.read_text(encoding='utf-8').strip(), f'Vazio: {f}'

print(f'PASS: {len(required)} arquivos obrigatórios; {len(list(root.rglob("*.md")))} arquivos Markdown; frontmatter válido.')
