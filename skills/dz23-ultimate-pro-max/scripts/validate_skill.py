import sys
from pathlib import Path
import re, sys
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
