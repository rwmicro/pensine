# Question 26 — Package Management

## Énoncé

Solve this question on: `app-srv1`

1. Install the package `tree` and write its version into `/opt/course/26/tree-version`.
2. Find which package owns the file `/usr/bin/vim` and write it into `/opt/course/26/owner`.
3. List all files installed by the `nginx` package into `/opt/course/26/nginx-files`.
4. Put a hold on the `openssh-server` package so it is not upgraded by `apt`.

## Solution

The LFCS exam may use either Debian (apt/dpkg) or RHEL (dnf/rpm). Know both.

### Debian / Ubuntu — apt + dpkg

```bash
sudo apt update                                # refresh indexes
sudo apt install tree                          # install
sudo apt remove tree                           # remove (keep config)
sudo apt purge tree                            # remove + config
sudo apt upgrade                               # upgrade all
sudo apt full-upgrade                          # may remove packages
apt list --installed | grep -i tree
apt-cache search keyword                       # search
apt-cache policy nginx                         # versions and origins
```

Lower-level `dpkg`:
```bash
dpkg -l                                        # all installed
dpkg -l tree                                   # status of one package
dpkg -s tree                                   # detailed status
dpkg -L nginx > /opt/course/26/nginx-files     # files installed by pkg
dpkg -S /usr/bin/vim > /opt/course/26/owner    # which pkg owns a file
sudo dpkg -i package.deb                       # install local .deb
sudo dpkg --configure -a                       # finish broken installs
```

Hold a package (prevents upgrade):
```bash
sudo apt-mark hold openssh-server
sudo apt-mark unhold openssh-server
apt-mark showhold
```

### RHEL / Fedora — dnf + rpm

```bash
sudo dnf install tree
sudo dnf remove tree
sudo dnf update                                # upgrade all
sudo dnf search keyword
sudo dnf info tree
sudo dnf provides /usr/bin/vim                 # which pkg owns a file
sudo dnf history                               # transaction log
sudo dnf history undo 42                       # roll back transaction
sudo dnf list installed
sudo dnf clean all
sudo dnf groupinstall "Development Tools"
```

Lower-level `rpm`:
```bash
rpm -qa                                        # all installed
rpm -qi tree                                   # info
rpm -ql nginx                                  # files in installed pkg
rpm -qf /usr/bin/vim                           # owning pkg
rpm -V nginx                                   # verify integrity
sudo rpm -ivh package.rpm
sudo rpm -e tree                               # erase
```

Version lock (RHEL):
```bash
sudo dnf install python3-dnf-plugin-versionlock
sudo dnf versionlock add openssh-server
sudo dnf versionlock list
sudo dnf versionlock delete openssh-server
```

### Step 1 — Tree version

```bash
sudo apt install -y tree
dpkg -s tree | awk '/^Version:/ {print $2}' > /opt/course/26/tree-version
# RHEL:
rpm -q --qf '%{VERSION}-%{RELEASE}\n' tree > /opt/course/26/tree-version
```

### Repositories

Debian: files under `/etc/apt/sources.list` and `/etc/apt/sources.list.d/*.list`.

RHEL: files under `/etc/yum.repos.d/*.repo`. Enable/disable:
```bash
sudo dnf config-manager --enable powertools
sudo dnf config-manager --add-repo https://example.com/repo.repo
```

### GPG keys

Debian: `/etc/apt/trusted.gpg.d/` or `/etc/apt/keyrings/`.
RHEL: `rpm --import https://example.com/key.gpg`.

---

[← Question 25](q25-sysctl-kernel-parameters.md) · [Index](Certifications/LFCS/notes.md) · [Question 27 →](q27-bash-scripting.md)
