# Kubernetes e orquestração

## Deployment mínimo
```yaml
spec:
  replicas: 3
  strategy: {type: RollingUpdate, rollingUpdate: {maxUnavailable: 0, maxSurge: 1}}
  template:
    spec:
      securityContext: {runAsNonRoot: true, seccompProfile: {type: RuntimeDefault}}
      containers:
        - name: app
          image: registry/app@sha256:...        # digest, não tag
          resources:
            requests: {cpu: 100m, memory: 256Mi}
            limits:   {cpu: 500m, memory: 512Mi}
          readinessProbe: {httpGet: {path: /ready, port: 8080}, initialDelaySeconds: 5, periodSeconds: 5}
          livenessProbe:  {httpGet: {path: /health, port: 8080}, initialDelaySeconds: 15, periodSeconds: 10}
          securityContext: {allowPrivilegeEscalation: false, readOnlyRootFilesystem: true, capabilities: {drop: ["ALL"]}}
```

## Probe: a diferença que evita outage
- **Readiness** = pode receber tráfego? Falso remove do Service. Use para dependência essencial e inicialização.
- **Liveness** = está travado? Falso reinicia o pod. **Nunca** aponte liveness para dependência externa (banco lento → restart em cascata).
- **Startup** para boot longo; evita `initialDelaySeconds` gigante.
- Probe que sempre responde 200 (health fake) é pior que nenhum: dá falsa segurança.

## Recursos
- `requests` define agendamento; `limits` define teto. Sem requests, o scheduler chuta e o nó fica instável.
- CPU limit baixo causa throttling silencioso — prefira limit alto ou ausente com requests realistas; memória **sempre** com limit (evita OOM do nó).
- HPA exige requests definidos e métrica correta (CPU/RPS/custom).

## Disponibilidade
- `PodDisruptionBudget` (`minAvailable` ou `maxUnavailable`) para não derrubar tudo em drain.
- `topologySpreadConstraints`/anti-affinity para não concentrar réplicas num nó.
- `terminationGracePeriodSeconds` + `preStop` com drain de conexão.
- `replicas: 1` em produção é risco declarado, não configuração.

## Namespace e isolamento
- Um namespace por ambiente/domínio; `ResourceQuota` e `LimitRange` no namespace.
- NetworkPolicy default-deny + liberar o necessário.
- Sem `kubectl apply` manual em produção: GitOps (Argo CD/Flux) ou pipeline como única via.

## Comandos úteis
```bash
kubectl rollout status deploy/app -w
kubectl rollout history deploy/app
kubectl describe pod <pod>            # eventos e motivo do restart
kubectl logs <pod> --previous         # crash anterior
kubectl top pods                      # consumo real vs requests
kubectl get events --sort-by=.lastTimestamp
```

## Critério de saída
(a) digest no manifesto; (b) readiness e liveness corretos; (c) requests e limits; (d) PDB e spread; (e) securityContext restritivo; (f) deploy só por pipeline/GitOps.
