"""validate_skill.py — dz23-autonomous-improvement-ultimate.

Esta é a skill que orquestra os `/goal` e define o contrato de evidência do arsenal, e
era a única sem validador próprio. O `quality-gate.py` costumava reportar "sem
validate_skill.py (pulado)" como OK, então ela podia perder seção obrigatória ou ter
evals quebrados sem que nenhum check percebesse.

Checa o que é específico desta skill, além das checagens comuns do arsenal:
  - as marcas estruturais que o SKILL.md promete ao leitor;
  - o anti-loop (teto de tentativas) continua escrito, porque é a regra central;
  - a matriz de requisitos e o vocabulário de estados de evidência;
  - os references/ que o SKILL.md declara existir;
  - o estado declarado em ROADMAP/CHANGELOG não contradiz o VERSION.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

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
    print("WARN: _achar_arsenal ausente - checagens comuns puladas")
    importar_validador_comum = None
if importar_validador_comum is not None:
    _validar_comum = importar_validador_comum(Path(__file__).resolve())
    if _validar_comum is None:
        print("WARN: arsenal nao localizado - checagens comuns puladas")
    else:
        _erros_comuns = _validar_comum(root, exigir_version_file=False)
        if _erros_comuns:
            # `assert` nao serve para gate: python -O remove a instrucao e o validador
            # passa a imprimir OK com referencia quebrada -- reproduzido nas dez skills
            # desta sessao. Um verificador que desaparece por uma flag do interpretador e
            # pior que a ausencia dele, porque continua parecendo conferido.
            for e in _erros_comuns:
                print(f"FALHA: {e}", file=sys.stderr)
            raise SystemExit(1)

REQUIRED_REFS = [
    'adversarial-review.md',
    'checkpoint-and-resume.md',
    'diagnostic-playbook.md',
    'goal-integration.md',
    'quality-gates.md',
]
REQUIRED_TEMPLATES = ['acceptance.md', 'state.md']
REQUIRED_TOP = ['SKILL.md', 'README.md', 'CHANGELOG.md', 'VERSION', 'INSTALL.md']

missing = [x for x in REQUIRED_TOP if not (root / x).is_file()]
missing += [f'references/{x}' for x in REQUIRED_REFS if not (root / 'references' / x).is_file()]
missing += [f'templates/{x}' for x in REQUIRED_TEMPLATES if not (root / 'templates' / x).is_file()]
assert not missing, 'Arquivos ausentes: ' + ', '.join(missing)

s = (root / 'SKILL.md').read_text(encoding='utf-8')

# A skill declara estas marcas no corpo; removê-las quebra quem depende delas para saber
# quando parar e o que conta como prova. Os nomes abaixo são as seções reais do SKILL.md.
MARCAS_OBRIGATORIAS = [
    '## Missão e limites',
    '## Precedência',
    '## Modos de execução',
    '## Fluxo obrigatório',
    '## Referências',
    '## Roteamento com as outras skills',
    'NOT_TESTED',
    'baseline',
]
for marca in MARCAS_OBRIGATORIAS:
    assert re.search(re.escape(marca), s, re.I), f'marca estrutural ausente no SKILL.md: {marca!r}'

# Regra central da skill: teto de tentativas antes de trocar de via. Sem isto ela vira
# loop infinito queimando tokens — o defeito que a seção existe para prevenir.
m_teto = re.search(r'(?:3|três)\s+(?:tentativas|rodadas|iterações)', s, re.I)
assert m_teto, ('a regra de anti-loop (teto de tentativas antes de nova via) sumiu do '
                'SKILL.md — é a razão de ser da skill')

# Vocabulário de estados: a skill não pode introduzir grafia própria e divergir do
# resto do arsenal. Observado: ela usava NOT_RUN enquanto as outras nove usam NOT_TESTED.
# A checagem original só procurava `\bNOT_[A-Z_]+\b` e por isso NÃO viu `UNVERIFIED`, um
# estado rival sem o prefixo NOT -- exatamente o tipo de caso que deveria denunciar
# (rodada 50).
#
# Dois erros meus corrigidos aqui na mesma rodada, ambos achados pela prova:
# - `assert`: sob `python -O` a linha inteira desaparece e a checagem vira decorativa. Este
#   arquivo era justamente o lugar onde a rodada 19 trocou assert por SystemExit; ao escrever
#   a checagem nova eu reintroduzi o padrão banido.
# - lista de prefixos (NOT|UN|BLOCKED|...): um rótulo inventado como `PENDING` nao comecando por
#   nenhum deles passava. O sinal certo e qualquer token em CAIXA ALTA usado como veredito dentro
#   de crase, comparado contra a lista FECHADA do vocabulario deste arsenal.
_rotulos = set(re.findall(r"`([A-Z][A-Z0-9_]{3,})`", s))
permitidos = {
    "NOT_TESTED", "NOT_RECOVERED", "UNAVAILABLE", "MISCONFIGURED", "AVAILABLE",
    "PASS", "FAIL", "PARTIAL", "BLOCKED", "STATUS",
    "BLOCKED_BY_EXTERNAL_DEPENDENCY", "SESSION_LIMIT_REACHED", "NEEDS_APPROVAL",
    "VERIFIED_COMPLETE", "CRITICAL", "HIGH", "MEDIUM", "LOW", "BLOCKER",
    # rotulos que nao sao vereditos: aparecem em crase por serem nomes de campo, sigla ou
    # marcador de rastreabilidade. A lista e fechada e curta de proposito -- cada item aqui
    # precisa ser justificado, senao o verificador vira colecao de excecoes.
    "REQ", "OBS", "ID", "SQL", "API", "UX", "UI", "CI", "RUM", "SLO", "N+1", "TODO", "FIXME",
}
estranhos = {r for r in _rotulos if r not in permitidos and not re.match(r"REQ-\d", r)}
if estranhos:
    print(f"FALHA: estados de evidência fora do vocabulário do arsenal: "
          f"{sorted(estranhos)} — use NOT_TESTED", file=sys.stderr)
    raise SystemExit(1)

# O CHANGELOG precisa documentar a versão corrente, senão VERSION avança e o histórico
# fica mentindo sobre o que mudou.
versao = (root / 'VERSION').read_text(encoding='utf-8').strip()
fm_versao = re.search(r'(?m)^version:\s*(\S+)', s)
if fm_versao:
    assert fm_versao.group(1) == versao, (f'frontmatter version={fm_versao.group(1)} != '
                                          f'VERSION={versao}')
changelog = (root / 'CHANGELOG.md').read_text(encoding='utf-8')
# Formato real do histórico nesta skill: "## [2.1.4] — data" (keep-a-changelog), não "v2.1.4".
assert re.search(rf'(?m)^#+\s*\[?v?{re.escape(versao)}\]?', changelog), (
    f'CHANGELOG.md não tem entrada para a versão corrente {versao}')

print(f'PASS: {len(REQUIRED_REFS)} references + {len(REQUIRED_TEMPLATES)} templates; '
      f'{len(list(root.rglob("*.md")))} Markdown; v{versao}; anti-loop e vocabulário OK.')
