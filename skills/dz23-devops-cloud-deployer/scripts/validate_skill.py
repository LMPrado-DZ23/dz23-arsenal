from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]

REQUIRED_REFS = [
    'container-images.md',
    'infrastructure-audit.md',
    'compose-and-networking.md',
    'edge-proxy-tls.md',
    'build-and-artifacts.md',
    'environments-and-config.md',
    'secrets-and-identity.md',
    'kubernetes-and-orchestration.md',
    'deploy-strategies.md',
    'migrations-safe.md',
    'rollback-and-recovery.md',
    'observability-backup-dr.md',
    'supply-chain-security.md',
    'quality-gates.md',
    'anti-patterns.md',
    'installation.md',
]
# observability-and-slo.md é legado mantido para não quebrar links antigos, mas não é obrigatório.
REQUIRED_TEMPLATES = [
    'Dockerfile', 'compose.template.yml', 'k8s-deployment.yaml', 'ci-pipeline.yml',
    'deployment-report.md', 'rollback-plan.md', 'deploy-runbook.md',
]
REQUIRED_SCRIPTS = ['validate_skill.py', 'preflight.sh', 'release_probe.py']
REQUIRED_TOP = ['SKILL.md', 'README.md', 'CHANGELOG.md', 'VERSION', 'PROMPT-ATIVACAO.txt']

missing = [x for x in REQUIRED_TOP if not (root / x).is_file()]
missing += [f'references/{x}' for x in REQUIRED_REFS if not (root / 'references' / x).is_file()]
missing += [f'templates/{x}' for x in REQUIRED_TEMPLATES if not (root / 'templates' / x).is_file()]
missing += [f'scripts/{x}' for x in REQUIRED_SCRIPTS if not (root / 'scripts' / x).is_file()]
missing += ['evals/evals.json'] if not (root / 'evals' / 'evals.json').is_file() else []
assert not missing, 'Arquivos ausentes: ' + ', '.join(missing)

s = (root / 'SKILL.md').read_text(encoding='utf-8')
assert s.startswith('---\n'), 'SKILL.md sem frontmatter'
assert re.search(r'(?m)^name: dz23-devops-cloud-deployer$', s), 'name do frontmatter incorreto'
assert re.search(r'(?m)^version: \d+\.\d+\.\d+$', s), 'version ausente ou inválida'
assert re.search(r'(?m)^description: .+', s), 'description ausente'

version = (root / 'VERSION').read_text(encoding='utf-8').strip()
assert re.fullmatch(r'\d+\.\d+\.\d+', version), f'VERSION inválido: {version!r}'
assert re.search(rf'(?m)^version: {re.escape(version)}$', s), 'VERSION difere do frontmatter'

for marker in ['## Pré-condições', '## Pipeline em 4 fases', '## Módulos de decisão',
               '5.1 ', '5.6 ', '## Estratégias de deploy', '## Gestão de segredos',
               '## Vereditos', '## Checklist de encerramento']:
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

for f in root.rglob('*.md'):
    assert f.read_text(encoding='utf-8').strip(), f'Vazio: {f}'

print(f'PASS: {len(REQUIRED_REFS)} references + {len(REQUIRED_TEMPLATES)} templates + '
      f'{len(REQUIRED_SCRIPTS)} scripts; {len(list(root.rglob("*.md")))} Markdown; '
      f'frontmatter v{version}; evals {len(cases)} casos.')
