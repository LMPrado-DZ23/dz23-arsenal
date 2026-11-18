#!/usr/bin/env bash
# Instala todas as skills DZ23 em ~/.agents/skills/
# Uso: ./scripts/install-all.sh [--force] [--dry-run]
#
# Nao sobrescreve skill existente, a menos que --force seja passado.

set -uo pipefail

FORCE=0
DRY=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --dry-run) DRY=1 ;;
    -h|--help)
      echo "uso: $0 [--force] [--dry-run]"
      exit 0
      ;;
    *) echo "argumento desconhecido: $arg" >&2; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="$SCRIPT_DIR/../skills"
DEST="${HOME}/.agents/skills"

if [ ! -d "$SKILLS_ROOT" ]; then
  echo "ERRO: pasta de skills nao encontrada: $SKILLS_ROOT" >&2
  exit 1
fi

if [ ! -d "$DEST" ]; then
  if [ "$DRY" -eq 1 ]; then
    echo "[dry-run] criaria $DEST"
  else
    mkdir -p "$DEST"
    echo "Criado: $DEST"
  fi
fi

instaladas=0
skipped=0
falhas=0

# Ponteiro para o checkout (mesmo motivo da versao .ps1): a skill instalada precisa
# localizar o arsenal para rodar as checagens comuns do validate_skill.py.
if [ "$DRY" -eq 0 ]; then
  if ARSENAL="$(cd "$SCRIPT_DIR/.." && pwd)" && printf '%s\n' "$ARSENAL" > "$DEST/.dz23-arsenal"; then
    echo "Ponteiro gravado: $DEST/.dz23-arsenal"
  else
    echo "AVISO: nao foi possivel gravar $DEST/.dz23-arsenal" >&2
  fi
fi

for dir in "$SKILLS_ROOT"/*/; do
  [ -d "$dir" ] || continue
  nome="$(basename "$dir")"
  alvo="$DEST/$nome"

  if [ -d "$alvo" ] && [ "$FORCE" -eq 0 ]; then
    echo "SKIP (ja existe): $nome"
    skipped=$((skipped + 1))
    continue
  fi

  versao="?"
  [ -f "$dir/VERSION" ] && versao="$(tr -d '[:space:]' < "$dir/VERSION")"

  if [ "$DRY" -eq 1 ]; then
    echo "[dry-run] copiaria $nome v$versao -> $alvo"
    continue
  fi

  if [ -d "$alvo" ] && [ "$FORCE" -eq 1 ]; then
    rm -rf "$alvo"
  fi

  if cp -R "$dir" "$alvo" 2>/dev/null; then
    echo "OK: $nome v$versao"
    instaladas=$((instaladas + 1))
  else
    echo "FALHA: $nome" >&2
    falhas=$((falhas + 1))
  fi
done

echo
echo "Instaladas: $instaladas | Puladas: $skipped | Falhas: $falhas"

if [ "$instaladas" -gt 0 ] || [ "$skipped" -gt 0 ]; then
  echo
  # Não apontar para script que não existe. A versão anterior mandava rodar
  # `bash scripts/verify-cli.sh`, e esse arquivo nunca foi escrito -- só existe o .ps1. Quem
  # seguia o passo recebia "No such file or directory" no fim de uma instalação bem-sucedida,
  # e `python3` também falha em alguns ambientes Windows (Git-bash sem Python no PATH).
  # As duas verificações reais são as abaixo; a de CLI é opcional e documentada em cli/.
  echo "Verifique com:"
  echo "  python3 scripts/audit-zips.py    # ou: py -3 / python, conforme o ambiente"
  echo "  pwsh scripts/verify-cli.ps1      # Windows (a contagem de CLIs em cli/verify.md)"
  echo "  # Linux/macOS não têm verify-cli.sh; use o one-liner de cli/verify.md"
fi

[ "$falhas" -gt 0 ] && exit 1
exit 0
