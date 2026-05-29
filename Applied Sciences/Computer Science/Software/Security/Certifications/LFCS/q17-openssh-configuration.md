# Question 17 — OpenSSH Configuration

## Énoncé

Solve this question on: `data-002`

You need to perform OpenSSH server configuration changes on `data-002`. Users `marta` and `cilla` exist on that server and can be used for testing. Passwords are their username and shouldn't be changed. Please go ahead and:
1. Disable `X11Forwarding`
2. Disable `PasswordAuthentication` for everyone but user `marta`
3. Enable `Banner` with file `/etc/ssh/sshd-banner` for users `marta` and `cilla`

> In case of misconfiguration you can still access the instance using `sudo lxc exec data-002 bash`

## Solution

### Step 1
We are required to perform ssh server config changes, always fun because nothing can ever go wrong!

We're doing a simple one first:
```bash
ssh data-002
root@data-002:~# sshd -T | grep -i X11Forwarding
x11forwarding yes
root@data-002:~$ vim /etc/ssh/sshd_config.d/custom.conf
X11Forwarding no
```

We could also edit `/etc/ssh/sshd_config` directly, but it is probably cleaner to override via drop-in config files. We can verify if the config change is accepted before restart:
```bash
root@data-002:~# sshd -T | grep -i X11Forwarding
x11forwarding no
```

Now we can restart the ssh service:
```bash
root@data-002:~$ service ssh restart # no error output means good
```

**Step 2+3**

We now need to first disable `PasswordAuthentication` globally and then enable it for user `marta`. Then we also add the `Banner` settings for users `marta` and `cilla`:
```bash
root@data-002:~$ vim /etc/ssh/sshd_config.d/custom.conf
X11Forwarding no
PasswordAuthentication no
Match User marta
  PasswordAuthentication yes
  Banner /etc/ssh/sshd-banner
Match User cilla
  Banner /etc/ssh/sshd-banner
```

Using `Match User` or `Match Group` we can override global settings for specific users and groups.

It's **very important** to add any `Match` lines at the very bottom of the `/etc/ssh/sshd_config` config file because all following lines are considered part of that block until another `Match` or the end of the file.

If drop-in configuration files are used, such as in `/etc/ssh/sshd_config.d/`, this rule still applies because all files are loaded in lexical (alphabetical) order.

Therefore, if you have multiple drop-in files and want to include `Match` directives safely, one reliable approach is to create a file named something like `sshd_config.d/99-match-users.conf` to ensure it will be read last.

We can verify our settings:
```bash
root@data-002:~# sshd -T | grep banner
debianbanner yes
banner none
root@data-002:~# sshd -T -C user=marta | grep banner
debianbanner yes
banner /etc/ssh/sshd-banner
root@data-002:~# sshd -T -C user=cilla | grep banner
debianbanner yes
banner /etc/ssh/sshd-banner
root@data-002:~# sshd -T -C user=root | grep banner
debianbanner yes
banner none
```

This looks great. Let's test if it works:
```bash
root@data-002:~$ service ssh restart
root@data-002:~$ exit
ssh marta@data-002
Hello our favorite user!
marta@data-002's password:
Last login: Tue Nov  4 13:27:24 2025 from 192.168.10.1
```

User `marta` sees the banner message and can log in using password.
```bash
ssh cilla@data-002
Hello our favorite user!
cilla@data-002: Permission denied (publickey).
```

User `cilla` sees the banner message but cannot log in using password.
```bash
ssh root@data-002
Last login: Tue Nov  4 13:38:00 2025 from 192.168.10.1
```

User `root` can still log in and does not see the banner message.

