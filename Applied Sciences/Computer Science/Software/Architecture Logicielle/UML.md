---
title: "UML — Unified Modeling Language"
domain: "Applied Sciences"
subdomain: "Computer Science > Architecture Logicielle"
tags: [sciences-appliquées, informatique, uml, architecture, modélisation]
date: "2026-04-07"
---

# UML — Unified Modeling Language

UML (Unified Modeling Language) est un langage de modélisation standardisé (OMG, 1997) permettant de représenter graphiquement la structure et le comportement d'un système logiciel.

## Types de diagrammes UML

UML 2.5 propose 14 types de diagrammes regroupés en deux catégories :

| Catégorie | Diagrammes |
|-----------|-----------|
| Structure | Classe, Objet, Composant, Déploiement, Package, Profil, Structure composite |
| Comportement | Cas d'utilisation, Activité, Machine à états, Séquence, Communication, Interaction, Temps |

En pratique, les plus utilisés sont : **Classe**, **Cas d'utilisation**, **Séquence**, et **Activité**.

## Diagramme de classes

Le diagramme de classes est le plus fondamental en UML. Il représente la structure statique d'un système : les classes, leurs attributs, méthodes et relations.

### Notation d'une classe

```
┌─────────────────────────┐
│       NomClasse         │  ← Compartiment nom
├─────────────────────────┤
│ - attributPrivé: Type   │  ← Compartiment attributs
│ # attributProtégé: Type │
│ + attributPublic: Type  │
│ ∼ attributPackage: Type │
├─────────────────────────┤
│ + methodePublique(): void│  ← Compartiment méthodes
│ - methodePrivée(): Type  │
│ {abstract} maMethode()  │
└─────────────────────────┘
```

**Modificateurs d'accès** :
- `+` public
- `-` private
- `#` protected
- `~` package (default)

**Modificateurs de propriété** :
- `{abstract}` ou en italique — méthode abstraite
- `{static}` ou souligné — membre statique
- `{final}` — constante ou méthode non-redéfinissable

### Exemple en Java

```java
// Classe Java → diagramme de classes UML

public abstract class Forme {
    private String couleur;             // - couleur: String
    protected static int compteur = 0;  // # {static} compteur: int

    public Forme(String couleur) {
        this.couleur = couleur;
    }

    public abstract double calculerAire();    // {abstract} + calculerAire(): double
    public String getCouleur() { return couleur; }  // + getCouleur(): String
}

public class Cercle extends Forme {
    private double rayon;              // - rayon: double

    public Cercle(String couleur, double rayon) {
        super(couleur);
        this.rayon = rayon;
    }

    @Override
    public double calculerAire() {     // + calculerAire(): double
        return Math.PI * rayon * rayon;
    }
}
```

### Relations entre classes

#### Héritage (Generalization)

Flèche pleine avec tête triangulaire creuse. "est-un" (is-a).

```
Forme
  △
  │
Cercle
```

```java
public class Cercle extends Forme { ... }
```

#### Implémentation d'interface (Realization)

Flèche pointillée avec tête triangulaire creuse.

```
<<interface>>
   Dessinable
    △ (pointillé)
    │
  Cercle
```

```java
public class Cercle implements Dessinable { ... }
```

#### Association

Ligne simple. "a une relation avec". Peut avoir une multiplicité.

```
Client ────────── Commande
        1    0..*
```

| Notation | Signification |
|----------|--------------|
| `1` | Exactement 1 |
| `0..1` | 0 ou 1 (optionnel) |
| `*` ou `0..*` | 0 à plusieurs |
| `1..*` | 1 à plusieurs |
| `2..5` | De 2 à 5 |

#### Agrégation

Losange creux côté "tout". Relation "a" — le tout peut exister sans la partie.

```
Equipe ◇──────── Joueur
  1        0..*
```

La `Equipe` contient des `Joueur`s, mais un `Joueur` peut exister sans `Equipe`.

#### Composition

Losange plein côté "tout". Relation forte — la partie ne peut exister sans le tout.

```
Maison ◆──────── Chambre
  1         1..*
```

Si `Maison` est détruite, `Chambre` est également détruite.

```java
public class Maison {
    private List<Chambre> chambres = new ArrayList<>();  // Composition
}
```

#### Dépendance

Flèche pointillée. Relation faible et temporaire (utilise dans une méthode).

```
Commande - - - - → Facture
```

```java
public class Commande {
    public Facture genererFacture() {  // Commande dépend de Facture
        return new Facture(this);
    }
}
```

### Diagramme de classes complet — exemple e-commerce

```
┌─────────────┐         ┌──────────────┐
│   Client    │ 1   0..* │  Commande   │
│─────────────│──────────│──────────────│
│-nom: String │         │-date: Date   │
│-email: String│        │-statut: Enum │
│─────────────│         │──────────────│
│+passer()   │         │+calculerTotal│
└─────────────┘         └──────┬───────┘
                               │ 1
                               │
                         1..*  │
                  ┌────────────┴──────┐
                  │  LigneCommande    │
                  │───────────────────│
                  │-quantite: int     │
                  │-prixUnitaire: dec │
                  └────────────┬──────┘
                         *     │
                               │ 1
                  ┌────────────┴──────┐
                  │    Produit        │
                  │───────────────────│
                  │-nom: String       │
                  │-prix: Decimal     │
                  │-stock: int        │
                  └───────────────────┘
```

## Diagramme de séquence

Représente les interactions entre objets dans le temps. Les participants sont des colonnes, le temps s'écoule vers le bas.

```
Client      :Contrôleur    :Service      :Dépôt
  │               │              │           │
  │─passer()─────►│              │           │
  │               │─valider()───►│           │
  │               │              │─trouver()►│
  │               │              │◄──client──│
  │               │◄─client──────│           │
  │               │─sauvegarder()►           │
  │               │              │─save()───►│
  │               │              │◄──ok──────│
  │◄──commande────│              │           │
  │               │              │           │
```

**Éléments** :
- **Ligne de vie** : ligne verticale pointillée sous chaque participant
- **Message** : flèche horizontale avec label
- **Message de retour** : flèche pointillée
- **Activation** : rectangle sur la ligne de vie (période d'exécution)
- **Fragments** : `loop`, `alt` (if/else), `opt` (optionnel), `par` (parallèle)

## Diagramme de cas d'utilisation

Représente les fonctionnalités d'un système du point de vue de l'utilisateur.

```
              ┌─────────────────────────────┐
              │         Système e-commerce   │
              │                             │
Client ──────►│  (Parcourir catalogue)      │
              │  (Ajouter au panier)        │
              │  (Passer commande)          │──────► Admin
              │  (Suivre livraison)         │  │
              │                             │  └── (Gérer produits)
              └─────────────────────────────┘
```

**Acteur** : représenté par un bonhomme. Rôle externe qui interagit avec le système.

**Relations** :
- `<<include>>` : cas d'utilisation toujours inclus (comme un appel de fonction)
- `<<extend>>` : cas d'utilisation conditionnel, extension optionnelle

```
(Passer commande) ─ <<include>> ─► (S'authentifier)
(Passer commande) ◄ <<extend>> ── (Utiliser bon de réduction)
```

## Diagramme d'activité

Représente un flux de travail ou un algorithme. Similaire à un organigramme.

```
    ●  (Début)
    │
    ▼
 [Saisir données]
    │
    ▼
  ◇ Données valides ?
  │ Oui               │ Non
  ▼                   ▼
 [Traiter]         [Afficher erreur]
  │                   │
  └─────────┬─────────┘
            ▼
         [Fin]
            │
           ◉  (Fin)
```

**Éléments** :
- Nœud initial (cercle plein)
- Nœud final (cercle plein entouré)
- Action (rectangle arrondi)
- Décision (losange)
- Fork/Join (barre horizontale) pour la parallélisation
- Couloirs (swimlanes) pour assigner des actions à des acteurs

## Polymorphisme en UML et Java

### Polymorphisme par héritage (override)

```java
// Classe mère abstraite
public abstract class Animal {
    private String nom;

    public Animal(String nom) { this.nom = nom; }
    public String getNom() { return nom; }

    public abstract String parler();  // Méthode abstraite
}

// Sous-classes — chacune redéfinit parler()
public class Chien extends Animal {
    public Chien(String nom) { super(nom); }

    @Override
    public String parler() { return "Woof !"; }
}

public class Chat extends Animal {
    public Chat(String nom) { super(nom); }

    @Override
    public String parler() { return "Miaou !"; }
}

// Polymorphisme : référence de type Animal → comportement du type réel
List<Animal> animaux = List.of(new Chien("Rex"), new Chat("Félix"));
for (Animal a : animaux) {
    System.out.println(a.getNom() + " dit : " + a.parler());
    // Rex dit : Woof !
    // Félix dit : Miaou !
}
```

### Polymorphisme par interface

```java
public interface Payable {
    double calculerMontant();
    default String formatMontant() {
        return String.format("%.2f €", calculerMontant());
    }
}

public class Salaire implements Payable {
    private double montantMensuel;
    public double calculerMontant() { return montantMensuel; }
}

public class Facture implements Payable {
    private double[] lignes;
    public double calculerMontant() {
        return Arrays.stream(lignes).sum();
    }
}

// Un même code traite Salaire et Facture via l'interface
void traiterPaiement(Payable p) {
    System.out.println("À payer : " + p.formatMontant());
}
```

### Surcharge (overloading) — polymorphisme statique

```java
public class Calculatrice {
    public int additionner(int a, int b) { return a + b; }
    public double additionner(double a, double b) { return a + b; }
    public int additionner(int a, int b, int c) { return a + b + c; }
    // Résolution à la compilation selon le type des arguments
}
```

## Encapsulation

L'encapsulation cache l'implémentation interne et expose uniquement une interface publique. Elle protège l'intégrité de l'objet et permet de changer l'implémentation sans affecter les clients.

```java
public class CompteBancaire {
    private double solde;         // Attribut privé — non accessible de l'extérieur
    private List<String> historique = new ArrayList<>();

    public CompteBancaire(double soldeInitial) {
        if (soldeInitial < 0) throw new IllegalArgumentException("Solde initial négatif");
        this.solde = soldeInitial;
    }

    // Getter — accès en lecture
    public double getSolde() { return solde; }

    // Pas de setter pour solde — uniquement via deposer/retirer (invariants garantis)

    public void deposer(double montant) {
        if (montant <= 0) throw new IllegalArgumentException("Montant invalide");
        solde += montant;
        historique.add("Dépôt : +" + montant);
    }

    public void retirer(double montant) {
        if (montant <= 0) throw new IllegalArgumentException("Montant invalide");
        if (montant > solde) throw new IllegalStateException("Solde insuffisant");
        solde -= montant;
        historique.add("Retrait : -" + montant);
    }

    // Copie défensive pour éviter que le client modifie l'historique interne
    public List<String> getHistorique() {
        return Collections.unmodifiableList(historique);
    }
}
```

## Choisir le bon diagramme

| Question | Diagramme |
|----------|-----------|
| Quelle est la structure des données et des classes ? | Classe |
| Comment les objets interagissent-ils dans un scénario ? | Séquence |
| Quelles sont les fonctionnalités du système ? | Cas d'utilisation |
| Comment se déroule un processus ou algorithme ? | Activité |
| Dans quels états peut se trouver un objet ? | Machine à états |
| Comment sont déployés les composants ? | Déploiement |
