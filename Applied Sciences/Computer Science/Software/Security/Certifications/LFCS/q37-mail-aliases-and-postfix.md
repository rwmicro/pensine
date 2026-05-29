# Question 37 — Mail Aliases and Postfix

## Énoncé

Solve this question on: `app-srv1`

1. Install Postfix as a **local-only** MTA listening on `127.0.0.1`.
2. Redirect mail addressed to `root` and `webmaster` to the local user `alice`.
3. Create a mailing-list alias `devs` that forwards to `alice`, `bob`, and an external `team@example.com`.
4. Send a test mail to `root` and verify it arrives in alice's mailbox; write the output of `mailq` into `/opt/course/37/queue`.

## Solution

### Install

Debian (choose **Local only** in the dialog):
```bash
sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix mailutils
```

RHEL:
```bash
sudo dnf install postfix mailx
sudo alternatives --set mta /usr/sbin/sendmail.postfix
sudo systemctl enable --now postfix
```

Main config: `/etc/postfix/main.cf`. Service map: `/etc/postfix/master.cf`.

### Step 1 — Local-only listening

In `/etc/postfix/main.cf`:
```
myhostname    = app-srv1.lfcs.lan
mydomain      = lfcs.lan
myorigin      = $mydomain
inet_interfaces = loopback-only
inet_protocols  = ipv4
mydestination = $myhostname, localhost.$mydomain, localhost
mynetworks    = 127.0.0.0/8
```

```bash
sudo postfix check
sudo systemctl restart postfix
ss -tlnp | grep :25
```

### Step 2+3 — Aliases

Edit `/etc/aliases`:
```
# basic redirections
postmaster: root
root:       alice
webmaster:  alice

# mailing list
devs:       alice, bob, team@example.com
```

Rebuild the hashed database (mandatory after every edit):
```bash
sudo newaliases
# or:
sudo postalias /etc/aliases
```

### Step 4 — Send a test mail and inspect

```bash
echo "test body" | mail -s "test subject" root
mailq > /opt/course/37/queue                  # mail queue
sudo postqueue -p                              # equivalent
sudo postqueue -f                              # flush queue (retry now)
sudo postsuper -d ALL                          # delete all queued msgs
```

Check delivery:
```bash
sudo su - alice
mail                                           # interactive client
# or just read the mbox:
cat /var/mail/alice
```

Postfix logs go to syslog / journald:
```bash
sudo journalctl -u postfix -n 50
sudo tail -f /var/log/mail.log                 # Debian
sudo tail -f /var/log/maillog                  # RHEL
```

### `.forward` per-user

Each user can override delivery with `~/.forward`:
```
# /home/alice/.forward
alice@example.com
\alice           # also keep a local copy
```

Permissions must be reasonable (`chmod 600 ~/.forward`).

### Virtual aliases (different domain hosting)

Useful when receiving mail for multiple domains. In `main.cf`:
```
virtual_alias_domains = otherdomain.test
virtual_alias_maps   = hash:/etc/postfix/virtual
```

`/etc/postfix/virtual`:
```
contact@otherdomain.test    alice
sales@otherdomain.test      alice, bob
@otherdomain.test           catchall
```

Build the hash and reload:
```bash
sudo postmap /etc/postfix/virtual
sudo systemctl reload postfix
```

### Useful diagnostics

```bash
postconf -n                                    # non-default settings
postconf -d mail_version                       # defaults
postmap -q root hash:/etc/aliases.db
postfix check
sudo postfix reload
```

### IMAP — Dovecot quickstart

If the question asks for IMAP/IMAPS:
```bash
sudo apt install dovecot-imapd
# /etc/dovecot/dovecot.conf
protocols = imap
listen = *
mail_location = mbox:~/mail:INBOX=/var/mail/%u
# enable SSL via /etc/dovecot/conf.d/10-ssl.conf
```

Test:
```bash
openssl s_client -connect localhost:993 -crlf
```

