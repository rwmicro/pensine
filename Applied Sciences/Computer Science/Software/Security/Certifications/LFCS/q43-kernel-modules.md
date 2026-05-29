# Question 43 — Kernel Modules

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
