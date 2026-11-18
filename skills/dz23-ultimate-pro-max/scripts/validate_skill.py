import sys
from pathlib import Path
import re, sys
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

required = ['SKILL.md','README.md','PROMPT-ATIVACAO.txt',
'references/installation.md','references/quality-gates.md',
'references/visual-direction.md','references/legacy-v1.md',
'references/art-direction-playbook.md','references/component-system.md',
'references/b3po-workspaces.md','references/qa-and-evidence.md']
missing = [x for x in required if not (root/x).is_file()]
s = (root/'SKILL.md').read_text(encoding='utf-8')
assert s.startswith('---\n') and re.search(r'(?m)^name: dz23-ultimate-pro-max$',s)
assert not missing, 'Arquivos ausentes: '+', '.join(missing)
for f in root.rglob('*.md'):
    assert f.read_text(encoding='utf-8').strip(), f'Vazio: {f}'
print(f'PASS: {len(required)} arquivos obrigatórios; {len(list(root.rglob("*.md")))} arquivos Markdown; frontmatter válido.')
