# Question 21 — GRUB and Bootloader

## Notes d'apprentissage

GRUB est le *bootloader* : le premier programme que le firmware charge, dont le rôle est de trouver un noyau, lui passer des paramètres, et lui donner la main. Comprendre cette chaîne permet de réparer une machine qui ne démarre plus.

**Modèle mental : la séquence de démarrage.**

```
firmware (BIOS/UEFI) ──► GRUB ──► noyau Linux + initramfs ──► systemd (PID 1) ──► services
                          │           │
                          │           └ reçoit la "kernel command line" (cmdline)
                          └ lit /boot/grub/grub.cfg, affiche le menu
```

**Le piège central : on n'édite JAMAIS `grub.cfg` à la main.** Ce fichier (`/boot/grub/grub.cfg`) est *généré*. La configuration se fait dans `/etc/default/grub`, puis on **régénère** :

```
/etc/default/grub  ──[ update-grub / grub-mkconfig ]──►  /boot/grub/grub.cfg
(ce qu'on édite)                                          (ce qui est lu au boot)
```

Oublier la régénération = les changements n'ont aucun effet au prochain démarrage. C'est l'erreur la plus fréquente.

**`GRUB_CMDLINE_LINUX` vs `GRUB_CMDLINE_LINUX_DEFAULT`** : le premier s'applique à **toutes** les entrées (y compris le mode rescue), le second seulement aux entrées normales. Choisir le bon selon que le paramètre doit valoir aussi en mode secours.

**La kernel command line en lecture seule** : `/proc/cmdline` montre les paramètres avec lesquels le noyau actuel a réellement démarré — utile pour vérifier.

**Pourquoi c'est vital en pratique** : éditer une entrée au menu GRUB (touche `e`) permet d'ajouter `single`, `systemd.unit=rescue.target` ou `init=/bin/bash` pour reprendre la main sur un système cassé ou dont on a perdu le mot de passe root. C'est l'outil de dépannage ultime — et donc aussi un point de sécurité physique (protéger GRUB par mot de passe).

**Pièges** :
- Pas de régénération (`update-grub`) après édition = aucun effet.
- Les chemins diffèrent : `/boot/grub/grub.cfg` (Debian) vs `/boot/grub2/grub.cfg` (RHEL BIOS) vs `/boot/efi/...` (UEFI). Voir [[q45-rhel-vs-debian-equivalents]].
- `grub-install` réinstalle le bootloader sur le disque ; à ne pas confondre avec la régénération de la config.

## Énoncé

Solve this question on: `terminal`

1. Set the default GRUB timeout to `3` seconds.
2. Add the kernel boot parameter `quiet` to all entries.
3. Regenerate the GRUB configuration file so the changes apply at next boot.
4. Write the current default kernel command line into `/opt/course/21/cmdline`.

## Solution

### Step 1 — Edit GRUB defaults

The main file to edit is `/etc/default/grub`:
```bash
sudo vim /etc/default/grub
```

Set or update:
```ini
GRUB_TIMEOUT=3
GRUB_CMDLINE_LINUX_DEFAULT="quiet"
```

Key variables to remember:
- `GRUB_DEFAULT` — index or title of the default entry (`0`, `saved`, …)
- `GRUB_TIMEOUT` — countdown in seconds before booting the default entry
- `GRUB_CMDLINE_LINUX` — applied to **all** entries (rescue included)
- `GRUB_CMDLINE_LINUX_DEFAULT` — applied to normal (non-rescue) entries only

### Step 2 — Regenerate the GRUB config

Debian/Ubuntu:
```bash
sudo update-grub
# equivalent to:
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

RHEL/Fedora (BIOS):
```bash
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
```

RHEL/Fedora (UEFI):
```bash
sudo grub2-mkconfig -o /boot/efi/EFI/redhat/grub.cfg
```

### Step 3 — Inspect the active kernel cmdline

```bash
cat /proc/cmdline > /opt/course/21/cmdline
```

### Reinstall GRUB on the MBR

If the bootloader itself is damaged:
```bash
sudo grub-install /dev/sda          # BIOS systems
sudo grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB
```

### Boot temporarily into another mode

At the GRUB menu, press `e` on the entry and append to the `linux` line:
- `single` or `1` — single-user (rescue) mode
- `systemd.unit=rescue.target`
- `systemd.unit=emergency.target`
- `init=/bin/bash` — bypass init entirely

Press `Ctrl+X` or `F10` to boot the modified entry once.

