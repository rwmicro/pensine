---
title: "Optique"
domain: "Applied Sciences"
subdomain: "Physics"
tags: [sciences-appliquées, physique]
date: "2026-02-04"
---

# Optique

## Vue d'ensemble

L'**optique** est l'étude de la lumière et de ses interactions avec la matière. Elle se divise en plusieurs branches selon le niveau de description.


## Nature de la lumière

### Dualité onde-corpuscule

**La lumière est à la fois onde et particule.**

**Onde électromagnétique** :
- Champ électrique + champ magnétique
- Se propage dans le vide à c = 299 792 458 m/s

**Particule (photon)** :
- Quantum d'énergie : E = hν = ℏω
- Quantité de mouvement : p = h/λ

### Spectre électromagnétique

```
Radio → Micro-ondes → IR → Visible → UV → X → Gamma
```

**Lumière visible** : 380-780 nm
- Violet : ~380-450 nm
- Bleu : ~450-495 nm
- Vert : ~495-570 nm
- Jaune : ~570-590 nm
- Orange : ~590-620 nm
- Rouge : ~620-780 nm


## Optique géométrique

**Approximation** : Propagation rectiligne (rayons lumineux)

### Lois de l'optique géométrique

#### Propagation rectiligne

**La lumière se propage en ligne droite dans un milieu homogène.**

#### Loi de la réflexion

**θ_i = θ_r**

- Angle d'incidence = angle de réflexion
- Même plan

**Types de réflexion** :
- **Spéculaire** : Surface lisse (miroir)
- **Diffuse** : Surface rugueuse (mur)

#### Loi de Snell-Descartes (réfraction)

**n₁ sin θ₁ = n₂ sin θ₂**

- n : indice de réfraction
- θ : angle par rapport à la normale

**Indices** :
- Vide : n = 1
- Air : n ≈ 1,0003
- Eau : n ≈ 1,33
- Verre : n ≈ 1,5
- Diamant : n ≈ 2,42

**Vitesse de la lumière dans un milieu** :
```
v = c / n
```

#### Réflexion totale

**Angle critique** :
```
sin θ_c = n₂ / n₁
```

- Si θ > θ_c : réflexion totale
- Base des fibres optiques

### Systèmes optiques

#### Miroirs

**Miroir plan** :
- Image virtuelle, symétrique

**Miroir sphérique** :

**Relation de conjugaison** :
```
1/f = 1/p + 1/p'
```
- f : distance focale
- p : distance objet
- p' : distance image

**Grandissement** :
```
γ = p' / p
```

#### Lentilles

**Lentille convergente** (biconvexe) :
- Fait converger les rayons
- f > 0

**Lentille divergente** (biconcave) :
- Fait diverger les rayons
- f < 0

**Formule des lentilles minces** :
```
1/f = 1/p + 1/p'
```

**Puissance** :
```
P = 1/f (en dioptries)
```

**Construction d'images** :
- Rayon parallèle → passe par F'
- Rayon par centre → non dévié
- Rayon par F → parallèle


## Optique ondulatoire

**Prend en compte la nature ondulatoire de la lumière.**

### Interférences

**Superposition de deux ondes cohérentes**

**Interférences constructives** :
- Chemin optique : Δ = kλ (k entier)
- Intensité maximale

**Interférences destructives** :
- Chemin optique : Δ = (k + 1/2)λ
- Intensité minimale

**Expériences** :

**Fentes de Young** :
- Deux sources cohérentes
- Franges d'interférence
- Preuve de la nature ondulatoire

**Interféromètre de Michelson** :
- Mesure de longueurs d'onde
- Détection d'ondes gravitationnelles (LIGO)

### Diffraction

**Déviation de la lumière passant par une ouverture ou un obstacle**

**Critère de Rayleigh** :
```
θ_min ≈ 1,22 λ / D
```
- Limite de résolution angulaire
- D : diamètre de l'ouverture

**Réseau de diffraction** :
- Multiples fentes
- Décompose la lumière (spectre)

### Polarisation

**Orientation du champ électrique**

**Types** :
- **Linéaire** : Oscillation dans un plan
- **Circulaire** : Rotation du vecteur
- **Elliptique** : Intermédiaire

**Polariseur** : Ne laisse passer qu'une composante

**Loi de Malus** :
```
I = I₀ cos²θ
```

**Applications** :
- Lunettes polarisées (anti-reflet)
- Écrans LCD
- Stéréoscopie 3D


## Optique physique

### Dispersion

**Dépendance de l'indice avec la longueur d'onde**

**Prisme** :
- Décompose la lumière blanche
- Arc-en-ciel

**Relation de Cauchy** :
```
n(λ) = A + B/λ²
```

### Absorption et émission

**Loi de Beer-Lambert** :
```
I = I₀ e^(-αx)
```
- α : coefficient d'absorption

**Émission** :
- Incandescence (corps noir)
- Luminescence (fluorescence, phosphorescence)
- Laser (émission stimulée)

### Effet Doppler

**Décalage de fréquence par mouvement**

**Source en mouvement** :
```
ν' = ν (c / (c ± v))
```

**Applications** :
- Radar de vitesse
- Redshift cosmologique
- Exoplanètes


## Instruments d'optique

### Œil humain

**Système optique naturel**

- Cornée + cristallin = lentille convergente
- Rétine = capteur
- Accommodation : f variable

**Défauts** :
- **Myopie** : Image avant rétine → lentille divergente
- **Hypermétropie** : Image après rétine → lentille convergente
- **Presbytie** : Perte d'accommodation (âge)
- **Astigmatisme** : Courbure inégale

### Lunettes et lentilles de contact

**Correction des défauts visuels**

### Loupe

**Lentille convergente simple**

**Grossissement** :
```
G = δ / f
```
- δ : distance minimale de vision distincte (≈ 25 cm)

### Microscope

**Système de deux lentilles**
- Objectif : fort grossissement
- Oculaire : observation

**Grossissement total** :
```
G = G_obj × G_oc
```

**Limite de résolution** :
```
d_min ≈ λ / (2 n sin α)
```

### Télescope / Lunette astronomique

**Observation d'objets lointains**

**Types** :
- **Réfracteur** : Lentilles (lunette)
- **Réflecteur** : Miroirs (télescope)

**Grossissement** :
```
G = f_obj / f_oc
```

### Appareil photo

**Capture d'image sur capteur**

- Objectif : lentille convergente
- Diaphragme : contrôle lumière (ouverture f/n)
- Capteur : CCD ou CMOS

**Profondeur de champ** : Zone nette

### Fibre optique

**Guidage de la lumière par réflexion totale**

**Applications** :
- Télécommunications (Internet)
- Médecine (endoscopie)
- Éclairage


## Phénomènes optiques naturels

### Arc-en-ciel

**Dispersion + réflexion dans gouttes d'eau**

- Arc primaire : 1 réflexion (~42°)
- Arc secondaire : 2 réflexions (~51°, inversé)

### Mirages

**Réfraction dans l'air chaud**

- Mirage inférieur : Désert (eau illusoire)
- Mirage supérieur : Mer froide (objets surélevés)

### Aurores boréales / australes

**Particules solaires + champ magnétique terrestre**

- Vert : Oxygène (~100 km)
- Rouge : Oxygène (~300 km)
- Bleu/violet : Azote

### Diffusion Rayleigh

**Ciel bleu**

- Diffusion ∝ 1/λ⁴
- Bleu diffusé plus que rouge
- Soleil couchant rouge (chemin long)


## Applications modernes

### Laser

**Light Amplification by Stimulated Emission of Radiation**

**Propriétés** :
- Cohérence spatiale et temporelle
- Monochromatique
- Directif

**Applications** :
- Médecine (chirurgie, ophtalmologie)
- Industrie (découpe, soudure)
- Télécommunications
- Lecteurs CD/DVD/Blu-ray
- Recherche (spectroscopie)

### Holographie

**Enregistrement du front d'onde complet**

- Image 3D
- Interférences laser

### Optique non-linéaire

**Réponse non-linéaire à forte intensité (laser)**

- Doublage de fréquence
- Effet Kerr

### Métamatériaux

**Matériaux artificiels avec propriétés inhabituelles**

- Indice négatif
- Cape d'invisibilité
- Super-lentille (dépasse limite de diffraction)


## Grands scientifiques

**Ibn al-Haytham (Alhazen)** (965-1040) : Père de l'optique moderne

**Isaac Newton** (1643-1727) : Décomposition de la lumière, théorie corpusculaire

**Christiaan Huygens** (1629-1695) : Principe de Huygens, théorie ondulatoire

**Thomas Young** (1773-1829) : Expérience des fentes, interférences

**Augustin Fresnel** (1788-1827) : Diffraction, théorie ondulatoire

**James Clerk Maxwell** (1831-1879) : Théorie électromagnétique de la lumière

**Albert Einstein** (1879-1955) : Photon, effet photoélectrique


## Liens connexes

- [[Mécanique quantique]] - Nature quantique de la lumière
- [[../Mathematics/Géométrie]] - Optique géométrique
- [[Électromagnétisme]] - Ondes EM


## Ressources

**Livres** :
- "Optique" - Eugène Hecht
- "Principles of Optics" - Max Born & Emil Wolf
- "Fundamentals of Photonics" - Saleh & Teich

**Expériences** :
- Décomposition de la lumière avec un prisme
- Interférences avec pointeur laser + fentes
- Polarisation avec filtres polarisants


*Créé le : 2026-01-01*  
*Dernière mise à jour : 2026-01-01*
