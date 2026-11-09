from pathlib import Path
import re, sys
root = Path(__file__).resolve().parents[1]
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
