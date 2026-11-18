# Instala todas as skills DZ23 em ~/.agents/skills/
# Uso: .\scripts\install-all.ps1 [-Force] [-DryRun]
#
# Nao sobrescreve skill existente, a menos que -Force seja passado.
# -DryRun mostra o que faria, sem copiar.

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$skillsRoot = Join-Path $PSScriptRoot '..\skills'
$destino = Join-Path $env:USERPROFILE '.agents\skills'

if (-not (Test-Path $skillsRoot)) {
    Write-Error "Pasta de skills nao encontrada: $skillsRoot"
    exit 1
}

if (-not (Test-Path $destino)) {
    if ($DryRun) {
        Write-Host "[dry-run] criaria $destino" -ForegroundColor Cyan
    } else {
        New-Item -ItemType Directory -Force -Path $destino | Out-Null
        Write-Host "Criado: $destino" -ForegroundColor Green
    }
}

$instaladas = 0
$skipped = 0
$falhas = 0

# Ponteiro para o checkout. Uma skill instalada em ~/.agents/skills nao consegue achar
# o arsenal contando niveis de diretorio (o repo pode estar em outro disco), e sem isso
# as checagens comuns do validate_skill.py sao puladas com WARN silencioso. Provar com:
#   Get-Content ~\.agents\skills\.dz23-arsenal
$ponteiro = Join-Path $destino '.dz23-arsenal'
if (-not $DryRun) {
    try {
        Set-Content -Path $ponteiro -Value (Resolve-Path (Join-Path $PSScriptRoot '..')).Path `
            -Encoding ascii -NoNewline
        Add-Content -Path $ponteiro -Value '' -Encoding ascii
        Write-Host "Ponteiro gravado: $ponteiro" -ForegroundColor DarkGray
    } catch {
        Write-Host "AVISO: nao foi possivel gravar $ponteiro -> $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Get-ChildItem -Path $skillsRoot -Directory | Sort-Object Name | ForEach-Object {
    $nome = $_.Name
    if ($nome -eq 'README.md') { return }

    $alvo = Join-Path $destino $nome

    if ((Test-Path $alvo) -and -not $Force) {
        Write-Host "SKIP (ja existe): $nome" -ForegroundColor Yellow
        $skipped++
        return
    }

    $versao = '?'
    $arqVersao = Join-Path $_.FullName 'VERSION'
    if (Test-Path $arqVersao) { $versao = (Get-Content $arqVersao -Raw).Trim() }

    if ($DryRun) {
        Write-Host "[dry-run] copiaria $nome v$versao -> $alvo" -ForegroundColor Cyan
        return
    }

    try {
        if ((Test-Path $alvo) -and $Force) {
            Remove-Item $alvo -Recurse -Force
        }
        Copy-Item -Path $_.FullName -Destination $alvo -Recurse -Force
        Write-Host "OK: $nome v$versao" -ForegroundColor Green
        $instaladas++
    } catch {
        Write-Host "FALHA: $nome -> $($_.Exception.Message)" -ForegroundColor Red
        $falhas++
    }
}

Write-Host ''
Write-Host "Instaladas: $instaladas | Puladas: $skipped | Falhas: $falhas"

if ($instaladas -gt 0 -or $skipped -gt 0) {
    Write-Host ''
    Write-Host 'Verifique com:' -ForegroundColor Cyan
    Write-Host '  python scripts/audit-zips.py'
    Write-Host '  pwsh scripts/verify-cli.ps1'
}

if ($falhas -gt 0) { exit 1 }
exit 0
