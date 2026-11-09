#!/usr/bin/env bash
# Preflight: reporta disponibilidade das CLIs de deploy/scan nesta máquina.
# Não instala nada. Não falha o pipeline — é relatório (exit 0 sempre).
set -u

ok=0
fail=0

check() {
  local name="$1" cmd="$2"
  local out
  if out=$(eval "$cmd" 2>/dev/null | head -1) && [ -n "$out" ]; then
    echo "PASS  ${name}: ${out}"
    ok=$((ok+1))
  else
    echo "FAIL  ${name}: indisponível"
    fail=$((fail+1))
  fi
}

echo "=== Preflight — CLIs de DevSecOps ==="
check "docker"    "docker --version"
check "podman"    "podman --version"
check "kubectl"   "kubectl version --client 2>/dev/null | head -1"
check "helm"      "helm version --short"
check "terraform" "terraform version | head -1"
check "tofu"      "tofu version | head -1"
check "trivy"     "trivy --version"
check "gitleaks"  "gitleaks version"
check "semgrep"   "semgrep --version"

echo
echo "=== Contexto (quando disponível) ==="
command -v kubectl >/dev/null 2>&1 && echo "kubectl context: $(kubectl config current-context 2>/dev/null || echo '(sem contexto)')"
command -v docker  >/dev/null 2>&1 && echo "docker context : $(docker context show 2>/dev/null || echo '(sem contexto)')"

echo
echo "RESULT: ${ok} PASS, ${fail} FAIL"
echo "Nota: ferramenta ausente => declare BLOCKED_BY_EXTERNAL_DEPENDENCY na etapa que depende dela."
exit 0
