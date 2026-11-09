from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]

REQUIRED_REFS = [
    'target-triage.md',
    'elf-and-native.md',
    'static-analysis.md',
    'dynamic-analysis.md',
    'firmware-formats.md',
    'firmware-extraction.md',
    'firmware-emulation.md',
    'boot-and-hardware.md',
    'anti-patterns.md',
    'quality-gates.md',
    'installation.md',
    'rea-integration.md',
]
REQUIRED_TEMPLATES = ['re-report.md', 'target-triage.md', 'firmware-map.md', 'findings-ledger.md']
REQUIRED_SCRIPTS = ['validate_skill.py', 'file_triage.py', 're_toolkit.py']
REQUIRED_TOP = ['SKILL.md', 'README.md', 'CHANGELOG.md', 'VERSION', 'PROMPT-ATIVACAO.txt']

missing = [x for x in REQUIRED_TOP if not (root / x).is_file()]
missing += [f'references/{x}' for x in REQUIRED_REFS if not (root / 'references' / x).is_file()]
missing += [f'templates/{x}' for x in REQUIRED_TEMPLATES if not (root / 'templates' / x).is_file()]
missing += [f'scripts/{x}' for x in REQUIRED_SCRIPTS if not (root / 'scripts' / x).is_file()]
missing += ['evals/evals.json'] if not (root / 'evals' / 'evals.json').is_file() else []
assert not missing, 'Arquivos ausentes: ' + ', '.join(missing)

s = (root / 'SKILL.md').read_text(encoding='utf-8')
assert s.startswith('---\n'), 'SKILL.md sem frontmatter'
assert re.search(r'(?m)^name: dz23-reverse-engineer-anything$', s), 'name do frontmatter incorreto'
assert re.search(r'(?m)^version: \d+\.\d+\.\d+$', s), 'version ausente ou inválida'
assert re.search(r'(?m)^description: .+', s), 'description ausente'

version = (root / 'VERSION').read_text(encoding='utf-8').strip()
assert re.fullmatch(r'\d+\.\d+\.\d+', version), f'VERSION inválido: {version!r}'
assert re.search(rf'(?m)^version: {re.escape(version)}$', s), 'VERSION difere do frontmatter'

for marker in ['## Workflow obrigatório', '## Módulos de decisão', '5.1 ', '5.6 ',
               '## Padrões inegociáveis', '## Quality gates']:
    assert marker in s, f'seção obrigatória ausente no SKILL.md: {marker}'

# regras de domínio que não podem desaparecer
for rule in ('autoriza', 'isolamento', 'offset', 'hash', 'BLOCKED'):
    assert rule.lower() in s.lower(), f'regra de domínio ausente no SKILL.md: {rule}'

for ref in set(re.findall(r'`((?:references|templates|scripts)/[A-Za-z0-9._-]+)`', s)):
    assert (root / ref).is_file(), f'referência citada não existe: {ref}'

DEAD = 'dz23' + '-premium' + '-ui-ultimate'
for f in root.rglob('*.md'):
    assert DEAD not in f.read_text(encoding='utf-8'), f'nome de skill descontinuada em {f}'

# fatos de firmware que sustentam a skill precisam estar presentes
fw = (root / 'references' / 'firmware-formats.md').read_text(encoding='utf-8')
for fact in ('0x50AA', '0xEBEB', '0x27051956', 'D00DFEED', 'hsqs', '0A324655'):
    assert fact.lower() in fw.lower(), f'fato de formato ausente em firmware-formats.md: {fact}'

evals = json.loads((root / 'evals' / 'evals.json').read_text(encoding='utf-8'))
assert evals.get('schema_version') == 1, 'evals.json com schema_version != 1'
cases = evals.get('cases', [])
assert len(cases) == 15, f'evals devem ter 15 casos, tem {len(cases)}'
assert len({c['id'] for c in cases}) == len(cases), 'ids de eval duplicados'
for c in cases:
    for k in ('id', 'title', 'input', 'expected', 'fails_if'):
        assert c.get(k), f'caso {c.get("id")} sem campo {k}'

triage = (root / 'scripts' / 'file_triage.py').read_text(encoding='utf-8')
assert 'executed_target' in triage and 'read_only' in triage, 'file_triage.py deve declarar read_only'
for sig in (r'\x7fELF', r'"MZ"', '"hsqs"', r'\x27\x05\x19\x56', r'\xd0\x0d\xfe\xed'):
    assert sig in triage, f'file_triage.py não reconhece {sig!r}'

toolkit = (root / 'scripts' / 're_toolkit.py').read_text(encoding='utf-8')
for sub in ('uimage', 'esp', 'dtb', 'uf2', 'intelhex', 'elf', 'squashfs', 'selftest'):
    assert f'cmd_{sub}' in toolkit, f're_toolkit.py sem subcomando {sub}'
for f in root.rglob('*.md'):
    assert f.read_text(encoding='utf-8').strip(), f'Vazio: {f}'

print(f'PASS: {len(REQUIRED_REFS)} references + {len(REQUIRED_TEMPLATES)} templates + '
      f'{len(REQUIRED_SCRIPTS)} scripts; {len(list(root.rglob("*.md")))} Markdown; '
      f'frontmatter v{version}; evals {len(cases)} casos; fatos de firmware conferidos.')
