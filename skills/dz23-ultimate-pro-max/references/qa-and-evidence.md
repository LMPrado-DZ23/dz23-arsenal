# QA, evidência e segurança da interface

## Baseline
Registrar commit, branch, comandos, versões, falhas preexistentes, telas críticas e ambiente. Nunca classificar falha como upstream sem reproduzir.

## Matriz por fluxo
UI -> evento -> API/IPC -> validação -> auth/RBAC/tenant -> persistência -> leitura -> feedback -> teste E2E -> evidência. Para ação crítica, testar duplicação, concorrência, erro de rede e reabertura.

## Verificações
- Código: lint, typecheck, unit, integration, API, build, security scanning pertinente.
- Visual: screenshots desktop/tablet/mobile e comparação antes/depois, overflow, truncamento, foco, contraste, densidade, modais.
- Acessibilidade: axe quando disponível + inspeção manual de teclado, leitor de tela, zoom 200%, reflow, reduced-motion e labels.
- Segurança: XSS, IDOR, CSRF conforme sessão, SSRF em fetch de mídia, uploads, autorização server-side/IPC e isolamento tenant.
- Performance: bundle, request waterfall, render, imagens, CLS, medidas antes/depois com ambiente idêntico.
- Resiliência: offline, timeout, erro 4xx/5xx, empty, loading, retry e feedback real.

## Evidência mínima
Comando executado, código de saída, resumo do resultado, captura com viewport, log de console/rede e hash/commit quando aplicável. Não alegar browser testado sem navegador. Estado PASS, PARTIAL, FAIL, NOT_TESTED ou BLOCKED_BY_EXTERNAL_DEPENDENCY.

## Critérios de bloqueio
Falha de autorização, perda de dados, botão enganoso, regressão funcional crítica, dados inventados ou teste obrigatório não realizado impedem PASS do escopo.
