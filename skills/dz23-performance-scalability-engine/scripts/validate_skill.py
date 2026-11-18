import sys
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
# --- checagens comuns do arsenal -------------------------------------------
# A skill instalada em ~/.agents/skills precisa achar o checkout (que pode estar em
# outro disco) para rodar as checagens compartilhadas. Contar niveis de diretorio nao
# funciona la: parents[3] aponta para ~/.agents. O localizador sobe a arvore, le o
# ponteiro .dz23-arsenal ou respeita DZ23_ARSENAL.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from _achar_arsenal import importar_validador_comum
except ImportError:
    print("WARN: _achar_arsenal ausente — checagens comuns puladas")
    importar_validador_comum = None
if importar_validador_comum is not None:
    _validar_comum = importar_validador_comum(Path(__file__).resolve())
    if _validar_comum is None:
        print("WARN: arsenal nao localizado — checagens comuns puladas")
    else:
        _erros_comuns = _validar_comum(root)
        if _erros_comuns:
            # `assert` nao serve para gate: python -O remove a instrucao e o validador
            # passa a imprimir OK com referencia quebrada -- reproduzido nas dez skills
            # desta sessao. Um verificador que desaparece por uma flag do interpretador e
            # pior que a ausencia dele, porque continua parecendo conferido.
            for e in _erros_comuns:
                print(f"FALHA: {e}", file=sys.stderr)
            raise SystemExit(1)


REQUIRED_REFS = [
    'measurement-first.md',
    'perf-budget.md',
    'frontend-layer.md',
    'network-layer.md',
    'backend-layer.md',
    'infra-layer.md',
    'diagnostic-playbook.md',
    'anti-patterns.md',
    'quality-gates.md',
    'installation.md',
]
REQUIRED_TEMPLATES = ['perf-plan.md', 'layer-checklist.md', 'perf-budget.md', 'benchmark-report.md',
                     'diagnosis-report.md', 'adr-performance.md']
REQUIRED_SCRIPTS = ['validate_skill.py', 'web_vitals_probe.py', 'compare_samples.py', 'check_budget.py']
REQUIRED_TOP = ['SKILL.md', 'README.md', 'CHANGELOG.md', 'VERSION', 'PROMPT-ATIVACAO.txt']

missing = [x for x in REQUIRED_TOP if not (root / x).is_file()]
missing += [f'references/{x}' for x in REQUIRED_REFS if not (root / 'references' / x).is_file()]
missing += [f'templates/{x}' for x in REQUIRED_TEMPLATES if not (root / 'templates' / x).is_file()]
missing += [f'scripts/{x}' for x in REQUIRED_SCRIPTS if not (root / 'scripts' / x).is_file()]
missing += ['evals/evals.json'] if not (root / 'evals' / 'evals.json').is_file() else []
assert not missing, 'Arquivos ausentes: ' + ', '.join(missing)

s = (root / 'SKILL.md').read_text(encoding='utf-8')
assert s.startswith('---\n'), 'SKILL.md sem frontmatter'
assert re.search(r'(?m)^name: dz23-performance-scalability-engine$', s), 'name do frontmatter incorreto'
assert re.search(r'(?m)^version: \d+\.\d+\.\d+$', s), 'version ausente ou inválida'
assert re.search(r'(?m)^description: .+', s), 'description ausente'

version = (root / 'VERSION').read_text(encoding='utf-8').strip()
assert re.fullmatch(r'\d+\.\d+\.\d+', version), f'VERSION inválido: {version!r}'
assert re.search(rf'(?m)^version: {re.escape(version)}$', s), 'VERSION difere do frontmatter'

for marker in ['## Workflow obrigatório', '## Módulos de decisão', '5.1 ', '5.6 ',
               '## Padrões inegociáveis', '## Quality gates']:
    assert marker in s, f'seção obrigatória ausente no SKILL.md: {marker}'

# as 4 camadas e os 20 itens precisam existir
for layer in ('Camada 1 — Frontend', 'Camada 2 — Comunicação', 'Camada 3 — Backend', 'Camada 4 — Infraestrutura'):
    assert layer in s, f'camada ausente no SKILL.md: {layer}'

refs_text = (root / 'references' / 'frontend-layer.md').read_text(encoding='utf-8')
for item in ('1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7'):
    assert f'## {item} ' in refs_text, f'item {item} ausente em frontend-layer.md'
for fname, items in (('network-layer.md', ('2.1', '2.2', '2.3', '2.4')),
                     ('backend-layer.md', ('3.1', '3.2', '3.3', '3.4')),
                     ('infra-layer.md', ('4.1', '4.2', '4.3', '4.4', '4.5'))):
    text = (root / 'references' / fname).read_text(encoding='utf-8')
    for item in items:
        assert f'## {item} ' in text, f'item {item} ausente em {fname}'
    assert '**Evita**' in text and '**Implementar**' in text and '**Diretriz**' in text, \
        f'{fname}: item sem a tríade Evita/Implementar/Diretriz'

for ref in set(re.findall(r'`((?:references|templates|scripts)/[A-Za-z0-9._-]+)`', s)):
    assert (root / ref).is_file(), f'referência citada não existe: {ref}'

DEAD = 'dz23' + '-premium' + '-ui-ultimate'
for f in root.rglob('*.md'):
    assert DEAD not in f.read_text(encoding='utf-8'), f'nome de skill descontinuada em {f}'

evals = json.loads((root / 'evals' / 'evals.json').read_text(encoding='utf-8'))
assert evals.get('schema_version') == 1, 'evals.json com schema_version != 1'
cases = evals.get('cases', [])
assert len(cases) == 16, f'evals devem ter 16 casos, tem {len(cases)}'
assert len({c['id'] for c in cases}) == len(cases), 'ids de eval duplicados'
for c in cases:
    for k in ('id', 'title', 'input', 'expected', 'fails_if'):
        assert c.get(k), f'caso {c.get("id")} sem campo {k}'

probe = (root / 'scripts' / 'web_vitals_probe.py').read_text(encoding='utf-8')
for need in ('Content-Encoding', 'Cache-Control', 'TTFB', 'executed_javascript'):
    assert need in probe or need.lower() in probe.lower(), f'sonda não cobre {need}'

for f in root.rglob('*.md'):
    assert f.read_text(encoding='utf-8').strip(), f'Vazio: {f}'

print(f'PASS: {len(REQUIRED_REFS)} references + {len(REQUIRED_TEMPLATES)} templates + '
      f'{len(REQUIRED_SCRIPTS)} scripts; 4 camadas e 20 itens verificados; '
      f'{len(list(root.rglob("*.md")))} Markdown; frontmatter v{version}; evals {len(cases)} casos.')
