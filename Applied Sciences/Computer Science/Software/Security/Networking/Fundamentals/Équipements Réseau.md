---
title: "Équipements Réseau"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2026-02-22"
---

# Équipements Réseau

## Équipements réseau

### Hub

- Layer 1 (Physique)
- Broadcast à tous les ports
- Collision domain partagé

### Switch

- Layer 2 (Data Link)
- MAC address table
- Chaque port = collision domain
- VLAN capable

### Router

- Layer 3 (Réseau)
- Routing entre réseaux
- NAT, firewall
- ACLs

### Firewall

**Types**
- Packet filtering
- Stateful inspection
- Application layer (WAF)
- Next-gen (NGFW)

**Règles**
```
ALLOW src:192.168.1.0/24 dst:any port:80,443
DENY src:any dst:any port:23
```

## Cisco IOS — Modes CLI

Cisco IOS organise ses commandes en plusieurs modes d'accès. La commande `?` liste les commandes disponibles dans le mode courant.

| Mode | Prompt | Accès | Commandes disponibles |
|------|--------|-------|----------------------|
| **User EXEC** | `Router>` | Accès initial | Commandes de statut de base, pas de redémarrage |
| **Privileged EXEC** | `Router#` | `enable` (depuis User EXEC) | Toutes les commandes EXEC, configuration, débogage |
| **Global Configuration** | `Router(config)#` | `configure terminal` (depuis Privileged) | Configuration à effet global sur l'appareil |
| **Interface Configuration** | `Router(config-if)#` | `interface <type><num>` | Configuration d'une interface spécifique |
| **ROMMON** | `>` ou `rommon1>` | Break/Ctrl-C pendant le boot | Boot, tests matériels, récupération |
| **Setup** | Dialog texte | Automatique si pas de config | Configuration initiale guidée |

```cisco
! Passage entre les modes
Router>enable                    ! → Privileged EXEC
Router#configure terminal        ! → Global Configuration
Router(config)#interface gi0/0   ! → Interface Configuration
Router(config-if)#end            ! → Privileged EXEC (Ctrl+Z équivalent)

! Sécuriser l'accès Privileged
Router(config)#enable secret MonMotDePasse

! Sauvegarde de la configuration
Router#copy running-config startup-config
Router#write memory              ! équivalent
```

### Débogage et logging

```cisco
! Activer le debug (prudence en production)
Router#debug ip routing

! Configurer le logging vers un serveur syslog
Router(config)#logging host 192.168.1.100
Router(config)#logging trap 7          ! niveau 7 = tout (debug)
Router(config)#logging trap warnings   ! niveau 4

! Vérifier les logs
Router#show logging
```

## VLANs

Un VLAN (Virtual Local Area Network) divise logiquement un switch physique en plusieurs réseaux isolés. Inventé par David Sincoskie en 1998, standardisé IEEE 802.1Q.

### Fonctionnement

Chaque trame Ethernet se voit ajouter un **VLAN Tag** (4 octets) contenant l'identifiant du VLAN. Le switch ne transmet les trames qu'aux ports appartenant au même VLAN.

### Types de VLAN

| Type | Rôle |
|------|------|
| Default VLAN | VLAN initial avant toute configuration (VLAN 1) |
| Native VLAN | VLAN utilisé pour les trames sans VLAN Tag |
| Data VLAN | VLAN pour les trames des équipements utilisateurs |
| Management VLAN | VLAN pour l'administration réseau (priorité élevée) |
| Voice VLAN | VLAN pour la téléphonie IP (priorité maximale) |

### Configuration Cisco

```cisco
! Créer un VLAN
Switch(config)#vlan 10
Switch(config-vlan)#name Comptabilite

! Assigner un port en mode access
Switch(config)#interface FastEthernet0/1
Switch(config-if)#switchport mode access
Switch(config-if)#switchport access vlan 10

! Configurer un port trunk (interconnexion switches)
Switch(config)#interface GigabitEthernet0/1
Switch(config-if)#switchport mode trunk
Switch(config-if)#switchport trunk allowed vlan 10,20,30

! Vérification
Switch#show vlan brief
Switch#show interfaces trunk
```

### Inter-VLAN Routing

Les VLANs étant isolés, la communication entre eux nécessite un routeur ou un switch de couche 3 :

**Router-on-a-stick** (sous-interfaces sur un routeur) :
```cisco
Router(config)#interface GigabitEthernet0/0.10
Router(config-subif)#encapsulation dot1Q 10
Router(config-subif)#ip address 192.168.10.1 255.255.255.0

Router(config)#interface GigabitEthernet0/0.20
Router(config-subif)#encapsulation dot1Q 20
Router(config-subif)#ip address 192.168.20.1 255.255.255.0
```

## STP — Spanning Tree Protocol

STP (IEEE 802.1D) prévient les boucles de commutation dans les topologies redondantes.

### Fonctionnement

STP bloque les liens redondants tout en maintenant une connexion physique de secours. En cas de défaillance du lien actif, le lien bloqué est réactivé.

### Types de ports STP

| Type | Rôle |
|------|------|
| Root Port | Port offrant le meilleur chemin vers le Root Bridge |
| Designated Port | Port transmettant le trafic vers un segment |
| Alternate Port | Port bloqué, remplaçant en cas de panne |
| Disabled Port | Port administrativement désactivé |

### États des ports STP

| État | BPDU | Trafic |
|------|------|--------|
| Blocking | Reçoit uniquement | Non |
| Listening | Reçoit et envoie | Non |
| Learning | Reçoit et envoie | Non (apprend MAC) |
| Forwarding | Reçoit et envoie | Oui |
| Disabled | Aucun | Non |

### Configuration Cisco

```cisco
! Activer PVST+
Switch(config)#spanning-tree mode pvst

! Activer Rapid PVST+ (convergence plus rapide)
Switch(config)#spanning-tree mode rapid-pvst

! Définir le Root Bridge principal
Switch(config)#spanning-tree vlan 10,20 root primary

! Définir le Root Bridge secondaire
Switch(config)#spanning-tree vlan 10,20 root secondary

! Activer PortFast et BPDUGuard sur un port d'accès
Switch(config)#interface FastEthernet0/1
Switch(config-if)#spanning-tree portfast
Switch(config-if)#spanning-tree bpduguard enable

! Vérification
Switch#show spanning-tree
```

## EtherChannel — Link Aggregation

EtherChannel combine plusieurs ports physiques en un seul lien logique, augmentant la bande passante et offrant la redondance.

### Protocoles de négociation

| Protocole | Type | Description |
|-----------|------|-------------|
| PAgP | Propriétaire Cisco | Port Aggregation Protocol |
| LACP | Standard IEEE 802.3ad | Link Aggregation Control Protocol |

### Configuration Cisco

```cisco
! EtherChannel avec LACP
Switch(config)#interface range FastEthernet0/1-2
Switch(config-if-range)#channel-protocol lacp
Switch(config-if-range)#channel-group 1 mode active

! Vérification
Switch#show etherchannel summary
```

## DHCP

### Configuration serveur DHCP sur routeur Cisco

```cisco
! Exclure des adresses du pool
Router(config)#ip dhcp excluded-address 192.168.1.1 192.168.1.10

! Créer le pool DHCP
Router(config)#ip dhcp pool LAN
Router(dhcp-config)#network 192.168.1.0 255.255.255.0
Router(dhcp-config)#default-router 192.168.1.1
Router(dhcp-config)#dns-server 8.8.8.8
Router(dhcp-config)#domain-name exemple.local

! DHCP Relay (relayer vers un serveur distant)
Router(config)#interface GigabitEthernet0/0
Router(config-if)#ip helper-address 10.0.0.1

! Vérification
Router#show ip dhcp pool
Router#show ip dhcp binding
```
