import sys
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]

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
            for e in _erros_comuns:
                print(f"FALHA: {e}", file=sys.stderr)
            raise SystemExit(1)

REQUIRED_TOP = ['SKILL.md', 'README.md', 'CHANGELOG.md', 'VERSION', 'PROMPT-ATIVACAO.txt']
REQUIRED_REFS = ['metodo.md', 'fontes-e-termos.md']
REQUIRED_TEMPLATES = ['fixes.md']
REQUIRED_SCRIPTS = ['validate_skill.py', 'reviews.py', 'themes.json']

missing = [x for x in REQUIRED_TOP if not (root / x).is_file()]
missing += [f'references/{x}' for x in REQUIRED_REFS if not (root / 'references' / x).is_file()]
missing += [f'templates/{x}' for x in REQUIRED_TEMPLATES if not (root / 'templates' / x).is_file()]
missing += [f'scripts/{x}' for x in REQUIRED_SCRIPTS if not (root / 'scripts' / x).is_file()]
missing += ['examples/reviews-exemplo.csv'] if not (root / 'examples' / 'reviews-exemplo.csv').is_file() else []
missing += ['evals/evals.json'] if not (root / 'evals' / 'evals.json').is_file() else []
assert not missing, 'Arquivos ausentes: ' + ', '.join(missing)

s = (root / 'SKILL.md').read_text(encoding='utf-8')
assert s.startswith('---\n'), 'SKILL.md sem frontmatter'
assert re.search(r'(?m)^name: replica-entrepreneur$', s), 'name do frontmatter incorreto'
assert re.search(r'(?m)^version: \d+\.\d+\.\d+$', s), 'version ausente ou invalida'
assert re.search(r'(?m)^  license: MIT$', s), 'licenca de origem (MIT) ausente no frontmatter'
assert re.search(r'(?m)^  origin: ', s), 'origin (proveniencia) ausente no frontmatter'

version = (root / 'VERSION').read_text(encoding='utf-8').strip()
assert re.fullmatch(r'\d+\.\d+\.\d+', version), f'VERSION invalido: {version!r}'
assert re.search(rf'(?m)^version: {re.escape(version)}$', s), 'VERSION difere do frontmatter'

for marker in ['## Regras inegociáveis', '## Como fazer', '## A ferramenta', '## Entregáveis',
               '## Estados de evidência', '## Veredito', '## Roteamento com outras skills']:
    assert marker in s, f'secao obrigatoria ausente no SKILL.md: {marker}'

for ref in set(re.findall(r'`((?:references|templates|scripts|examples)/[A-Za-z0-9._-]+)`', s)):
    assert (root / ref).is_file(), f'referencia citada nao existe: {ref}'

# themes.json é JSON válido com temas
themes = json.loads((root / 'scripts' / 'themes.json').read_text(encoding='utf-8'))
assert isinstance(themes.get('themes'), list) and themes['themes'], 'themes.json sem temas'

evals = json.loads((root / 'evals' / 'evals.json').read_text(encoding='utf-8'))
assert evals.get('schema_version') == 1, 'evals.json com schema_version != 1'
cases = evals.get('cases', [])
assert len(cases) == 6, f'evals devem ter 6 casos, tem {len(cases)}'
assert len({c['id'] for c in cases}) == len(cases), 'ids de eval duplicados'
for c in cases:
    for k in ('id', 'title', 'input', 'expected', 'fails_if'):
        assert c.get(k), f'caso {c.get("id")} sem campo {k}'

for f in root.rglob('*.md'):
    assert f.read_text(encoding='utf-8').strip(), f'Vazio: {f}'

print(f'PASS: {len(REQUIRED_REFS)} references + {len(REQUIRED_TEMPLATES)} templates + reviews.py/themes.json; '
      f'{len(list(root.rglob("*.md")))} Markdown; frontmatter v{version}; evals {len(cases)} casos.')
