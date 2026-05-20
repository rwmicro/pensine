---
title: "Principes SOLID"
domain: "Applied Sciences"
subdomain: "Computer Science > Architecture Logicielle"
tags: [sciences-appliquées, informatique]
date: "2026-02-25"
---

# Principes SOLID

Les principes SOLID sont cinq règles de conception orientée objet formulées par Robert C. Martin. Ils guident la création de code maintenable, extensible et testable.

## S — Single Responsibility Principle

**Un module, une classe, une fonction n'a qu'une seule raison de changer.**

Une "raison de changer" correspond à un acteur ou un groupe de parties prenantes (ex : le service comptabilité, le service RH).

**Violation** :

```python
class Rapport:
    def generer(self):
        return "Rapport: ..."

    def formater_en_pdf(self, contenu):  # responsabilité 2
        print(f"PDF: {contenu}")

    def sauvegarder_en_bdd(self, contenu):  # responsabilité 3
        print(f"BDD: {contenu}")
```

La classe `Rapport` change si le format PDF change, si la logique métier change, ou si le schéma BDD change.

**Respecté** :

```python
class Rapport:
    def generer(self) -> str:
        return "Rapport: ..."

class FormateurPDF:
    def formater(self, contenu: str) -> bytes:
        print(f"PDF: {contenu}")

class DepotRapport:
    def sauvegarder(self, contenu: str) -> None:
        print(f"BDD: {contenu}")

# Chaque classe a une seule raison de changer
rapport = Rapport()
contenu = rapport.generer()
FormateurPDF().formater(contenu)
DepotRapport().sauvegarder(contenu)
```

## O — Open/Closed Principle

**Les entités logicielles doivent être ouvertes à l'extension mais fermées à la modification.**

On doit pouvoir ajouter de nouveaux comportements sans modifier le code existant (et donc sans risquer de casser ce qui fonctionne).

**Violation** :

```python
class CalculateurRemise:
    def calculer(self, commande, type_client: str) -> float:
        if type_client == "standard":
            return 0.0
        elif type_client == "fidele":
            return 0.1
        elif type_client == "vip":
            return 0.2
        # Ajouter un type oblige à modifier cette classe
```

**Respecté** :

```python
from abc import ABC, abstractmethod

class StrategieRemise(ABC):
    @abstractmethod
    def calculer(self, montant: float) -> float:
        pass

class RemiseStandard(StrategieRemise):
    def calculer(self, montant: float) -> float:
        return 0.0

class RemiseFidele(StrategieRemise):
    def calculer(self, montant: float) -> float:
        return montant * 0.10

class RemiseVIP(StrategieRemise):
    def calculer(self, montant: float) -> float:
        return montant * 0.20

class RemiseSaisonnier(StrategieRemise):  # Nouveau type — aucune modification nécessaire
    def calculer(self, montant: float) -> float:
        return montant * 0.15

class CalculateurRemise:
    def calculer(self, commande, strategie: StrategieRemise) -> float:
        return strategie.calculer(commande.montant)
```

## L — Liskov Substitution Principle

**Les objets d'une classe dérivée doivent pouvoir remplacer ceux de leur classe de base sans altérer le comportement correct du programme.**

Si `B` hérite de `A`, alors tout code qui fonctionne avec `A` doit continuer à fonctionner correctement avec `B`.

**Violation** (le classique carré/rectangle) :

```python
class Rectangle:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur

    def surface(self):
        return self.largeur * self.hauteur

class Carre(Rectangle):
    def __setattr__(self, nom, valeur):
        super().__setattr__(nom, valeur)
        if nom == "largeur":
            super().__setattr__("hauteur", valeur)
        if nom == "hauteur":
            super().__setattr__("largeur", valeur)

def verifier_surface(rectangle: Rectangle):
    rectangle.largeur = 5
    rectangle.hauteur = 4
    assert rectangle.surface() == 20  # Échoue pour un Carré !

verifier_surface(Carre(3, 3))  # AssertionError : 25 ≠ 20
```

**Respecté** :

```python
from abc import ABC, abstractmethod

class Forme(ABC):
    @abstractmethod
    def surface(self) -> float:
        pass

class Rectangle(Forme):
    def __init__(self, largeur: float, hauteur: float):
        self.largeur = largeur
        self.hauteur = hauteur

    def surface(self) -> float:
        return self.largeur * self.hauteur

class Carre(Forme):
    def __init__(self, cote: float):
        self.cote = cote

    def surface(self) -> float:
        return self.cote ** 2

# Rectangle et Carré respectent le contrat de Forme sans se contraindre mutuellement
```

**Règles concrètes du LSP** :
- Les préconditions des méthodes surchargées ne doivent pas être plus strictes
- Les postconditions ne doivent pas être plus faibles
- Les invariants de la classe de base doivent être préservés
- Les méthodes ne doivent pas lever d'exceptions non prévues par la classe de base

## I — Interface Segregation Principle

**Les clients ne doivent pas être forcés de dépendre d'interfaces qu'ils n'utilisent pas.**

Préférer plusieurs interfaces spécialisées plutôt qu'une seule interface généraliste.

**Violation** :

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def manger(self): pass

    @abstractmethod
    def voler(self): pass  # Tous les animaux ne volent pas !

    @abstractmethod
    def nager(self): pass  # Tous les animaux ne nagent pas !

class Chien(Animal):
    def manger(self): print("Le chien mange")
    def voler(self): raise NotImplementedError  # Obligé d'implémenter
    def nager(self): print("Le chien nage")
```

**Respecté** :

```python
from abc import ABC, abstractmethod

class Mangeable(ABC):
    @abstractmethod
    def manger(self): pass

class Volant(ABC):
    @abstractmethod
    def voler(self): pass

class Nageant(ABC):
    @abstractmethod
    def nager(self): pass

class Chien(Mangeable, Nageant):
    def manger(self): print("Le chien mange")
    def nager(self): print("Le chien nage")

class Aigle(Mangeable, Volant):
    def manger(self): print("L'aigle mange")
    def voler(self): print("L'aigle vole")

class Canard(Mangeable, Volant, Nageant):
    def manger(self): print("Le canard mange")
    def voler(self): print("Le canard vole")
    def nager(self): print("Le canard nage")
```

## D — Dependency Inversion Principle

**Les modules de haut niveau ne doivent pas dépendre des modules de bas niveau. Les deux doivent dépendre d'abstractions.**

**Les abstractions ne doivent pas dépendre des détails. Les détails doivent dépendre des abstractions.**

**Violation** :

```python
class MySQLDatabase:  # Détail concret
    def sauvegarder(self, utilisateur): pass

class ServiceUtilisateur:  # Module de haut niveau
    def __init__(self):
        self.bdd = MySQLDatabase()  # Dépendance directe sur un détail

    def creer(self, utilisateur):
        self.bdd.sauvegarder(utilisateur)
        # Impossible de changer la BDD sans modifier ServiceUtilisateur
```

**Respecté** :

```python
from abc import ABC, abstractmethod

class DepotUtilisateur(ABC):  # Abstraction
    @abstractmethod
    def sauvegarder(self, utilisateur) -> None: pass
    @abstractmethod
    def trouver_par_id(self, id: int): pass

class MySQLDepot(DepotUtilisateur):  # Détail concret
    def sauvegarder(self, utilisateur) -> None:
        print(f"MySQL: sauvegarde {utilisateur}")
    def trouver_par_id(self, id: int):
        return {"id": id}

class PostgreSQLDepot(DepotUtilisateur):  # Autre détail concret
    def sauvegarder(self, utilisateur) -> None:
        print(f"PostgreSQL: sauvegarde {utilisateur}")
    def trouver_par_id(self, id: int):
        return {"id": id}

class ServiceUtilisateur:  # Dépend de l'abstraction
    def __init__(self, depot: DepotUtilisateur):  # Injection de dépendance
        self.depot = depot

    def creer(self, utilisateur):
        self.depot.sauvegarder(utilisateur)

# Utilisation
service = ServiceUtilisateur(MySQLDepot())
service = ServiceUtilisateur(PostgreSQLDepot())  # Changement sans modifier ServiceUtilisateur
```

## Autres principes importants

### DRY — Don't Repeat Yourself

Chaque connaissance dans un système ne doit avoir qu'une seule représentation faisant autorité. La duplication de code est une dette technique : corriger un bug dans une copie oblige à retrouver toutes les autres.

### KISS — Keep It Simple, Stupid

La simplicité est une vertu. Éviter les abstractions prématurées et les solutions sur-engineerées.

### YAGNI — You Aren't Gonna Need It

N'implémenter que ce dont on a besoin maintenant. Ajouter des fonctionnalités "au cas où" alourdit le code sans valeur.

### Loi de Déméter

Un objet ne devrait appeler que les méthodes de :
- Lui-même
- Ses attributs directs
- Les objets passés en paramètre
- Les objets qu'il crée

```python
# Violation : "train wreck"
utilisateur.commande.paiement.carte.numero

# Respecté : délégation
utilisateur.obtenir_numero_carte()
```

### Code smells courants

| Smell | Description | Solution |
|---|---|---|
| Long Method | Méthode trop longue | Extraire des sous-méthodes |
| Large Class | Classe qui fait trop | Séparer les responsabilités (SRP) |
| Long Parameter List | Trop de paramètres | Regrouper en objet |
| Duplicate Code | Même code en plusieurs endroits | Extraire (DRY) |
| Feature Envy | Méthode qui utilise surtout les données d'une autre classe | Déplacer la méthode |
| Shotgun Surgery | Un changement nécessite des modifications partout | Regrouper (SRP) |
| Inappropriate Intimacy | Deux classes trop couplées | Réduire le couplage |
| Magic Numbers | Valeurs littérales sans contexte | Nommer les constantes |
