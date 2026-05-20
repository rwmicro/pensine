---
title: "Mécanique quantique"
domain: "Applied Sciences"
subdomain: "Physics"
tags: [sciences-appliquées, physique]
date: "2026-02-04"
---

# Mécanique quantique

## Vue d'ensemble

La **mécanique quantique** est la théorie physique qui décrit le comportement de la matière et de l'énergie à l'échelle atomique et subatomique. Elle révolutionne notre compréhension de la nature en introduisant des concepts contre-intuitifs.

**Naissance** : Début du XXe siècle (1900-1930)

**Révolution** : Rupture avec la physique classique (Newton, Maxwell)


## Principes fondamentaux

### 1. Dualité onde-corpuscule

**Toute particule possède à la fois des propriétés ondulatoires et corpusculaires.**

**Expérience des fentes de Young** :
- Un électron passe par deux fentes simultanément
- Crée des franges d'interférence (comportement ondulatoire)
- Détecté comme une particule localisée

**Relation de De Broglie** :
```
λ = h / p
```
- λ : longueur d'onde
- h : constante de Planck (6.626 × 10⁻³⁴ J·s)
- p : quantité de mouvement

### 2. Principe d'incertitude de Heisenberg

**On ne peut pas connaître simultanément avec précision la position et la vitesse d'une particule.**

```
Δx · Δp ≥ ℏ/2
```

- Δx : incertitude sur la position
- Δp : incertitude sur la quantité de mouvement
- ℏ : constante de Planck réduite (h/2π)

**Implications** :
- Limitation fondamentale, pas technique
- Plus on connaît précisément la position, moins on connaît la vitesse
- La mesure perturbe le système

### 3. Quantification de l'énergie

**L'énergie ne peut prendre que des valeurs discrètes (quantas).**

**Photon** (quantum de lumière) :
```
E = hν = ℏω
```
- ν : fréquence
- ω : pulsation

**Oscillateur harmonique quantique** :
```
E_n = ℏω(n + 1/2)
```
- n = 0, 1, 2, 3, ...

### 4. Fonction d'onde et probabilité

**État quantique décrit par une fonction d'onde ψ(x,t)**

**Équation de Schrödinger** (temps-dépendante) :
```
iℏ ∂ψ/∂t = Ĥψ
```
- Ĥ : opérateur hamiltonien (énergie)

**Interprétation de Born** :
- |ψ(x,t)|² = densité de probabilité de présence
- La particule n'a pas de position définie avant la mesure
- **Superposition d'états** : la particule est dans tous les états possibles simultanément

### 5. Principe de superposition

**Un système quantique peut être dans plusieurs états à la fois.**

**Chat de Schrödinger** (expérience de pensée) :
- Chat dans une boîte avec un mécanisme quantique
- Avant observation : vivant ET mort (superposition)
- Après observation : vivant OU mort (effondrement)

### 6. Intrication quantique

**Deux particules peuvent être corrélées de manière non-locale.**

Einstein : "Action fantôme à distance"

**EPR (Einstein-Podolsky-Rosen)** :
- Mesure sur particule A affecte instantanément particule B
- Même séparées par des années-lumière
- Vérifié expérimentalement (Alain Aspect, 1982)

**Applications** :
- Cryptographie quantique
- Téléportation quantique
- Ordinateurs quantiques


## Modèle de l'atome

### Modèle de Bohr (1913)

**Électrons sur des orbites quantifiées**

Énergie de l'électron :
```
E_n = -13.6 eV / n²
```
- n = 1, 2, 3, ... (nombre quantique principal)

**Rayon de Bohr** :
```
a_0 = 0.529 Å
```

### Modèle quantique moderne

**Électrons décrits par des orbitales (fonctions d'onde)**

**Nombres quantiques** :
1. **n** : niveau d'énergie (1, 2, 3, ...)
2. **l** : moment angulaire (0, 1, ..., n-1)
   - l=0 : s, l=1 : p, l=2 : d, l=3 : f
3. **m** : projection du moment angulaire (-l, ..., +l)
4. **s** : spin (±1/2)

**Principe d'exclusion de Pauli** :
- Deux fermions ne peuvent avoir les mêmes nombres quantiques
- Explique la structure du tableau périodique


## Phénomènes quantiques

### Effet tunnel

**Une particule peut traverser une barrière de potentiel classiquement infranchissable.**

**Applications** :
- Microscope à effet tunnel (STM)
- Fusion nucléaire dans le Soleil
- Transistors à effet tunnel
- Désintégration alpha

### Décohérence

**Perte des propriétés quantiques par interaction avec l'environnement.**

- Explique la transition quantique → classique
- Pourquoi on ne voit pas de chats en superposition
- Défi majeur pour les ordinateurs quantiques

### Effet Casimir

**Deux plaques conductrices dans le vide s'attirent.**

- Fluctuations quantiques du vide
- Preuve de l'énergie du vide quantique


## Interprétations de la mécanique quantique

### Interprétation de Copenhague

**Orthodoxe, majoritaire**

- La fonction d'onde s'effondre lors de la mesure
- Avant mesure : superposition
- Après mesure : état défini
- **Problème** : qu'est-ce qu'une "mesure" ?

### Interprétation des mondes multiples (Everett)

**Pas d'effondrement**

- Chaque mesure crée un embranchement de l'univers
- Tous les résultats possibles se réalisent
- Dans des univers parallèles

### Interprétation de De Broglie-Bohm

**Variables cachées**

- Particules ont des trajectoires déterministes
- Guidées par une onde pilote
- Non-locale

### Décohérence et états relatifs

**Moderne**

- Pas d'effondrement mystérieux
- Intrication avec l'environnement
- États relatifs à l'observateur


## Applications technologiques

### Laser

**Émission stimulée de photons**
- Cohérence quantique
- Applications : médecine, industrie, communication

### Transistor et semi-conducteurs

**Électronique moderne**
- Effet tunnel
- Bandes d'énergie quantifiées
- Informatique, smartphones

### IRM (Imagerie par Résonance Magnétique)

**Résonance magnétique nucléaire**
- Spin des noyaux atomiques
- Médecine diagnostique

### LED et écrans

**Électroluminescence quantique**
- Recombinaison électron-trou
- Éclairage, affichage

### Ordinateur quantique

**Calcul sur qubits (bits quantiques)**
- Superposition : 0 ET 1 simultanément
- Intrication : corrélation entre qubits
- Puissance exponentielle pour certains problèmes
- **Défis** : décohérence, correction d'erreurs

### Cryptographie quantique

**Sécurité inconditionnelle**
- Distribution de clés quantiques (QKD)
- Impossible d'espionner sans être détecté
- Principe d'incertitude + no-cloning theorem


## Grands scientifiques

**Fondateurs** :
- **Max Planck** (1900) : Quantification de l'énergie
- **Albert Einstein** (1905) : Effet photoélectrique, photon
- **Niels Bohr** (1913) : Modèle atomique
- **Louis de Broglie** (1924) : Dualité onde-corpuscule
- **Werner Heisenberg** (1925) : Mécanique matricielle, principe d'incertitude
- **Erwin Schrödinger** (1926) : Équation d'onde
- **Max Born** (1926) : Interprétation probabiliste
- **Paul Dirac** (1928) : Équation relativiste, antimatière
- **Wolfgang Pauli** (1925) : Principe d'exclusion

**Développements** :
- **Richard Feynman** : Intégrales de chemin, électrodynamique quantique
- **John Bell** : Inégalités de Bell, test de la non-localité
- **Alain Aspect** : Vérification expérimentale de l'intrication


## Équations fondamentales

### Équation de Schrödinger (indépendante du temps)

```
Ĥψ = Eψ
```

### Équation de Schrödinger (temps-dépendante)

```
iℏ ∂ψ/∂t = Ĥψ
```

### Commutateur position-impulsion

```
[x̂, p̂] = iℏ
```

### Hamiltonien de l'oscillateur harmonique

```
Ĥ = p̂²/2m + ½mω²x̂²
```

### Équation de Dirac (relativiste)

```
(iℏγ^μ∂_μ - mc)ψ = 0
```


## Expériences célèbres

### Effet photoélectrique (Einstein, 1905)

- Lumière éjecte des électrons d'un métal
- Énergie des électrons dépend de la fréquence, pas de l'intensité
- Preuve de la nature corpusculaire de la lumière

### Fentes de Young (version quantique)

- Particules une à une créent des interférences
- Observation modifie le résultat
- Complémentarité onde-corpuscule

### Expérience d'Aspect (1982)

- Violation des inégalités de Bell
- Preuve de la non-localité quantique
- Fin des théories à variables cachées locales

### Chat de Schrödinger (1935)

- Expérience de pensée sur la superposition
- Critique de l'interprétation de Copenhague
- Illustre le problème de la mesure


## Liens avec d'autres domaines

**Chimie quantique** :
- Liaisons chimiques
- Tableau périodique
- Réactivité moléculaire

**Physique des particules** :
- Modèle standard
- Théorie quantique des champs
- Chromodynamique quantique (QCD)

**Cosmologie** :
- Fluctuations quantiques primordiales
- Inflation cosmique
- Rayonnement de Hawking (trous noirs)

**Information quantique** :
- Qubits et calcul quantique
- Téléportation quantique
- Cryptographie

**Biologie quantique** (émergent) :
- Photosynthèse
- Odorat
- Navigation des oiseaux


## Paradoxes et questions ouvertes

### Problème de la mesure

- Quand et comment se produit l'effondrement ?
- Qu'est-ce qu'un "observateur" ?

### Chat de Schrödinger

- Pourquoi ne voit-on pas de superpositions macroscopiques ?
- Rôle de la décohérence

### EPR et non-localité

- Comment l'information voyage-t-elle ?
- Incompatible avec la relativité ?

### Interprétation

- Quelle est la "vraie" nature de la réalité quantique ?
- Mondes multiples vs effondrement

### Gravité quantique

- Comment unifier mécanique quantique et relativité générale ?
- Théorie des cordes ? Gravitation quantique à boucles ?


## Ressources d'apprentissage

### Livres

**Vulgarisation** :
- "L'Univers élégant" - Brian Greene
- "Le grand roman de la physique quantique" - Manjit Kumar
- "Le cantique des quantiques" - Sven Ortoli & Jean-Pierre Pharabod

**Intermédiaire** :
- "Mécanique quantique" - Claude Cohen-Tannoudji (Tome 1 & 2)
- "Introduction to Quantum Mechanics" - David J. Griffiths

**Avancé** :
- "Principes de mécanique quantique" - Paul Dirac
- "Quantum Mechanics and Path Integrals" - Richard Feynman

### Cours en ligne

- MIT OpenCourseWare : 8.04 Quantum Physics I
- Stanford : Leonard Susskind - Quantum Mechanics
- Coursera : Quantum Mechanics for Everyone

### Vidéos

- Chaîne YouTube : ScienceClic
- Chaîne YouTube : Science étonnante (Bruce Benamran)
- Minutephysics : Quantum Mechanics playlist


*Créé le : 2026-01-01*  
*Dernière mise à jour : 2026-01-01*
