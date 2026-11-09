# Terraform AWS VPC

**Autor:** terraform-aws-modules
**Repo:** https://github.com/terraform-aws-modules/terraform-aws-vpc
**Licença:** Apache-2.0 (verificar no repositório)

## O que faz

O módulo canônico de VPC para AWS em Terraform: subnets públicas/privadas, NAT gateway, route tables,
flow logs, endpoints de VPC e as combinações de alta disponibilidade entre AZs. É o módulo mais usado do
registro Terraform para AWS.

Usar o módulo em vez de escrever a VPC à mão evita a classe de erro mais cara em cloud: subnet com rota
errada, AZ única, NAT em subnet pública.

## Por que usar em conjunto com DZ23

| Skill DZ23 | Papel |
|---|---|
| `dz23-devops-cloud-deployer` | pipeline, imagem, deploy progressivo, rollback, backup 3-2-1 |
| **Terraform AWS VPC** | a camada de rede como código, testada por milhares de usuários |

A skill DZ23 sabe **quando** provisionar, **como** validar e **como** reverter; o módulo entrega a rede
pronta e revisada. Escrever VPC do zero é onde o agente mais erra.

## Instalação

Não é skill de agente — é módulo Terraform. Uso via bloco `module`:

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "app-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = false   # uma NAT por AZ = mais caro, mais disponível
  enable_dns_hostnames = true
  enable_flow_log      = true    # auditoria de tráfego
}
```

```bash
terraform init
terraform plan
terraform apply
```

## Exemplo de uso com o agente

```
"Provisiona a VPC de produção usando o módulo oficial, 3 AZs, NAT por AZ, flow logs ligados.
 Antes do apply, me mostra o plan e o custo estimado. Não aplica sem eu confirmar."
```

## Alternativas

- `terraform-aws-modules/vpc` (este) — padrão de fato.
- OpenTofu — fork compatível; o módulo funciona.
- Módulos internos da sua organização — se existirem, siga o padrão interno.

## Cuidados

- **`terraform apply` é ação destrutiva em potencial.** Peça plan e confirmação; nunca aplique
  automaticamente em produção.
- **NAT gateway é o item mais caro** de uma VPC. `single_nat_gateway = true` economiza e reduz
  disponibilidade — é trade-off, declare.
- `terraform` **não está instalado** nesta máquina (ver `cli/recommended.md`); sem ele, a skill declara
  `BLOCKED_BY_EXTERNAL_DEPENDENCY`.
- Estado do Terraform contém dado sensível: nunca commitar `*.tfstate`.
