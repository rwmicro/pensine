# Question 25 — Sysctl Kernel Parameters

## Notes d'apprentissage

`sysctl` lit et modifie les **paramètres du noyau en cours d'exécution** : routage, mémoire virtuelle, sécurité réseau… C'est le réglage fin du comportement du système, sans recompiler ni redémarrer.

**Modèle mental : un paramètre = un fichier sous `/proc/sys/`.** La notation à points de sysctl reflète l'arborescence : les points deviennent des slashes.

```
net.ipv4.ip_forward   ◄────►   /proc/sys/net/ipv4/ip_forward
   sysctl net.ipv4.ip_forward         cat /proc/sys/net/ipv4/ip_forward
```

**La distinction centrale : temporaire vs persistant.**

```
sysctl -w clé=valeur          → appliqué MAINTENANT, perdu au reboot
echo v > /proc/sys/.../clé    → idem (écriture directe du fichier)

fichier dans /etc/sysctl.d/   → PERSISTANT, rejoué à chaque boot
   + sysctl --system          → appliquer tout de suite
```

C'est exactement le tri de l'exercice : `vm.swappiness` « pour cette session » = `sysctl -w` ; le forwarding/IPv6 « persistant » = un fichier `.conf`.

**Pourquoi un fichier dans `/etc/sysctl.d/` plutôt que `/etc/sysctl.conf` ?** Même logique que partout en systemd : les fichiers drop-in sont plus propres, survivent aux mises à jour, et se chargent dans un ordre déterministe. Le préfixe numérique (`99-`) contrôle la priorité — le plus grand nombre gagne, d'où `99-` pour surcharger les défauts du système.

**Paramètres à reconnaître** (sécurité et perf) :
- `net.ipv4.ip_forward` : transforme la machine en routeur.
- `net.ipv4.tcp_syncookies` : protection anti SYN-flood.
- `net.ipv4.conf.all.rp_filter` : anti-spoofing (reverse path).
- `vm.swappiness` (0–100) : agressivité du swap.

**Pièges** :
- Un `sysctl -w` n'est **pas** persistant : pour survivre au reboot, écrire un fichier `.conf` puis `sysctl --system` (ou `-p`).
- Désactiver IPv6 demande souvent **trois** lignes (`all`, `default`, `lo`) — en oublier une laisse IPv6 actif quelque part.
- `sysctl -n clé` affiche **uniquement** la valeur (pratique pour écrire dans un fichier sans le nom de la clé).
- Lié au démarrage : `net.ipv4.ip_forward` était la question q01 en lecture seule.

## Énoncé

Solve this question on: `terminal`

1. Enable IPv4 packet forwarding **persistently**.
2. Disable IPv6 on all interfaces persistently.
3. Set `vm.swappiness` to `10` for the current session only.
4. Write the value of `kernel.hostname` into `/opt/course/25/hostname`.

## Solution

### Read current values

```bash
sysctl kernel.hostname
sysctl -a                                   # dump everything
sysctl -a 2>/dev/null | grep forward
cat /proc/sys/net/ipv4/ip_forward           # equivalent direct read
```

Each kernel parameter maps to a file under `/proc/sys/` — dots become slashes (`net.ipv4.ip_forward` ↔ `/proc/sys/net/ipv4/ip_forward`).

### Step 1 — Persistent IP forwarding

Create a drop-in file (preferred over editing `/etc/sysctl.conf`):
```bash
sudo tee /etc/sysctl.d/99-forwarding.conf <<'EOF'
net.ipv4.ip_forward = 1
EOF
sudo sysctl --system            # reload all .conf files
# or apply that file only:
sudo sysctl -p /etc/sysctl.d/99-forwarding.conf
```

### Step 2 — Disable IPv6 persistently

```bash
sudo tee /etc/sysctl.d/99-no-ipv6.conf <<'EOF'
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
EOF
sudo sysctl --system
```

### Step 3 — Set a value only for this session

```bash
sudo sysctl -w vm.swappiness=10
# equivalent:
echo 10 | sudo tee /proc/sys/vm/swappiness
```

Non-persistent changes are lost at reboot.

### Step 4 — Write a single value

```bash
sysctl -n kernel.hostname > /opt/course/25/hostname
```

### Order of evaluation

`sysctl --system` reads, in order:
1. `/etc/sysctl.d/*.conf`
2. `/run/sysctl.d/*.conf`
3. `/usr/local/lib/sysctl.d/*.conf`
4. `/usr/lib/sysctl.d/*.conf`
5. `/lib/sysctl.d/*.conf`
6. `/etc/sysctl.conf`

Within a directory, files are sorted by name — use `99-` prefix to override vendor defaults.

### Common tunables to recognise

| Key | Effect |
|---|---|
| `net.ipv4.ip_forward` | enable IP routing |
| `net.ipv4.conf.all.rp_filter` | reverse-path filtering (anti-spoof) |
| `net.ipv4.tcp_syncookies` | SYN-flood protection |
| `vm.swappiness` | swap aggressiveness (0–100) |
| `vm.overcommit_memory` | memory overcommit policy |
| `kernel.pid_max` | max PID |
| `fs.file-max` | system-wide open file limit |
| `kernel.panic` | seconds before reboot on panic |
