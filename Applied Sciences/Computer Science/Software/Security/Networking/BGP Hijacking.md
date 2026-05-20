---
title: BGP Hijacking
domain: sciences-appliquées
subdomain: informatique / sécurité / réseau
tags: [bgp, hijacking, routage, as, réseau, sécurité]
date: 2026-03-22
---

# BGP Hijacking

## BGP — Border Gateway Protocol

BGP est le protocole de routage inter-domaine d'internet. Il permet aux Systèmes Autonomes (AS) — les grandes entités réseau (FAI, hébergeurs, entreprises) — d'échanger des informations sur les préfixes IP qu'ils peuvent atteindre.

### Concepts fondamentaux

```
AS (Autonomous System) : réseau sous une seule administration, identifié par un ASN
  - AS15169 = Google
  - AS16509 = Amazon AWS
  - AS32934 = Facebook/Meta
  - AS1234  = votre FAI

Préfixe : bloc d'adresses IP annoncé par un AS
  Exemple : AS15169 annonce "203.0.113.0/24 est chez moi"

BGP session (peering) :
  eBGP : entre AS différents (sessions externes)
  iBGP : au sein d'un même AS (sessions internes)

Attributs de chemin (path attributes) :
  AS_PATH : liste des AS traversés (évite les boucles, influence le choix de route)
  NEXT_HOP : prochain saut pour atteindre un préfixe
  LOCAL_PREF : préférence locale (interne à l'AS)
  MED : Multi-Exit Discriminator (hint pour l'AS voisin)
```

### Sélection de route BGP

```
Règles de préférence (ordre de priorité décroissant) :
1. Plus long préfixe (specificity) — /24 préféré à /16
2. WEIGHT (Cisco propriétaire, local)
3. LOCAL_PREF (plus élevé = préféré)
4. Chemin appris en local
5. AS_PATH le plus court
6. ORIGIN (IGP < EGP < Incomplete)
7. MED le plus bas
8. eBGP préféré à iBGP
9. Chemin le plus court vers le NEXT_HOP
10. Plus ancien (stabilité)
```

## BGP Hijacking

Un AS malveillant (ou compromis) annonce des préfixes IP qui ne lui appartiennent pas. Les autres AS acceptent ces annonces car BGP n'a pas de mécanisme d'authentification natif.

### Types d'attaques

#### 1. Prefix Hijacking (annonce de préfixe volé)

```
Situation normale :
AS100 (Amazon) annonce 54.239.0.0/16

Attaque :
AS666 (attaquant) annonce aussi 54.239.0.0/16
→ Les AS voisins de AS666 voient un chemin alternatif
→ Selon les politiques locales, certains peuvent préférer AS666
→ Une partie du trafic est redirigée vers AS666

Impact : interception du trafic, blackholing (suppression), redirection
```

#### 2. More-Specific Prefix Hijacking (plus efficace)

```
Situation normale :
AS100 annonce 54.239.0.0/16

Attaque :
AS666 annonce 54.239.25.0/24 (préfixe plus spécifique /24 > /16)
→ Les routes plus spécifiques sont TOUJOURS préférées par BGP
→ Tout le trafic vers ce /24 est redirigé vers AS666, même si l'AS_PATH est plus long
```

#### 3. AS Path Manipulation

```
AS666 annonce un préfixe avec un AS_PATH falsifié :
AS_PATH: 666 100 (au lieu de 666 seul)
→ Fait croire que le chemin passe par AS100
→ Contourne des filtres basés sur l'AS_PATH
```

### Cas réels notables

```
Pakistan Telecom (2008) :
  Pakistan Telecom annonce les préfixes YouTube (208.65.153.0/24)
  → YouTube inaccessible dans le monde entier pendant ~2 heures
  → Erreur de configuration propagée globalement

Renesys / Belarusian Telecom (2013) :
  Des préfixes d'opérateurs financiers (eTrade, etc.) redirigés vers la Biélorussie
  → Trafic intercepté avant d'être renvoyé vers la destination légitime (MITM)

Rostelecom (2020) :
  Préfixes d'Amazon, Akamai, Cloudflare, autres
  → ~8000 préfixes affectés pendant ~1 heure

China Telecom (multiples incidents) :
  Annonces de préfixes nord-américains et européens
  → Soupçons d'interception délibérée
```

## Détection

```bash
# Monitoring BGP public
# BGPmon, RIPE Routing Information Service, RouteViews

# Vérifier les annonces actuelles pour un préfixe
whois -h whois.cymru.com " -v 8.8.8.8"     # Team Cymru
curl "https://api.bgpview.io/prefix/8.8.8.0/24"  # BGPView API

# Outils de monitoring
# RIPE RIS (Routing Information Service) : https://ris.ripe.net
# BGPlay : visualisation des changements de route
# Cloudflare Radar : https://radar.cloudflare.com/bgp

# Détection d'anomalie via AS_PATH
# Un préfixe soudainement accessible via un nouveau AS_PATH = suspect
# Un préfixe /24 annoncé alors que seul un /16 existait = plus-specific hijack
```

## Contre-mesures

### RPKI (Resource Public Key Infrastructure)

Mécanisme de validation cryptographique des annonces BGP.

```
Fonctionnement :
1. Le détenteur d'un bloc IP crée un ROA (Route Origin Authorization)
   ROA = "Le préfixe 203.0.113.0/24 peut être annoncé par AS15169"
2. Le ROA est signé avec la clé de l'autorité régionale (RIR : RIPE, ARIN, APNIC...)
3. Les routeurs BGP vérifient les ROA avant d'accepter une annonce

États RPKI :
  Valid   : préfixe et AS correspondent à un ROA valide → accepter
  Invalid : préfixe/AS ne correspondent pas → rejeter
  NotFound : aucun ROA → politique locale (souvent accepté par défaut)
```

```bash
# Vérifier le statut RPKI d'un préfixe
curl "https://rpki-validator.ripe.net/api/v1/validity/AS15169/8.8.8.0/24"

# Créer un ROA (via l'interface de son RIR)
# RIPE NCC → MyAPNIC → RIPE Portal → "RPKI" → "Create ROA"

# Configuration Cisco IOS-XR pour validation RPKI
router bgp 65000
  bgp rpki server tcp rpki-validator.example.com port 3323
  !
  neighbor 10.0.0.1
    address-family ipv4 unicast
      validation enable
      send-community
```

### BGPsec

Extension de BGP qui signe cryptographiquement le chemin AS_PATH entier. Encore peu déployé en pratique.

### Filtrage de préfixes

```
Bonnes pratiques de configuration BGP :

1. Prefix filtering — listes de préfixes autorisés par voisin
   Accepter uniquement les préfixes annoncés par le registre du voisin (IRR)

2. IRR filtering — Internet Routing Registry
   Les AS enregistrent leurs préfixes dans des bases IRR (RIPE, ARIN, RADB...)
   Les voisins vérifient que les annonces correspondent aux enregistrements

3. Max-prefix limit
   Couper la session si un voisin annonce plus de X préfixes (anormal = erreur ou attaque)

4. GTSM (Generalized TTL Security Mechanism)
   Rejeter les paquets BGP avec TTL < 255 (difficile à forger pour un attaquant distant)
```

```
# Cisco IOS — exemple de filtrage
router bgp 65000
  neighbor 10.0.0.1 prefix-list ALLOWED-IN in
  neighbor 10.0.0.1 maximum-prefix 1000 90  # Alerte à 90%, coupe à 100%

ip prefix-list ALLOWED-IN permit 203.0.113.0/24
ip prefix-list ALLOWED-IN permit 198.51.100.0/24
ip prefix-list ALLOWED-IN deny 0.0.0.0/0 le 32  # Bloquer tout le reste
```

## Impact et enjeux

```
BGP hijacking peut être utilisé pour :
- Interception de trafic (MITM) : capturer emails, identifiants (si non chiffrés)
- Contournement de sanctions (rediriger le trafic via un pays non sanctionné)
- Attaques DDoS par blackholing (annonce d'une victime vers un AS /dev/null)
- Espionnage étatique (interception de communications)
- Cryptomining : rediriger des pools de minage

L'adoption de RPKI progresse :
- Cloudflare, Amazon, Facebook : ROA créés et validation RPKI activée
- ~ 30-40% des préfixes internet couverts par des ROA valides (2024)
- Mais seulement ~20% des AS filtrent les annonces RPKI Invalid
```
