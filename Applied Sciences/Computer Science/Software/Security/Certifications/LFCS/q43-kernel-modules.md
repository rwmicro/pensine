# Question 43 — Kernel Modules

## Notes d'apprentissage

Le noyau Linux est *modulaire* : au lieu de tout embarquer en dur, il charge des **modules** (pilotes, systèmes de fichiers, protocoles réseau) à la demande. Cela garde le noyau léger et permet d'ajouter le support d'un matériel sans recompiler.

**Modèle mental : du fichier `.ko` au noyau vivant.**

```
/lib/modules/$(uname -r)/*.ko   ──modprobe──►   noyau en cours d'exécution
(modules disponibles sur disque)               (modules chargés, vus par lsmod)
```

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

**Blacklister n'est pas bloquer totalement.** `blacklist NAME` empêche le chargement *automatique* (par détection matérielle ou dépendance), mais un `modprobe NAME` manuel passe encore. Pour bloquer même le manuel : `install NAME /bin/false`.

**Pièges** :
- Un module déjà chargé reste actif malgré une blacklist tant qu'on ne redémarre pas (ou `modprobe -r`).
- `modprobe -r` refuse de décharger un module **en cours d'utilisation** (compteur *used by* > 0 dans `lsmod`).
- Si un module est intégré à l'initramfs, blacklister ne suffit pas : régénérer l'initramfs (`update-initramfs -u` / `dracut -f`).
- Les paramètres au boot se mettent dans `/etc/modprobe.d/`, pas dans `/etc/modules-load.d/`.

## Énoncé

Solve this question on: `terminal`

1. List all currently loaded kernel modules and write the count into `/opt/course/43/count`.
2. Show detailed information about the `vfat` module and write its `description` line into `/opt/course/43/vfat-desc`.
3. Load the `dummy` module now, then unload it.
4. Ensure the `dummy` module is **loaded automatically at boot**.
5. **Blacklist** the `pcspkr` module so it is never loaded automatically.

## Solution

Kernel modules are pieces of code (drivers, filesystems, network protocols) that can be loaded into and removed from the running kernel on demand. Modules live under `/lib/modules/$(uname -r)/` and have the `.ko` extension.

### Step 1 — List loaded modules

```bash
lsmod                               # name, size, used-by count, dependents
lsmod | wc -l                       # includes the header line
# count without the header:
echo $(($(lsmod | wc -l) - 1)) > /opt/course/43/count
```

`lsmod` is just a formatted view of `/proc/modules`.

### Step 2 — Inspect a module

```bash
modinfo vfat                        # full metadata
modinfo -F description vfat         # only the description field
modinfo -n vfat                     # path to the .ko file
modinfo -F depends vfat             # dependencies

modinfo -F description vfat > /opt/course/43/vfat-desc
```

`modinfo` works on a module name **or** a `.ko` path, even if the module is not loaded.

### Step 3 — Load and unload now

```bash
sudo modprobe dummy                 # load (resolves dependencies)
lsmod | grep dummy                  # verify
sudo modprobe -r dummy              # unload (and unused deps)
```

- `modprobe` resolves dependencies via `/lib/modules/$(uname -r)/modules.dep`. Always prefer it.
- `insmod /path/to.ko` / `rmmod name` are the low-level tools — they do **not** resolve dependencies. Rarely the right choice.
- `modprobe -r` refuses to unload a module that is still in use (`used by` count > 0 in `lsmod`).

Pass parameters when loading:
```bash
sudo modprobe dummy numdummies=2
modinfo -p dummy                    # list accepted parameters
```

### Step 4 — Load automatically at boot

Create a file under `/etc/modules-load.d/` (one module name per line):
```bash
echo dummy | sudo tee /etc/modules-load.d/dummy.conf
```

`systemd-modules-load.service` reads every `*.conf` in `/etc/modules-load.d/` at boot and `modprobe`s each listed module.

To also pass **parameters** at every load, add a file under `/etc/modprobe.d/`:
```bash
echo "options dummy numdummies=2" | sudo tee /etc/modprobe.d/dummy.conf
```

> Debian also reads the legacy `/etc/modules` file for boot-time loading; `/etc/modules-load.d/` is the systemd-native, distro-agnostic way.

### Step 5 — Blacklist a module

```bash
echo "blacklist pcspkr" | sudo tee /etc/modprobe.d/blacklist-pcspkr.conf
```

`blacklist` prevents **automatic** loading (by udev/hardware detection or as a dependency-by-alias). It does **not** stop a manual `modprobe pcspkr`. To block even manual loading, redirect the install command:
```bash
echo "install pcspkr /bin/false" | sudo tee -a /etc/modprobe.d/blacklist-pcspkr.conf
```

A module already loaded into the running kernel must be removed manually (`modprobe -r pcspkr`) or after a reboot. If it is built into the initramfs, regenerate it:
```bash
sudo update-initramfs -u              # Debian/Ubuntu
sudo dracut -f                        # RHEL/Fedora
```

### Reference

| Command | Purpose |
|---|---|
| `lsmod` | list loaded modules |
| `modinfo NAME` | show module metadata / parameters |
| `modprobe NAME` | load (with dependency resolution) |
| `modprobe -r NAME` | unload |
| `insmod` / `rmmod` | low-level load/unload (no deps) |
| `depmod` | rebuild `modules.dep` after adding a `.ko` |

| File / directory | Role |
|---|---|
| `/etc/modules-load.d/*.conf` | modules to load at boot |
| `/etc/modprobe.d/*.conf` | options, aliases, blacklist, install rules |
| `/lib/modules/$(uname -r)/` | the modules themselves |
| `/proc/modules` | raw loaded-module table (source of `lsmod`) |
