---
title: PAM — Privileged Access Management
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [pam, iam, privileged-access, zero-trust, active-directory, sécurité]
date: 2026-03-22
---

# PAM — Privileged Access Management

Le Privileged Access Management (PAM) est l'ensemble des processus et technologies pour contrôler, surveiller et auditer les accès privilégiés aux systèmes critiques. Les comptes à privilèges (administrateurs, comptes de service, root) sont la cible principale des attaquants : 80% des violations impliquent des credentials privilégiés compromis.

## Pourquoi PAM ?

```mermaid
graph LR
    attacker[Attaquant] -->|Objectif| privaccount[Compte privilégié]
    privaccount --> everything[Accès à tout :\nBases de données\nActive Directory\nServeurs critiques\nBackups]

    pam[PAM] -->|Protège| privaccount
    pam --> vault[Coffre-fort\nde credentials]
    pam --> jit[Just-in-Time\nAccess]
    pam --> record[Enregistrement\ndes sessions]
    pam --> mfa[MFA sur\nchaque élévation]
```

**Comptes privilégiés à gérer :**
- Administrateurs de domaine (Domain Admins)
- Administrateurs locaux sur les serveurs
- Comptes root Linux/Unix
- Comptes de service (souvent avec mots de passe statiques anciens)
- Comptes d'applications (accès base de données)
- Comptes d'équipements réseau (Cisco enable, JUNOS)
- Comptes de solutions de sauvegarde
- Comptes "break glass" d'urgence

## Coffre-fort de credentials (Password Vault)

Le coffre-fort est le composant central du PAM : il stocke, génère et fait tourner automatiquement les mots de passe.

```mermaid
graph LR
    admin[Administrateur] -->|S'authentifie| vault[Vault PAM]
    vault -->|Récupère le mdp| db[(Coffre chiffré)]
    vault -->|Injecte les credentials| target[Serveur cible]
    admin -->|Session établie| target
    admin -.->|Ne voit jamais| mdp[Mot de passe]
```

**Fonctionnement :**
1. L'admin s'authentifie au vault (MFA obligatoire)
2. Il demande l'accès à un serveur cible
3. Le vault récupère le mot de passe depuis le coffre chiffré
4. La connexion est établie en proxy (l'admin ne voit jamais le mot de passe)
5. La session est enregistrée
6. Après usage, le mot de passe est automatiquement changé

```bash
# CyberArk — exemple de récupération via API
curl -X POST https://vault.monentreprise.com/PasswordVault/API/auth/Cyberark/Logon \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Récupérer un compte
curl -X GET "https://vault.monentreprise.com/PasswordVault/api/Accounts?search=prod-db" \
  -H "Authorization: Bearer $TOKEN"

# Rotation automatique post-usage
# → Configuré dans la politique du compte (RotateCredentials=true)
```

## Just-in-Time Access (JIT)

Le JIT accorde des accès privilégiés à la demande, pour une durée limitée, avec une justification.

```mermaid
graph LR
    request[Admin demande\naccès domain admin\npour patch critique]
    approval[Approbation\nautomatique ou manager]
    grant[Accès accordé\npour 2 heures]
    use[Admin effectue\nla tâche]
    revoke[Accès révoqué\nautomatiquement]
    audit[Enregistrement\naudit log]

    request --> approval --> grant --> use --> revoke --> audit
```

**Implémentation avec Azure AD PIM (Privileged Identity Management) :**

```powershell
# Activer un rôle éligible (JIT Azure AD)
# Depuis le portail Azure AD → PIM → Mes rôles → Activer

# PowerShell
$params = @{
    principalId = "userId"
    roleDefinitionId = "62e90394-69f5-4237-9190-012177145e10"  # Global Admin
    directoryScopeId = "/"
    action = "selfActivate"
    justification = "Patch critique CVE-2024-XXXX déploiement d'urgence"
    scheduleInfo = @{
        startDateTime = (Get-Date).ToUniversalTime()
        expiration = @{
            type = "AfterDuration"
            duration = "PT2H"  # 2 heures
        }
    }
}
New-MgRoleManagementDirectoryRoleAssignmentScheduleRequest -BodyParameter $params
```

## Just-Enough-Access (JEA)

JEA limite les administrateurs à exécuter uniquement les commandes nécessaires à leur rôle, même avec une session PowerShell "administrative".

```powershell
# Créer une configuration JEA
# RoleCapabilities — définit ce qu'un rôle peut faire
@{
    VisibleCmdlets = @{
        Name = 'Restart-Service'
        Parameters = @{ Name = 'Name'; ValidateSet = 'DNS', 'DHCP', 'WinRM' }
    }
    VisibleExternalCommands = @()
    VisibleFunctions = 'Get-EventLog'
}

# SessionConfiguration — endpoint PowerShell restreint
Register-PSSessionConfiguration -Name 'WebAdminSession' `
    -RunAsCredential (Get-Credential) `
    -Path 'C:\JEA\WebAdminConfig.pssc'

# Connexion en session JEA
Enter-PSSession -ComputerName serveur -ConfigurationName 'WebAdminSession'
# L'utilisateur peut UNIQUEMENT Restart-Service DNS/DHCP/WinRM
```

## LAPS — Local Administrator Password Solution

Microsoft LAPS génère et fait tourner automatiquement les mots de passe administrateurs locaux de chaque machine, stockés dans l'AD.

```powershell
# Déploiement LAPS
# 1. Étendre le schéma AD
Update-LapsADSchema

# 2. Configurer les permissions (qui peut lire quel mdp)
Set-LapsADComputerSelfPermission -Identity "OU=Servers,DC=contoso,DC=com"

# 3. GPO pour configurer la rotation (ex: 30 jours)
# Computer Configuration → LAPS → Password Settings

# 4. Récupérer le mdp d'une machine (admin seulement)
Get-LapsADPassword -Identity "SERVEUR01" -AsPlainText

# RÉSULTAT : chaque poste a un mdp admin local unique
# → Pass-the-Hash ne fonctionne plus (mdp différent sur chaque machine)
```

## Enregistrement des sessions (Session Recording)

Chaque session privilégiée est enregistrée pour l'audit et les investigations forensiques.

```
Données enregistrées :
- Video de la session (ce que l'admin a vu à l'écran)
- Frappes clavier (keylogging)
- Commandes exécutées
- Fichiers transférés
- Connexions réseau initiées

Fonctionnalités avancées :
- Recherche full-text dans les sessions enregistrées
- Alertes en temps réel (commandes dangereuses détectées)
- Blocage de commandes non autorisées
- Watermarking (si des données sont exfiltrées, on sait qui)
```

## Sécurité des comptes de service

Les comptes de service (utilisés par les applications) sont souvent négligés et deviennent des cibles privilégiées.

```powershell
# Problèmes courants :
# - Mots de passe qui n'expirent jamais (PasswordNeverExpires)
# - Droits Domain Admin (bien trop élevés pour une app)
# - Mot de passe connu de plusieurs personnes

# Solution : gMSA (group Managed Service Account)
# → Mot de passe géré automatiquement par l'AD (120 caractères)
# → Aucun humain ne connaît le mot de passe
# → Rotation automatique tous les 30 jours

# Créer un gMSA
New-ADServiceAccount -Name "gMSA-AppService" `
    -DNSHostName "appservice.contoso.com" `
    -PrincipalsAllowedToRetrieveManagedPassword "WebServers-Group"

# Assigner à un service Windows (remplace les credentials manuels)
Set-ADServiceAccount -Identity "gMSA-AppService" -TrustedForDelegation $false
```

## Détection des abus de comptes privilégiés

```
Événements Windows à surveiller :

4672 : Special Logon (compte avec privilèges sensibles)
4673 : Opération de service privilégié appelée
4728 : Membre ajouté à un groupe de sécurité global (Domain Admins !)
4732 : Membre ajouté à un groupe local
4756 : Membre ajouté à un groupe universel
4768/4769 : Ticket Kerberos demandé (détection Kerberoasting)
4776 : NTLM authentication
```

```yaml
# Sigma — Détection ajout à Domain Admins
title: User Added to Domain Admin Group
logsource:
    product: windows
    service: security
detection:
    selection:
        EventID: 4728
        TargetUserName: 'Domain Admins'
    condition: selection
level: critical
```

## Solutions PAM du marché

| Solution | Type | Points forts |
|---|---|---|
| **CyberArk** | Enterprise | Leader marché, fonctionnalités complètes |
| **BeyondTrust** | Enterprise | Password Safe + Remote Support |
| **Delinea (Thycotic)** | Enterprise | Secret Server, plus accessible |
| **Azure AD PIM** | Cloud | Native Azure, JIT pour ressources Azure |
| **HashiCorp Vault** | Open source + Enterprise | Secrets management, très flexible |
| **Teleport** | Open source + Enterprise | SSH/K8s/DB access, audit intégré |

```bash
# HashiCorp Vault — gestion des secrets
# Stocker et récupérer un secret
vault kv put secret/myapp/database \
  username="dbadmin" \
  password="$(openssl rand -base64 32)"

vault kv get -field=password secret/myapp/database

# Rotation automatique (Dynamic Secrets)
# Vault crée un compte temporaire dans la BDD à la demande
vault secrets enable database
vault write database/config/my-postgresql \
    plugin_name=postgresql-database-plugin \
    allowed_roles="my-role" \
    connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb" \
    username="vault-admin" password="..."

# Chaque demande crée un compte temporaire avec un TTL
vault read database/creds/my-role
# → Username: v-root-myapp-xK7pQ2
# → Password: A1B2C3D4...
# → Expiration: 1h
```
