---
title: "Networking Fundamentals (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, networking, pentest, pnpt]
date: "2026-05-18"
---
# Networking Fundamentals

Comprendre le réseau, ce n'est pas mémoriser des couches, c'est savoir devant un paquet, à quel niveau il vit et qui peut l'intercepter. Un pentester qui connaît mal OSI confond une attaque ARP (couche 2) avec une attaque DNS (couche 7) et applique les mauvaises contre-mesures.

## Modèle OSI : qui parle à qui

Chaque couche s'appuie sur celle du dessous et ne sait rien des autres. Quand un paquet HTTP traverse le réseau, il est progressivement encapsulé puis désencapsulé.

```
Émission (descend)                       Réception (remonte)
─────────────────                        ────────────────────
[7] HTTP "GET /"                         [7] HTTP "GET /"
[6] TLS (chiffre)                        [6] TLS (déchiffre)
[5] Session                              [5] Session
[4] TCP (port 443, séquence, ACK)        [4] TCP (réassemble)
[3] IP (10.0.0.1 → 8.8.8.8)             [3] IP (vérifie destination)
[2] Ethernet (MAC src → MAC dst)         [2] Ethernet (vérifie MAC)
[1] Signal électrique                    [1] Signal électrique
        │                                        ▲
        └──── câble / fibre / radio ─────────────┘
```

| Couche | Nom          | Exemples                  | Surface d'attaque typique        |
| ------ | ------------ | ------------------------- | -------------------------------- |
| 7      | Application  | HTTP, FTP, SSH, DNS, SMTP | Injections, auth, logique métier |
| 6      | Présentation | SSL/TLS, JPEG, ASCII      | TLS downgrade, padding oracle    |
| 5      | Session      | NetBIOS, RPC              | Détournement de session          |
| 4      | Transport    | TCP, UDP                  | Scan de ports, SYN flood         |
| 3      | Réseau       | IP, ICMP                  | Spoofing IP, routage             |
| 2      | Liaison      | Ethernet, ARP, MAC        | ARP poisoning, MAC flooding      |
| 1      | Physique     | Câbles, hubs              | Accès physique, tap réseau       |

**À retenir** : une attaque sur la couche N est invisible aux couches au-dessus. ARP poisoning intercepte tout HTTP non chiffré sans que l'application ne voie rien.

## TCP vs UDP

TCP garantit la livraison, UDP non. Cette différence change tout — y compris la manière dont on les scanne.

```
TCP : 3-way handshake avant tout transfert

Client                    Serveur
  │  ───── SYN ─────►        │     "Je veux parler"
  │  ◄── SYN-ACK ────         │     "OK, je suis prêt"
  │  ───── ACK ─────►        │     "Bien reçu, on commence"
  │                          │
  │ ◄══ données utiles ══►   │

UDP : on envoie, et on espère

Client                    Serveur
  │  ─── datagramme ──►      │     pas de réponse garantie
```

**Conséquence pratique** : un scan TCP voit clairement les ports ouverts (SYN-ACK reçu). Un scan UDP est lent et imprécis — si rien ne répond, le port peut être ouvert OU filtré.

## Ports courants

À mémoriser : voir un port, savoir le service, savoir l'enjeu en pentest.

| Port  | Service        | Pourquoi c'est intéressant en pentest          |
|-------|----------------|-------------------------------------------------|
| 21    | FTP            | Souvent anonymous, transmission en clair        |
| 22    | SSH            | Brute force, clés faibles                       |
| 23    | Telnet         | Tout en clair — credentials sniffables          |
| 25    | SMTP           | User enumeration (VRFY/EXPN), relay ouvert      |
| 53    | DNS            | Zone transfer, DNS exfil                        |
| 80    | HTTP           | Vulnérabilités web                              |
| 88    | Kerberos       | AS-REP Roasting, Kerberoasting                  |
| 110   | POP3           | Credentials en clair sans TLS                   |
| 135   | MSRPC          | Énumération RPC Windows                         |
| 139   | NetBIOS        | Énumération SMB legacy                          |
| 389   | LDAP           | Énumération AD complète                         |
| 443   | HTTPS          | Vulnérabilités web (TLS chiffre, pas protège)   |
| 445   | SMB            | EternalBlue, shares ouverts, relay NTLM         |
| 636   | LDAPS          | LDAP chiffré                                    |
| 3306  | MySQL          | Brute force, mots de passe par défaut           |
| 3389  | RDP            | BlueKeep, brute force                           |
| 5985  | WinRM (HTTP)   | Exécution distante Windows (evil-winrm)         |
| 5986  | WinRM (HTTPS)  | Idem en chiffré                                 |

## Subnetting : combien d'adresses

Le masque indique combien de bits sont fixes (réseau) et combien sont libres (hôtes).

```
192.168.1.0/24
─────┬───── ─┬
réseau (24 bits fixes) → hôtes : 32-24 = 8 bits libres = 256 adresses

Calcul rapide :
  /24 → 256 adresses    (2^8)
  /25 → 128 adresses    (2^7)
  /26 →  64 adresses
  /27 →  32 adresses
  /28 →  16 adresses
  /29 →   8 adresses
  /30 →   4 adresses    (lien point-à-point)
```

**Adresses non utilisables** : la première (adresse réseau) et la dernière (broadcast). Donc `/24` = 254 hôtes utilisables, pas 256.

### Plages privées (RFC 1918)

Ces plages ne sont pas routées sur Internet. Si tu vois ces IPs sur ton scan externe, il y a NAT.

- `10.0.0.0/8`        → grandes infrastructures
- `172.16.0.0/12`     → réseau d'entreprise classique (Docker l'utilise aussi)
- `192.168.0.0/16`    → réseaux domestiques

## Pièges courants

- **TCP open ≠ service exploitable** : un port 22 ouvert ne dit rien de la version SSH ni de l'auth acceptée. Toujours fingerprinter (`nmap -sV`).
- **UDP "open|filtered"** : nmap ne sait pas trancher sans réponse. Utiliser `--script` pour les services UDP courants (SNMP, DNS, NTP, IPMI).
- **HTTPS ne protège que la couche 7** : un attaquant en MITM ARP voit toujours les destinations (SNI dans le ClientHello, IPs, tailles de paquets).
- **NAT ne sécurise pas** : c'est de la traduction d'adresses, pas un pare-feu. Beaucoup confondent.
- **Le routeur par défaut est .1 par convention, pas par règle** — sur des réseaux mal configurés, la passerelle peut être .254 ou autre.
