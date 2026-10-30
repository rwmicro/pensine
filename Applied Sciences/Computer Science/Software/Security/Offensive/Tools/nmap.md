---
title: "nmap"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Offensive > Tools"
tags: [sciences-appliquées, informatique, sécurité, réseau, nmap, scan]
date: "2025-02-15"
prerequis: ["[[Recon Automation]]"]
---

# nmap

Nmap (Network Mapper) est un scanner de ports en ligne de commande. Il permet de découvrir des hôtes, d'identifier les ports ouverts, de détecter les services et leurs versions, et d'exécuter des scripts de reconnaissance ou de vulnérabilité.

> Une TTL de 128 indique généralement un système Windows ; une TTL de 64, un système Linux ou Unix.

## Pourquoi nmap scanne certains ports par défaut

Nmap construit une carte des ports les plus fréquemment utilisés. Une commande `nmap IP` sans option scanne les 1 000 ports les plus courants. Cette liste se trouve dans `/usr/share/nmap/nmap-services`.

> [!warning] Piège
> Un scan par défaut (top 1000) rate systématiquement les services déplacés sur un port non standard — une pratique courante en pentest réel pour échapper aux scans rapides. Pour un audit exhaustif, `-p-` (tous les ports) est nécessaire, quitte à accepter le temps de scan supplémentaire.

## Options de scan

| Option | Description |
|---|---|
| `-sn` | Désactive le scan de ports ; effectue uniquement la découverte d'hôtes. |
| `-Pn` | Désactive la découverte d'hôtes et considère toutes les cibles comme actives. |
| `-n` | Désactive la résolution DNS. |
| `-PE` | Découverte d'hôtes par requêtes ICMP Echo. |
| `--packet-trace` | Affiche tous les paquets envoyés et reçus. |
| `--reason` | Affiche la raison d'un résultat (type de réponse reçue). |
| `--disable-arp-ping` | Désactive les requêtes ARP de découverte. |
| `--top-ports=<num>` | Scanne les `<num>` ports les plus fréquents. |
| `-p-` | Scanne les 65 535 ports TCP. |
| `-p22-110` | Scanne la plage de ports 22 à 110. |
| `-p22,25` | Scanne uniquement les ports 22 et 25. |
| `-F` | Scanne les 100 ports les plus fréquents. |
| `-sS` | Scan TCP SYN (half-open), rapide et discret. |
| `-sA` | Scan TCP ACK, utile pour cartographier les règles de filtrage. |
| `-sU` | Scan UDP. |
| `-sV` | Détecte la version des services découverts. |
| `-sC` | Exécute les scripts NSE de catégorie `default`. |
| `--script <script>` | Exécute un ou plusieurs scripts NSE nommés. |
| `-O` | Détection du système d'exploitation. |
| `-A` | Active la détection OS, la détection de version, le traceroute et les scripts `default`. |
| `-D RND:5` | Utilise cinq leurres (decoys) aléatoires pour brouiller la source du scan. |
| `-e` | Spécifie l'interface réseau utilisée pour le scan. |
| `-S 10.10.10.200` | Spécifie l'adresse IP source du scan. |
| `-g` | Spécifie le port source du scan. |
| `--dns-server <ns>` | Utilise un serveur DNS spécifique pour la résolution. |

## Options de sortie

| Option | Description |
|---|---|
| `-oA filename` | Enregistre les résultats dans tous les formats disponibles, avec `filename` comme base. |
| `-oN filename` | Enregistre les résultats au format normal. |
| `-oG filename` | Enregistre les résultats au format « grepable ». |
| `-oX filename` | Enregistre les résultats au format XML. |

## Options de performance

| Option | Description |
|---|---|
| `--max-retries <num>` | Nombre maximal de retransmissions pour un port. |
| `--stats-every=5s` | Affiche l'état d'avancement toutes les 5 secondes. |
| `-v` / `-vv` | Augmente la verbosité de la sortie. |
| `--initial-rtt-timeout 50ms` | Timeout RTT initial. |
| `--max-rtt-timeout 100ms` | Timeout RTT maximal. |
| `--min-rate 300` | Envoie au moins 300 paquets par seconde. |
| `-T <0-5>` | Choisit un modèle de temporisation, de `paranoid` (0) à `insane` (5). |

## Scripts NSE disponibles

Nmap propose de nombreux scripts pour des usages spécifiques.

> [!warning] Piège
> Les catégories `Intrusive`, `Exploit` et `Dos` peuvent activement perturber ou faire planter un service (voire un système industriel fragile). En engagement client, ne les lancer que si les règles d'engagement l'autorisent explicitement — `-sC` / `--script=default` reste `safe` par construction.

| Catégorie | Description | Exemples de scripts |
|---|---|---|
| **Auth** | Contournement ou test d'authentification. | `http-auth`, `ssh-auth-methods`, `smb-brute` |
| **Broadcast** | Découverte d'hôtes par broadcast et multicast. | `broadcast-dhcp-discover`, `broadcast-ping` |
| **Brute** | Attaques par force brute de mots de passe. | `ftp-brute`, `http-brute`, `smtp-brute` |
| **Default** | Scripts exécutés avec `-sC` ou `--script=default`. | `ssl-cert`, `dns-service-discovery`, `http-title` |
| **Discovery** | Découverte d'hôtes, de services et d'informations. | `dns-zone-transfer`, `snmp-brute`, `ssh-hostkey` |
| **Dos** | Tests ou attaques par déni de service. | `syn-flood`, `http-slowloris` |
| **Exploit** | Exploitation de vulnérabilités connues. | `http-shellshock`, `ms08-067`, `cve-2020-0796` |
| **External** | Utilisation de services web externes pour l'information. | `ip-geolocation`, `whois` |
| **Fuzzer** | Fuzzing de services pour trouver des vulnérabilités. | `ftp-fuzz`, `http-fuzz` |
| **Intrusive** | Vérifications intrusives ou potentiellement dangereuses. | `http-sql-injection`, `smb-vuln-ms17-010` |
| **Malware** | Détection de malware ou de portes dérobées. | `http-malware-host`, `irc-botnet-channels` |
| **Safe** | Scripts non intrusifs, utilisables en production. | `banner`, `http-headers` |
| **Version** | Améliore la détection de version des services. | `ssl-enum-ciphers`, `http-server-header` |
| **Vuln** | Détection de vulnérabilités connues. | `http-vuln-cve2017-5638`, `smb-vuln-ms08-067` |

Pour explorer les scripts disponibles sur le système :

```bash
ls /usr/share/nmap/scripts
```

Pour les compter :

```bash
ls /usr/share/nmap/scripts | wc -l
```

Ou pour obtenir l'aide directement depuis nmap :

```bash
nmap --script-help all
```

> [!quiz] À quoi sert l'option `-Pn` et dans quel cas est-elle indispensable ?
> Elle désactive la découverte d'hôtes et considère la cible comme active. Elle est indispensable quand un pare-feu ou un équipement filtre les requêtes ICMP/ARP et que nmap conclurait à tort que l'hôte est hors ligne.

> [!abstract] Définition — Scan SYN
> Un scan SYN (`-sS`) envoie un paquet SYN sans terminer la poignée de main TCP. Si la cible répond SYN-ACK, le port est ouvert ; si elle répond RST, il est fermé. Le scan est plus rapide et moins visible qu'un scan connecté complet.
