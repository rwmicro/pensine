# Question 36 — HTTP Proxy

## Énoncé

Solve this question on: `web-srv1`

1. Install Squid as a forward HTTP proxy listening on port `3128`.
2. Allow only the subnet `192.168.50.0/24` to use the proxy.
3. Block any access to domain `*.example.com`.
4. Require basic authentication for users not coming from `192.168.50.10`.

## Solution

### Install

```bash
sudo apt install squid              # Debian
sudo dnf install squid              # RHEL
sudo systemctl enable --now squid
```

Main config: `/etc/squid/squid.conf`. Cache directory: `/var/spool/squid`. Logs: `/var/log/squid/access.log`.

### Step 1+2 — Listening port and ACL

`squid.conf` (key directives):
```
http_port 3128

acl lan src 192.168.50.0/24
acl trusted src 192.168.50.10

http_access allow lan
http_access deny all
```

### Step 3 — Block a domain

Create `/etc/squid/blocked-domains.txt`:
```
.example.com
```
Add to `squid.conf` **above** the allow rule:
```
acl bad_domains dstdomain "/etc/squid/blocked-domains.txt"
http_access deny bad_domains
```

Order matters: Squid evaluates `http_access` top-to-bottom and stops at the first match.

### Step 4 — Conditional basic auth

Generate passwords:
```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/squid/passwd alice
```

In `squid.conf`:
```
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
auth_param basic realm Proxy
auth_param basic credentialsttl 2 hours

acl authenticated proxy_auth REQUIRED

http_access allow trusted
http_access allow lan authenticated
http_access deny all
```

Apply:
```bash
sudo squid -k parse                 # check syntax
sudo systemctl reload squid
```

### Test the proxy

```bash
curl -x http://192.168.50.20:3128 -I https://www.kernel.org
curl -x http://alice:pw@192.168.50.20:3128 -I https://www.kernel.org
tail -f /var/log/squid/access.log
```

### Useful ACL types

| Type | Example |
|---|---|
| `src` | client IP/CIDR |
| `dst` | destination IP |
| `dstdomain` | destination FQDN (or file) |
| `dstdom_regex` | regex on hostname |
| `url_regex` | regex on full URL |
| `port` / `myport` | destination / local port |
| `time` | day + hour ranges (`MTWHF 09:00-18:00`) |
| `proto` | `HTTP`, `FTP`, `HTTPS` |
| `proxy_auth` | requires authentication |
| `method` | `GET`, `POST`, `CONNECT` |

### Reverse proxy alternative

Squid can also act as a reverse proxy, but for that role most environments prefer **Nginx** or **HAProxy** — see [[q16-loadbalancer]] for HAProxy and [[q34-apache-http-server]] for Apache `mod_proxy`.

Quick Nginx reverse proxy:
```nginx
server {
    listen 80;
    server_name app.lfcs.lan;

    location / {
        proxy_pass http://10.0.0.50:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

[← Question 35](q35-database-server.md) · [Index](Certifications/LFCS/notes.md) · [Question 37 →](q37-mail-aliases-and-postfix.md)
