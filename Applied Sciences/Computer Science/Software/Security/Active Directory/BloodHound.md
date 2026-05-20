---
title: BloodHound
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [bloodhound, active-directory, graphe, attaque-path, sécurité, pentest]
date: 2026-03-22
---

# BloodHound

BloodHound est un outil d'analyse graphique des environnements Active Directory. Il modélise les relations entre objets AD (utilisateurs, groupes, ordinateurs, GPO) et identifie automatiquement les chemins d'attaque vers des cibles à hauts privilèges (Domain Admins, DC).

## Architecture

```
SharpHound / BloodHound.py  →  Collecte des données AD
            ↓
        Données JSON
            ↓
    Neo4j (base de graphes)  ←  BloodHound GUI (React)
            ↓
    Requêtes Cypher → Chemins d'attaque visualisés
```

## Collecte avec SharpHound

```powershell
# Télécharger SharpHound sur la machine compromise
# https://github.com/BloodHoundAD/SharpHound

# Collecte standard (la plus complète)
.\SharpHound.exe -c All

# Collecte ciblée — seulement les sessions actives
.\SharpHound.exe -c Session

# Collecte silencieuse (LDAP uniquement, moins bruyante)
.\SharpHound.exe -c DCOnly

# Collecte depuis une autre session (pass-the-hash)
.\SharpHound.exe --ldapusername alice --ldappassword password

# Avec un DC spécifique
.\SharpHound.exe -d domaine.local --domaincontroller 192.168.1.10

# Sortie : archive ZIP contenant des fichiers JSON
# computers.json, users.json, groups.json, sessions.json, domains.json...
```

### Collecte avec BloodHound.py (sans accès local à la machine Windows)

```bash
# Depuis Kali/Linux avec des credentials
bloodhound-python -u alice -p password -d domaine.local -dc dc01.domaine.local -c All

# Avec pass-the-hash
bloodhound-python -u alice --hashes :ntlm_hash -d domaine.local -ns 192.168.1.10 -c All

# Collecte DNS-less
bloodhound-python -u alice -p password -d domaine.local -ns 192.168.1.10 -c All --dns-timeout 5
```

## Importation et interface

```bash
# 1. Démarrer Neo4j
sudo neo4j start
# Interface : http://localhost:7474 (défaut : neo4j/neo4j → changer au 1er login)

# 2. Démarrer BloodHound GUI
bloodhound

# 3. Importer les données
# Menu → Upload Data → sélectionner le ZIP ou les JSON
# Ou glisser-déposer les fichiers
```

## Requêtes pré-construites (GUI)

BloodHound propose des requêtes prêtes à l'emploi :

```
Analysis → Pre-Built Analytics Queries :

"Find all Domain Admins"
  → Liste tous les Domain Admins

"Find Shortest Paths to Domain Admins"
  → Chemin d'attaque le plus court depuis n'importe quel utilisateur

"Find Principals with DCSync Rights"
  → Qui peut effectuer un DCSync ?

"Find Computers where Domain Users are Local Admin"
  → Tous les postes où les utilisateurs du domaine ont admin local

"Shortest Paths to Unconstrained Delegation Systems"
  → Délégation Kerberos non contrainte (vecteur d'escalade)

"Find AS-REP Roastable Users"
  → Comptes sans pré-authentification Kerberos

"Find Kerberoastable Users"
  → Comptes avec SPN (cibles du Kerberoasting)
```

## Requêtes Cypher personnalisées

BloodHound utilise le langage de requête Neo4j Cypher.

```cypher
// Trouver tous les chemins d'attaque depuis "alice" vers "Domain Admins"
MATCH p=shortestPath(
    (n:User {name:"ALICE@DOMAINE.LOCAL"})-[*1..]->(m:Group {name:"DOMAIN ADMINS@DOMAINE.LOCAL"})
)
RETURN p

// Trouver les utilisateurs qui ont GenericAll sur un autre objet
MATCH (n)-[r:GenericAll]->(m)
WHERE n.name <> m.name
RETURN n.name, m.name, type(r)

// Ordinateurs avec délégation non contrainte (sauf les DC)
MATCH (c:Computer {unconstraineddelegation:true})
WHERE NOT c.name CONTAINS "DC"
RETURN c.name

// Utilisateurs membres de groupes imbriqués menant à Domain Admins
MATCH (u:User)-[:MemberOf*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAINE.LOCAL"})
RETURN u.name

// Sessions actives sur les DC
MATCH (u:User)-[:HasSession]->(c:Computer {domain:"DOMAINE.LOCAL"})
WHERE c.name CONTAINS "DC"
RETURN u.name, c.name

// Comptes avec des droits sur les GPO
MATCH (n)-[r:GPLink|WriteGPLink|AllExtendedRights|GenericAll|GenericWrite]->(g:GPO)
RETURN n.name, type(r), g.name

// High value targets qui sont atteignables
MATCH (n {highvalue:true})
RETURN n.name, labels(n)

// Tous les chemins depuis les utilisateurs du groupe "IT" vers Domain Admins
MATCH p=shortestPath(
    (g:Group {name:"IT@DOMAINE.LOCAL"})-[*1..]->(m:Group {name:"DOMAIN ADMINS@DOMAINE.LOCAL"})
)
RETURN p
```

## Edges (relations) exploitables

| Edge | Description | Exploitation |
|---|---|---|
| `MemberOf` | Appartenance à un groupe | Héritage des droits du groupe |
| `AdminTo` | Admin local sur un ordinateur | psexec, WMI, DCOM |
| `HasSession` | Session active d'un utilisateur | Vol de token, dump LSASS |
| `GenericAll` | Contrôle total d'un objet | Modifier le mot de passe, ajouter aux groupes |
| `GenericWrite` | Écriture sur un objet | Modifier des attributs (scriptPath, servicePrincipalName) |
| `WriteOwner` | Changer le propriétaire | S'attribuer GenericAll |
| `WriteDACL` | Modifier la liste d'accès | S'accorder n'importe quel droit |
| `ForceChangePassword` | Forcer le changement de MDP | Changer le mot de passe sans le connaître |
| `DCSync` | GetChangesAll sur le domaine | Dump de tous les hashes |
| `AllowedToDelegate` | Délégation Kerberos contrainte | Impersonate n'importe quel utilisateur |
| `AllowedToAct` | RBCD (Resource-Based Constrained Delegation) | Escalade via délégation basée sur les ressources |
| `AddMember` | Ajouter des membres à un groupe | S'ajouter à Domain Admins |
| `GPLink` | Lien vers une GPO | Si écriture sur GPO → exécution de code sur les objets liés |

## Marquer les assets et construire une stratégie

```
Dans l'interface :
1. Clic droit sur un utilisateur/ordinateur → "Mark as Owned" (objectif compromis)
2. Clic droit sur un groupe → "Mark as High Value" (cible)

→ BloodHound montre automatiquement les chemins depuis les "Owned" vers les "High Value"

Workflow typique :
1. Importer les données
2. Marquer le compte compromis initial comme "Owned"
3. "Find Shortest Paths to Domain Admins" → voir le chemin graphique
4. Identifier la relation exploitable suivante (GenericAll, AdminTo, etc.)
5. Exploiter cette relation → marquer le prochain objet comme Owned
6. Répéter jusqu'à Domain Admin
```

## Contre-mesures (détection et hardening)

```
Détection de la collecte BloodHound :
  - Volume anormal de requêtes LDAP (SharpHound → beaucoup de requêtes)
  - Requêtes LDAP avec de nombreux attributs (objectClass, adminCount, etc.)
  - Connexions SMB anormales (pour la collecte des sessions)
  - Outil : Purple Knight, PingCastle (audit AD)

Hardening des chemins d'attaque :
  - Réduire le nombre d'AdminTo (pas d'admin local pour les utilisateurs normaux)
  - Tier Model (Admin Tier 0/1/2 — séparation des comptes par criticité)
  - Nettoyer les ACL excessives (GenericAll, WriteDACL sur des objets sensibles)
  - Activer la pré-authentification Kerberos sur tous les comptes
  - Supprimer les SPN inutiles
  - Protected Users Security Group pour les comptes sensibles
```

## Pièges courants

- **Collecte partielle = chemins manquants** : `SharpHound -c Default` ne ramasse pas les sessions ni les LocalGroup. Toujours `-c All` (plus lent, mais complet). Sans sessions, "Find Shortest Path to Domain Admins" rate des chemins critiques.
- **SharpHound vs bloodhound.py — données différentes** : SharpHound (Windows) collecte plus que bloodhound.py (Linux) sur les sessions. Si possible, faire les deux et fusionner.
- **Cache stale** : BloodHound interroge un cache local. Si on importe de nouvelles données sans clear, les chemins sont obsolètes. Toujours "Clear database" entre deux engagements.
- **Edge "HasSession" éphémère** : une session BloodHound = un user était connecté à un moment. Six heures après, le user n'est probablement plus là. Recoller la collecte avant exploitation.
- **Custom queries vs canned queries** : les requêtes prédéfinies couvrent les cas classiques. Les chemins exotiques (cross-trust, ACL chains avec 6+ étapes) demandent du Cypher manuel.
- **`AdminTo` vs `CanRDP`** : AdminTo = admin local sur la machine (exécution code SYSTEM). CanRDP = peut se connecter en RDP mais pas forcément admin. Bien lire le edge type.
- **`DCSync` peut être trompeur** : BloodHound annonce DCSync via les permissions ACL classiques (`Replicating Directory Changes`, `Replicating Directory Changes All`). Mais il manque parfois des chemins indirects via ACL groupes/OUs imbriqués.
- **GenericAll sur ordinateur ≠ admin local** : GenericAll dans AD = modifier l'objet AD. Pour devenir admin local, il faut combiner avec RBCD ou Shadow Credentials. BloodHound montre `GenericAll → ResourceBasedConstrainedDelegation → AdminTo`.
- **Volume de données pour grands AD** : sur un AD avec 50000 users, SharpHound peut prendre 30+ minutes et générer des Go. Filtrer par OU ou domain si possible.
- **AzureHound pour Entra ID** : BloodHound on-prem ne couvre PAS Azure AD / Entra ID. Pour le cloud, utiliser AzureHound. Les graphes peuvent être merged dans BloodHound Community Edition.
