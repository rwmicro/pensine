# Question 21 — GRUB and Bootloader

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

---

[← Question 20](q20-user-and-group-limits.md) · [Index](Certifications/LFCS/notes.md) · [Question 22 →](q22-systemd-targets-and-services.md)
