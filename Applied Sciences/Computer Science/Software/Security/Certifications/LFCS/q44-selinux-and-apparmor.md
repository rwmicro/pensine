# Question 44 — SELinux and AppArmor (MAC)

## Énoncé

Solve this question on: `terminal`

RHEL family (`data-001`, SELinux) — tasks 1 to 5.
Debian family (`web-srv1`, AppArmor) — tasks 6 to 7.

1. Report the current SELinux mode and write it into `/opt/course/44/mode`.
2. Switch SELinux to **permissive** for the current session without rebooting.
3. Configure SELinux to be **enforcing** persistently after reboot.
4. The web root has moved to `/srv/www`. Set the correct SELinux file context so Apache (`httpd`) can serve it.
5. Allow the `httpd` service to make outbound network connections by setting the right SELinux boolean persistently.
6. (AppArmor) List all loaded profiles and their mode.
7. (AppArmor) Put the `usr.sbin.tcpdump` profile into **complain** mode.

## Solution

Mandatory Access Control (MAC) adds a policy layer **on top of** standard Unix permissions: even root is constrained by the policy. RHEL/Fedora use **SELinux**; Debian/Ubuntu/SUSE use **AppArmor**. The two are mutually exclusive in practice — know whichever matches your exam distro.

## SELinux (RHEL family)

SELinux labels every process and file with a context `user:role:type:level`. The **type** is what matters most (type enforcement): a process running in domain `httpd_t` may only touch files labelled `httpd_sys_content_t`, etc.

### Step 1 — Current mode

```bash
getenforce                          # Enforcing | Permissive | Disabled
sestatus                            # detailed: current + config-file mode
getenforce > /opt/course/44/mode
```

- **Enforcing** — policy denials are blocked and logged.
- **Permissive** — denials are only logged (great for debugging).
- **Disabled** — SELinux off entirely (requires reboot to change to/from).

### Step 2 — Change mode for the current session

```bash
sudo setenforce 0                   # → Permissive
sudo setenforce 1                   # → Enforcing
```

This is **not** persistent and cannot move to/from `Disabled`.

### Step 3 — Persistent mode

Edit `/etc/selinux/config`:
```bash
SELINUX=enforcing                   # enforcing | permissive | disabled
```
Takes effect on next boot. Going from `disabled` to `enforcing` triggers a full filesystem relabel on reboot (or force it with `sudo fixfiles -F onboot`).

### Step 4 — Fix a file context

The right type for web content served by Apache is `httpd_sys_content_t`. Add a persistent rule, then apply it:
```bash
# add the rule to the local policy (persists across relabels)
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/www(/.*)?'
# apply it to existing files now
sudo restorecon -Rv /srv/www
```

- `semanage fcontext -a` records the mapping permanently.
- `restorecon` resets a file's context to what policy says it should be.
- `chcon -t httpd_sys_content_t -R /srv/www` changes it **temporarily** — a relabel will revert it. Prefer `semanage` + `restorecon` for anything persistent.
- Inspect contexts with `ls -Z`, processes with `ps -eZ`.

If `semanage` is missing: `sudo dnf install policycoreutils-python-utils`.

### Step 5 — SELinux booleans

Booleans toggle predefined policy behaviours without writing custom policy.
```bash
getsebool -a | grep httpd           # list httpd-related booleans
sudo setsebool -P httpd_can_network_connect on
```
`-P` makes it persistent across reboots (writes to policy). Without `-P` it reverts on reboot.

### Troubleshooting denials

```bash
sudo ausearch -m AVC -ts recent     # raw audit denials
sudo sealert -a /var/log/audit/audit.log   # human-readable, suggests fixes (setroubleshoot)
```
A common exam pattern: a service fails to start *only* when SELinux is enforcing → set it permissive to confirm it's SELinux, then read the AVC and fix the context or boolean.

---

## AppArmor (Debian family)

AppArmor is **path-based** (not label-based): each profile (under `/etc/apparmor.d/`) lists the files and capabilities a specific binary may use. Modes are **enforce** (block + log) or **complain** (log only).

### Step 6 — List profiles

```bash
sudo aa-status                      # or: sudo apparmor_status
```
Shows how many profiles are loaded, and which are in enforce vs complain mode and which processes they apply to.

### Step 7 — Put a profile in complain mode

```bash
sudo aa-complain /usr/sbin/tcpdump          # complain (log only)
sudo aa-enforce /usr/sbin/tcpdump           # back to enforce
sudo aa-disable /usr/sbin/tcpdump           # unload + disable the profile
```
The helpers live in the `apparmor-utils` package. Profiles are named after the binary path with `/` → `.` (e.g. `usr.sbin.tcpdump`). After editing a profile file, reload it:
```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.tcpdump
```

### Reference

| SELinux | AppArmor | Purpose |
|---|---|---|
| `getenforce` / `sestatus` | `aa-status` | show current state |
| `setenforce 0/1` | `aa-complain` / `aa-enforce` | switch mode (per object) |
| `/etc/selinux/config` | enable/disable per profile | persistent mode |
| `ls -Z`, `ps -eZ` | profile path lists files | inspect access |
| `semanage` + `restorecon` | edit `/etc/apparmor.d/` + `apparmor_parser -r` | adjust policy |
| `setsebool -P` | (n/a — edit profile) | toggle behaviour |
| `ausearch` / `sealert` | `dmesg` / `journalctl` | read denials |
