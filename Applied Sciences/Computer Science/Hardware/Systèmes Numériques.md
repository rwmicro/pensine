---
title: "Systèmes Numériques"
domain: "Applied Sciences"
subdomain: "Computer Science > Hardware"
tags: [sciences-appliquées, informatique]
date: "2026-02-25"
---

# Systèmes Numériques

Les systèmes numériques traitent l'information sous forme de valeurs discrètes. Comprendre comment les nombres sont représentés et comment les circuits les manipulent est fondamental pour l'informatique bas niveau.

## Systèmes de numération

### Bases usuelles

| Base | Nom | Chiffres | Préfixe (C/Python) |
|---|---|---|---|
| 2 | Binaire | 0, 1 | 0b |
| 8 | Octal | 0-7 | 0o |
| 10 | Décimal | 0-9 | (aucun) |
| 16 | Hexadécimal | 0-9, A-F | 0x |

### Conversions

**Décimal → Binaire** : divisions successives par 2, lire les restes de bas en haut.

```
45 ÷ 2 = 22 reste 1
22 ÷ 2 = 11 reste 0
11 ÷ 2 =  5 reste 1
 5 ÷ 2 =  2 reste 1
 2 ÷ 2 =  1 reste 0
 1 ÷ 2 =  0 reste 1

45 en décimal = 101101 en binaire
```

**Binaire → Décimal** : sommer les puissances de 2.

```
101101 = 1×2⁵ + 0×2⁴ + 1×2³ + 1×2² + 0×2¹ + 1×2⁰
       = 32 + 0 + 8 + 4 + 0 + 1 = 45
```

**Hexadécimal ↔ Binaire** : chaque chiffre hex correspond exactement à 4 bits.

```
0xAB = 1010 1011
   A = 1010 (10 en décimal)
   B = 1011 (11 en décimal)

0xFF = 1111 1111 = 255
0x1F4 = 0001 1111 0100 = 500
```

**Python pour les conversions** :

```python
# Décimal → autres bases
bin(45)    # '0b101101'
oct(45)    # '0o55'
hex(255)   # '0xff'

# Autres bases → décimal
int('101101', 2)   # 45
int('55', 8)       # 45
int('FF', 16)      # 255
int('0xFF', 16)    # 255

# Formatage
f"{45:08b}"   # '00101101' (8 bits, zéros devant)
f"{255:02X}"  # 'FF' (hexadécimal majuscule)
```

## Représentation des entiers

### Entiers non signés (unsigned)

Sur n bits, représente les entiers de 0 à 2ⁿ - 1.

```
8 bits unsigned : 0 à 255
16 bits unsigned : 0 à 65 535
32 bits unsigned : 0 à 4 294 967 295
64 bits unsigned : 0 à 18 446 744 073 709 551 615
```

### Entiers signés — Complément à 2

Le complément à 2 est la représentation standard des entiers signés. Sur n bits, représente les entiers de -2^(n-1) à 2^(n-1) - 1.

```
8 bits signé : -128 à 127
16 bits signé : -32 768 à 32 767
32 bits signé : -2 147 483 648 à 2 147 483 647
```

**Calcul du complément à 2 d'un nombre négatif** :
1. Écrire la valeur absolue en binaire
2. Inverser tous les bits (complément à 1)
3. Ajouter 1

```
-5 sur 8 bits :
+5  = 00000101
~+5 = 11111010  (inverser)
+1  = 11111011  (ajouter 1)
-5  = 11111011

Vérification : 11111011 = -128 + 64 + 32 + 16 + 8 + 0 + 2 + 1 = -5 ✓
```

**Astuce** : le bit de poids fort est le bit de signe. Si MSB=1, le nombre est négatif.

**Overflow** : dépasser la plage représentable. Sur 8 bits signés, 127 + 1 = -128 (overflow). En C/C++, l'overflow d'entiers signés est un comportement indéfini.

```python
import ctypes
# Simuler l'overflow 8 bits signé
ctypes.c_int8(127 + 1).value  # -128
```

### Représentation IEEE 754 (virgule flottante)

Les nombres réels sont représentés selon la norme IEEE 754.

**Simple précision (float, 32 bits)** :
```
Bit 31   : signe (1 bit)
Bits 30-23 : exposant (8 bits, biais 127)
Bits 22-0  : mantisse (23 bits, fraction après le point binaire)

Valeur = (-1)^signe × 1.mantisse × 2^(exposant - 127)
```

**Double précision (double, 64 bits)** :
```
Signe : 1 bit
Exposant : 11 bits, biais 1023
Mantisse : 52 bits

Valeur = (-1)^signe × 1.mantisse × 2^(exposant - 1023)
```

**Valeurs spéciales** :

| Exposant | Mantisse | Valeur |
|---|---|---|
| Tous 0 | 0 | ±0 |
| Tous 0 | ≠ 0 | Nombre dénormalisé |
| Tous 1 | 0 | ±∞ |
| Tous 1 | ≠ 0 | NaN (Not a Number) |

```python
float('inf')   # +infini
float('nan')   # NaN
float('nan') == float('nan')  # False ! NaN n'est jamais égal à lui-même

# Précision des flottants
0.1 + 0.2 == 0.3  # False en Python/C !
0.1 + 0.2         # 0.30000000000000004

import math
math.isclose(0.1 + 0.2, 0.3)  # True (comparaison avec tolérance)
```

## Portes logiques

Les portes logiques sont les briques de base des circuits numériques. Elles opèrent sur des bits (0 ou 1).

| Porte | Symbole | Opération | Table de vérité |
|---|---|---|---|
| NOT | ¬A | Inversion | 0→1, 1→0 |
| AND | A∧B | ET | 1 seulement si A=1 ET B=1 |
| OR | A∨B | OU | 1 si A=1 OU B=1 (ou les deux) |
| XOR | A⊕B | OU exclusif | 1 si A≠B |
| NAND | ¬(A∧B) | NON-ET | Inverse de AND |
| NOR | ¬(A∨B) | NON-OU | Inverse de OR |

**Tables de vérité complètes** :

```
A  B  AND  OR  XOR  NAND  NOR
0  0   0    0   0     1    1
0  1   0    1   1     1    0
1  0   0    1   1     1    0
1  1   1    1   0     0    0
```

**NAND et NOR sont universels** : avec seulement des portes NAND (ou seulement NOR), on peut construire n'importe quel circuit. C'est important pour la fabrication de circuits intégrés.

## Algèbre de Boole

L'algèbre de Boole est le système mathématique qui décrit la logique binaire.

**Propriétés fondamentales** :

```
Identité :     A + 0 = A      A · 1 = A
Annulation :   A + 1 = 1      A · 0 = 0
Idempotence :  A + A = A      A · A = A
Complément :   A + ¬A = 1    A · ¬A = 0
Double négation : ¬(¬A) = A

Lois de De Morgan :
¬(A + B) = ¬A · ¬B    (NOR = AND des compléments)
¬(A · B) = ¬A + ¬B    (NAND = OR des compléments)
```

**Simplification** : réduire une expression booléenne pour minimiser le nombre de portes.

```
F = A·B·C + A·B·¬C + A·¬B·C
  = A·B·(C + ¬C) + A·¬B·C     # factorisation
  = A·B·1 + A·¬B·C             # C + ¬C = 1
  = A·B + A·¬B·C               # A·B·1 = A·B
  = A·(B + ¬B·C)               # factorisation par A
  = A·(B + C)                  # loi d'absorption : B + ¬B·C = B + C
```

## Circuits combinatoires

La sortie dépend uniquement des entrées présentes (pas de mémoire).

### Additionneur

**Demi-additionneur** : additionne deux bits.

```
Entrées : A, B
Sorties : Somme = A ⊕ B (XOR)
          Retenue = A · B (AND)

A  B  Somme  Retenue
0  0    0       0
0  1    1       0
1  0    1       0
1  1    0       1
```

**Additionneur complet** : additionne deux bits et une retenue entrante.

```
Entrées : A, B, Cin
Sorties : Somme = A ⊕ B ⊕ Cin
          Cout = A·B + Cin·(A⊕B)
```

On chaîne 8 additionneurs complets pour additionner deux octets.

### Multiplexeur (MUX)

Sélectionne une entrée parmi plusieurs et la dirige vers la sortie selon des bits de sélection. Un MUX 2:1 : `S=0 → Y=A, S=1 → Y=B`.

### Décodeur

Convertit un code binaire à n bits en activation d'une parmi 2ⁿ sorties. Exemple : décodeur d'adresse mémoire.

### Comparateur

Compare deux nombres binaires et produit des signaux `A>B`, `A=B`, `A<B`.

## Circuits séquentiels

La sortie dépend des entrées ET de l'état mémorisé (mémoire).

### Bascule RS (Set-Reset)

Mémorise un bit. S=1 met la sortie à 1 (Set), R=1 la remet à 0 (Reset). L'état S=R=1 est indéfini.

### Bascule D (Data)

Capture la valeur de l'entrée D à chaque front d'horloge. Élimine l'état indéfini de la RS.

```
À chaque front montant de l'horloge : Q ← D
```

### Registre

N bascules D montées en parallèle pour mémoriser N bits simultanément. Un registre 64 bits = 64 bascules D.

### Compteur

Circuit séquentiel dont la valeur de sortie s'incrémente à chaque coup d'horloge. Utilisé pour les adresses, les temporisateurs.

### Horloge et synchronisation

Tous les circuits séquentiels sont synchronisés par une horloge (signal carré oscillant à fréquence fixe). La fréquence d'horloge (en GHz) détermine le nombre d'opérations par seconde. Le setup time et hold time doivent être respectés pour éviter les violations de timing.

## Opérations bit à bit en programmation

```python
a = 0b1010  # 10
b = 0b1100  # 12

a & b   # 0b1000 = 8  — ET bit à bit
a | b   # 0b1110 = 14 — OU bit à bit
a ^ b   # 0b0110 = 6  — XOR bit à bit
~a      # -11 (complément à 2)
a << 2  # 0b101000 = 40 — décalage gauche = ×4
a >> 1  # 0b0101 = 5  — décalage droite = ÷2

# Opérations utiles avec les masques
# Vérifier si le bit i est à 1
def bit_set(n, i): return bool(n & (1 << i))

# Mettre le bit i à 1
def set_bit(n, i): return n | (1 << i)

# Mettre le bit i à 0
def clear_bit(n, i): return n & ~(1 << i)

# Inverser le bit i
def toggle_bit(n, i): return n ^ (1 << i)

# Compter les bits à 1 (popcount)
bin(42).count('1')   # 3
```
