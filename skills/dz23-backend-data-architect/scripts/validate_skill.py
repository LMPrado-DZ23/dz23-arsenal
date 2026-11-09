from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
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
