---
title: "NAT et ACL"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, sécurité, réseau, nat, acl]
date: "2026-04-07"
---

# NAT et ACL

## NAT — Network Address Translation

NAT est une technique permettant de faire communiquer plusieurs hôtes d'un réseau privé avec Internet en utilisant une seule (ou quelques) adresse(s) IP publique(s).

### Motivation

La pénurie d'adresses IPv4 publiques impose l'utilisation de plages d'adresses privées (RFC 1918) en interne. NAT traduit ces adresses privées en adresses publiques à la frontière du réseau.

### Terminologie NAT

| Terme | Définition |
|-------|-----------|
| Inside Local | Adresse IP privée d'un hôte interne |
| Inside Global | Adresse IP publique représentant l'hôte interne vers l'extérieur |
| Outside Local | Adresse d'un hôte externe vue depuis le réseau interne |
| Outside Global | Adresse IP réelle d'un hôte externe |

### Types de NAT

#### NAT Statique (Static NAT)

Correspondance un-pour-un permanente entre une adresse privée et une adresse publique. Utilisé pour exposer un serveur interne sur Internet.

```cisco
! Étape 1 : Définir la correspondance statique
Router(config)#ip nat inside source static 192.168.1.10 203.0.113.10

! Étape 2 : Marquer l'interface interne
Router(config)#interface GigabitEthernet0/0
Router(config-if)#ip nat inside

! Étape 3 : Marquer l'interface externe
Router(config)#interface GigabitEthernet0/1
Router(config-if)#ip nat outside
```

#### NAT Dynamique (Dynamic NAT)

Correspondance dynamique à partir d'un pool d'adresses publiques. Plusieurs hôtes internes peuvent utiliser les adresses du pool.

```cisco
! Étape 1 : Définir le pool d'adresses publiques
Router(config)#ip nat pool MON_POOL 203.0.113.10 203.0.113.20 netmask 255.255.255.0

! Étape 2 : Définir les adresses internes autorisées (via ACL)
Router(config)#access-list 1 permit 192.168.1.0 0.0.0.255

! Étape 3 : Associer l'ACL au pool
Router(config)#ip nat inside source list 1 pool MON_POOL

! Étapes 4-5 : Marquer les interfaces (même que statique)
```

#### PAT — Port Address Translation (NAT Overload)

Traduction de nombreuses adresses internes vers une seule adresse publique en différenciant les connexions par les numéros de port. C'est le NAT le plus courant (réseaux domestiques, entreprises).

```cisco
! Avec un pool
Router(config)#ip nat inside source list 1 pool MON_POOL overload

! Avec l'adresse de l'interface externe (plus simple)
Router(config)#ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

### Vérification NAT

```cisco
show ip nat translations       ! Table de traduction NAT
show ip nat statistics         ! Statistiques NAT
debug ip nat                   ! Débogage (attention en production)
clear ip nat translation *     ! Vider la table NAT
```

## ACL — Access Control List

Les ACLs filtrent le trafic réseau en autorisant ou refusant des paquets selon des critères définis (adresse source/destination, protocole, port).

### Types d'ACL

| Type | Numérotation | Critères de filtrage |
|------|-------------|---------------------|
| Standard | 1-99 et 1300-1999 | Adresse IP source uniquement |
| Étendue | 100-199 et 2000-2699 | Source, destination, protocole, port |
| Nommée | Nom textuel | Standard ou étendue avec nom |

### ACL Standard

Filtre uniquement sur l'adresse IP source. À placer **près de la destination** pour éviter de bloquer trop tôt.

```cisco
! Créer une ACL standard numérotée
Router(config)#access-list 10 permit 192.168.1.0 0.0.0.255
Router(config)#access-list 10 deny any

! Appliquer sur une interface
Router(config)#interface GigabitEthernet0/1
Router(config-if)#ip access-group 10 out
```

### ACL Étendue

Filtre sur source, destination, protocole et ports. À placer **près de la source** pour bloquer tôt.

```cisco
! Autoriser HTTP depuis 192.168.1.0/24 vers n'importe quelle destination
Router(config)#access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 80

! Autoriser HTTPS
Router(config)#access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 443

! Bloquer tout le reste
Router(config)#access-list 100 deny ip any any

! Appliquer en entrée sur l'interface interne
Router(config)#interface GigabitEthernet0/0
Router(config-if)#ip access-group 100 in
```

### ACL Nommée

Plus lisible, permet la suppression de lignes individuelles (contrairement aux ACLs numérotées).

```cisco
! Créer une ACL étendue nommée
Router(config)#ip access-list extended FILTRAGE_WEB
Router(config-ext-nacl)#permit tcp 192.168.1.0 0.0.0.255 any eq 80
Router(config-ext-nacl)#permit tcp 192.168.1.0 0.0.0.255 any eq 443
Router(config-ext-nacl)#deny ip any any log

! Appliquer
Router(config)#interface GigabitEthernet0/0
Router(config-if)#ip access-group FILTRAGE_WEB in
```

### Règles importantes

- Chaque ACL se termine implicitement par **deny any** (tout ce qui n'est pas explicitement autorisé est bloqué)
- Les règles sont évaluées dans l'ordre — la première correspondance gagne
- Une ACL **standard** doit être placée près de la **destination**
- Une ACL **étendue** doit être placée près de la **source**
- Une seule ACL par interface, par direction (in ou out)

### Vérification

```cisco
show access-lists              ! Afficher toutes les ACLs et compteurs
show ip interface GigabitEthernet0/0   ! Voir les ACLs appliquées
```

## WAN — Wide Area Network

### Technologies WAN

| Type | Description | Exemple |
|------|-------------|---------|
| Circuit Switched | Connexion établie par numérotation | ISDN |
| Packet Switched | Paquets routés via identifiants | Frame Relay, MPLS |
| Leased Line | Lien dédié point-à-point | PPP, HDLC |

### PPP — Point-to-Point Protocol

PPP est un protocole d'encapsulation pour les liaisons série point-à-point (couche 2). Il supporte les communications synchrones et asynchrones.

**Composants PPP** :
- **HDLC** : protocole de base pour l'encapsulation
- **LCP** (Link Control Protocol) : établit, configure et teste la connexion
- **NCP** (Network Control Protocol) : configure les protocoles de couche réseau

**Authentification PPP** :

| Protocole | Sécurité |
|-----------|---------|
| PAP (Password Authentication Protocol) | Faible — mot de passe en clair |
| CHAP (Challenge Handshake Authentication Protocol) | Fort — challenge/réponse MD5 |

```cisco
! Configuration PPP avec authentification CHAP
interface Serial0/1/0
 encapsulation ppp
 ppp authentication chap
 ppp chap hostname ROUTEUR_A
 ppp chap password MOT_DE_PASSE
```

### Frame Relay

Frame Relay est une technologie WAN à commutation de paquets utilisant des **circuits virtuels permanents (PVC)**. Identifiés par des **DLCI** (Data-Link Connection Identifier).

```cisco
! Configuration Frame Relay de base
interface Serial0/1/0
 encapsulation frame-relay
 frame-relay lmi-type ansi
 ip address 10.0.0.1 255.255.255.0
 frame-relay map ip 10.0.0.2 102 broadcast
```
