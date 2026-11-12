---
title: "BloodHound"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Active Directory"
tags: [bloodhound, active-directory, graphe, attaque-path, sécurité, pentest]
date: "2026-03-22"
prerequis: ["[[Active Directory Security]]"]
---

# BloodHound

En 2016, trois chercheurs en sécurité, Andy Robbins, Will Schroeder et Rohan Vazarkar, présentent à la conférence DEF CON un outil qui change la façon d'attaquer et de défendre Active Directory. Jusque-là, auditer un domaine revenait à passer en revue les objets un par un, à la recherche d'une mauvaise configuration isolée. Leur idée est de voir le domaine autrement : comme un graphe où chaque flèche est une relation (« est membre de », « est administrateur de », « peut réinitialiser le mot de passe de »). Dès lors, trouver un chemin d'attaque n'est plus une inspection manuelle mais un calcul de plus court chemin, celui qu'un GPS fait entre deux adresses. Cet outil, c'est **BloodHound**.

BloodHound modélise les relations entre objets Active Directory (utilisateurs, groupes, ordinateurs, GPO) et identifie automatiquement les chemins qui mènent à des cibles à hauts privilèges, comme les administrateurs du domaine ou les contrôleurs de domaine.

> [!important] Idée clé
> BloodHound ne cherche pas des vulnérabilités — il modélise AD comme un graphe de relations (`MemberOf`, `AdminTo`, `GenericAll`...) et calcule le plus court chemin entre "où je suis" et "Domain Admin". C'est un changement de paradigme : au lieu d'auditer chaque objet isolément, on cherche des chemins d'attaque à travers leurs relations combinées.

## Architecture

BloodHound se compose de trois maillons. Un **collecteur** parcourt l'annuaire et en extrait les objets et leurs relations : SharpHound en C# sur une machine Windows du domaine, ou BloodHound.py depuis Linux. Il produit des fichiers JSON, qui sont importés dans une **base de graphes Neo4j**, le moteur qui stocke les nœuds et les relations. Enfin, une **interface graphique** interroge cette base avec le langage Cypher, propre à Neo4j, et dessine les chemins d'attaque. Les requêtes sont donc des requêtes de graphe, et c'est ce qui donne à l'outil sa puissance.

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

Sans écrire la moindre requête, l'onglet d'analyse propose des recherches prêtes à l'emploi qui couvrent les questions les plus fréquentes. « Find all Domain Admins » liste les administrateurs du domaine ; « Find Shortest Paths to Domain Admins » calcule le chemin d'attaque le plus court depuis n'importe quel utilisateur ; « Find Principals with DCSync Rights » révèle qui peut répliquer les secrets du domaine. D'autres repèrent les postes où les utilisateurs du domaine sont administrateurs locaux, les systèmes en délégation Kerberos non contrainte, ou encore les comptes vulnérables à l'AS-REP Roasting (sans pré-authentification) et au Kerberoasting (porteurs d'un SPN). Chacune pointe directement vers un vecteur d'attaque documenté dans les notes voisines.

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

Le vrai usage de BloodHound passe par deux marqueurs. On marque comme **Owned** (par un clic droit) tout objet déjà compromis, et comme **High Value** les cibles visées ; BloodHound affiche alors automatiquement les chemins qui relient les uns aux autres.

Le déroulement d'une intrusion suit ce fil. On importe les données, on marque comme *Owned* le premier compte obtenu, puis on demande le plus court chemin vers les administrateurs du domaine. BloodHound dessine ce chemin comme une suite de relations ; on exploite la première (un GenericAll, un AdminTo…), ce qui donne le contrôle de l'objet suivant, qu'on marque à son tour *Owned*, et on recommence jusqu'à l'administrateur du domaine. Le graphe transforme ainsi une intrusion en une série d'étapes lisibles, ce qui en fait autant un outil d'attaque qu'un outil d'audit défensif.

## Contre-mesures (détection et hardening)

La **détection** vise d'abord la phase de collecte. SharpHound émet un volume anormal de requêtes LDAP, souvent lourdes (nombreux attributs comme `objectClass` ou `adminCount`), et ouvre de multiples connexions SMB pour recenser les sessions actives. Ce profil se repère dans les journaux, et des outils d'audit comme PingCastle ou Purple Knight signalent par ailleurs les mêmes faiblesses que BloodHound révélerait.

Le **durcissement**, surtout, consiste à casser les chemins eux-mêmes plutôt qu'à empêcher la collecte. Réduire le nombre de machines où les utilisateurs ordinaires sont administrateurs locaux supprime d'un coup beaucoup d'arêtes `AdminTo`. Le modèle en couches (*Tier Model*) sépare les comptes selon leur criticité, le nettoyage des ACL excessives élimine les raccourcis de type GenericAll ou WriteDACL, l'activation de la pré-authentification Kerberos et la suppression des SPN inutiles ferment les attaques de cassage de tickets, et le groupe *Protected Users* durcit les comptes sensibles. Chaque chemin supprimé rend le graphe moins traversable.

## Pièges courants

> [!warning] Pièges courants
> - **Collecte partielle = chemins manquants** : `SharpHound -c Default` ne ramasse pas les sessions ni les LocalGroup. Toujours `-c All` (plus lent, mais complet). Sans sessions, "Find Shortest Path to Domain Admins" rate des chemins critiques.
> - **SharpHound vs bloodhound.py — données différentes** : SharpHound (Windows) collecte plus que bloodhound.py (Linux) sur les sessions. Si possible, faire les deux et fusionner.
> - **Cache stale** : BloodHound interroge un cache local. Si on importe de nouvelles données sans clear, les chemins sont obsolètes. Toujours "Clear database" entre deux engagements.
> - **Edge "HasSession" éphémère** : une session BloodHound = un user était connecté à un moment. Six heures après, le user n'est probablement plus là. Recoller la collecte avant exploitation.
> - **Custom queries vs canned queries** : les requêtes prédéfinies couvrent les cas classiques. Les chemins exotiques (cross-trust, ACL chains avec 6+ étapes) demandent du Cypher manuel.
> - **`AdminTo` vs `CanRDP`** : AdminTo = admin local sur la machine (exécution code SYSTEM). CanRDP = peut se connecter en RDP mais pas forcément admin. Bien lire le edge type.
> - **`DCSync` peut être trompeur** : BloodHound annonce DCSync via les permissions ACL classiques (`Replicating Directory Changes`, `Replicating Directory Changes All`). Mais il manque parfois des chemins indirects via ACL groupes/OUs imbriqués.
> - **GenericAll sur ordinateur ≠ admin local** : GenericAll dans AD = modifier l'objet AD. Pour devenir admin local, il faut combiner avec RBCD ou Shadow Credentials. BloodHound montre `GenericAll → ResourceBasedConstrainedDelegation → AdminTo`.
> - **Volume de données pour grands AD** : sur un AD avec 50000 users, SharpHound peut prendre 30+ minutes et générer des Go. Filtrer par OU ou domain si possible.
> - **AzureHound pour Entra ID** : BloodHound on-prem ne couvre PAS Azure AD / Entra ID. Pour le cloud, utiliser AzureHound. Les graphes peuvent être merged dans BloodHound Community Edition.
