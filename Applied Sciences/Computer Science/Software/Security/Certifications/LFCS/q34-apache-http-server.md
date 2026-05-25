# Question 34 — Apache HTTP Server

## Énoncé

Solve this question on: `web-srv1`

1. Install Apache and serve a virtual host `site1.lfcs.lan` from `/var/www/site1` on port 80.
2. Protect the URL `/admin` with HTTP Basic auth, user `admin` password `secret`.
3. Enable HTTPS on the same vhost using a self-signed certificate.
4. Restrict access to `/private` to clients in `192.168.50.0/24`.

## Solution

### Install

Debian:
```bash
sudo apt install apache2
sudo systemctl enable --now apache2
```

RHEL:
```bash
sudo dnf install httpd mod_ssl
sudo systemctl enable --now httpd
```

Key paths:

| Distro | Config root | Sites/modules layout |
|---|---|---|
| Debian | `/etc/apache2/` | `sites-available/` + `sites-enabled/`, `mods-available/` + `mods-enabled/` (use `a2ensite`, `a2enmod`) |
| RHEL | `/etc/httpd/` | `conf.d/`, modules under `conf.modules.d/` |

### Step 1 — Virtual host

Create `/etc/apache2/sites-available/site1.conf`:
```
<VirtualHost *:80>
    ServerName site1.lfcs.lan
    DocumentRoot /var/www/site1

    <Directory /var/www/site1>
        Require all granted
        AllowOverride None
    </Directory>

    ErrorLog  ${APACHE_LOG_DIR}/site1-error.log
    CustomLog ${APACHE_LOG_DIR}/site1-access.log combined
</VirtualHost>
```

Enable + reload:
```bash
sudo mkdir -p /var/www/site1
echo "hello" | sudo tee /var/www/site1/index.html
sudo a2ensite site1.conf
sudo a2dissite 000-default.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

On RHEL, just drop the file in `/etc/httpd/conf.d/` — no enable step.

### Step 2 — Basic auth on `/admin`

Generate the password file:
```bash
sudo apt install apache2-utils         # provides htpasswd
sudo htpasswd -c /etc/apache2/.htpasswd admin
```

Add inside the vhost:
```
Alias /admin /var/www/site1/admin
<Location /admin>
    AuthType Basic
    AuthName "Restricted"
    AuthUserFile /etc/apache2/.htpasswd
    Require valid-user
</Location>
```

### Step 3 — HTTPS

Generate a self-signed cert:
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout /etc/ssl/private/site1.key \
     -out    /etc/ssl/certs/site1.crt \
     -subj "/CN=site1.lfcs.lan"
sudo chmod 600 /etc/ssl/private/site1.key
```

Enable SSL module (Debian only):
```bash
sudo a2enmod ssl
```

Add a second vhost:
```
<VirtualHost *:443>
    ServerName site1.lfcs.lan
    DocumentRoot /var/www/site1

    SSLEngine on
    SSLCertificateFile    /etc/ssl/certs/site1.crt
    SSLCertificateKeyFile /etc/ssl/private/site1.key
</VirtualHost>
```

Reload + test:
```bash
sudo systemctl reload apache2
curl -k https://site1.lfcs.lan/
```

### Step 4 — IP-based restriction

```
<Location /private>
    Require ip 192.168.50.0/24
</Location>
```

Combine with auth (need **both**):
```
<Location /private>
    AuthType Basic
    AuthName "VIP"
    AuthUserFile /etc/apache2/.htpasswd
    <RequireAll>
        Require valid-user
        Require ip 192.168.50.0/24
    </RequireAll>
</Location>
```

### Nginx equivalent (alternative)

```nginx
server {
    listen 80;
    server_name site1.lfcs.lan;
    root /var/www/site1;

    location /admin {
        auth_basic "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }

    location /private {
        allow 192.168.50.0/24;
        deny  all;
    }
}
```

### Useful diagnostics

```bash
sudo apache2ctl -S                      # list vhosts + binding
sudo apache2ctl -M                      # loaded modules
sudo apache2ctl configtest
ss -tlnp | grep -E ':80|:443'
curl -I http://site1.lfcs.lan/
journalctl -u apache2 -n 50
tail -f /var/log/apache2/site1-error.log
```

If SELinux is enforcing on RHEL and you serve files outside `/var/www/html`:
```bash
sudo semanage fcontext -a -t httpd_sys_content_t '/var/www/site1(/.*)?'
sudo restorecon -Rv /var/www/site1
sudo setsebool -P httpd_can_network_connect on
```

---

[← Question 33](q33-dns-server.md) · [Index](Certifications/LFCS/notes.md) · [Question 35 →](q35-database-server.md)
