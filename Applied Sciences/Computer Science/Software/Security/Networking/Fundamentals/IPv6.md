---
title: "IPv6"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2025-05-04"
---

# IPv6

IPv6 est la nouvelle version du protocole Internet, conçue pour remplacer IPv4 qui manque d'adresses. Là où IPv4 offre ~4 milliards d'adresses, IPv6 en offre **340 undécillions** (340 × 10³⁶) — de quoi adresser chaque grain de sable de la Terre plusieurs fois.

## Format d'une adresse IPv6

Une adresse IPv6 = **128 bits**, écrite en **8 blocs de 16 bits** séparés par `:`, en hexadécimal.

```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

### Règles d'écriture simplifiée

**1. Omettre les zéros en tête dans chaque bloc**
```
2001:0db8:85a3:0000:0000:8a2e:0370:7334
→ 2001:db8:85a3:0:0:8a2e:370:7334
```

**2. Remplacer une ou plusieurs suites de blocs `0000` par `::`** (une seule fois par adresse)
```
2001:db8:85a3:0:0:8a2e:370:7334
→ 2001:db8:85a3::8a2e:370:7334
```

## Types d'adresses IPv6

| Type               | Préfixe     | Description                          |
| ------------------ | ----------- | ------------------------------------ |
| **Global Unicast** | `2000::/3`  | Équivalent des IP publiques IPv4     |
| **Link-Local**     | `fe80::/10` | Réseau local seulement, non routable |
| **Loopback**       | `::1`       | Équivalent de `127.0.0.1`            |
| **Multicast**      | `ff00::/8`  | Envoi à un groupe de machines        |
| **Unspecified**    | `::`        | Équivalent de `0.0.0.0`              |

## Différences clés avec IPv4

|               | IPv4                           | IPv6                                           |
| ------------- | ------------------------------ | ---------------------------------------------- |
| Taille        | 32 bits                        | 128 bits                                       |
| Notation      | Décimale pointée (192.168.1.1) | Hexadécimale (2001:db8::1)                     |
| Broadcast     | Oui                            | Non (remplacé par multicast)                   |
| NAT           | Nécessaire (manque d'adresses) | Inutile (adresses en abondance)                |
| Configuration | Manuel ou DHCP                 | Auto-configuration (SLAAC)                     |
| En-tête       | Complexe                       | Simplifié et fixe                              |
| IPSec         | Optionnel                      | Intégré nativement                             |
| ARP           | Oui                            | Remplacé par NDP (Neighbor Discovery Protocol) |

## Auto-configuration (SLAAC)

En IPv6, une machine peut se configurer **toute seule** sans DHCP :
1. Elle génère une adresse link-local (`fe80::` + son adresse MAC modifiée)
2. Elle contacte le routeur pour obtenir le préfixe réseau
3. Elle combine le préfixe + son identifiant MAC → adresse globale unique

## Commandes utiles

```bash
# Voir ses adresses IPv6 (Linux)
ip -6 addr show
ip addr show | grep inet6

# Ping IPv6
ping6 ::1                    # Loopback
ping6 fe80::1%eth0           # Link-local (préciser l'interface)
ping6 2001:db8::1

# Table de routage IPv6
ip -6 route show

# Windows
ipconfig                     # Affiche aussi les adresses IPv6
ping ::1
netsh interface ipv6 show addresses
```

## Coexistence IPv4 / IPv6

Pendant la transition, plusieurs mécanismes permettent aux deux protocoles de coexister :
- **Dual Stack** : machine configurée en IPv4 et IPv6 simultanément
- **Tunneling** : encapsuler IPv6 dans IPv4 (6to4, Teredo)
- **NAT64** : traduction entre IPv6 et IPv4
