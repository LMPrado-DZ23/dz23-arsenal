# Auditoria de infraestrutura

## Antes de qualquer mudança
Inventarie e registre o estado atual. Sem inventário, o "deploy" vira tentativa.

## Inventário obrigatório
| Item | O que registrar |
|---|---|
| Stack | linguagem, versão, runner, build tool |
| Containers | serviços, imagem, portas publicadas, volumes, networks |
| Orquestração | Compose version, cluster, namespace, contexto kubectl |
| Volumes | nomeado vs bind mount; quem é stateful |
| Portas | o que está em `0.0.0.0` e o que está em `127.0.0.1` |
| Redes | `edge_net` × `internal_net`; quem fala com quem |
| Registries | privado/público, imutabilidade de tag |
| CI/CD | workflow, permissões, secrets usados |
| Cloud | conta, região, IAM, DNS, certificado |
| Health | `/healthz`, `/readyz`, probe configurada |
| Backup | frequência, destino, último restore ensaiado |
| Rollback | comando, última versão estável, tempo |

## Blast radius
Classifique cada mudança por alcance:

| Nível | Exemplo | Consequência se falhar |
|---|---|---|
| Serviço | deploy de 1 app | queda parcial |
| Nó/host | limite de recurso, driver de log | derruba vizinhos |
| Cluster | RBAC, ingress, CNI | queda ampla |
| Conta/rede | firewall, DNS, IAM | indisponibilidade total |
| Dado | migração, drop, rotação de segredo | perda irreversível |

## Threat model (curto)
- **Portas expostas**: o que responde de fora? `0.0.0.0:5432` é incidente esperando.
- **Privilégios**: root no container? `privileged`? capabilities extras? `hostPath`?
- **Proveniência**: imagem de onde? tag mutável? assinada?
- **TLS**: certificado válido, renovação automática, HSTS.
- **Supply chain**: dependência sem pin, Action por tag, base sem digest.
- **RBAC**: service account com permissão ampla? CI com role de admin?
- **Isolamento de tenant**: um namespace por cliente ou tudo junto?

## Matriz de prioridade
| Tier | Conteúdo |
|---|---|
| **P0** | indisponibilidade total, vazamento de dado, perda irreversível, exposição de credencial |
| **P1** | degradação relevante, falha de autorização, backup não restaurável |
| **P2** | higiene (tag, log, limite), dívida de observabilidade |

## Saída da auditoria
Lista de riscos com: item, evidência (comando/saída), tier, ação proposta e reversibilidade. Riscos P0
bloqueiam o deploy até resolver ou aceitar por escrito.
