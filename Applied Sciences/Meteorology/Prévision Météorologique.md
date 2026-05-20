---
title: "Prévision Météorologique"
domain: "Applied Sciences"
subdomain: "Meteorology"
tags: [sciences-appliquées, météorologie]
date: "2026-02-22"
---

# Prévision Météorologique


### Observation

**Stations Météo Au Sol**
- **Mesures** : Température, pression, humidité, vent, précipitations
- **Réseau** : Dizaines milliers mondialement
- **Automatiques** : Transmission temps réel

**Radiosondage**
- **Ballons-Sondes** : Lancés 2×/jour mondialement
- **Instruments** : Radiosonde (T, P, humidité, GPS)
- **Altitude** : Jusqu'à 30-40 km
- **Données** : Profils verticaux atmosphère

**Radar Météorologique**
- **Principe** : Ondes radio réfléchies par précipitations
- **Doppler** : Vitesse particules (vents)
- **Applications** : 
  - Détection précipitations (intensité, type)
  - Suivi orages, tornades
  - Estimation pluies

**Satellites Météorologiques**
- **Géostationnaires** : 
  - Altitude 36 000 km, fixe au-dessus équateur
  - Vue continue zone (1/3 Terre)
  - Exemples : GOES (USA), Meteosat (Europe)
- **Polaires** :
  - Orbite basse (~800 km), passage pôles
  - Couverture globale 2×/jour
  - Résolution supérieure
- **Instruments** : Imageurs (visible, IR), sondeurs atmosphère

**Bouées et Navires**
- Océans : Zones peu couvertes autrement
- Bouées dérivantes, ancrées
- Navires marchands (observations volontaires)

### Modélisation Numérique

**Principe**
1. **Équations** : Physique atmosphère (Navier-Stokes, thermodynamique)
2. **Discrétisation** : Grille 3D (mailles 1-50 km)
3. **Conditions Initiales** : Observations actuelles
4. **Intégration Temporelle** : Calcul évolution future
5. **Sorties** : Cartes prévisions (T, P, vents, précipitations)

**Modèles Globaux**
- **GFS** (USA) : Global Forecast System, 13 km
- **ECMWF** : European Centre, 9 km, considéré le meilleur
- **ARPEGE** (Météo-France) : Mailles variables
- **Portée** : 10-15 jours

**Modèles Régionaux**
- **Résolution** : 1-5 km
- **Domaine Limité** : Conditions frontières modèle global
- **Exemples** : AROME (France), WRF, NAM
- **Portée** : 48-72h

**Prévisions d'Ensemble**
- **Principe** : Plusieurs simulations, conditions initiales légèrement différentes
- **Incertitude** : Dispersion résultats = incertitude
- **Probabilités** : Pluie, température, etc.

### Limites Prévisibilité

**Chaos Déterministe**
- **Effet Papillon** (Edward Lorenz) : Petites erreurs initiales s'amplifient
- **Horizon** : ~10-14 jours maximum prévisions déterministes
- **Statistiques** : Prévisions climatologiques au-delà

**Sources Incertitude**
- **Observations** : Lacunes (océans, régions isolées), erreurs mesure
- **Modèles** : Simplifications physique, résolution limitée
- **Conditions Initiales** : Impossibilité connaissance parfaite

### Communication Prévisions

**Bulletins Météo**
- **Quotidiens** : Prévisions 3-7 jours
- **Nowcasting** : 0-6h (radar, satellite)
- **Vigilance** : Couleurs (vert, jaune, orange, rouge) selon dangers

**Applications**
- **Aviation** : TAF (Terminal Aerodrome Forecast), METAR
- **Marine** : Bulletins haute mer
- **Agriculture** : Gel, pluies optimales
- **Énergie** : Demande chauffage/clim, production éolienne/solaire

