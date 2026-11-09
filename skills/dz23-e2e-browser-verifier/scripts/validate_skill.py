from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]

REQUIRED_REFS = [
    'test-strategy.md',
    'playwright-strategy.md',
    'browser-security.md',
    'visual-accessibility.md',
    'flaky-debugging.md',
    'ci-and-evidence.md',
    'anti-patterns.md',
    'quality-gates.md',
    'test-data-and-environments.md',
    'installation.md',
]
REQUIRED_TEMPLATES = [
    'playwright.config.ts',
    'e2e-smoke.spec.ts',
    'axe-audit.spec.ts',
    'e2e-report.md',
]
REQUIRED_TOP = ['SKILL.md', 'README.md', 'CHANGELOG.md', 'VERSION', 'PROMPT-ATIVACAO.txt']

missing = [x for x in REQUIRED_TOP if not (root / x).is_file()]
missing += [f'references/{x}' for x in REQUIRED_REFS if not (root / 'references' / x).is_file()]
missing += [f'templates/{x}' for x in REQUIRED_TEMPLATES if not (root / 'templates' / x).is_file()]
missing += ['evals/evals.json'] if not (root / 'evals' / 'evals.json').is_file() else []
missing += ['scripts/validate_skill.py'] if not (root / 'scripts' / 'validate_skill.py').is_file() else []
assert not missing, 'Arquivos ausentes: ' + ', '.join(missing)

s = (root / 'SKILL.md').read_text(encoding='utf-8')
assert s.startswith('---\n'), 'SKILL.md sem frontmatter'
assert re.search(r'(?m)^name: dz23-e2e-browser-verifier$', s), 'name do frontmatter incorreto'
assert re.search(r'(?m)^version: \d+\.\d+\.\d+$', s), 'version ausente ou inválida'
assert re.search(r'(?m)^description: .+', s), 'description ausente'

version = (root / 'VERSION').read_text(encoding='utf-8').strip()
assert re.fullmatch(r'\d+\.\d+\.\d+', version), f'VERSION inválido: {version!r}'
assert re.search(rf'(?m)^version: {re.escape(version)}$', s), 'VERSION difere do frontmatter'

# módulos de decisão preservados e tiers presentes
for marker in ['## Tiers de risco', '## Módulos de decisão', '5.1 ', '5.6 ']:
    assert marker in s, f'seção obrigatória ausente no SKILL.md: {marker}'

# cross-refs citadas no SKILL.md resolvem
for ref in set(re.findall(r'`((?:references|templates)/[A-Za-z0-9._-]+)`', s)):
    assert (root / ref).is_file(), f'referência citada não existe: {ref}'

# nenhuma referência à skill morta (nome montado para não poluir grep do repositório)
DEAD = 'dz23' + '-premium' + '-ui-ultimate'
for f in root.rglob('*.md'):
    assert DEAD not in f.read_text(encoding='utf-8'), f'nome de skill descontinuada em {f}'

# evals
evals = json.loads((root / 'evals' / 'evals.json').read_text(encoding='utf-8'))
assert evals.get('schema_version') == 1, 'evals.json com schema_version != 1'
cases = evals.get('cases', [])
assert len(cases) == 16, f'evals devem ter 16 casos, tem {len(cases)}'
assert len({c['id'] for c in cases}) == len(cases), 'ids de eval duplicados'
for c in cases:
    for k in ('id', 'title', 'input', 'expected', 'fails_if'):
        assert c.get(k), f'caso {c.get("id")} sem campo {k}'

for f in root.rglob('*.md'):
    assert f.read_text(encoding='utf-8').strip(), f'Vazio: {f}'

print(f'PASS: {len(REQUIRED_REFS)} references + {len(REQUIRED_TEMPLATES)} templates; '
      f'{len(list(root.rglob("*.md")))} Markdown; frontmatter v{version}; evals {len(cases)} casos.')
