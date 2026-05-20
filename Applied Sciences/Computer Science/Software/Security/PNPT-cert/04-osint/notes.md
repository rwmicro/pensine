---
title: "OSINT (PNPT)"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > PNPT"
tags: [sciences-appliquées, informatique, sécurité, osint, reconnaissance, pnpt]
date: "2026-05-18"
---

# OSINT (Open Source Intelligence)

L'OSINT, c'est tout ce qu'on apprend sur une cible sans jamais lui envoyer un seul paquet. Avant qu'un pentest soit "actif", il y a souvent des jours d'enquête passive — c'est ce qui distingue un bon attaquant d'un script kiddie. L'objectif n'est pas de tout savoir, mais de trouver le point faible : l'employé qui poste son badge sur LinkedIn, le sous-domaine oublié, le fichier `.git` exposé.

## Le funnel OSINT

L'OSINT n'est pas une checklist plate — c'est un entonnoir qui transforme une cible large en surface d'attaque concrète.

```
                  [Entreprise cible]
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   Domaines         Personnes        Infrastructure
   (DNS, certs)    (LinkedIn,        (IPs, services,
                    emails, leaks)    technos)
        │                │                │
        ▼                ▼                ▼
  Sous-domaines    Format d'email   Services exposés
  oubliés          + employés       (Shodan, scans)
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  Surface d'attaque
                  (cibles concrètes)
```

À chaque étape, on cherche à corréler : un email trouvé via Hunter doit être recoupé avec HaveIBeenPwned, qui peut donner un mot de passe d'une vieille fuite, qui peut être réutilisé sur le portail VPN identifié par sous-domaine.

## Domaines et DNS

Premier travail : cartographier la présence DNS de la cible. Beaucoup d'organisations oublient des sous-domaines en dev/staging/admin sans protection.

```bash
# Whois — propriétaire, dates, contacts (souvent anonymisés aujourd'hui)
whois cible.com

# Énumération de sous-domaines
sublist3r -d cible.com
amass enum -d cible.com           # plus exhaustif, plus lent
assetfinder cible.com

# crt.sh — sous-domaines via certificats SSL publics
curl -s "https://crt.sh/?q=%25.cible.com&output=json" | jq -r '.[].name_value' | sort -u

# DNS direct
dig cible.com any
dig axfr @ns.cible.com cible.com  # zone transfer (rarement permis, jackpot si oui)
```

**Pourquoi crt.sh est magique** : depuis 2018, tous les certificats SSL doivent être publiés dans Certificate Transparency logs. Donc tout sous-domaine qui a un jour eu un certificat (même expiré) est trouvable. `dev-staging.cible.com`, `vpn-old.cible.com`, etc.

## Personnes et emails

```bash
# theHarvester — collecte multi-sources
theHarvester -d cible.com -b google,linkedin,bing,duckduckgo

# Hunter.io (web) — format d'email + employés
# DNSDumpster (web) — cartographie visuelle
```

```
Pourquoi le format d'email importe :

Si Hunter révèle "prenom.nom@cible.com", alors une fois LinkedIn scrapé pour
récupérer 200 noms d'employés, on a 200 emails valides → cibles de phishing
ou d'AS-REP Roasting si on accède au DC.
```

**HaveIBeenPwned + DeHashed** : croiser ces emails avec les bases de fuites. Un mot de passe d'il y a 5 ans peut encore servir (réutilisation = constante humaine).

## Google Dorking

Les opérateurs de recherche Google sont une arme. Le but : retrouver ce que l'indexation a capturé par erreur.

```
site:cible.com                           Pages indexées du domaine
site:cible.com -www                      Sous-domaines (exclut www)
filetype:pdf site:cible.com              PDFs publics (souvent metadata juteuses)
intitle:"index of" site:cible.com        Directory listings ouverts
inurl:admin site:cible.com               Panneaux d'admin
intext:"password" site:cible.com         Mots de passe en clair
ext:log site:cible.com                   Logs exposés
```

**Astuce** : combiner avec la Wayback Machine. Un fichier sensible supprimé du site est souvent encore dans `web.archive.org`.

## Réseaux sociaux et identité

```bash
# Sherlock — chercher un username sur des centaines de plateformes
sherlock <username>

# LinkedIn (manuel) — employés, technos utilisées, mouvements RH
# CrossLinked — extraction structurée de noms LinkedIn
crosslinked -f '{first}.{last}@cible.com' -l 'Cible Corp' -o employees.txt
```

**LinkedIn** = mine d'or pour AD :
- Noms d'employés → username probable (`prenom.nom`)
- Technologies citées dans les offres d'emploi → stack interne
- Photos avec badges visibles → format des badges, accès physique

## Métadonnées de fichiers

Tout fichier produit a un historique. Les PDFs et documents Office contiennent souvent :

```bash
exiftool fichier.pdf
# Auteur, logiciel utilisé, dates, parfois chemin local "C:\Users\jdoe\..."

# Images
exiftool photo.jpg
# Modèle d'appareil, GPS (rarement aujourd'hui mais ça arrive)
```

Un `Author: J. Doe` + `Software: Microsoft Word 2016` + un chemin `C:\Users\jdoe\Documents\` te donne nom + version logicielle + nom de session Windows. Recoupé avec LinkedIn = identité confirmée + format username.

## Infrastructure : Shodan et Censys

Avant tout scan actif, Shodan et Censys ont déjà scanné Internet pour toi.

```
shodan search hostname:cible.com
shodan search ssl.cert.subject.cn:cible.com    # via certificats
shodan search org:"Cible Corp"                  # via organisation enregistrée

Censys → équivalent, souvent plus à jour
```

Voir `[[Shodan]]` pour les requêtes avancées.

## Pièges courants

- **OSINT passif ≠ totalement invisible** : certaines requêtes (Shodan en lookup direct, crt.sh, certains scans archive.org) laissent des traces. Le vrai "passif" se limite à ce qui ne touche jamais l'infrastructure cible.
- **Données obsolètes** : un sous-domaine trouvé dans crt.sh peut ne plus pointer nulle part. Toujours vérifier avec `dig` avant d'investir.
- **LinkedIn applique du rate-limiting et bannit les profils suspects** — utiliser un compte dédié, jamais le pro réel du pentester.
- **Les fuites HIBP sont des hashes ou des plaintexts ?** Vérifier la nature de la fuite. Un hash bcrypt non cracké n'est pas immédiatement exploitable.
- **L'OSINT n'est pas un pré-requis seulement initial** : pendant l'engagement, revenir à l'OSINT (par exemple LinkedIn pour comprendre la hiérarchie sociale après accès aux emails) reste utile.
