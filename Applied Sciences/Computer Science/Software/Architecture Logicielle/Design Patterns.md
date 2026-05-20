---
title: "Design Patterns"
domain: "Applied Sciences"
subdomain: "Computer Science > Architecture Logicielle"
tags: [sciences-appliquées, informatique]
date: "2026-02-25"
---

# Design Patterns

Les design patterns (patrons de conception) sont des solutions réutilisables à des problèmes récurrents de conception logicielle. Formalisés par le Gang of Four (GoF) en 1994, ils se divisent en trois catégories : créationnels, structurels et comportementaux.

Un pattern n'est pas du code copier-coller, mais un modèle conceptuel qu'on adapte au contexte.

## Patterns Créationnels

Traitent de la création d'objets, en découplant le système du comment et du qui crée les objets.

### Singleton

Garantit qu'une classe n'a qu'une seule instance et fournit un point d'accès global.

```python
class Configuration:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.parametres = {}
        return cls._instance

# Toujours la même instance
config1 = Configuration()
config2 = Configuration()
assert config1 is config2  # True

# Thread-safe avec threading.Lock pour les contextes multithreadés
```

Quand l'utiliser : registre de configuration, pool de connexions, gestionnaire de logs. Anti-pattern si surutilisé (rend le code difficile à tester).

### Factory Method

Définit une interface pour créer un objet, mais laisse les sous-classes décider quelle classe instancier.

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def envoyer(self, message: str) -> None:
        pass

class NotificationEmail(Notification):
    def envoyer(self, message: str) -> None:
        print(f"Email : {message}")

class NotificationSMS(Notification):
    def envoyer(self, message: str) -> None:
        print(f"SMS : {message}")

class NotificationFactory:
    @staticmethod
    def creer(type_notif: str) -> Notification:
        if type_notif == "email":
            return NotificationEmail()
        elif type_notif == "sms":
            return NotificationSMS()
        raise ValueError(f"Type inconnu : {type_notif}")

notif = NotificationFactory.creer("email")
notif.envoyer("Bienvenue !")
```

### Builder

Construit des objets complexes étape par étape. Utile quand un constructeur aurait trop de paramètres.

```python
class RequeteSQL:
    def __init__(self):
        self._table = ""
        self._colonnes = []
        self._conditions = []
        self._limite = None

    def de(self, table: str) -> "RequeteSQL":
        self._table = table
        return self

    def selectionner(self, *colonnes) -> "RequeteSQL":
        self._colonnes.extend(colonnes)
        return self

    def ou(self, condition: str) -> "RequeteSQL":
        self._conditions.append(condition)
        return self

    def limiter(self, n: int) -> "RequeteSQL":
        self._limite = n
        return self

    def construire(self) -> str:
        cols = ", ".join(self._colonnes) if self._colonnes else "*"
        sql = f"SELECT {cols} FROM {self._table}"
        if self._conditions:
            sql += " WHERE " + " AND ".join(self._conditions)
        if self._limite:
            sql += f" LIMIT {self._limite}"
        return sql

requete = (RequeteSQL()
    .de("clients")
    .selectionner("nom", "email")
    .ou("solde > 1000")
    .limiter(10)
    .construire())
# SELECT nom, email FROM clients WHERE solde > 1000 LIMIT 10
```

### Abstract Factory

Fabrique de fabriques. Crée des familles d'objets liés sans spécifier leurs classes concrètes.

```python
from abc import ABC, abstractmethod

class UIFactory(ABC):
    @abstractmethod
    def creer_bouton(self): pass
    @abstractmethod
    def creer_input(self): pass

class WindowsFactory(UIFactory):
    def creer_bouton(self): return BoutonWindows()
    def creer_input(self): return InputWindows()

class MacFactory(UIFactory):
    def creer_bouton(self): return BoutonMac()
    def creer_input(self): return InputMac()

# Le code client ne connaît que UIFactory
def creer_interface(factory: UIFactory):
    bouton = factory.creer_bouton()
    input_field = factory.creer_input()
    return bouton, input_field
```

### Prototype

Clone des objets existants plutôt que de les recréer from scratch.

```python
import copy

class ConfigServeur:
    def __init__(self, host, port, timeout, options=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.options = options or {}

    def clone(self):
        return copy.deepcopy(self)

config_prod = ConfigServeur("prod.example.com", 443, 30, {"ssl": True})
config_test = config_prod.clone()
config_test.host = "test.example.com"
config_test.port = 8080
```

## Patterns Structurels

Traitent de la composition d'objets et de classes.

### Adapter

Permet à des interfaces incompatibles de fonctionner ensemble.

```python
# Interface attendue par le code existant
class LoggerModerne:
    def log(self, niveau: str, message: str): pass

# Bibliothèque tierce avec une interface différente
class AncienLogger:
    def ecrire_info(self, msg): print(f"INFO: {msg}")
    def ecrire_erreur(self, msg): print(f"ERREUR: {msg}")

# Adapter qui traduit l'interface
class AdapterLogger(LoggerModerne):
    def __init__(self, ancien_logger: AncienLogger):
        self._logger = ancien_logger

    def log(self, niveau: str, message: str):
        if niveau == "INFO":
            self._logger.ecrire_info(message)
        elif niveau == "ERROR":
            self._logger.ecrire_erreur(message)

logger = AdapterLogger(AncienLogger())
logger.log("INFO", "Application démarrée")
```

### Decorator

Ajoute dynamiquement des responsabilités à un objet sans modifier sa classe.

```python
from abc import ABC, abstractmethod
from functools import wraps

# Décorateur Python natif
def mesurer_temps(func):
    import time
    @wraps(func)
    def wrapper(*args, **kwargs):
        debut = time.time()
        resultat = func(*args, **kwargs)
        print(f"{func.__name__} : {time.time() - debut:.3f}s")
        return resultat
    return wrapper

def mise_en_cache(func):
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@mesurer_temps
@mise_en_cache
def calcul_lourd(n):
    return sum(range(n))
```

### Facade

Fournit une interface simplifiée à un sous-système complexe.

```python
class ServiceEmail:
    def envoyer(self, destinataire, sujet, corps): pass

class ServiceSMS:
    def envoyer(self, numero, message): pass

class ServicePush:
    def envoyer(self, token, titre, corps): pass

class ServiceNotification:
    """Facade qui simplifie l'envoi multi-canal."""
    def __init__(self):
        self._email = ServiceEmail()
        self._sms = ServiceSMS()
        self._push = ServicePush()

    def notifier_utilisateur(self, utilisateur, message):
        if utilisateur.email:
            self._email.envoyer(utilisateur.email, "Notification", message)
        if utilisateur.telephone:
            self._sms.envoyer(utilisateur.telephone, message)
        if utilisateur.token_push:
            self._push.envoyer(utilisateur.token_push, "Notif", message)
```

### Proxy

Fournit un substitut ou un représentant d'un autre objet pour contrôler l'accès.

```python
class ServiceDonnees:
    def obtenir(self, id_ressource: str) -> dict:
        print(f"Requête BDD pour {id_ressource}")
        return {"id": id_ressource, "data": "..."}

class ProxyCache:
    def __init__(self, service: ServiceDonnees):
        self._service = service
        self._cache = {}

    def obtenir(self, id_ressource: str) -> dict:
        if id_ressource not in self._cache:
            self._cache[id_ressource] = self._service.obtenir(id_ressource)
        return self._cache[id_ressource]

service = ProxyCache(ServiceDonnees())
service.obtenir("user:1")  # Requête BDD
service.obtenir("user:1")  # Depuis le cache
```

### Composite

Permet de traiter uniformément des objets individuels et des compositions d'objets.

```python
from abc import ABC, abstractmethod

class Composant(ABC):
    @abstractmethod
    def afficher(self, indent=0): pass

class Fichier(Composant):
    def __init__(self, nom):
        self.nom = nom

    def afficher(self, indent=0):
        print(" " * indent + self.nom)

class Dossier(Composant):
    def __init__(self, nom):
        self.nom = nom
        self.enfants = []

    def ajouter(self, composant: Composant):
        self.enfants.append(composant)

    def afficher(self, indent=0):
        print(" " * indent + f"[{self.nom}]")
        for enfant in self.enfants:
            enfant.afficher(indent + 2)

racine = Dossier("projet")
racine.ajouter(Fichier("README.md"))
src = Dossier("src")
src.ajouter(Fichier("main.py"))
src.ajouter(Fichier("utils.py"))
racine.ajouter(src)
racine.afficher()
```

## Patterns Comportementaux

Traitent des algorithmes et des responsabilités entre les objets.

### Observer

Définit une dépendance un-à-plusieurs : quand un objet change d'état, tous ses observateurs sont notifiés automatiquement.

```python
from typing import List

class Observable:
    def __init__(self):
        self._observateurs: List = []

    def abonner(self, observateur):
        self._observateurs.append(observateur)

    def notifier(self, evenement, donnees=None):
        for obs in self._observateurs:
            obs.update(evenement, donnees)

class StockProduit(Observable):
    def __init__(self):
        super().__init__()
        self._stock = {}

    def modifier_stock(self, produit, quantite):
        self._stock[produit] = quantite
        self.notifier("stock_change", {"produit": produit, "quantite": quantite})

class AlerteStock:
    def update(self, evenement, donnees):
        if evenement == "stock_change" and donnees["quantite"] < 10:
            print(f"ALERTE : stock faible pour {donnees['produit']}")

stock = StockProduit()
stock.abonner(AlerteStock())
stock.modifier_stock("laptop", 5)  # ALERTE : stock faible
```

### Strategy

Définit une famille d'algorithmes interchangeables.

```python
from typing import Protocol

class StrategieCalculPrix(Protocol):
    def calculer(self, prix_base: float) -> float: ...

class PrixNormal:
    def calculer(self, prix_base: float) -> float:
        return prix_base

class PrixSolde:
    def __init__(self, reduction: float):
        self.reduction = reduction
    def calculer(self, prix_base: float) -> float:
        return prix_base * (1 - self.reduction)

class PrixMembre:
    def calculer(self, prix_base: float) -> float:
        return prix_base * 0.9

class Produit:
    def __init__(self, nom: str, prix_base: float):
        self.nom = nom
        self.prix_base = prix_base
        self.strategie: StrategieCalculPrix = PrixNormal()

    def afficher_prix(self):
        return self.strategie.calculer(self.prix_base)

produit = Produit("Laptop", 1000)
produit.strategie = PrixSolde(0.20)
print(produit.afficher_prix())  # 800.0
```

### Command

Encapsule une requête en objet, permettant de paramétrer, mettre en file, annuler des opérations.

```python
from abc import ABC, abstractmethod
from typing import List

class Commande(ABC):
    @abstractmethod
    def executer(self): pass
    @abstractmethod
    def annuler(self): pass

class TexteEditeur:
    def __init__(self):
        self.texte = ""
        self.historique: List[Commande] = []

    def executer_commande(self, commande: Commande):
        commande.executer()
        self.historique.append(commande)

    def annuler(self):
        if self.historique:
            self.historique.pop().annuler()

class CommandeInserer(Commande):
    def __init__(self, editeur: TexteEditeur, texte: str, position: int):
        self.editeur = editeur
        self.texte = texte
        self.position = position

    def executer(self):
        t = self.editeur.texte
        self.editeur.texte = t[:self.position] + self.texte + t[self.position:]

    def annuler(self):
        t = self.editeur.texte
        self.editeur.texte = t[:self.position] + t[self.position + len(self.texte):]
```

### Template Method

Définit le squelette d'un algorithme, en laissant les sous-classes implémenter certaines étapes.

```python
from abc import ABC, abstractmethod

class GenerateurRapport(ABC):
    def generer(self):  # Template method
        donnees = self.collecter_donnees()
        traitees = self.traiter_donnees(donnees)
        self.formater_sortie(traitees)

    @abstractmethod
    def collecter_donnees(self): pass

    @abstractmethod
    def traiter_donnees(self, donnees): pass

    def formater_sortie(self, donnees):  # Comportement par défaut
        print(donnees)

class RapportCSV(GenerateurRapport):
    def collecter_donnees(self): return [{"nom": "Alice", "score": 95}]
    def traiter_donnees(self, donnees): return donnees
    def formater_sortie(self, donnees):
        print("nom,score")
        for d in donnees:
            print(f"{d['nom']},{d['score']}")
```

### State

Permet à un objet de modifier son comportement quand son état interne change.

```python
from abc import ABC, abstractmethod

class EtatCommande(ABC):
    @abstractmethod
    def payer(self, commande): pass
    @abstractmethod
    def expedier(self, commande): pass
    @abstractmethod
    def livrer(self, commande): pass

class EtatEnAttente(EtatCommande):
    def payer(self, commande):
        print("Paiement accepté")
        commande.etat = EtatPayee()
    def expedier(self, commande): print("Impossible : pas encore payée")
    def livrer(self, commande): print("Impossible : pas encore payée")

class EtatPayee(EtatCommande):
    def payer(self, commande): print("Déjà payée")
    def expedier(self, commande):
        print("Commande expédiée")
        commande.etat = EtatExpediee()
    def livrer(self, commande): print("Impossible : pas encore expédiée")

class Commande:
    def __init__(self):
        self.etat = EtatEnAttente()

    def payer(self): self.etat.payer(self)
    def expedier(self): self.etat.expedier(self)
    def livrer(self): self.etat.livrer(self)
```

## Implémentations Java

### Factory Method en Java

```java
// Interface produit
public interface Enemy {
    void update(float delta);
}

// Produits concrets
public class OrcEnemy implements Enemy {
    @Override
    public void update(float delta) { /* déplacer l'orc */ }
}

// Factory abstraite
public abstract class EnemyFactory {
    public abstract Enemy createEnemy();  // Factory Method

    public Enemy spawnEnemy() {
        Enemy enemy = createEnemy();
        System.out.println("Spawned: " + enemy.getClass().getSimpleName());
        return enemy;
    }
}

// Factory concrète
public class OrcFactory extends EnemyFactory {
    @Override
    public Enemy createEnemy() { return new OrcEnemy(); }
}
```

### Observer Pattern en Java

```java
import java.util.ArrayList;
import java.util.List;

// Interface observateur
interface Observer {
    void update(String message);
}

// Sujet observable
class NewsAgency {
    private List<Observer> observers = new ArrayList<>();
    private String news;

    public void addObserver(Observer o) { observers.add(o); }
    public void removeObserver(Observer o) { observers.remove(o); }

    public void setNews(String news) {
        this.news = news;
        notifyObservers(news);
    }

    private void notifyObservers(String message) {
        for (Observer o : observers) { o.update(message); }
    }
}

// Observateur concret
class NewsChannel implements Observer {
    private String name;
    public NewsChannel(String name) { this.name = name; }

    @Override
    public void update(String message) {
        System.out.println(name + " reçoit : " + message);
    }
}
```

### Command Pattern en Java

```java
// Interface commande
public interface Command {
    void execute();
}

// Récepteur
public class Light {
    public void turnOn() { System.out.println("Lumière allumée"); }
    public void turnOff() { System.out.println("Lumière éteinte"); }
}

// Commande concrète
public class LightOnCommand implements Command {
    private Light light;
    public LightOnCommand(Light light) { this.light = light; }

    @Override
    public void execute() { light.turnOn(); }
}

// Invocateur
public class RemoteControl {
    private Command command;
    public void setCommand(Command command) { this.command = command; }
    public void pressButton() { command.execute(); }
}
```

### Object Pool Pattern

L'Object Pool réutilise des objets coûteux à créer plutôt que de les instancier et détruire constamment.

```java
import java.util.LinkedList;
import java.util.Queue;

public class ObjectPool<T> {
    private Queue<T> pool = new LinkedList<>();
    private final int maxSize;

    public ObjectPool(int maxSize) { this.maxSize = maxSize; }

    public T acquire() {
        return pool.isEmpty() ? null : pool.poll();
    }

    public void release(T obj) {
        if (pool.size() < maxSize) {
            pool.offer(obj);
        }
    }
}
```

Cas d'usage : connexions BDD, threads, objets graphiques (sprites), connexions réseau.

## Patterns de développement de jeux vidéo

Les patterns GoF s'appliquent directement au développement de jeux, mais certains patterns spécifiques au domaine sont également très répandus.

### Game Loop

Le Game Loop est le pattern central de tout jeu : une boucle qui tourne continuellement, traitant les entrées, mettant à jour l'état du monde et affichant le rendu.

```java
// Implémentation LibGDX (Java game framework)
public class MonJeu extends ApplicationAdapter {

    // Singleton pour l'accès global au jeu
    private static MonJeu instance;
    public static MonJeu getInstance() { return instance; }

    private SpriteBatch batch;
    private float tempsTotal = 0;

    @Override
    public void create() {
        instance = this;
        batch = new SpriteBatch();
        // Initialisation des ressources
    }

    // Méthode appelée à chaque frame (≈60 fois/seconde)
    @Override
    public void render() {
        float delta = Gdx.graphics.getDeltaTime();  // Temps depuis la dernière frame
        tempsTotal += delta;

        // 1. Traiter les entrées
        if (Gdx.input.isKeyPressed(Input.Keys.ESCAPE)) {
            Gdx.app.exit();
        }

        // 2. Mettre à jour la logique du jeu
        mettreAJour(delta);

        // 3. Afficher le rendu
        Gdx.gl.glClearColor(0, 0, 0, 1);
        Gdx.gl.glClear(GL20.GL_COLOR_BUFFER_BIT);
        afficher();
    }

    private void mettreAJour(float delta) {
        // Déplacer les entités, vérifier les collisions, gérer l'IA...
    }

    private void afficher() {
        batch.begin();
        // Dessiner sprites, textures...
        batch.end();
    }

    @Override
    public void dispose() {
        batch.dispose();
    }
}
```

**Game Loop avec pas de temps fixe** (pour la physique déterministe) :

```java
// Découpler la logique de jeu (pas de temps fixe) du rendu (variable)
private float accumulateur = 0;
private static final float PAS_PHYSIQUE = 1f / 60f;  // 60 Hz

@Override
public void render() {
    float delta = Math.min(Gdx.graphics.getDeltaTime(), 0.25f);  // Limiter le delta
    accumulateur += delta;

    // Plusieurs mises à jour physiques si nécessaire
    while (accumulateur >= PAS_PHYSIQUE) {
        mettreAJourPhysique(PAS_PHYSIQUE);
        accumulateur -= PAS_PHYSIQUE;
    }

    // Interpolation pour le rendu fluide
    float alpha = accumulateur / PAS_PHYSIQUE;
    afficher(alpha);
}
```

### Entity-Component System (ECS)

Architecture alternative à l'héritage de classes. Les entités sont de simples identifiants ; les composants sont des données ; les systèmes contiennent la logique.

```java
// Composants (données uniquement)
class Position { float x, y; }
class Vitesse  { float vx, vy; }
class Sprite   { Texture texture; }
class Sante    { int pv, pvMax; }

// Système (logique)
class SystemeMouvement {
    void mettreAJour(List<Entite> entites, float delta) {
        for (Entite e : entites) {
            if (e.a(Position.class) && e.a(Vitesse.class)) {
                Position pos = e.get(Position.class);
                Vitesse  vit = e.get(Vitesse.class);
                pos.x += vit.vx * delta;
                pos.y += vit.vy * delta;
            }
        }
    }
}
```

**Avantages ECS vs héritage classique** :
- Pas de hiérarchie rigide de classes (Personnage → Guerrier → GuerrierMagicien...)
- Composition flexible (ajouter/retirer des composants à l'exécution)
- Cache-friendly pour les performances (données regroupées par type)
- Exemples de frameworks ECS : Ashley (LibGDX), EnTT (C++), Unity DOTS

### State Machine dans les jeux

```java
// Gestion des états d'un personnage
enum EtatPersonnage { IDLE, MARCHE, COURSE, SAUT, ATTAQUE, MORT }

class Personnage {
    private EtatPersonnage etat = EtatPersonnage.IDLE;

    void mettreAJour(float delta) {
        switch (etat) {
            case IDLE:
                if (Gdx.input.isKeyPressed(Input.Keys.LEFT)) {
                    etat = EtatPersonnage.MARCHE;
                }
                if (Gdx.input.isKeyJustPressed(Input.Keys.SPACE)) {
                    etat = EtatPersonnage.SAUT;
                }
                break;
            case MARCHE:
                deplacer(delta);
                if (!Gdx.input.isKeyPressed(Input.Keys.LEFT) &&
                    !Gdx.input.isKeyPressed(Input.Keys.RIGHT)) {
                    etat = EtatPersonnage.IDLE;
                }
                break;
            // ...
        }
    }
}
```

## Choisir un pattern

| Problème | Pattern |
|---|---|
| Une seule instance globale | Singleton |
| Créer des objets sans connaître leur type exact | Factory Method |
| Construire des objets complexes étape par étape | Builder |
| Familles d'objets liés | Abstract Factory |
| Interfaces incompatibles | Adapter |
| Ajouter des fonctionnalités sans héritage | Decorator |
| Simplifier un sous-système complexe | Facade |
| Notifier plusieurs objets d'un changement | Observer |
| Algorithmes interchangeables | Strategy |
| Undo/redo, files de tâches | Command |
| Comportement qui change selon l'état | State |
| Squelette d'algorithme avec variations | Template Method |
| Réutiliser des objets coûteux | Object Pool |
| Boucle principale d'un jeu | Game Loop |
| Entités composables sans héritage | Entity-Component System |
