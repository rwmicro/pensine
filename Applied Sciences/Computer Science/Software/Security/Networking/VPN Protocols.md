---
title: VPN Protocols
domain: sciences-appliquées
subdomain: informatique / sécurité / réseau
tags: [vpn, wireguard, openvpn, ipsec, ikev2, sécurité, réseau]
date: 2026-03-22
---

# VPN Protocols

Un VPN (Virtual Private Network) crée un tunnel chiffré entre deux points sur un réseau public. Le choix du protocole détermine les performances, la sécurité et la compatibilité.

## Comparaison générale

| Protocole | Couche OSI | Chiffrement | Performance | Complexité | Usage principal |
|---|---|---|---|---|---|
| WireGuard | 3 (IP) | ChaCha20-Poly1305 | Excellent | Faible | VPN moderne, usage perso |
| OpenVPN | 3/4 (TUN/TAP) | AES-256-GCM | Bon | Modérée | Entreprise, routage flexible |
| IPSec/IKEv2 | 3 (IP) | AES-256-GCM | Très bon | Élevée | Site-to-site, mobiles Apple |
| L2TP/IPSec | 2 + 3 | AES-256 | Moyen | Modérée | Héritage, support natif OS |
| PPTP | 2 | MPPE (RC4) | Excellent | Faible | Obsolète, non sécurisé |
| SSTP | 4 (TLS) | AES-256 | Bon | Faible | Windows only |

## WireGuard

Protocole moderne (2018) à la base de code réduite (~4000 lignes vs ~600 000 pour OpenVPN). Intégré au noyau Linux depuis 5.6.

### Primitives cryptographiques

```
Chiffrement symétrique : ChaCha20-Poly1305 (AEAD)
Échange de clés        : Curve25519 (ECDH)
Hachage                : BLAKE2s
MAC                    : HMAC
Handshake              : Noise Protocol Framework (IKpsk2)
Perfect Forward Secrecy : oui (clés de session éphémères)
```

### Configuration

```ini
# Serveur — /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <clé_privée_serveur>
Address = 10.0.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = <clé_publique_client>
AllowedIPs = 10.0.0.2/32  # Seule IP autorisée pour ce peer
```

```ini
# Client — /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <clé_privée_client>
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = <clé_publique_serveur>
Endpoint = serveur.example.com:51820
AllowedIPs = 0.0.0.0/0   # Tout le trafic passe par le VPN
PersistentKeepalive = 25  # Maintenir la connexion derrière NAT
```

```bash
# Générer une paire de clés
wg genkey | tee private.key | wg pubkey > public.key

# Démarrer / arrêter
wg-quick up wg0
wg-quick down wg0
wg show              # État des connexions, trafic
```

### Avantages et limites

```
+ Très rapide (performances noyau, ChaCha20 optimisé)
+ Code minimal = surface d'attaque réduite = audits faciles
+ Roaming natif (changement d'IP sans reconnecter)
+ Stateless par conception (pas de négociation complexe)

- Pas de masquage : les paquets WireGuard sont identifiables (UDP port 51820)
- Identité permanente : les IPs sont fixes dans la config (problème vie privée)
- Pas de TCP natif (peut être bloqué dans des environnements restrictifs)
- WireGuard over TCP : via udp2raw ou obfuscation supplémentaire
```

## OpenVPN

Protocole mature (2001) utilisant TLS pour la couche de contrôle et OpenSSL pour le chiffrement.

### Architecture

```
Canal de contrôle (TLS) : authentification, échange de clés, paramètres
Canal de données (chiffrement symétrique) : tunneling du trafic réel

Mode TUN (couche 3) : tunnel IP — routage
Mode TAP (couche 2) : tunnel Ethernet — bridging (LAN virtuel)
```

### Configuration serveur

```
# /etc/openvpn/server.conf
port 1194
proto udp
dev tun

ca      /etc/openvpn/ca.crt
cert    /etc/openvpn/server.crt
key     /etc/openvpn/server.key
dh      /etc/openvpn/dh.pem
tls-auth /etc/openvpn/ta.key 0  # Protection anti-DDoS sur le handshake

server 10.8.0.0 255.255.255.0   # Plage d'adresses clients
push "redirect-gateway def1"    # Router tout le trafic client
push "dhcp-option DNS 1.1.1.1"

cipher AES-256-GCM
auth SHA256
tls-version-min 1.2

keepalive 10 120
user nobody
group nogroup
persist-key
persist-tun
```

```bash
# Générer l'infrastructure PKI avec easy-rsa
make-cadir ~/openvpn-ca && cd ~/openvpn-ca
./easyrsa init-pki
./easyrsa build-ca
./easyrsa gen-dh
./easyrsa build-server-full server nopass
./easyrsa build-client-full client1 nopass
openvpn --genkey secret ta.key
```

### Avantages et limites

```
+ Protocole mature avec large écosystème
+ Supporte TCP (port 443 → difficile à bloquer)
+ PKI complète avec révocation de certificats (CRL)
+ Mode TAP pour ponter des réseaux entiers
+ Supporte plusieurs méthodes d'authentification (certs, MFA, LDAP)

- Performance inférieure à WireGuard
- Configuration complexe
- Code large (~600k lignes)
- Dépendance à OpenSSL
```

## IPSec / IKEv2

IPSec opère au niveau IP et est souvent utilisé pour les VPN site-to-site en entreprise. IKEv2 est le protocole de négociation de clés (phase de handshake).

### Composants IPSec

```
IKE (Internet Key Exchange) : Protocole de négociation des SA (Security Associations)
AH (Authentication Header)  : Intégrité et authentification (pas de chiffrement)
ESP (Encapsulating Security Payload) : Chiffrement + intégrité (utilisé en pratique)

Modes IPSec :
Transport : chiffre uniquement le payload IP (en-tête IP visible)
Tunnel    : chiffre le paquet IP entier (en-tête IP original caché dans un nouveau paquet)
```

### IKEv2 — phases de négociation

```
Phase 1 — IKE_SA_INIT :
  Échange DH → secret partagé
  Génération des clés de session IKE

Phase 2 — IKE_AUTH :
  Authentification mutuelle (certificats ou PSK)
  Négociation de la Child SA (pour ESP)

Phase 3 — CREATE_CHILD_SA :
  Renouvellement des clés (PFS — Perfect Forward Secrecy)
```

### Configuration strongSwan (IKEv2)

```
# /etc/ipsec.conf
config setup
    charondebug="ike 1, knl 1, cfg 0"

conn ikev2-vpn
    auto=add
    compress=no
    type=tunnel
    keyexchange=ikev2
    ike=aes256gcm16-prfsha256-ecp256!
    esp=aes256gcm16-ecp256!
    fragmentation=yes
    forceencaps=yes
    dpdaction=clear
    dpddelay=300s
    rekey=no
    left=%any
    leftid=@server.example.com
    leftcert=server-cert.pem
    leftsendcert=always
    leftsubnet=0.0.0.0/0
    right=%any
    rightid=%any
    rightauth=eap-mschapv2
    rightsourceip=10.10.10.0/24
    rightdns=1.1.1.1
    rightsendcert=never
    eap_identity=%identity
```

### Avantages et limites

```
+ Intégré nativement dans iOS, macOS, Windows
+ Très performant (implémentations kernel)
+ Robuste pour les connexions mobiles (MOBIKE — changement d'IP)
+ Standard IETF

- Configuration très complexe
- Potentiellement ciblé par des portes dérobées NSA (selon documents Snowden)
  → Utiliser des courbes EC non-NIST (Curve25519) si possible
- Négociation IKEv1 vulnérable (utiliser IKEv2 uniquement)
```

## Sécurité VPN — considérations

### DNS leaks

```bash
# Tester si le DNS fuit en dehors du tunnel
curl https://dnsleaktest.com/

# Protection : forcer le DNS à travers le tunnel
# WireGuard : DNS = 10.0.0.1 dans [Interface]
# OpenVPN   : push "dhcp-option DNS 10.8.0.1"
# Désactiver systemd-resolved / nsswitch en dehors du VPN
```

### VPN kill switch

```bash
# Empêcher tout trafic si le VPN se déconnecte
# WireGuard — via iptables
iptables -P FORWARD DROP
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -A OUTPUT -o wg0 -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A OUTPUT -p udp --dport 51820 -j ACCEPT  # Autoriser WireGuard lui-même
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT     # DNS initial (résolution du serveur)

# NetworkManager sur Linux — nmcli connection modify wg0 vpn.persistent yes
```

### Audit d'implémentation VPN

```
Points à vérifier :
✓ Algorithmes : AES-256-GCM, ChaCha20-Poly1305 (pas AES-CBC, pas RC4)
✓ DH : groupes ≥ 3072 bits ou Curve25519 (pas groupe 1/2/5 Oakley)
✓ Perfect Forward Secrecy activé
✓ Certificats : SHA-256+, clés RSA ≥ 2048 bits ou ECDSA P-256+
✓ TLS minimum 1.2 (si TLS utilisé)
✓ Authentification mutuelle (pas seulement clé pré-partagée en entreprise)
✓ Logs : sans connexion (no-log policy vérifiable pour VPN commerciaux)
```

## GRE Tunnel

GRE (Generic Routing Encapsulation) est une méthode de création de VPN site-à-site développée par Cisco (RFC 2784). GRE n'est **pas chiffré par défaut** — il encapsule simplement les paquets dans un nouvel en-tête IP.

### Caractéristiques GRE

- Protocole IP numéro 47
- Supporte l'encapsulation de tous les protocoles de couche 3
- Stateless, sans mécanisme de contrôle de flux
- Pas de sécurité intégrée (nécessite IPSec pour le chiffrement)

### GRE over IPSec

La combinaison GRE + IPSec est courante en entreprise : GRE fournit le tunnel multi-protocoles, IPSec assure le chiffrement.

```cisco
! Créer le tunnel GRE
interface Tunnel0
 ip address 10.0.0.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.2
 tunnel mode gre ip

! Chiffrer avec IPSec (mode transport recommandé pour GRE over IPSec)
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
!
crypto isakmp key MOT_DE_PASSE address 203.0.113.2
!
crypto ipsec transform-set TS esp-aes 256 esp-sha256-hmac
 mode transport
!
crypto map CMAP 10 ipsec-isakmp
 set peer 203.0.113.2
 set transform-set TS
 match address ACL_GRE
!
interface GigabitEthernet0/0
 crypto map CMAP
```

### Types de VPN

| Type | Usage |
|------|-------|
| Site-to-Site | Connexion permanente entre deux sites distants (siège ↔ agence) |
| Remote Access | Connexion individuelle depuis n'importe où (télétravail) |
| GRE Tunnel | Tunnel multi-protocoles, souvent combiné avec IPSec |
| IPSec VPN | VPN sécurisé site-à-site avec chiffrement complet |

### Avantages du VPN en entreprise

- Bonne scalabilité
- Compatible avec les technologies broadband
- Niveau de sécurité élevé
- Réduit le coût des lignes dédiées (WAN)

## Obfuscation (contournement de censure)

```bash
# obfs4 — obfusque le trafic OpenVPN pour ressembler à du trafic aléatoire
# Utilisé avec Tor et OpenVPN dans des pays avec censure

# Shadowsocks — proxy SOCKS5 chiffré
# Stunnel — encapsule dans TLS
# v2ray/xray — frameworks de contournement avancés

# WireGuard over TCP via udp2raw
# Convertit les paquets UDP WireGuard en paquets TCP (voire ICMP)
```
