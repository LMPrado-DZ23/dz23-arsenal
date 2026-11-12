#!/usr/bin/env pwsh
# Registra o MCP `pentagi` nos harnesses desta maquina. Idempotente.
# O token NAO e copiado: os configs apontam para PENTAGI_TOKEN_FILE (segredo em um lugar so).
[CmdletBinding()]
param(
  [string]$TokenFile = "D:\IA-Workspace\Deepseek\projects\pentagi\api-token.txt",
  [string]$Url = "https://127.0.0.1:8443",
  [string]$ServerJs = "D:\IA-Workspace\Deepseek\projects\pentagi-mcp\src\index.js",
  [string]$DshPatch = "D:\IA-Workspace\Deepseek\.dsh\profiles\desktop\cordis.patch.yml"
)

$nodeExe = (Get-Command node).Source
Write-Host "== pre-checagens =="
Write-Host "  node    : $nodeExe"
Write-Host "  server  : $ServerJs"
Write-Host "  token   : $TokenFile"
Write-Host "  url     : $Url"
if (-not (Test-Path $TokenFile)) { Write-Host "ERRO: token ausente em $TokenFile" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $ServerJs)) { Write-Host "ERRO: server ausente em $ServerJs" -ForegroundColor Red; exit 1 }

# ---------------------------------------------------------------- DSH
Write-Host "`n== DSH =="
if (Test-Path $DshPatch) {
  $texto = Get-Content $DshPatch -Raw
  if ($texto -match 'mcp-pentagi') {
    Write-Host "  ja registrado"
  } else {
    $linhas = @(
      ''
      '# PentAGI: pentest autonomo self-hosted. Ponte MCP sobre a API GraphQL; token fica em arquivo.'
      '- insert:'
      '    - id: mcp-pentagi'
      "      name: '@deepseek-ai/dsh-mcp-client'"
      '      config:'
      '        serverName: pentagi'
      '        transport: stdio'
      '        command: node'
      "        args: [ '$ServerJs' ]"
      '        env:'
      "          PENTAGI_URL: '$Url'"
      "          PENTAGI_TOKEN_FILE: '$TokenFile'"
      '        toolCallTimeoutMs: 300000'
    )
    Add-Content -Path $DshPatch -Value $linhas -Encoding UTF8
    Write-Host "  bloco mcp-pentagi anexado (reinicie o DSH para carregar)" -ForegroundColor Yellow
  }
} else { Write-Host "  patch do perfil nao encontrado: $DshPatch" -ForegroundColor Yellow }

# ---------------------------------------------------------------- Codex
Write-Host "`n== Codex CLI =="
$codex = Join-Path $env:USERPROFILE ".codex\config.toml"
if (Test-Path $codex) {
  if ((Get-Content $codex -Raw) -match '\[mcp_servers\.pentagi\]') {
    Write-Host "  ja registrado"
  } else {
    $linhas = @(
      ''
      '[mcp_servers.pentagi]'
      'command = "node"'
      "args = [`"$ServerJs`"]"
      'startup_timeout_sec = 60'
      ''
      '[mcp_servers.pentagi.env]'
      "PENTAGI_URL = `"$Url`""
      "PENTAGI_TOKEN_FILE = `"$TokenFile`""
    )
    Add-Content -Path $codex -Value $linhas -Encoding UTF8
    Write-Host "  registrado (vale no proximo codex)"
  }
} else { Write-Host "  config ausente" -ForegroundColor Yellow }

# ---------------------------------------------------------------- Claude Code
Write-Host "`n== Claude Code =="
$claude = Join-Path $env:USERPROFILE ".claude.json"
if (Test-Path $claude) {
  $json = Get-Content $claude -Raw | ConvertFrom-Json
  $tem = ($json.PSObject.Properties.Name -contains 'mcpServers') -and
         ($json.mcpServers.PSObject.Properties.Name -contains 'pentagi')
  if ($tem) {
    Write-Host "  ja registrado"
  } else {
    if ($json.PSObject.Properties.Name -notcontains 'mcpServers') {
      $json | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{})
    }
    $entrada = [pscustomobject][ordered]@{
      type    = 'stdio'
      command = $nodeExe
      args    = @($ServerJs)
      env     = [pscustomobject][ordered]@{ PENTAGI_URL = $Url; PENTAGI_TOKEN_FILE = $TokenFile }
    }
    $json.mcpServers | Add-Member -NotePropertyName pentagi -NotePropertyValue $entrada -Force
    $json | ConvertTo-Json -Depth 32 | Set-Content $claude -Encoding UTF8
    Write-Host "  registrado"
  }
} else { Write-Host "  config ausente" -ForegroundColor Yellow }

# ---------------------------------------------------------------- outros
Write-Host "`n== outros harnesses (nao instalados aqui) =="
$snippets = Join-Path $PSScriptRoot 'harnesses-snippets.txt'
if (Test-Path $snippets) {
  $txt = (Get-Content $snippets -Raw).Replace('<SERVER_JS>', $ServerJs).Replace('<URL>', $Url).Replace('<TOKEN_FILE>', $TokenFile)
  Write-Host $txt
}

Write-Host "`n== resumo =="
Write-Host "  selftest sem harness: node scripts/selftest.js  (nesta pasta)"
Write-Host "  DSH: reiniciar o app para o MCP aparecer na sessao"
exit 0
