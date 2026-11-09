# Anti-padrões de DevSecOps e deploy

Cada item: **sintoma** → **por que dói** → **correção**.

## Imagem e build
1. **`FROM node:latest`** → build muda sem commit mudar → pin por digest.
2. **Roda como root** → container comprometido vira root no host (com falha de isolamento) → `USER` numérico + securityContext.
3. **Imagem com toolchain** → 1,2 GB, mais CVE → multi-stage + distroless.
4. **Segredo em `ARG`/`ENV`** → aparece no `docker history` → secret em runtime.
5. **Build diferente por ambiente** → o que passou no gate não é o que roda → um build, promoção por digest.
6. **`COPY . .` antes das deps** → cache inútil, build lento → copiar lockfile primeiro.

## Pipeline
7. **Gate que só avisa** → falha conhecida convive com verde → gate bloqueia.
8. **Rebuild após aprovação** → artefato novo, sem teste → promover o mesmo digest.
9. **Cache servindo branch errado** → dependência fantasma → chave de cache por lockfile.
10. **Repetir job de teste até passar** → mascara flake e bug → repetir só falha de infra.
11. **Credencial de admin no CI** → compromisso do CI = compromisso da nuvem → OIDC + menor privilégio.

## Config e segredo
12. **Config no código** → deploy por ambiente exige rebuild → config por ambiente.
13. **App sobe com config inválida** → falha em runtime, difícil de diagnosticar → validar e abortar no boot.
14. **Segredo em `ConfigMap`** → legível por qualquer pod do namespace → `Secret`/secret manager.
15. **Rotação sem plano** → troca quebra o app → reload vs restart documentado.

## Kubernetes
16. **Liveness apontando para o banco** → banco lento reinicia todos os pods → liveness só do processo.
17. **Readiness sempre 200** → pod sem dependência recebe tráfego → readiness real.
18. **Sem requests/limits** → agendamento aleatório, OOM do nó → requests realistas + limit de memória.
19. **`replicas: 1` em produção** → qualquer drain derruba → ≥ 2 + PDB.
20. **`kubectl apply` manual em prod** → deriva do Git, ninguém sabe o que roda → GitOps.
21. **Sem `terminationGracePeriodSeconds`** → conexão cortada no deploy → drain + preStop.

## Deploy
22. **Deploy sem critério de sucesso** → ninguém sabe se melhorou → SLO e métrica comparadas.
23. **Rollback nunca testado** → descobre na hora do incidente → ensaio em staging.
24. **Rollout sem `progressDeadlineSeconds`** → trava para sempre sem alarme → definir prazo.
25. **Canary sem métrica por versão** → impossível comparar → label de versão em métrica/log.
26. **Deploy na sexta sem janela** → incidente sem time → janela e plantão declarados.

## Dados
27. **Migração destrutiva antes do código** → rollback de app quebra → expand/contract.
28. **Backup nunca restaurado** → desastre descoberto no desastre → restore ensaiado.
29. **Delete de namespace/PVC "por limpeza"** → perda irreversível → confirmação explícita + lista.

## Observabilidade
30. **Log sem versão** → não se sabe qual release falhou → `git_sha` no log e no `/health`.
31. **Alerta para tudo** → ruído, ninguém olha → alerta acionável no SLO.
32. **Painel sem erro por versão** → regressão invisível → métrica segmentada por versão.
33. **Debug ligado em produção** → log gigante e PII → nível adequado + amostragem.

## Supply chain
34. **Sem SBOM** → não se sabe o que está exposto → gerar no build.
35. **CVE crítica publicada** → vulnerabilidade conhecida em produção → scan bloqueante + exceção com prazo.
36. **Imagem sem rebuild há meses** → base desatualizada → rebuild agendado.

## Borda, rede e host (Gemini)
37. **Porta publicada em `0.0.0.0`** (`"5432:5432"`) → o Docker escreve no `iptables` e **ignora o UFW**; o banco fica exposto na internet mesmo com `ufw deny` → rede interna ou bind em `127.0.0.1:5432:5432`.
38. **Compose sem `internal_net`** → DB/cache alcançáveis de qualquer container e sem segmentação → rede `internal: true` para estado.
39. **Container sem `max-size` de log** → `*-json.log` cresce até encher o disco, corrompendo banco e derrubando o host → `max-size: "10m"` + `max-file: "5"`.
40. **`npm start` como PID 1** → npm não repassa SIGTERM; container é morto com SIGKILL após 10 s e derruba requisição → `CMD ["node", "dist/server.js"]` ou `init: true`.
41. **`ARG` de build com segredo** → fica gravado no `docker history` da imagem → injetar em runtime (secret/env do orquestrador).
42. **Readiness que não checa o banco** → pod recebe tráfego e quebra na primeira query → `/readyz` com DB/cache/serviço essencial.
43. **`terraform apply` sem `plan`** → mudança não revisada, inclusive `destroy` → plan obrigatório, revisão humana em produção.
44. **Ação de CI pinada por tag** (`uses: org/action@v4`) → tag pode ser movida, executa código novo sem revisão → pin por SHA completo.
45. **Backup sem restore ensaiado** → desastre descoberto no desastre → restaurar em ambiente separado e medir tempo.
46. **Migração sem expand/contract** → rollback do app falha contra schema novo → expand → code → backfill → contract.
47. **Rollback não testado** → descobre o tempo real no incidente → ensaio em staging com tempo medido.
48. **`latest` em produção** → deploy pode puxar artefato diferente do testado → digest imutável.

## Como usar
Na revisão do diff/pipeline, percorra a lista: **não se aplica / aplicado / pendente com risco**. Achado vira issue com severidade de `references/quality-gates.md`.
