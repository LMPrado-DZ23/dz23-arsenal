# Configuração e ambientes

## 12-factor aplicado
- **Config no ambiente**, não no código. Defaults seguros para dev; produção exige valor explícito.
- **Falhar cedo**: validar config na inicialização (schema) e abortar com mensagem clara. App que sobe com config inválida e falha em runtime é pior.
- **Sem paridade, sem confiança**: o mesmo artefato roda em dev/staging/prod mudando apenas config e secret.
- **Logs como stream**, sem arquivo local (container é efêmero).
- **Processo stateless**: estado em banco/objeto, não em disco do pod.

## Variável de ambiente
| Categoria | Exemplo | Regra |
|---|---|---|
| Não sensível | `LOG_LEVEL`, `PORT`, `FEATURE_X` | pode ficar no manifesto/compose |
| Endpoint | `DB_HOST`, `REDIS_URL` | por ambiente, nunca hardcode |
| Segredo | `DB_PASSWORD`, `API_KEY` | **nunca** em env público; usar secret manager/secret do cluster |
| Metadado | `GIT_SHA`, `BUILD_TIME` | injetado no build/deploy para rastreio |

`GIT_SHA` na resposta de `/health` e no log fecha a rastreabilidade do release.

## ConfigMap / Secret (k8s)
- `ConfigMap` para não sensível; `Secret` para sensível (e ainda assim: etcd não cifra por padrão — avalie encryption at rest + external secret operator).
- Montar `Secret` como volume em vez de `env` reduz exposição em `kubectl describe` e em crash dump.
- Rotação: quem troca, quando, como o app recarrega (reload vs restart).

## Ambientes
| Ambiente | Dados | Deploy | Acesso |
|---|---|---|---|
| dev | sintético/local | livre | time |
| staging | sintético/anonimizado | automático | time |
| produção | real | autorizado + progressivo | restrito |

Paridade mínima: mesma imagem, mesmo runtime, mesma versão de banco (major) — senão staging não prevê nada.

## Validação de config
```js
const required = ['DATABASE_URL','JWT_SECRET'];
const missing = required.filter(k => !process.env[k]);
if (missing.length) { console.error('config ausente:', missing.join(',')); process.exit(1); }
```
Nunca logar o **valor** de segredo; logar só a chave ausente.

## Critério de saída
(a) config fora do código; (b) validação na inicialização; (c) segredo só em secret manager/secret; (d) `GIT_SHA` exposto; (e) paridade de imagem confirmada.
