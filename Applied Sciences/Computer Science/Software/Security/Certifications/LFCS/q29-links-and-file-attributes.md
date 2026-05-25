# Question 29 — Links and File Attributes

## Énoncé

Solve this question on: `terminal`

1. Create a hard link `/opt/course/29/hard-passwd` pointing to `/etc/passwd`.
2. Create a symbolic link `/opt/course/29/soft-passwd` pointing to `/etc/passwd`.
3. Make `/etc/resolv.conf` immutable so even root cannot edit it without removing the attribute.
4. Write the inode number of `/etc/hostname` into `/opt/course/29/inode`.

## Solution

### Step 1 — Hard link

```bash
sudo ln /etc/passwd /opt/course/29/hard-passwd
ls -li /etc/passwd /opt/course/29/hard-passwd
# both entries share the same inode and link count goes up
```

Hard link properties:
- Points to the **same inode** as the original.
- Cannot cross filesystems.
- Cannot point to a directory (kernel protection).
- The file is only deleted when **all** hard links are removed.

### Step 2 — Symbolic link

```bash
ln -s /etc/passwd /opt/course/29/soft-passwd
ls -l /opt/course/29/soft-passwd
# lrwxrwxrwx ... soft-passwd -> /etc/passwd
```

Symbolic link properties:
- Stores a **path** (not an inode reference).
- Can cross filesystems and link directories.
- Broken if the target moves or is deleted (`ls -l` shows red).

Useful flags:
- `ln -sf target name` — force replace existing link
- `ln -sr target name` — make the symlink relative
- `readlink -f link` — resolve to absolute path
- `stat file` — show inode, links, size, timestamps

### Step 3 — File attributes with chattr

```bash
sudo chattr +i /etc/resolv.conf       # immutable
lsattr /etc/resolv.conf
# ----i---------e----- /etc/resolv.conf
sudo chattr -i /etc/resolv.conf       # remove
```

Common attributes:

| Attr | Meaning |
|---|---|
| `i` | immutable — no edit, rename, delete, link |
| `a` | append-only — only appends, no rewrite/delete |
| `A` | no atime updates |
| `c` | compressed (filesystem dependent) |
| `d` | excluded from `dump` |
| `e` | extent format (informational, ext4) |
| `j` | data journaling |
| `s` | secure deletion (zeroed on delete) |
| `S` | synchronous writes |
| `u` | undeletable — content kept after `rm` |

### Step 4 — Inode number

```bash
stat -c %i /etc/hostname > /opt/course/29/inode
# or:
ls -i /etc/hostname | awk '{print $1}' > /opt/course/29/inode
```

### Extended attributes (xattr)

Separate from `chattr`; used by SELinux, ACLs, custom metadata:
```bash
getfattr -d -m '.*' file              # show all
setfattr -n user.note -v "hello" file
setfattr -x user.note file
```

---

[← Question 28](q28-permissions-and-acl.md) · [Index](Certifications/LFCS/notes.md) · [Question 30 →](q30-pam-configuration.md)
