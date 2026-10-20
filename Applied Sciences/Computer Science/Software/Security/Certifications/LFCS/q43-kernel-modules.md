---
title: "LFCS Q43 — Modules du noyau"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Certifications > LFCS"
tags: [lfcs, linux, certification, kernel, modules]
date: "2026-08-09"
---

# Question 43 — Modules du noyau

## Notes d'apprentissage

Le noyau Linux est *modulaire* : au lieu de tout embarquer en dur, il charge des **modules** (pilotes, systèmes de fichiers, protocoles réseau) à la demande. Cela garde le noyau léger et permet d'ajouter le support d'un matériel sans recompiler.

> [!tip] Modèle mental : du fichier `.ko` au noyau vivant
> ```
> /lib/modules/$(uname -r)/*.ko   ──modprobe──►   noyau en cours d'exécution
> (modules disponibles sur disque)               (modules chargés, vus par lsmod)
> ```

Un module est un fichier `.ko` (*kernel object*). Chargé, il devient partie intégrante du noyau ; déchargé, il libère ses ressources.

**`modprobe` plutôt que `insmod` — la distinction clé.** `modprobe` résout les **dépendances** automatiquement (via `modules.dep`) et travaille par nom ; `insmod`/`rmmod` sont bas niveau, exigent un chemin complet et ne gèrent aucune dépendance. Préférer **toujours** `modprobe`.

```bash
lsmod                 # modules chargés (vue de /proc/modules)
modinfo NAME          # métadonnées + paramètres acceptés
modprobe NAME         # charger (avec dépendances)
modprobe -r NAME      # décharger (si non utilisé)
```

**Persistance : deux dossiers, deux rôles.**
- `/etc/modules-load.d/*.conf` → modules à **charger au boot** (un nom par ligne).
- `/etc/modprobe.d/*.conf` → **options**, alias, et **blacklist** (empêcher le chargement).

> [!warning] Blacklister n'est pas bloquer totalement
> `blacklist NAME` empêche le chargement *automatique* (par détection matérielle ou dépendance), mais un `modprobe NAME` manuel passe encore. Pour bloquer même le manuel : `install NAME /bin/false`.

> [!warning] Pièges
> - Un module déjà chargé reste actif malgré une blacklist tant qu'on ne redémarre pas (ou `modprobe -r`).
> - `modprobe -r` refuse de décharger un module **en cours d'utilisation** (compteur *used by* > 0 dans `lsmod`).
> - Si un module est intégré à l'initramfs, blacklister ne suffit pas : régénérer l'initramfs (`update-initramfs -u` / `dracut -f`).
> - Les paramètres au boot se mettent dans `/etc/modprobe.d/`, pas dans `/etc/modules-load.d/`.

## Énoncé

Résolvez cette question sur : `terminal`

1. Listez tous les modules du noyau actuellement chargés et écrivez leur nombre dans `/opt/course/43/count`.
2. Affichez les informations détaillées sur le module `vfat` et écrivez sa ligne `description` dans `/opt/course/43/vfat-desc`.
3. Chargez le module `dummy` maintenant, puis déchargez-le.
4. Assurez-vous que le module `dummy` est **chargé automatiquement au démarrage**.
5. **Blacklistez** le module `pcspkr` afin qu'il ne soit jamais chargé automatiquement.

## Solution

Les modules du noyau sont des morceaux de code (pilotes, systèmes de fichiers, protocoles réseau) qui peuvent être chargés dans le noyau en cours d'exécution et en retirés à la demande. Les modules résident sous `/lib/modules/$(uname -r)/` et portent l'extension `.ko`.

### Étape 1 — Lister les modules chargés

```bash
lsmod                               # name, size, used-by count, dependents
lsmod | wc -l                       # includes the header line
# count without the header:
echo $(($(lsmod | wc -l) - 1)) > /opt/course/43/count
```

`lsmod` n'est qu'une vue formatée de `/proc/modules`.

### Étape 2 — Inspecter un module

```bash
modinfo vfat                        # full metadata
modinfo -F description vfat         # only the description field
modinfo -n vfat                     # path to the .ko file
modinfo -F depends vfat             # dependencies

modinfo -F description vfat > /opt/course/43/vfat-desc
```

`modinfo` fonctionne avec un nom de module **ou** un chemin de fichier `.ko`, même si le module n'est pas chargé.

### Étape 3 — Charger et décharger maintenant

```bash
sudo modprobe dummy                 # load (resolves dependencies)
lsmod | grep dummy                  # verify
sudo modprobe -r dummy              # unload (and unused deps)
```

- `modprobe` résout les dépendances via `/lib/modules/$(uname -r)/modules.dep`. Préférez-le toujours.
- `insmod /path/to.ko` / `rmmod name` sont les outils bas niveau — ils ne résolvent **pas** les dépendances. Rarement le bon choix.
- `modprobe -r` refuse de décharger un module encore utilisé (compteur `used by` > 0 dans `lsmod`).

Passer des paramètres au chargement :
```bash
sudo modprobe dummy numdummies=2
modinfo -p dummy                    # list accepted parameters
```

### Étape 4 — Charger automatiquement au démarrage

Créez un fichier sous `/etc/modules-load.d/` (un nom de module par ligne) :
```bash
echo dummy | sudo tee /etc/modules-load.d/dummy.conf
```

`systemd-modules-load.service` lit chaque `*.conf` de `/etc/modules-load.d/` au démarrage et exécute `modprobe` pour chaque module listé.

Pour passer aussi des **paramètres** à chaque chargement, ajoutez un fichier sous `/etc/modprobe.d/` :
```bash
echo "options dummy numdummies=2" | sudo tee /etc/modprobe.d/dummy.conf
```

> Debian lit aussi le fichier historique `/etc/modules` pour le chargement au démarrage ; `/etc/modules-load.d/` est la méthode native systemd, indépendante de la distribution.

### Étape 5 — Blacklister un module

```bash
echo "blacklist pcspkr" | sudo tee /etc/modprobe.d/blacklist-pcspkr.conf
```

`blacklist` empêche le chargement **automatique** (par udev, détection matérielle ou via un alias de dépendance). Cela n'empêche **pas** un `modprobe pcspkr` manuel. Pour bloquer même le chargement manuel, redirigez la commande d'installation :
```bash
echo "install pcspkr /bin/false" | sudo tee -a /etc/modprobe.d/blacklist-pcspkr.conf
```

Un module déjà chargé dans le noyau en cours d'exécution doit être retiré à la main (`modprobe -r pcspkr`) ou après un redémarrage. S'il est intégré à l'initramfs, régénérez celui-ci :
```bash
sudo update-initramfs -u              # Debian/Ubuntu
sudo dracut -f                        # RHEL/Fedora
```

### Référence

| Commande | Rôle |
|---|---|
| `lsmod` | lister les modules chargés |
| `modinfo NAME` | afficher les métadonnées et paramètres du module |
| `modprobe NAME` | charger (avec résolution des dépendances) |
| `modprobe -r NAME` | décharger |
| `insmod` / `rmmod` | chargement/déchargement bas niveau (sans dépendances) |
| `depmod` | reconstruire `modules.dep` après l'ajout d'un `.ko` |

| Fichier / répertoire | Rôle |
|---|---|
| `/etc/modules-load.d/*.conf` | modules à charger au démarrage |
| `/etc/modprobe.d/*.conf` | options, alias, blacklist, règles d'installation |
| `/lib/modules/$(uname -r)/` | les modules eux-mêmes |
| `/proc/modules` | table brute des modules chargés (source de `lsmod`) |
