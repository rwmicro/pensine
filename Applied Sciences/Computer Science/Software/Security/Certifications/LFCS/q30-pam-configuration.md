# Question 30 — PAM Configuration

## Énoncé

Solve this question on: `app-srv1`

1. Block the user `mallory` from logging in via SSH using PAM (`pam_listfile`).
2. Enforce a minimum password length of `12` characters with at least one digit and one upper-case letter.
3. Lock a local account after `5` consecutive failed login attempts for `15` minutes.

## Solution

### PAM crash course

PAM = **Pluggable Authentication Modules**. Each service (sshd, login, sudo…) has a config file under `/etc/pam.d/`.

A PAM rule has the form:
```
<type>   <control>   <module>   [arguments]
```

| Type | Purpose |
|---|---|
| `auth` | identify the user (password, key, token) |
| `account` | account validity (expired? allowed?) |
| `password` | password change rules |
| `session` | set up/tear down session (mount homedir, logging) |

| Control | Behaviour |
|---|---|
| `required` | must pass; continues either way |
| `requisite` | must pass; stops immediately on failure |
| `sufficient` | success → stop with success |
| `optional` | result ignored unless only module |
| `[success=1 default=ignore]` | precise jump syntax |

### Step 1 — Deny specific users via pam_listfile

Create the deny list:
```bash
sudo bash -c 'echo mallory > /etc/ssh/denied-users'
sudo chmod 600 /etc/ssh/denied-users
```

Edit `/etc/pam.d/sshd`, add **near the top** of the `auth` stack:
```
auth required pam_listfile.so item=user sense=deny file=/etc/ssh/denied-users onerr=succeed
```

- `sense=deny` — listed users are denied
- `sense=allow` — only listed users are allowed
- `item=user|group|tty|rhost|ruser|shell`
- `onerr=succeed` — if the file is missing, do not block

Restart sshd: `sudo systemctl restart sshd`.

### Step 2 — Password strength via pam_pwquality

Install if needed:
```bash
sudo apt install libpam-pwquality       # Debian
sudo dnf install libpwquality           # RHEL
```

Edit `/etc/security/pwquality.conf`:
```ini
minlen = 12
dcredit = -1          # require at least 1 digit
ucredit = -1          # at least 1 uppercase
lcredit = -1          # at least 1 lowercase
ocredit = -1          # at least 1 other
minclass = 3
retry = 3
```

Negative values = **required count**; positive values = bonus credit.

Make sure `/etc/pam.d/common-password` (Debian) or `/etc/pam.d/system-auth` (RHEL) contains:
```
password requisite pam_pwquality.so retry=3
```

### Step 3 — Account lockout with pam_faillock (RHEL) / pam_tally2 (older)

RHEL 8+ / Fedora — `pam_faillock`:

Edit `/etc/security/faillock.conf`:
```ini
deny = 5
unlock_time = 900
fail_interval = 900
even_deny_root = no
```

Then in `/etc/pam.d/system-auth` and `/etc/pam.d/password-auth`:
```
auth        required      pam_faillock.so preauth silent
auth        sufficient    pam_unix.so nullok
auth        [default=die] pam_faillock.so authfail
account     required      pam_faillock.so
```

Manage manually:
```bash
sudo faillock --user alice               # show count
sudo faillock --user alice --reset       # clear
```

Debian — `pam_tally2` (older) or `pam_faillock`:
```
auth required pam_tally2.so deny=5 unlock_time=900 onerr=fail
account required pam_tally2.so
```

Reset:
```bash
sudo pam_tally2 --user alice --reset
```

### Test PAM rules safely

Always keep a second open root session before editing PAM — a syntax error can lock everyone out.

```bash
sudo pamtester sshd alice authenticate
```

### Other useful PAM modules

| Module | Purpose |
|---|---|
| `pam_limits.so` | enforce `/etc/security/limits.conf` (see [[q20-user-and-group-limits]]) |
| `pam_unix.so` | classic /etc/shadow check |
| `pam_access.so` | per-user/group/host access rules (`/etc/security/access.conf`) |
| `pam_time.so` | restrict by hour/day |
| `pam_nologin.so` | block non-root when `/etc/nologin` exists |
| `pam_env.so` | set env vars from `/etc/security/pam_env.conf` |
| `pam_mkhomedir.so` | create home dir on first login |
| `pam_lastlog.so` | display last login info |

---

[← Question 29](q29-links-and-file-attributes.md) · [Index](Certifications/LFCS/notes.md) · [Question 31 →](q31-network-configuration.md)
