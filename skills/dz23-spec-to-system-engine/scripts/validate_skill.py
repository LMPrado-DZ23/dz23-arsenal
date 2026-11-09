from pathlib import Path
import json
import re
import sys

root = Path(__file__).resolve().parents[1]

REQUIRED_REFS = [
    'discovery-and-framing.md',
    'domain-and-invariants.md',
    'state-machines.md',
    'interface-contracts.md',
    'data-model.md',
    'requirements-and-acceptance.md',
    'gherkin-and-bdd.md',
    'risk-and-spikes.md',
    'decomposition-and-slicing.md',
    'decomposition-tree.md',
    'nfr-and-thresholds.md',
    'planning-and-estimation.md',
    'traceability-and-gates.md',
    'execution-and-reconciliation.md',
    'anti-patterns.md',
    'quality-gates.md',
    'installation.md',
]
REQUIRED_TEMPLATES = [
    'spec.md', 'tasks.md', 'gherkin.feature', 'openapi.yaml', 'state-machine.md',
    'traceability.md', 'adr.md', 'vertical-slice-plan.md',
]
REQUIRED_SCRIPTS = ['validate_skill.py', 'validate_spec.py', 'check_gherkin.py']
# examples/ é opcional: fixtures de dado, não artefato obrigatório da skill.
OPTIONAL_EXAMPLES = ['spec-example.json']
REQUIRED_TOP = ['SKILL.md', 'README.md', 'CHANGELOG.md', 'VERSION', 'PROMPT-ATIVACAO.txt',
                'schema/spec.schema.json']

missing = [x for x in REQUIRED_TOP if not (root / x).is_file()]
missing += [f'references/{x}' for x in REQUIRED_REFS if not (root / 'references' / x).is_file()]
missing += [f'templates/{x}' for x in REQUIRED_TEMPLATES if not (root / 'templates' / x).is_file()]
missing += [f'scripts/{x}' for x in REQUIRED_SCRIPTS if not (root / 'scripts' / x).is_file()]
missing += ['evals/evals.json'] if not (root / 'evals' / 'evals.json').is_file() else []
optional_missing = [f'examples/{x}' for x in OPTIONAL_EXAMPLES if not (root / 'examples' / x).is_file()]
assert not missing, 'Arquivos ausentes: ' + ', '.join(missing)

s = (root / 'SKILL.md').read_text(encoding='utf-8')
assert s.startswith('---\n'), 'SKILL.md sem frontmatter'
assert re.search(r'(?m)^name: dz23-spec-to-system-engine$', s), 'name do frontmatter incorreto'
assert re.search(r'(?m)^version: \d+\.\d+\.\d+$', s), 'version ausente ou inválida'
assert re.search(r'(?m)^description: .+', s), 'description ausente'

version = (root / 'VERSION').read_text(encoding='utf-8').strip()
assert re.fullmatch(r'\d+\.\d+\.\d+', version), f'VERSION inválido: {version!r}'
assert re.search(rf'(?m)^version: {re.escape(version)}$', s), 'VERSION difere do frontmatter'

for marker in ['## Workflow obrigatório', '## Módulos de decisão', '5.1 ', '5.6 ',
               '## Padrões inegociáveis', '## Qualidade gates'.replace('Qualidade', 'Quality'),
               '## Artefatos obrigatórios', '## Estados de requisito', '## Veredito',
               '## Checklist de encerramento']:
    assert marker in s, f'seção obrigatória ausente no SKILL.md: {marker}'

for ref in set(re.findall(r'`((?:references|templates|scripts|schema)/[A-Za-z0-9._-]+)`', s)):
    assert (root / ref).is_file(), f'referência citada não existe: {ref}'

DEAD = 'dz23' + '-premium' + '-ui-ultimate'
GHOST = 'dz23' + '-codebase' + '-cartographer'
for f in root.rglob('*.md'):
    text = f.read_text(encoding='utf-8')
    assert DEAD not in text, f'nome de skill descontinuada em {f}'
    assert GHOST not in text, f'referência a skill inexistente em {f}'

evals = json.loads((root / 'evals' / 'evals.json').read_text(encoding='utf-8'))
assert evals.get('schema_version') == 1, 'evals.json com schema_version != 1'
cases = evals.get('cases', [])
assert len(cases) == 15, f'evals devem ter 15 casos, tem {len(cases)}'
assert len({c['id'] for c in cases}) == len(cases), 'ids de eval duplicados'
for c in cases:
    for k in ('id', 'title', 'input', 'expected', 'fails_if'):
        assert c.get(k), f'caso {c.get("id")} sem campo {k}'

schema = json.loads((root / 'schema' / 'spec.schema.json').read_text(encoding='utf-8'))
assert schema.get('$schema', '').endswith('2020-12/schema'), 'schema não é JSON Schema 2020-12'
assert schema['properties']['schema_version']['const'] == 1, 'schema_version deve ser const 1'

for f in root.rglob('*.md'):
    assert f.read_text(encoding='utf-8').strip(), f'Vazio: {f}'

print(f'PASS: {len(REQUIRED_REFS)} references + {len(REQUIRED_TEMPLATES)} templates + '
      f'{len(REQUIRED_SCRIPTS)} scripts + schema; {len(list(root.rglob("*.md")))} Markdown; '
      f'frontmatter v{version}; evals {len(cases)} casos.'
      + (f' (examples ausentes: {optional_missing})' if optional_missing else ''))
