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
  echo "Verifique com:"
  echo "  python3 scripts/audit-zips.py"
  echo "  bash scripts/verify-cli.sh"
fi

[ "$falhas" -gt 0 ] && exit 1
exit 0
