---
title: "VPC — Virtual Private Cloud"
domain: "Applied Sciences"
subdomain: "Computer Science > AWS"
tags: [sciences-appliquées, informatique, aws]
date: "2026-02-25"
---

# VPC — Virtual Private Cloud

Un VPC est un réseau virtuel privé dans AWS, logiquement isolé des autres réseaux AWS. Il fournit un contrôle total sur l'environnement réseau : plages d'adresses IP, sous-réseaux, tables de routage, passerelles.

## Concepts de base réseau

### Notation CIDR

CIDR (Classless Inter-Domain Routing) note un bloc d'adresses IP sous la forme `adresse/préfixe`.

```
10.0.0.0/16 → 65 536 adresses (10.0.0.0 à 10.0.255.255)
10.0.1.0/24 → 256 adresses (10.0.1.0 à 10.0.1.255)
10.0.1.0/28 → 16 adresses (10.0.1.0 à 10.0.1.15)

/préfixe → nombre d'adresses = 2^(32 - préfixe)
/16 → 2^16 = 65 536
/24 → 2^8  = 256
/28 → 2^4  = 16
```

**AWS réserve 5 adresses par sous-réseau** : réseau (.0), routeur VPC (.1), DNS (.2), futur (.3), broadcast (.255).

### Plages d'adresses privées (RFC 1918)

```
10.0.0.0/8      → 10.0.0.0 à 10.255.255.255
172.16.0.0/12   → 172.16.0.0 à 172.31.255.255
192.168.0.0/16  → 192.168.0.0 à 192.168.255.255
```

Recommandation AWS : utiliser `10.0.0.0/16` pour le VPC et `/24` pour les sous-réseaux.

## Composants d'un VPC

### Sous-réseaux (Subnets)

Un sous-réseau est une subdivision du VPC dans une Availability Zone.

**Public subnet** : a une route vers Internet Gateway. Les ressources avec une IP publique sont accessibles depuis internet.

**Private subnet** : pas de route directe vers Internet Gateway. Les ressources n'ont pas d'IP publique et ne sont pas accessibles depuis internet (mais peuvent accéder à internet via NAT).

**Isolated subnet** : pas de route vers internet dans aucune direction. Pour les bases de données, les ressources les plus sensibles.

```bash
# Créer un VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
    --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=mon-vpc}]'

# Créer des sous-réseaux
aws ec2 create-subnet \
    --vpc-id vpc-12345 \
    --cidr-block 10.0.1.0/24 \
    --availability-zone eu-west-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-1a}]'

aws ec2 create-subnet \
    --vpc-id vpc-12345 \
    --cidr-block 10.0.10.0/24 \
    --availability-zone eu-west-1a \
    --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-1a}]'
```

### Internet Gateway (IGW)

Permet la communication bidirectionnelle entre le VPC et internet. Hautement disponible et redondant par nature (géré par AWS).

```bash
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --internet-gateway-id igw-12345 --vpc-id vpc-12345
```

### NAT Gateway

Permet aux ressources dans un subnet privé d'initier des connexions vers internet (mises à jour, téléchargements) sans être accessibles de l'extérieur.

```bash
# Allouer une IP Elastic (IP publique fixe)
aws ec2 allocate-address --domain vpc

# Créer le NAT Gateway dans un subnet PUBLIC
aws ec2 create-nat-gateway \
    --subnet-id subnet-public-1a \
    --allocation-id eipalloc-12345
```

**NAT Gateway vs NAT Instance** :

| Critère | NAT Gateway | NAT Instance |
|---|---|---|
| Gestion | Entièrement managé AWS | Auto-géré |
| Disponibilité | Haute disponibilité native | Une seule instance |
| Performance | Jusqu'à 100 Gbit/s | Limité par le type d'instance |
| Prix | ~0.045$/h + transfert | Instance EC2 + transfert |

Préférer NAT Gateway sauf pour des besoins de contrôle très spécifiques.

### Tables de routage

Chaque sous-réseau a une table de routage qui détermine où le trafic est envoyé.

```bash
# Créer une table de routage pour les subnets publics
aws ec2 create-route-table --vpc-id vpc-12345

# Route par défaut vers internet via IGW
aws ec2 create-route \
    --route-table-id rtb-public \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id igw-12345

# Associer au subnet public
aws ec2 associate-route-table \
    --route-table-id rtb-public \
    --subnet-id subnet-public-1a

# Table de routage pour subnets privés (via NAT Gateway)
aws ec2 create-route \
    --route-table-id rtb-private \
    --destination-cidr-block 0.0.0.0/0 \
    --nat-gateway-id nat-12345
```

## Architecture 3 tiers typique

```
Internet
    │
    ▼
[Internet Gateway]
    │
    ├── Subnet Public 1a (10.0.1.0/24)       ├── Subnet Public 1b (10.0.2.0/24)
    │   [ALB]  [NAT GW]  [Bastion]            │   [ALB]  [NAT GW]
    │
    ├── Subnet Private 1a (10.0.10.0/24)      ├── Subnet Private 1b (10.0.11.0/24)
    │   [EC2 App Servers]                      │   [EC2 App Servers]
    │
    └── Subnet Isolated 1a (10.0.20.0/24)     └── Subnet Isolated 1b (10.0.21.0/24)
        [RDS Primary]                              [RDS Standby]
```

## NACL vs Security Groups

| Dimension | NACL | Security Group |
|---|---|---|
| Niveau | Sous-réseau | Instance (ENI) |
| Stateful | Non (stateless) | Oui (stateful) |
| Règles Allow | Oui | Oui |
| Règles Deny | Oui | Non |
| Évaluation | Numéro de règle croissant | Toutes les règles |
| Par défaut | Tout autorisé | Tout refusé |

**Stateless NACL** : les règles entrantes et sortantes doivent être définies séparément. Ex : pour une connexion HTTP entrante sur le port 80, il faut une règle entrante (port 80) ET une règle sortante pour les ports éphémères (1024-65535).

```bash
# Exemple NACL : bloquer une IP malveillante
aws ec2 create-network-acl-entry \
    --network-acl-id acl-12345 \
    --rule-number 50 \
    --protocol -1 \  # tout trafic
    --rule-action deny \
    --cidr-block 192.0.2.100/32 \
    --ingress
```

## VPC Peering

Connexion réseau privée entre deux VPCs (même ou comptes différents, même ou régions différentes).

```bash
aws ec2 create-vpc-peering-connection \
    --vpc-id vpc-local \
    --peer-vpc-id vpc-distant \
    --peer-region eu-west-2  # si cross-region

# Accepter la demande (côté destinataire)
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id pcx-12345

# Ajouter les routes dans chaque table de routage
aws ec2 create-route \
    --route-table-id rtb-12345 \
    --destination-cidr-block 10.1.0.0/16 \  # CIDR du VPC distant
    --vpc-peering-connection-id pcx-12345
```

**Limitation** : le peering n'est pas transitif. Si A est peeré avec B et B avec C, A ne voit pas C.

## Transit Gateway

Solution au problème de transitivité. Un hub central connecte plusieurs VPCs, réseaux on-premise et VPNs.

```
VPC-A ──┐
VPC-B ──┤── Transit Gateway ──── VPN Site-to-Site ──── Datacenter
VPC-C ──┘
```

## VPN Site-to-Site

Connecte un datacenter ou bureau on-premise à AWS via un tunnel VPN chiffré (IPsec).

```bash
# Créer un Customer Gateway (représente votre routeur on-premise)
aws ec2 create-customer-gateway \
    --type ipsec.1 \
    --public-ip 203.0.113.10 \
    --bgp-asn 65000

# Créer une Virtual Private Gateway
aws ec2 create-vpn-gateway --type ipsec.1
aws ec2 attach-vpn-gateway --vpn-gateway-id vgw-12345 --vpc-id vpc-12345

# Créer la connexion VPN
aws ec2 create-vpn-connection \
    --type ipsec.1 \
    --customer-gateway-id cgw-12345 \
    --vpn-gateway-id vgw-12345
```

## VPC Endpoints

Connexion privée aux services AWS sans passer par internet. Le trafic reste dans le réseau AWS.

**Gateway Endpoint** (gratuit) : S3 et DynamoDB.

```bash
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-12345 \
    --service-name com.amazonaws.eu-west-1.s3 \
    --route-table-ids rtb-private-1a rtb-private-1b
```

**Interface Endpoint** (payant) : tous les autres services AWS (SQS, SNS, ECR, Secrets Manager, SSM...). Crée une ENI avec une IP privée dans votre subnet.

```bash
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-12345 \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.eu-west-1.secretsmanager \
    --subnet-ids subnet-private-1a subnet-private-1b \
    --security-group-ids sg-endpoint
```

## Flow Logs

Capturent les informations sur le trafic IP dans le VPC. Stockés dans CloudWatch Logs ou S3.

```bash
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-12345 \
    --traffic-type ALL \  # ACCEPT, REJECT ou ALL
    --log-destination-type cloud-watch-logs \
    --log-group-name /vpc/flow-logs
```

Format d'un log : `version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status`

```
2 123456789012 eni-abc123 10.0.0.5 10.0.1.100 54321 443 6 20 4000 1705316400 1705316460 ACCEPT OK
```
