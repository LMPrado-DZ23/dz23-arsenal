from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]

REQUIRED_REFS = [
    'discovery-scan.md',
    'entrypoints-and-spine.md',
    'dependency-graph.md',
    'data-and-flow.md',
    'context-budget.md',
    'conventions-and-style.md',
    'hotspots-and-debt.md',
    'risk-zones.md',
    'security-and-evidence.md',
    'mapping-playbook.md',
    'context-brief.md',
    'verification-and-freshness.md',
    'anti-patterns.md',
    'quality-gates.md',
    'installation.md',
]
REQUIRED_TEMPLATES = [
    'codebase-map.md', 'context-brief.md', 'change-impact.md', 'hotspot-report.md',
    'EVIDENCE_LEDGER.md', 'AGENT_HANDOFF.md', 'context-pack.md',
]
REQUIRED_SCRIPTS = ['validate_skill.py', 'repo_probe.py', 'repo_inventory.py']
REQUIRED_TOP = ['SKILL.md', 'README.md', 'CHANGELOG.md', 'VERSION', 'PROMPT-ATIVACAO.txt']

missing = [x for x in REQUIRED_TOP if not (root / x).is_file()]
missing += [f'references/{x}' for x in REQUIRED_REFS if not (root / 'references' / x).is_file()]
missing += [f'templates/{x}' for x in REQUIRED_TEMPLATES if not (root / 'templates' / x).is_file()]
missing += [f'scripts/{x}' for x in REQUIRED_SCRIPTS if not (root / 'scripts' / x).is_file()]
missing += ['evals/evals.json'] if not (root / 'evals' / 'evals.json').is_file() else []
assert not missing, 'Arquivos ausentes: ' + ', '.join(missing)

s = (root / 'SKILL.md').read_text(encoding='utf-8')
assert s.startswith('---\n'), 'SKILL.md sem frontmatter'
assert re.search(r'(?m)^name: dz23-codebase-cartographer$', s), 'name do frontmatter incorreto'
assert re.search(r'(?m)^version: \d+\.\d+\.\d+$', s), 'version ausente ou inválida'
assert re.search(r'(?m)^description: .+', s), 'description ausente'

version = (root / 'VERSION').read_text(encoding='utf-8').strip()
assert re.fullmatch(r'\d+\.\d+\.\d+', version), f'VERSION inválido: {version!r}'
assert re.search(rf'(?m)^version: {re.escape(version)}$', s), 'VERSION difere do frontmatter'

for marker in ['## Workflow obrigatório', '## Módulos de decisão', '5.1 ', '5.6 ',
               '## Declaração de escopo', '## Entregáveis obrigatórios',
               '## Estados de evidência', '## Veredito',
               '## Padrões inegociáveis', '## Quality gates',
               '## Checklist de encerramento']:
    assert marker in s, f'seção obrigatória ausente no SKILL.md: {marker}'

for ref in set(re.findall(r'`((?:references|templates|scripts)/[A-Za-z0-9._-]+)`', s)):
    assert (root / ref).is_file(), f'referência citada não existe: {ref}'

DEAD = 'dz23' + '-premium' + '-ui-ultimate'
for f in root.rglob('*.md'):
    assert DEAD not in f.read_text(encoding='utf-8'), f'nome de skill descontinuada em {f}'

evals = json.loads((root / 'evals' / 'evals.json').read_text(encoding='utf-8'))
assert evals.get('schema_version') == 1, 'evals.json com schema_version != 1'
cases = evals.get('cases', [])
assert len(cases) == 15, f'evals devem ter 15 casos, tem {len(cases)}'
assert len({c['id'] for c in cases}) == len(cases), 'ids de eval duplicados'
for c in cases:
    for k in ('id', 'title', 'input', 'expected', 'fails_if'):
        assert c.get(k), f'caso {c.get("id")} sem campo {k}'

# inventário não pode abrir conteúdo: checar que o script não lê arquivos do repo
inv = (root / 'scripts' / 'repo_inventory.py').read_text(encoding='utf-8')
for forbidden in ('read_text(', 'read_bytes(', '.read()', 'open(full', 'open(root'):
    assert forbidden not in inv, f'repo_inventory.py parece ler conteúdo ({forbidden}) — deve usar só metadata'
assert 'content_read": False' in inv, 'repo_inventory.py deve declarar content_read=false'

for f in root.rglob('*.md'):
    assert f.read_text(encoding='utf-8').strip(), f'Vazio: {f}'

print(f'PASS: {len(REQUIRED_REFS)} references + {len(REQUIRED_TEMPLATES)} templates + '
      f'{len(REQUIRED_SCRIPTS)} scripts; {len(list(root.rglob("*.md")))} Markdown; '
      f'frontmatter v{version}; evals {len(cases)} casos.')
