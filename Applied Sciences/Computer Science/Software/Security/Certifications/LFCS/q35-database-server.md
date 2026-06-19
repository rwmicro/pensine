# Question 35 — Database Server

## Notes d'apprentissage

Installer et sécuriser un SGBD (MariaDB/MySQL) est un classique de l'administration. L'exercice couvre le cycle complet : installer, durcir, créer une base/utilisateur avec droits minimaux, exposer sur le réseau, sauvegarder.

**Modèle mental : deux niveaux d'authentification.**

```
réseau ──► (1) le serveur écoute-t-il sur cette interface ?  (bind-address)
       ──► (2) cet utilisateur@hôte a-t-il le droit ?         (GRANT)
```

Se connecter à distance suppose **les deux** : le serveur doit écouter sur la bonne interface (`bind-address`, par défaut `127.0.0.1` = local seulement) **et** l'utilisateur doit être autorisé depuis son hôte. Oublier l'un des deux = connexion refusée — piège récurrent.

**`mysql_secure_installation`** : script de durcissement post-installation (mot de passe root, suppression des comptes anonymes et de la base `test`, désactivation du login root distant). Réflexe systématique sur un nouveau serveur.

**Utilisateur = `nom@hôte`.** En MariaDB, l'identité inclut la provenance : `app@'localhost'` et `app@'%'` sont **deux comptes distincts**. Le `%` est un joker (n'importe quel hôte).
```sql
CREATE USER 'app'@'%' IDENTIFIED BY 'appsecret';
GRANT SELECT, INSERT, UPDATE ON appdb.* TO 'app'@'%';   -- principe du moindre privilège
FLUSH PRIVILEGES;
```
Le **principe du moindre privilège** : ne donner que `SELECT/INSERT/UPDATE`, jamais `ALL` ni `GRANT OPTION`, à un compte applicatif.

**Sauvegarde logique avec `mysqldump`** : exporte la base en instructions SQL rejouables.
```bash
mysqldump appdb > /opt/course/35/appdb.sql      # sauvegarde
mysql appdb < /opt/course/35/appdb.sql          # restauration
```

**Pièges** :
- `bind-address = 127.0.0.1` (défaut) empêche **tout** accès distant, même avec un `GRANT` correct — il faut le passer à l'IP du LAN (ou `0.0.0.0`) puis redémarrer.
- `app@'localhost'` ≠ `app@'%'` : créer le bon hôte selon d'où l'app se connecte.
- Penser au pare-feu : le port 3306 doit être ouvert (voir [[q07-network-packet-filtering]]).
- `FLUSH PRIVILEGES` après manipulation directe des tables de droits.

## Énoncé

Solve this question on: `data-001`

1. Install MariaDB and start it.
2. Run the secure installation procedure (set a root password, drop anonymous users).
3. Create a database `appdb` and a user `app@'%'` with password `appsecret`, granting only SELECT/INSERT/UPDATE on `appdb`.
4. Configure MariaDB to listen on the LAN interface (`192.168.50.10`) so the app server can connect.
5. Write a backup of `appdb` into `/opt/course/35/appdb.sql`.

## Solution

### Install

Debian:
```bash
sudo apt install mariadb-server mariadb-client
sudo systemctl enable --now mariadb
```

RHEL:
```bash
sudo dnf install mariadb-server mariadb
sudo systemctl enable --now mariadb
```

### Step 2 — Secure installation

```bash
sudo mysql_secure_installation
```

Answers the prompts about:
- root password (set one)
- remove anonymous users
- disallow root login remotely
- remove test database
- reload privilege tables

### Step 3 — Database, user, grants

```bash
sudo mysql -u root -p
```
```sql
CREATE DATABASE appdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'app'@'%' IDENTIFIED BY 'appsecret';
GRANT SELECT, INSERT, UPDATE ON appdb.* TO 'app'@'%';
FLUSH PRIVILEGES;
SHOW GRANTS FOR 'app'@'%';
\q
```

Host syntax:
- `'app'@'localhost'` — Unix socket only
- `'app'@'192.168.50.%'` — subnet
- `'app'@'%'` — any host
- `'app'@'app-srv1.lfcs.lan'`

Revoke / drop:
```sql
REVOKE INSERT ON appdb.* FROM 'app'@'%';
DROP USER 'app'@'%';
DROP DATABASE appdb;
```

### Step 4 — Network binding

Edit:
- Debian: `/etc/mysql/mariadb.conf.d/50-server.cnf`
- RHEL: `/etc/my.cnf.d/server.cnf`

```ini
[mysqld]
bind-address = 192.168.50.10
port         = 3306
```

Restart and verify:
```bash
sudo systemctl restart mariadb
ss -tlnp | grep 3306
```

Open the firewall if needed (see [[q07-network-packet-filtering]]):
```bash
sudo firewall-cmd --permanent --add-service=mysql
sudo firewall-cmd --reload
```

Test from the client side:
```bash
mysql -h 192.168.50.10 -u app -p appdb -e "SELECT NOW();"
```

### Step 5 — Backup and restore

Logical dump:
```bash
sudo mysqldump --single-transaction --routines --triggers appdb \
  > /opt/course/35/appdb.sql

# all databases
sudo mysqldump --all-databases --single-transaction > full.sql

# restore
sudo mysql appdb < /opt/course/35/appdb.sql
```

For large or hot databases, prefer `mariabackup` (physical backup):
```bash
sudo mariabackup --backup --target-dir=/var/backups/mariadb/$(date +%F) --user=root --password=...
```

### PostgreSQL quick equivalents

```bash
sudo apt install postgresql
sudo systemctl enable --now postgresql
sudo -u postgres psql

# inside psql:
CREATE DATABASE appdb;
CREATE USER app WITH PASSWORD 'appsecret';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app;
```

Network binding:
- `/etc/postgresql/<ver>/main/postgresql.conf` → `listen_addresses = '*'`
- `/etc/postgresql/<ver>/main/pg_hba.conf` → add `host appdb app 192.168.50.0/24 md5`

Dump:
```bash
sudo -u postgres pg_dump appdb > appdb.sql
sudo -u postgres pg_dumpall > full.sql
```

### Useful day-to-day commands

```bash
mysql -e "SHOW DATABASES;"
mysql -e "SHOW PROCESSLIST;"
mysql -e "SHOW VARIABLES LIKE 'bind%';"
mysql -e "SHOW STATUS LIKE 'Threads%';"
sudo mysqladmin status
sudo mysqladmin shutdown
```

