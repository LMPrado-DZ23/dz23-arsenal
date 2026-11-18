import sys
from pathlib import Path
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
        assert not _erros_comuns, ("checagens comuns falharam:\n  - "
                                   + "\n  - ".join(_erros_comuns))

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
