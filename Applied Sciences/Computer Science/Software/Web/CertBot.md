---
title: "Certbot — certificats TLS Let's Encrypt"
domain: "Applied Sciences"
subdomain: "Computer Science > Web"
tags: [sciences-appliquées, informatique, web, tls]
date: "2024-11-01"
---

# Certbot — certificats TLS Let's Encrypt

**Certbot** est le client officiel de l'Electronic Frontier Foundation (EFF) pour obtenir et renouveler automatiquement des certificats TLS via **Let's Encrypt**, une autorité de certification gratuite et automatisée. Les certificats Let's Encrypt ont une durée de vie courte (**90 jours**), ce qui impose un renouvellement automatisé.

## Installation

```bash
# Debian / Ubuntu
sudo apt install certbot python3-certbot-nginx

# RHEL / Fedora
sudo dnf install certbot python3-certbot-nginx

# Avec snap (recommandé upstream)
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Modules d'intégration selon le serveur : `python3-certbot-apache`, `python3-certbot-nginx`.

## Trois modes de challenge

Let's Encrypt vérifie que tu contrôles bien le domaine via un *challenge* ACME :

| Challenge | Principe | Usage typique |
|---|---|---|
| **HTTP-01** | Certbot pose un fichier sous `/.well-known/acme-challenge/` que Let's Encrypt récupère sur le port 80 | Sites web classiques avec IP publique |
| **DNS-01** | Certbot demande d'ajouter un enregistrement `TXT _acme-challenge.example.com` | Wildcards, domaines internes, pas de port 80 accessible |
| **TLS-ALPN-01** | Négociation TLS sur le port 443 | Cas où seul le 443 est ouvert |

## Certificat simple (HTTP-01)

```bash
# Mode autonome (certbot ouvre son propre serveur, port 80 libre requis)
sudo certbot certonly --standalone -d example.com -d www.example.com

# Mode plugin Nginx (reconfigure automatiquement nginx)
sudo certbot --nginx -d example.com -d www.example.com

# Mode webroot (si un serveur web tourne déjà)
sudo certbot certonly --webroot -w /var/www/html -d example.com
```

Les certificats et clés sont stockés dans `/etc/letsencrypt/live/<domaine>/` :
- `fullchain.pem` — certificat + chaîne intermédiaire (à utiliser côté serveur)
- `privkey.pem` — clé privée
- `cert.pem` — certificat seul
- `chain.pem` — chaîne intermédiaire seule

## Certificat wildcard (DNS-01 obligatoire)

Un wildcard couvre tous les sous-domaines (`*.example.com`). Let's Encrypt impose le challenge DNS-01 pour ces certificats.

```bash
# Mode manuel : certbot demande d'ajouter un TXT à la main
sudo certbot certonly --manual --preferred-challenges dns \
  -d example.com -d '*.example.com'

# Mode automatisé via plugin DNS (exemple Cloudflare)
sudo certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/cloudflare.ini \
  -d example.com -d '*.example.com'
```

Plugins DNS officiels : `dns-cloudflare`, `dns-route53`, `dns-digitalocean`, `dns-ovh`, `dns-google`, `dns-gandi` (via extension), etc.

Exemple `~/.secrets/cloudflare.ini` (chmod 600) :
```ini
dns_cloudflare_api_token = <TOKEN_SCOPED_ZONE_DNS_EDIT>
```

## Renouvellement automatique

Certbot installe un timer systemd ou une tâche cron qui tente un renouvellement 2 fois par jour. Un certificat n'est renouvelé qu'à partir de 30 jours avant expiration.

```bash
# Test à blanc (ne renouvelle pas réellement)
sudo certbot renew --dry-run

# Forcer le renouvellement
sudo certbot renew --force-renewal

# Vérifier l'état du timer
systemctl list-timers | grep certbot
```

Pour recharger le service après renouvellement :
```bash
sudo certbot renew --deploy-hook "systemctl reload nginx"
```

## Commandes utiles

```bash
# Lister tous les certificats gérés
sudo certbot certificates

# Révoquer un certificat (clé compromise)
sudo certbot revoke --cert-path /etc/letsencrypt/live/example.com/cert.pem

# Supprimer un certificat de la configuration certbot
sudo certbot delete --cert-name example.com
```

## Limites Let's Encrypt

À connaître avant un déploiement massif :

- **50 certificats par domaine enregistré et par semaine**
- **5 certificats identiques (mêmes noms) par semaine** — attention si un script boucle
- **300 *new orders* par compte toutes les 3 heures**
- En cas d'échec répété, utiliser l'environnement de staging : `--staging` (certificats non valides mais sans quota)

## Pièges fréquents

- **Port 80 bloqué en entrée** → HTTP-01 impossible, passer en DNS-01
- **Fichier `.well-known` servi par un framework** (ex. Next.js, SPA) → configurer une exception ou utiliser webroot
- **CAA record manquant/incorrect** sur le DNS → Let's Encrypt refuse d'émettre si la règle CAA exclut `letsencrypt.org`
- **Horloge système décalée** → ACME refuse le nonce, synchroniser avec `ntpd` ou `chrony`
