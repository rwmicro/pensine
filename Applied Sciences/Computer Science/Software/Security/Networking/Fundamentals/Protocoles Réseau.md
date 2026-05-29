---
title: "Protocoles Réseau"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > Fundamentals"
tags: [sciences-appliquées, informatique, sécurité, réseau]
date: "2026-02-25"
---

# Protocoles Réseau

Les protocoles réseau définissent les règles de communication entre systèmes. Cette note couvre les protocoles fondamentaux avec un focus sur leurs mécanismes, leurs ports, et leurs implications pour la sécurité.

## Modèle TCP/IP vs OSI

| Couche TCP/IP | Couche OSI | Protocoles | PDU |
|--------------|-----------|-----------|-----|
| Application | 7 Application, 6 Présentation, 5 Session | HTTP, DNS, SMTP, SSH, FTP | Message/Data |
| Transport | 4 Transport | TCP, UDP, SCTP | Segment/Datagramme |
| Internet | 3 Réseau | IP, ICMP, ARP, BGP | Paquet |
| Accès réseau | 2 Liaison, 1 Physique | Ethernet, WiFi (802.11), PPP | Trame/Bit |

## Protocoles de transport

### TCP (Transmission Control Protocol)

**Caractéristiques** : orienté connexion, fiable, ordonné, contrôle de flux et de congestion.

**Three-way handshake** :
```
Client → Serveur : SYN (seq=x)
Serveur → Client : SYN-ACK (seq=y, ack=x+1)
Client → Serveur : ACK (ack=y+1)
```

**Fermeture** :
```
Initiateur → Autre : FIN
Autre → Initiateur : ACK
Autre → Initiateur : FIN
Initiateur → Autre : ACK
État : TIME_WAIT (2×MSL = ~4 min)
```

**Drapeaux TCP** :

| Flag | Signification | Usage |
|------|--------------|-------|
| SYN | Synchronize | Initiation connexion |
| ACK | Acknowledge | Confirmation réception |
| FIN | Finish | Fermeture connexion |
| RST | Reset | Fermeture abrupte |
| PSH | Push | Envoyer immédiatement |
| URG | Urgent | Données urgentes |
| ECE | ECN-Echo | Congestion notification |
| CWR | Congestion Window Reduced | Fenêtre réduite |

**Numéros de séquence** : 32 bits, aléatoires à l'initialisation (ISN — Initial Sequence Number). Déterminent la fiabilité et l'ordre des données.

### UDP (User Datagram Protocol)

**Caractéristiques** : sans connexion, non fiable, pas d'ordre garanti, très rapide.

**En-tête UDP** : Source Port (2B), Dest Port (2B), Length (2B), Checksum (2B) = 8 bytes seulement.

**Usage préféré pour** :
- DNS (requêtes rapides, retry simple)
- DHCP
- NTP
- Streaming vidéo/audio (QUIC, RTP)
- Jeux vidéo online
- SNMP, TFTP

**Implications sécurité** : UDP ne valide pas l'IP source → utilisé pour les attaques d'amplification DDoS (DNS amplification, NTP monlist, Memcached).

## Fonctions de la couche Transport

La couche Transport (couche 4 du modèle OSI) assure la communication de bout en bout entre processus applicatifs.

### Fonctions clés

**Adressage** : utilisation des numéros de port pour identifier les applications destinataires.

**Livraison de bout en bout** : garantit que les données arrivent intégralement à la bonne destination.

**Contrôle de flux** : empêche l'émetteur d'envoyer plus de données que le récepteur peut absorber (fenêtre TCP).

**Multiplexage / Démultiplexage** :
- **Multiplexage** (couche Application → Transport) : regroupement de plusieurs flux applicatifs en segments avec leurs numéros de port.
- **Démultiplexage** (Transport → Application) : distribution des segments reçus aux bonnes applications selon le numéro de port.

**Livraison fiable** (TCP) : contrôle d'erreur, contrôle de séquence, contrôle de perte, contrôle de doublons.

### Comparaison TCP vs UDP

| Critère | TCP | UDP |
|---------|-----|-----|
| Connexion | Orienté connexion (3-way handshake) | Sans connexion |
| Fiabilité | Garantie (retransmission, ACK) | Non garantie |
| Ordre | Garanti (numéros de séquence) | Non garanti |
| Contrôle de flux | Oui (fenêtre glissante) | Non |
| Vitesse | Plus lent | Plus rapide |
| En-tête | 20-60 octets | 8 octets |
| Usage | HTTP, FTP, SMTP, SSH | DNS, DHCP, VoIP, streaming |

### Autres protocoles de transport

| Protocole | Sigle | Caractéristiques |
|-----------|-------|-----------------|
| DCCP | Datagram Congestion Control Protocol | Contrôle de congestion sans fiabilité |
| SCTP | Stream Control Transmission Protocol | Multihoming, multi-streaming |
| RDP | Reliable Data Protocol | Livraison fiable sans connexion |

### Numéros de port courants

| Port | Protocole | Service |
|------|-----------|---------|
| 20/21 | TCP | FTP (données/contrôle) |
| 22 | TCP | SSH |
| 23 | TCP | Telnet |
| 25 | TCP | SMTP |
| 53 | TCP/UDP | DNS |
| 67-68 | UDP | DHCP |
| 80 | TCP | HTTP |
| 110 | TCP | POP3 |
| 143 | TCP | IMAP |
| 443 | TCP | HTTPS |
| 3306 | TCP | MySQL |
| 5432 | TCP | PostgreSQL |
| 6379 | TCP | Redis |
| 27017 | TCP | MongoDB |

## Protocole IP

### IPv4

- Adresses 32 bits : `A.B.C.D` (ex: `192.168.1.1`)
- Notation CIDR : `/24` = 256 adresses, `/32` = 1 adresse
- Plages privées (RFC 1918) : `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
- TTL : limite le nombre de sauts (décrémenté par chaque routeur) → ICMP Time Exceeded à 0

**En-tête IPv4 (20 bytes minimum)** :
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |Type of Service|          Total Length         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|      Fragment Offset    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Time to Live |    Protocol   |         Header Checksum       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source Address                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination Address                        |
```

### IPv6

- Adresses 128 bits : `2001:0db8:85a3::8a2e:0370:7334`
- Pas de NAT (chaque device a une adresse globale unique)
- IPsec intégré (optionnel en pratique)
- NDP (Neighbor Discovery Protocol) remplace ARP
- Adresses link-local (`fe80::/10`), multicast, anycast

**Implications sécurité** : IPv6 souvent mal filtré par les firewalls, vecteur de bypass.

### ICMP (Internet Control Message Protocol)

**Types courants** :

| Type | Code | Description |
|------|------|-------------|
| 0 | 0 | Echo Reply (ping réponse) |
| 3 | 0-15 | Destination Unreachable |
| 5 | 0-3 | Redirect |
| 8 | 0 | Echo Request (ping) |
| 11 | 0 | Time Exceeded (TTL=0) |
| 12 | 0 | Parameter Problem |

**Usage sécurité** :
- `ping` : test de connectivité
- `traceroute` : chemin réseau (exploite TTL)
- ICMP Redirect : peut être exploité pour la redirection de trafic
- Covert channel : tunneler des données dans les champs ICMP data

## Protocoles d'application

### DNS (Domain Name System)

**Ports** : UDP/53 (requêtes standard), TCP/53 (transferts de zone, réponses > 512 bytes), DoT/853, DoH/443.

**Types d'enregistrements** :

| Type | Description | Exemple |
|------|-------------|---------|
| A | IPv4 address | `example.com → 93.184.216.34` |
| AAAA | IPv6 address | `example.com → 2606:2800::68` |
| CNAME | Canonical name (alias) | `www → example.com` |
| MX | Mail exchanger | `mail.example.com priority 10` |
| NS | Name server | `ns1.example.com` |
| PTR | Reverse lookup | `34.216.184.93.in-addr.arpa → example.com` |
| TXT | Text | SPF, DKIM, DMARC, domaine verification |
| SOA | Start of Authority | Serial, refresh, retry, expire |
| SRV | Service locator | `_sip._tcp.example.com` |
| CAA | Certificate Authority Authorization | Autoriser seulement Let's Encrypt |

**Hiérarchie DNS** :
```
. (root)
├── com
│   └── example.com (autoritative NS)
│       ├── www.example.com
│       └── mail.example.com
├── org
└── fr
```

**Résolution récursive** :
```
Client → Résolveur récursif (FAI ou 8.8.8.8)
Résolveur → Root NS → TLD NS (.com) → Autoritative NS
Autoritative NS → Résolveur → Client
```

**Sécurité DNS** :
- DNSSEC : signatures RRSIG, clés DNSKEY, chaîne de confiance jusqu'à la root
- DoH (DNS over HTTPS) : résolution via HTTPS, chiffre et masque les requêtes
- DoT (DNS over TLS) : résolution via TLS port 853
- DANE (DNS-based Authentication of Named Entities) : lier certificats TLS aux enregistrements DNS

### HTTP/HTTPS

Voir note dédiée : `Software/Web/HTTP en profondeur.md`

**Ports** : HTTP/80, HTTPS/443

**Méthodes et propriétés** :

| Méthode | Sûre | Idempotente | Cache |
|---------|------|------------|-------|
| GET | Oui | Oui | Oui |
| HEAD | Oui | Oui | Oui |
| POST | Non | Non | Non |
| PUT | Non | Oui | Non |
| DELETE | Non | Oui | Non |
| PATCH | Non | Non | Non |
| OPTIONS | Oui | Oui | Non |

### SSH (Secure Shell)

**Port** : 22/TCP

**Fonctionnalités** :
- Shell sécurisé chiffré (remplace Telnet/rsh)
- SFTP (transfert de fichiers)
- SCP (copie sécurisée)
- Tunneling (local, remote, dynamic)
- Agent forwarding

**Méthodes d'authentification** :
- Password (déconseillé)
- Public Key (clés RSA, ECDSA, Ed25519)
- Certificate-based
- GSSAPI/Kerberos

**Algorithmes** (openssh récent) :
```
Key Exchange: curve25519-sha256, ecdh-sha2-nistp256
Host Key: ssh-ed25519, rsa-sha2-512
Cipher: chacha20-poly1305, aes256-gcm
MAC: hmac-sha2-256, umac-128
```

**Configurations sécurisées** (`/etc/ssh/sshd_config`) :
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers user1 user2
MaxAuthTries 3
Protocol 2
X11Forwarding no
AllowTcpForwarding no  # si tunneling non requis
```

### TLS (Transport Layer Security)

**TLS 1.3 Handshake** (1.5 RTT) :
```
Client → Serveur : ClientHello (key_share, supported_ciphers)
Serveur → Client : ServerHello + Certificat + CertificateVerify + Finished
Client → Serveur : Finished
→ Application data
```

**Suites cryptographiques TLS 1.3** :
- `TLS_AES_256_GCM_SHA384`
- `TLS_CHACHA20_POLY1305_SHA256`
- `TLS_AES_128_GCM_SHA256`

**TLS 1.2 et antérieur** : déprécié (SHA-1, RC4, export ciphers). PCI DSS exige TLS 1.2 minimum depuis 2018.

**Vérification** :
```bash
openssl s_client -connect target.com:443 -tls1_3
nmap --script ssl-enum-ciphers -p 443 target.com
testssl.sh target.com
```

### SMTP/POP3/IMAP — Emails

| Protocole | Port | Chiffré | Usage |
|-----------|------|---------|-------|
| SMTP | 25/TCP | Non (MTA-to-MTA) | Envoi entre serveurs |
| SMTP Submission | 587/TCP | STARTTLS | Envoi client-to-server |
| SMTPS | 465/TCP | TLS | Envoi client-to-server (ancien) |
| POP3 | 110/TCP | Non | Réception (télécharge) |
| POP3S | 995/TCP | TLS | Réception chiffrée |
| IMAP | 143/TCP | Non | Réception (synchronisation) |
| IMAPS | 993/TCP | TLS | Réception chiffrée |

**Sécurité email** :
- **SPF** (Sender Policy Framework) : enregistrement DNS TXT listant les IPs autorisées à envoyer
- **DKIM** (DomainKeys Identified Mail) : signature cryptographique des emails
- **DMARC** : politique sur les emails échouant SPF/DKIM (none/quarantine/reject)

```bash
# Vérifier SPF
dig TXT example.com | grep spf

# Vérifier DKIM
dig TXT mail._domainkey.example.com

# Vérifier DMARC
dig TXT _dmarc.example.com
```

### FTP / SFTP

| Protocole | Port | Sécurisé |
|-----------|------|---------|
| FTP control | 21/TCP | Non (credentials en clair) |
| FTP data (actif) | 20/TCP | Non |
| FTP data (passif) | Dynamique | Non |
| FTPS (SSL) | 990/TCP | Oui |
| SFTP | 22/TCP (SSH) | Oui |

**FTP anonyme** : permettre l'accès sans credentials (anonymous/email). Souvent présent sur vieux serveurs, vérifier avec :
```bash
nmap --script ftp-anon -p 21 target.com
```

### DHCP (Dynamic Host Configuration Protocol)

**Ports** : UDP/67 (serveur), UDP/68 (client)

**Séquence DORA** :
```
Client → Broadcast : DHCP Discover
Serveur → Client : DHCP Offer (IP proposée, durée bail)
Client → Broadcast : DHCP Request (acceptation)
Serveur → Client : DHCP ACK (confirmation)
```

**Sécurité** :
- **DHCP Starvation** : épuiser le pool d'adresses avec des MACs aléatoires
- **Rogue DHCP** : serveur DHCP malveillant attribuant fausse gateway (MITM)
- **Contremesure** : DHCP Snooping sur les switches, réserver IPs aux MACs connus

### SNMP (Simple Network Management Protocol)

**Ports** : UDP/161 (agent), UDP/162 (traps)

**Versions** :

| Version | Sécurité | Statut |
|---------|---------|--------|
| SNMPv1 | Community string en clair | Obsolète |
| SNMPv2c | Community string en clair | Courant mais déconseillé |
| SNMPv3 | Authentification + chiffrement | Recommandé |

**Community strings** : `public` (lecture) et `private` (écriture) par défaut → toujours changer.

```bash
# Énumération SNMP
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.1   # Infos système
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.25.4 # Processus
snmpwalk -v2c -c public 192.168.1.1 1.3.6.1.2.1.4.22 # Table ARP

# Brute force community string
onesixtyone -c communities.txt 192.168.1.1
```

### LDAP (Lightweight Directory Access Protocol)

**Ports** : TCP/389 (LDAP), TCP/636 (LDAPS)

Protocole d'accès aux annuaires (Active Directory, OpenLDAP). Structure hiérarchique DN (Distinguished Name) :
```
CN=John Doe,OU=Users,DC=company,DC=local
```

**Opérations LDAP** : Bind, Search, Add, Delete, Modify, ModifyDN, Compare, Abandon.

```bash
# Requête LDAP anonyme (si autorisé)
ldapsearch -x -H ldap://192.168.1.1 -b "dc=company,dc=local"

# Avec authentification
ldapsearch -x -H ldap://192.168.1.1 -D "CN=user,DC=company,DC=local" -w password \
    -b "DC=company,DC=local" "(objectClass=user)"

# Récupérer les utilisateurs AD
ldapsearch -x -H ldap://dc01.company.local -b "DC=company,DC=local" \
    "(objectClass=person)" sAMAccountName mail
```

### NTP (Network Time Protocol)

**Port** : UDP/123

Synchronisation des horloges. Précision de l'ordre de la milliseconde. Crucial pour Kerberos (tickets invalides si horloge décalée > 5 minutes).

**Sécurité** :
- NTP Amplification : commande `monlist` renvoie jusqu'à 600 entrées (facteur ×556)
- **Contremesure** : désactiver `monlist` (`noquery` dans ntp.conf), filtrer UDP/123 entrant

## Ports courants à connaître

| Port | Protocole | Service |
|------|-----------|---------|
| 21 | TCP | FTP control |
| 22 | TCP | SSH, SFTP |
| 23 | TCP | Telnet (non chiffré) |
| 25 | TCP | SMTP |
| 53 | TCP/UDP | DNS |
| 67-68 | UDP | DHCP |
| 80 | TCP | HTTP |
| 110 | TCP | POP3 |
| 123 | UDP | NTP |
| 135 | TCP | Microsoft RPC |
| 137-139 | TCP/UDP | NetBIOS |
| 143 | TCP | IMAP |
| 161-162 | UDP | SNMP |
| 389 | TCP | LDAP |
| 443 | TCP | HTTPS |
| 445 | TCP | SMB (Windows shares) |
| 587 | TCP | SMTP submission |
| 636 | TCP | LDAPS |
| 993 | TCP | IMAPS |
| 995 | TCP | POP3S |
| 1433 | TCP | Microsoft SQL Server |
| 1521 | TCP | Oracle DB |
| 3306 | TCP | MySQL |
| 3389 | TCP | RDP (Remote Desktop) |
| 5432 | TCP | PostgreSQL |
| 5985-5986 | TCP | WinRM (HTTP/HTTPS) |
| 6379 | TCP | Redis |
| 8080 | TCP | HTTP alternatif |
| 8443 | TCP | HTTPS alternatif |
| 27017 | TCP | MongoDB |
