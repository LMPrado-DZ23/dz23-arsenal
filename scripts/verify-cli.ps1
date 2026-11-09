# verify-cli.ps1 — lista CLIs disponiveis e faltando nesta maquina.
# Uso: pwsh scripts/verify-cli.ps1 [-Json] [-Quiet]
#
# Nao instala nada. Usa Get-Command (presenca no PATH), nao prova funcionamento.

[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$Quiet
)

$categorias = [ordered]@{
    'VCS'        = @('git', 'gh', 'svn')
    'Runtimes'   = @('node', 'npm', 'npx', 'pnpm', 'bun', 'deno', 'python', 'python3', 'py', 'pip', 'uv', 'java', 'dotnet', 'go', 'rustc', 'cargo')
    'Containers' = @('docker', 'docker-compose', 'podman', 'kubectl', 'helm', 'k9s', 'terraform', 'tofu', 'act', 'hadolint')
    'Seguranca'  = @('trivy', 'gitleaks', 'semgrep', 'bandit', 'snyk', 'openssl')
    'Dados'      = @('psql', 'mysql', 'mongosh', 'redis-cli', 'sqlite3', 'jq')
    'Web'        = @('curl', 'wget', 'httpie', 'http', 'grpcurl', 'playwright', 'scrapling')
    'Build'      = @('make', 'cmake', 'gcc', 'g++', 'clang', 'mvn', 'gradle')
    'Binario'    = @('objdump', 'readelf', 'strings', 'nm', 'strip', 'ghidra', 'qemu-system-arm')
    'Rede'       = @('nmap', 'tcpdump', 'netstat')
    'Produtividade' = @('rg', 'fd', 'bat', 'fzf', 'lazygit', 'delta', 'eza', 'nvim', 'code', '7z', 'ffmpeg')
    'Sistema'    = @('pwsh', 'powershell', 'winget', 'wsl', 'ssh', 'scp', 'tar', 'bash')
}

$resultado = [ordered]@{}
$disponiveis = 0
$faltando = 0

foreach ($cat in $categorias.Keys) {
    $linhas = @()
    foreach ($cmd in $categorias[$cat]) {
        $existe = [bool](Get-Command $cmd -ErrorAction SilentlyContinue)
        if ($existe) { $disponiveis++ } else { $faltando++ }
        $linhas += [pscustomobject]@{ cli = $cmd; disponivel = $existe }
    }
    $resultado[$cat] = $linhas
}

if ($Json) {
    $saida = [ordered]@{
        maquina     = $env:COMPUTERNAME
        data        = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssK')
        disponiveis = $disponiveis
        faltando    = $faltando
        categorias  = $resultado
    }
    $saida | ConvertTo-Json -Depth 6
    exit 0
}

if (-not $Quiet) {
    Write-Host "=== CLIs por categoria ===" -ForegroundColor Cyan
    Write-Host "(Get-Command; presenca no PATH, nao prova funcionamento)" -ForegroundColor DarkGray
    Write-Host ''

    foreach ($cat in $resultado.Keys) {
        Write-Host "[$cat]" -ForegroundColor White
        foreach ($item in $resultado[$cat]) {
            if ($item.disponivel) {
                $pode = 'OK   '
                $cor = 'Green'
            } else {
                $pode = 'FALTA'
                $cor = 'DarkYellow'
            }
            Write-Host ("  {0} {1}" -f $pode, $item.cli) -ForegroundColor $cor
        }
        Write-Host ''
    }

    Write-Host ("Disponiveis: {0} | Faltando: {1}" -f $disponiveis, $faltando) -ForegroundColor Cyan
    Write-Host ''
    Write-Host "Ver o que instalar: cli/recommended.md" -ForegroundColor Gray
    Write-Host "Ver o que cada skill exige: cli/required.md" -ForegroundColor Gray
}

# exit 1 se faltar alguma das obrigatorias
$obrigatorias = @('git', 'python', 'node', 'rg', 'jq', 'curl')
$faltamObrigatorias = $obrigatorias | Where-Object { -not (Get-Command $_ -ErrorAction SilentlyContinue) }

if ($faltamObrigatorias) {
    if (-not $Quiet) {
        Write-Host ''
        Write-Host ("OBRIGATORIAS AUSENTES: {0}" -f ($faltamObrigatorias -join ', ')) -ForegroundColor Red
    }
    exit 1
}

exit 0
