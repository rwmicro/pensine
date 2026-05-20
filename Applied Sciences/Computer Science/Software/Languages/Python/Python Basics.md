---
title: "Python"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Python"
tags: [sciences-appliquées, informatique, python]
date: "2026-02-16"
---

# Python

Python est un langage interprété, dynamiquement typé, multiparadigme (impératif, orienté objet, fonctionnel). Sa philosophie est exprimée dans le *Zen of Python* : lisibilité compte, explicite vaut mieux qu'implicite, simple vaut mieux que complexe.

## Types de base et variables

```python
# Entiers, flottants, complexes
x = 42
y = 3.14
z = 2 + 3j

# Chaînes
nom = "Alice"
multi = """ligne 1
ligne 2"""

# Booléens (sous-classe de int : True == 1)
actif = True

# None (équivalent de null)
valeur = None

# Conversion de types
int("42")       # 42
float("3.14")   # 3.14
str(42)         # "42"
bool(0)         # False  — 0, None, [], {}, "" sont falsy
```

## F-strings et formatage (Python 3.6+)

```python
nom = "Alice"
age = 30
pi = 3.14159

# F-string — la manière recommandée
print(f"Bonjour {nom}, tu as {age} ans")
print(f"Pi vaut environ {pi:.2f}")       # 3.14
print(f"Hex de 255 : {255:#x}")          # 0xff
print(f"Aligné : {nom!r:>10}")           # repr, aligné à droite sur 10

# Débogage avec = (Python 3.8+)
print(f"{age=}")   # age=30
```

## Structures de données

### Listes

```python
fruits = ["pomme", "banane", "cerise"]

# Accès et slicing
fruits[0]       # "pomme"
fruits[-1]      # "cerise"
fruits[1:3]     # ["banane", "cerise"]
fruits[::-1]    # inversé

# Méthodes principales
fruits.append("mangue")           # ajout en fin
fruits.insert(1, "fraise")        # insertion à l'index 1
fruits.remove("banane")           # supprime la première occurrence
dernier = fruits.pop()            # retire et retourne le dernier
fruits.sort()                     # tri en place
fruits.sort(key=len)              # tri par longueur
triee = sorted(fruits, reverse=True)  # nouvelle liste triée
"pomme" in fruits                 # True/False
len(fruits)                       # taille
fruits.index("cerise")            # index de l'élément
```

### Tuples

```python
point = (3, 4)        # immutable
x, y = point          # déstructuration
a, *reste = (1, 2, 3, 4)  # a=1, reste=[2, 3, 4]

# Named tuple
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p.y)
```

### Dictionnaires

```python
scores = {"Alice": 95, "Bob": 82}

# Accès sécurisé
scores.get("Charlie", 0)   # 0 si absent

# Méthodes
scores.keys()       # dict_keys
scores.values()     # dict_values
scores.items()      # dict_items — pour itérer

# Fusion (Python 3.9+)
d1 = {"a": 1}
d2 = {"b": 2}
d3 = d1 | d2        # {"a": 1, "b": 2}

# defaultdict — valeur par défaut automatique
from collections import defaultdict
groupes = defaultdict(list)
groupes["A"].append("Alice")
```

### Ensembles

```python
a = {1, 2, 3}
b = {2, 3, 4}

a | b    # union : {1, 2, 3, 4}
a & b    # intersection : {2, 3}
a - b    # différence : {1}
a ^ b    # différence symétrique : {1, 4}
3 in a   # True
```

## Compréhensions

```python
# Liste
carres = [x**2 for x in range(10)]
pairs = [x for x in range(20) if x % 2 == 0]

# Dictionnaire
longueurs = {mot: len(mot) for mot in ["chat", "chien", "oiseau"]}

# Ensemble
uniques = {x % 5 for x in range(20)}

# Générateur (évaluation paresseuse, pas de liste en mémoire)
somme = sum(x**2 for x in range(1000000))

# Imbriquées (matricielle)
matrice = [[i * j for j in range(1, 4)] for i in range(1, 4)]
# [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
```

## Contrôle de flux

```python
# if / elif / else
age = 20
if age < 18:
    statut = "mineur"
elif age < 65:
    statut = "adulte"
else:
    statut = "senior"

# Opérateur ternaire
statut = "majeur" if age >= 18 else "mineur"

# match / case (Python 3.10+, structural pattern matching)
commande = ("deplacer", 10, 20)
match commande:
    case ("deplacer", x, y):
        print(f"Déplacer vers {x}, {y}")
    case ("tourner", angle):
        print(f"Tourner de {angle}°")
    case _:
        print("Commande inconnue")

# Boucles
for i in range(5):       # 0, 1, 2, 3, 4
    pass

for i, val in enumerate(["a", "b", "c"]):
    print(i, val)        # 0 a, 1 b, 2 c

for a, b in zip([1, 2], ["x", "y"]):
    print(a, b)          # 1 x, 2 y

# while avec break/continue
n = 0
while True:
    n += 1
    if n == 3: continue
    if n == 5: break
```

## Fonctions

```python
# Paramètres positionnels, valeur par défaut, *args, **kwargs
def creer_profil(nom, age=0, *tags, **meta):
    return {"nom": nom, "age": age, "tags": tags, "meta": meta}

creer_profil("Alice", 30, "dev", "python", ville="Paris")

# Keyword-only (après *)
def tracer(x, y, *, couleur="noir", epaisseur=1):
    pass

tracer(0, 0, couleur="rouge")

# Positional-only (avant /, Python 3.8+)
def aire(longueur, largeur, /):
    return longueur * largeur

# Annotations de types (Python 3.5+)
def additionner(a: int, b: int) -> int:
    return a + b

# Fonctions lambda (une expression)
trier_par_age = sorted(personnes, key=lambda p: p["age"])
```

### Hints de types avancés

```python
from typing import Optional, Union, List, Dict, Tuple, Callable

def trouver(liste: List[str], valeur: str) -> Optional[int]:
    try:
        return liste.index(valeur)
    except ValueError:
        return None

# Python 3.10+ : union avec |
def traiter(valeur: int | str | None) -> str:
    return str(valeur)
```

## Programmation orientée objet

```python
class Animal:
    espece = "inconnu"  # attribut de classe (partagé)

    def __init__(self, nom: str, age: int) -> None:
        self.nom = nom       # attribut d'instance
        self.age = age

    def parler(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{type(self).__name__}(nom={self.nom!r}, age={self.age})"

    def __str__(self) -> str:
        return f"{self.nom} ({self.age} ans)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Animal):
            return NotImplemented
        return self.nom == other.nom and self.age == other.age


class Chien(Animal):
    espece = "Canis lupus familiaris"

    def __init__(self, nom: str, age: int, race: str) -> None:
        super().__init__(nom, age)   # appel au constructeur parent
        self.race = race

    def parler(self) -> str:
        return "Woof !"


class Chat(Animal):
    def parler(self) -> str:
        return "Miaou !"


# Polymorphisme
animaux: list[Animal] = [Chien("Rex", 3, "Berger"), Chat("Mimi", 5)]
for a in animaux:
    print(f"{a.nom} dit : {a.parler()}")
```

### Méthodes spéciales (dunder methods)

| Méthode | Déclenchée par |
|---|---|
| `__init__` | `Objet()` |
| `__repr__` | `repr(obj)`, débogage |
| `__str__` | `str(obj)`, `print()` |
| `__len__` | `len(obj)` |
| `__getitem__` | `obj[clé]` |
| `__setitem__` | `obj[clé] = val` |
| `__contains__` | `x in obj` |
| `__iter__` | `for x in obj` |
| `__next__` | `next(obj)` |
| `__enter__` / `__exit__` | `with obj:` |
| `__add__` | `obj + autre` |
| `__eq__` / `__lt__` | `==`, `<` |
| `__hash__` | `hash(obj)`, membership dans set/dict |

### Propriétés

```python
class Cercle:
    def __init__(self, rayon: float) -> None:
        self._rayon = rayon

    @property
    def rayon(self) -> float:
        return self._rayon

    @rayon.setter
    def rayon(self, valeur: float) -> None:
        if valeur < 0:
            raise ValueError("Le rayon ne peut pas être négatif")
        self._rayon = valeur

    @property
    def aire(self) -> float:
        import math
        return math.pi * self._rayon ** 2


c = Cercle(5)
print(c.aire)    # 78.53...
c.rayon = 10
```

### Dataclasses (Python 3.7+)

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float
    etiquette: str = ""
    historique: list = field(default_factory=list)

    def distance_origine(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5


p = Point(3.0, 4.0)
print(p.distance_origine())  # 5.0
print(p)  # Point(x=3.0, y=4.0, etiquette='', historique=[])
```

## Décorateurs

Un décorateur est une fonction qui enveloppe une autre fonction pour modifier ou augmenter son comportement.

```python
import functools

def logger(func):
    @functools.wraps(func)       # préserve __name__, __doc__
    def wrapper(*args, **kwargs):
        print(f"Appel de {func.__name__} avec {args}, {kwargs}")
        resultat = func(*args, **kwargs)
        print(f"  → {resultat}")
        return resultat
    return wrapper


@logger
def additionner(a, b):
    return a + b

additionner(3, 4)
# Appel de additionner avec (3, 4), {}
#   → 7
```

### Décorateur avec paramètres

```python
def repeter(n):
    def decorateur(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorateur


@repeter(3)
def dire_bonjour(nom):
    print(f"Bonjour {nom}")

dire_bonjour("Alice")  # imprime 3 fois
```

### Décorateurs de classe intégrés

```python
class MaClasse:
    compteur = 0

    @classmethod
    def incrementer(cls):      # premier arg = classe
        cls.compteur += 1

    @staticmethod
    def valider(valeur: int) -> bool:  # pas d'accès à cls ou self
        return valeur > 0
```

## Générateurs

Un générateur produit les valeurs à la demande (évaluation paresseuse) sans stocker toute la séquence en mémoire.

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


gen = fibonacci()
print([next(gen) for _ in range(8)])  # [0, 1, 1, 2, 3, 5, 8, 13]


# Générateur avec retour de valeur
def plages(limite):
    n = 0
    while n < limite:
        recu = yield n     # peut recevoir une valeur avec send()
        if recu is not None:
            n = recu
        else:
            n += 1

g = plages(10)
next(g)        # 0
g.send(5)      # reprend à 5


# yield from — déléguer à un sous-générateur
def chainer(*iterables):
    for it in iterables:
        yield from it

list(chainer([1, 2], [3, 4], [5]))  # [1, 2, 3, 4, 5]
```

## Gestionnaires de contexte

```python
# Utilisation
with open("fichier.txt", "r", encoding="utf-8") as f:
    contenu = f.read()
# f.close() est appelé automatiquement même en cas d'exception

# Implémentation manuelle via __enter__ / __exit__
class Timer:
    import time

    def __enter__(self):
        self.debut = __import__("time").time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duree = __import__("time").time() - self.debut
        print(f"Durée : {self.duree:.3f}s")
        return False  # ne supprime pas l'exception


# Via contextlib (plus simple)
from contextlib import contextmanager

@contextmanager
def chrono(label):
    import time
    t = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label} : {time.perf_counter() - t:.3f}s")


with chrono("tri"):
    sorted(range(1000000))
```

## Gestion des exceptions

```python
# Hiérarchie : BaseException → Exception → (ValueError, TypeError, ...)
try:
    resultat = int("abc")
except ValueError as e:
    print(f"Erreur de valeur : {e}")
except (TypeError, AttributeError) as e:
    print(f"Erreur de type : {e}")
except Exception:
    raise          # relance l'exception courante
else:
    print("Aucune exception")   # exécuté si pas d'exception
finally:
    print("Toujours exécuté")   # nettoyage


# Exception personnalisée
class ErreurMetier(Exception):
    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


# raise ... from ... (chaîne d'exceptions)
try:
    connexion = connexion_bdd()
except ConnectionError as e:
    raise ErreurMetier("Impossible de joindre la base", 503) from e
```

## Modules de la bibliothèque standard

### os et pathlib

```python
import os
from pathlib import Path

# pathlib (recommandé sur os.path)
p = Path("/home/user/documents")
p / "fichier.txt"           # chemin combiné
p.exists()
p.is_file()
p.stat().st_size            # taille en octets
p.read_text(encoding="utf-8")
p.write_text("contenu", encoding="utf-8")
list(p.glob("*.py"))        # fichiers .py
list(p.rglob("*.py"))       # récursif

# Variables d'environnement
os.environ.get("HOME", "/tmp")
```

### json

```python
import json

# Sérialisation
data = {"nom": "Alice", "scores": [95, 82]}
chaine = json.dumps(data, indent=2, ensure_ascii=False)
json.dump(data, open("data.json", "w"))

# Désérialisation
obj = json.loads(chaine)
obj = json.load(open("data.json"))
```

### csv

```python
import csv

# Écriture
with open("notes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["nom", "note"])
    writer.writeheader()
    writer.writerow({"nom": "Alice", "note": 95})

# Lecture
with open("notes.csv", newline="", encoding="utf-8") as f:
    for ligne in csv.DictReader(f):
        print(ligne["nom"], ligne["note"])
```

### datetime

```python
from datetime import datetime, timedelta, date, timezone

maintenant = datetime.now()
utc = datetime.now(timezone.utc)
d = datetime(2024, 1, 15, 10, 30)

# Formatage
d.strftime("%d/%m/%Y %H:%M")   # "15/01/2024 10:30"
datetime.strptime("15/01/2024", "%d/%m/%Y")

# Arithmétique
demain = maintenant + timedelta(days=1)
delta = datetime(2025, 1, 1) - maintenant
print(delta.days)
```

### collections

```python
from collections import Counter, defaultdict, deque, OrderedDict

# Counter — comptage d'éléments
mots = ["chat", "chien", "chat", "oiseau", "chat"]
c = Counter(mots)
c.most_common(2)   # [('chat', 3), ('chien', 1)]
c["chat"]          # 3

# defaultdict — valeur par défaut
d = defaultdict(int)
for mot in mots:
    d[mot] += 1

# deque — file double extrémité (O(1) des deux côtés)
file = deque(maxlen=100)
file.appendleft(0)
file.append(1)
file.popleft()
```

### itertools et functools

```python
import itertools
import functools

# itertools
list(itertools.chain([1, 2], [3, 4]))          # [1, 2, 3, 4]
list(itertools.combinations([1,2,3], 2))        # [(1,2),(1,3),(2,3)]
list(itertools.permutations("AB", 2))           # [('A','B'),('B','A')]
list(itertools.islice(itertools.count(10), 5))  # [10,11,12,13,14]
list(itertools.groupby("AABBBCC", lambda x: x)) # groupes

# functools
@functools.lru_cache(maxsize=128)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)

functools.reduce(lambda acc, x: acc + x, [1,2,3,4], 0)  # 10
double = functools.partial(pow, exp=2)   # pow(x, exp=2)
```

## L'opérateur walrus := (Python 3.8+)

L'opérateur d'affectation dans une expression permet d'assigner et d'utiliser une valeur dans la même expression.

```python
# Évite de lire deux fois depuis un itérable coûteux
import re
if m := re.search(r"\d+", "abc123"):
    print(m.group())   # "123"

# Dans une boucle while
while chunk := f.read(8192):
    traiter(chunk)

# Dans une compréhension
resultats = [y for x in donnees if (y := traiter(x)) is not None]
```

## Programmation fonctionnelle

```python
# map, filter, reduce
nombres = [1, 2, 3, 4, 5]
carres = list(map(lambda x: x**2, nombres))
pairs = list(filter(lambda x: x % 2 == 0, nombres))

# Privilégier les compréhensions à map/filter
carres = [x**2 for x in nombres]
pairs = [x for x in nombres if x % 2 == 0]

# zip — combiner des itérables
noms = ["Alice", "Bob"]
ages = [30, 25]
for nom, age in zip(noms, ages):
    print(nom, age)

# dict depuis deux listes
dico = dict(zip(noms, ages))   # {"Alice": 30, "Bob": 25}

# zip_longest (itertools) pour des listes de tailles différentes
from itertools import zip_longest
for a, b in zip_longest([1, 2, 3], ["x", "y"], fillvalue=None):
    print(a, b)
```

## Aperçu des performances

| Opération | Structure | Complexité |
|---|---|---|
| Accès par index | list, tuple | O(1) |
| Recherche | list | O(n) |
| Appartenance | set, dict | O(1) amorti (*amortized*) |
| Insertion/suppression début | list | O(n) |
| Insertion/suppression début | deque | O(1) |
| Tri | list.sort() | O(n log n) |
| Accès | dict | O(1) amorti |
