---
title: "DFIR (Digital Forensics and Incident Response)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > SOC Analysis > DFIR"
tags: [sciences-appliquées, informatique, sécurité, soc, dfir]
date: "2025-02-15"
---

# DFIR (Digital Forensics and Incident Response)

Le DFIR regroupe deux disciplines complémentaires : la **réponse à incident** (contenir et éradiquer une menace active) et la **forensique numérique** (analyser les preuves numériques après coup). En pratique, elles se chevauchent : l'analyste collecte des preuves pendant la réponse.

## Phases d'une réponse à incident

Le cadre le plus utilisé est celui du NIST (SP 800-61) :

```
1. Préparation
   └── Playbooks, outils, sauvegardes, contacts, accès

2. Identification (Detection & Analysis)
   └── Alertes SIEM, corrélation de logs, triage

3. Confinement
   ├── Court terme : isoler la machine compromise
   └── Long terme : patcher, surveiller les mouvements latéraux

4. Éradication
   └── Supprimer le malware, corriger la vulnérabilité exploitée

5. Rétablissement
   └── Restaurer les systèmes, monitorer pour s'assurer de l'absence de réinfection

6. Leçons apprises (Post-Incident Activity)
   └── Rapport, amélioration des défenses, mise à jour des playbooks
```

## Chaîne de custody (Chain of Custody)

La chaîne de custody garantit l'intégrité et la traçabilité des preuves numériques pour qu'elles soient recevables en justice.

Principes fondamentaux :
- Documenter chaque action sur la preuve (qui, quand, quoi)
- Travailler sur des **copies forensiques**, jamais sur les originaux
- Calculer et vérifier les **hashes** (SHA-256) avant et après chaque opération
- Stocker les originaux dans un endroit sécurisé et scellé

```bash
# Calculer le hash d'une image disque
sha256sum image_disque.dd

# Créer une image disque bit-à-bit avec dd
dd if=/dev/sdb of=image_disque.dd bs=4M status=progress

# Avec dcfldd (version forensique de dd — vérifie le hash pendant la copie)
dcfldd if=/dev/sdb of=image.dd hash=sha256 hashlog=hash.txt

# Ou avec FTK Imager (Windows, format .E01 avec compression et vérification intégrée)
```

## Artefacts Windows

### Registre

Le registre Windows est une mine d'informations forensiques.

| Ruche | Localisation | Intérêt forensique |
|---|---|---|
| `SYSTEM` | `%WinDir%\System32\config\SYSTEM` | Disques montés, services, hostname |
| `SOFTWARE` | `%WinDir%\System32\config\SOFTWARE` | Logiciels installés, AppCompatCache |
| `SAM` | `%WinDir%\System32\config\SAM` | Comptes locaux (hashes NTLM) |
| `NTUSER.DAT` | `%UserProfile%\NTUSER.DAT` | MRU, UserAssist, RecentDocs, ShellBags |
| `UsrClass.dat` | `%UserProfile%\AppData\Local\Microsoft\Windows\` | ShellBags pour Explorer |

Artefacts clés dans le registre :
- **UserAssist** : programmes exécutés par l'utilisateur (encodés en ROT13)
- **ShellBags** : dossiers accédés dans l'explorateur (même sur disques déconnectés)
- **RecentDocs** : fichiers récemment ouverts
- **MRU (Most Recently Used)** : listes de fichiers et commandes récentes
- **RunKeys** : programmes lancés au démarrage (`HKCU\...\Run`, `HKLM\...\Run`)
- **AppCompatCache (Shimcache)** : historique des exécutables (nom, taille, date modif)
- **Amcache.hve** : informations sur les exécutables (SHA1, publisher, timestamp d'installation)

### Logs Windows

| Journal | Chemin | Contenu |
|---|---|---|
| System | `%WinDir%\System32\winevt\Logs\System.evtx` | Services, drivers, erreurs matérielles |
| Security | `...Logs\Security.evtx` | Connexions (4624/4625), créations de comptes (4720) |
| Application | `...Logs\Application.evtx` | Applications, erreurs de services |
| PowerShell | `...Logs\Microsoft-Windows-PowerShell%4Operational.evtx` | Commandes exécutées (4103, 4104) |
| Sysmon | `...Logs\Microsoft-Windows-Sysmon%4Operational.evtx` | Processus, connexions, fichiers (si installé) |

Événements de sécurité importants :

| ID | Signification |
|---|---|
| 4624 | Connexion réussie |
| 4625 | Échec de connexion |
| 4648 | Connexion avec credentials explicites (Pass-the-Hash) |
| 4663 | Accès à un objet (fichier, registre) |
| 4688 | Création d'un processus |
| 4720 | Création d'un compte utilisateur |
| 4732 | Ajout à un groupe |
| 7045 | Nouveau service installé |

### Artefacts de l'activité utilisateur

- **Prefetch** (`%WinDir%\Prefetch\`) : fichiers `.pf` indiquant les 8 derniers chemins d'accès d'un exécutable et le nombre de fois qu'il a été lancé
- **LNK files** (`%UserProfile%\AppData\Roaming\Microsoft\Windows\Recent\`) : raccourcis créés automatiquement à l'ouverture de fichiers
- **JumpLists** : fichiers récents par application
- **Thumbcache** : miniatures des images affichées dans l'explorateur (preuve de visualisation)
- **Browser History** : SQLite dans `%UserProfile%\AppData\Local\...` (Chrome, Firefox, Edge)
- **Pagefile.sys / hiberfil.sys** : mémoire virtuelle et hibernation — contiennent des fragments de mémoire

## Artefacts Linux

| Artefact | Chemin | Contenu |
|---|---|---|
| Logs syslog | `/var/log/syslog` ou `/var/log/messages` | Événements système généraux |
| Auth | `/var/log/auth.log` | Authentifications, sudo, SSH |
| Connexions | `/var/log/wtmp` | Historique des connexions (`last`) |
| Tentatives | `/var/log/btmp` | Échecs de connexion (`lastb`) |
| Connexions actuelles | `/var/run/utmp` | Utilisateurs connectés (`who`) |
| Bash history | `~/.bash_history` | Commandes exécutées |
| Crontabs | `/etc/cron*`, `/var/spool/cron/` | Tâches planifiées (persistance) |
| Systemd | `journalctl` | Logs des services systemd |

## Outils DFIR principaux

| Outil | Plateforme | Usage |
|---|---|---|
| **Eric Zimmerman Tools** | Windows | Suite d'outils pour le registre, LNK, prefetch, MFT, timeline |
| **KAPE** (Kroll Artifact Parser) | Windows | Collecte et parsing automatisés d'artefacts |
| **Autopsy** | Multi | Analyse de disques (open source, GUI) |
| **Volatility 3** | Multi | Analyse de mémoire vive |
| **Redline** (FireEye) | Windows | Collecte forensique et analyse comportementale |
| **Velociraptor** | Multi | Endpoint monitoring et collecte à distance |
| **Plaso / log2timeline** | Multi | Création de timeline unifiée (super-timeline) |
| **The Sleuth Kit (TSK)** | Multi | Analyse bas niveau de systèmes de fichiers |
| **FTK Imager** | Windows | Acquisition d'images disque |
| **Wireshark / tshark** | Multi | Analyse de captures réseau |

## Timeline forensique

La super-timeline consolide tous les horodatages en un seul fichier CSV pour analyser la chronologie d'un incident.

```bash
# Créer une timeline avec log2timeline/plaso
log2timeline.py --storage-file timeline.plaso image.dd

# Filtrer et exporter
psort.py -o dynamic -w timeline.csv timeline.plaso

# Exemple de filtrage sur une période
psort.py -o dynamic timeline.plaso "date > '2024-01-01' AND date < '2024-02-01'"
```

Les horodatages NTFS (Windows) se décomposent en quatre timestamps par fichier : `$STANDARD_INFORMATION` (visible) et `$FILE_NAME` (plus difficile à manipuler). Une discordance entre les deux peut indiquer un **timestomping** (manipulation des horodatages par un attaquant).
