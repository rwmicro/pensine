---
title: "Terraform — Fiche Technique"
domain: "Applied Sciences"
subdomain: "Computer Science > DevSecOps > Terraform"
tags: [sciences-appliquées, informatique, devsecops, terraform]
date: "2025-05-04"
---

# Terraform — Fiche Technique

Terraform (HashiCorp) est un outil d'**Infrastructure as Code** (IaC) qui permet de provisionner et gérer des ressources cloud de manière déclarative et reproductible.

### Commandes utiles `v1.8`
- `terraform init` -> initialisation de la config
- `terraform validate` -> Validation de la config
- `terraform plan` -> Visualiser les modifications qui seront appliquées
- `terraform apply` -> Appliquer les modifications
- `terraform destroy` -> Détruire les modifications
- `terraform fmt` -> Formater les fichiers `.tf` à la syntaxe Terraform
- `terraform output`
   - Extraire les valeurs des sorties définies dans le fichier de configuration.
- `terraform refresh`
   - Met à jour l'état local de Terraform en synchronisation avec l'état réel de l'infrastructure, ce qui peut changer en raison des actions externes ou des modifications directes.

### Parties d'un fichier de configuration Terraform

1. **Provider**
   - Spécifie le fournisseur de service cloud (comme AWS, Azure, GCP) et configure les détails nécessaires pour l'accès. Chaque provider peut gérer un ensemble de ressources.

   ```hcl
   provider "aws" {
     region = "us-west-2"
   }
   ```

2. **Resource**
   - Déclare une ou plusieurs ressources que Terraform doit gérer. Chaque ressource est associée à un type et à un nom, suivis de plusieurs paramètres.

   ```hcl
   resource "aws_instance" "my_instance" {
     ami           = "ami-123456"
     instance_type = "t2.micro"
   }
   ```

3. **Variable**
   - Les variables permettent de personnaliser les configurations sans altérer le code principal. Les valeurs peuvent être fournies par différents moyens, y compris des fichiers de variables ou des variables d'environnement.

   ```hcl
   variable "instance_type" {
     description = "Type of instance"
     default     = "t2.micro"
   }
   ```

4. **Output**
   - Les sorties définissent des données qui doivent être affichées après l'application du plan. Cela peut inclure des adresses IP, des identifiants de ressources, et d'autres informations importantes.

   ```hcl
   output "instance_ip" {
     value = aws_instance.my_instance.public_ip
   }
   ```

5. **Module**
   - Les modules permettent de regrouper et de réutiliser des configurations. Un module peut être appelé par d'autres configurations Terraform.

   ```hcl
   module "network" {
     source = "./modules/network"
     vpc_id = "vpc-123456"
   }
   ```

6. **Data Sources**
   - Les sources de données permettent à Terraform de faire usage d'informations configurées ou générées en dehors de Terraform mais nécessaires à la gestion des ressources.

   ```hcl
   data "aws_ami" "example" {
     most_recent = true

     owners = ["self"]
     tags = {
       Name = "app-server"
     }
   }
   ```

Cette structure permet de configurer et de gérer l'infrastructure de manière efficace et prévisible, en adaptant l'environnement aux besoins spécifiques de chaque projet ou organisation.
