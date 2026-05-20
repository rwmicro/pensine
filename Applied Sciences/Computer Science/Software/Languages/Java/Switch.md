---
title: "Switch"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java]
date: "2026-02-16"
---

# Switch

L'instruction `switch` est une structure de contrôle qui sélectionne un bloc à exécuter selon la valeur d'une expression. Java a considérablement amélioré `switch` au fil des versions.

## Switch classique (Java 1-13)

```java
int jour = 3;
String nom;

switch (jour) {
    case 1:
        nom = "Lundi";
        break;
    case 2:
        nom = "Mardi";
        break;
    case 3:
    case 4:
        nom = "Mercredi ou Jeudi";  // plusieurs cases pour la même branche
        break;
    case 5:
        nom = "Vendredi";
        break;
    case 6:
    case 7:
        nom = "Week-end";
        break;
    default:
        nom = "Invalide";
        break;  // optionnel en dernier mais bonne pratique
}
```

### Fall-through

Sans `break`, l'exécution "tombe" dans le case suivant.

```java
int mois = 4;
int nbJours;

switch (mois) {
    case 1: case 3: case 5: case 7:
    case 8: case 10: case 12:
        nbJours = 31;
        break;
    case 4: case 6: case 9: case 11:
        nbJours = 30;
        break;
    case 2:
        nbJours = 28;  // simplification
        break;
    default:
        nbJours = -1;
}
```

Le fall-through est parfois intentionnel (regrouper plusieurs cases) mais souvent source de bugs quand le `break` est oublié par inadvertance.

## Switch sur String (Java 7+)

```java
String commande = "start";

switch (commande) {
    case "start":
        System.out.println("Démarrage...");
        break;
    case "stop":
        System.out.println("Arrêt...");
        break;
    case "restart":
        System.out.println("Redémarrage...");
        break;
    default:
        System.out.println("Commande inconnue : " + commande);
}
```

La comparaison est sensible à la casse et utilise `equals()` en interne. `commande` ne doit pas être null (NullPointerException sinon).

## Switch sur enum

```java
public enum Direction { NORD, SUD, EST, OUEST }

Direction dir = Direction.NORD;

switch (dir) {
    case NORD:
        System.out.println("Cap au nord");
        break;
    case SUD:
        System.out.println("Cap au sud");
        break;
    case EST:
        System.out.println("Cap à l'est");
        break;
    case OUEST:
        System.out.println("Cap à l'ouest");
        break;
}
```

Avantage : le compilateur avertit si tous les membres de l'enum ne sont pas traités (avec certains outils d'analyse statique). Ne pas mettre `Direction.NORD` dans les cases, juste `NORD`.

## Switch Expression (Java 14+ stable)

Java 14 introduit les **switch expressions** qui retournent une valeur et utilisent la syntaxe flèche (`->`). Plus concis, pas de fall-through, pas de `break`.

```java
int jour = 3;

// Switch expression avec arrow syntax
String nom = switch (jour) {
    case 1 -> "Lundi";
    case 2 -> "Mardi";
    case 3 -> "Mercredi";
    case 4 -> "Jeudi";
    case 5 -> "Vendredi";
    case 6, 7 -> "Week-end";     // plusieurs valeurs avec virgule
    default -> "Invalide";
};
System.out.println(nom);  // "Mercredi"
```

### Avec yield (blocs multi-lignes)

Quand une branche nécessite plusieurs instructions, utiliser `yield` pour retourner la valeur.

```java
int code = 404;

String description = switch (code) {
    case 200 -> "OK";
    case 201 -> "Created";
    case 400 -> "Bad Request";
    case 401 -> "Unauthorized";
    case 404 -> {
        System.out.println("Ressource non trouvée !");
        yield "Not Found";  // yield remplace return dans un switch expression
    }
    case 500 -> "Internal Server Error";
    default -> {
        System.out.printf("Code inconnu : %d%n", code);
        yield "Unknown";
    }
};
```

### Switch expression comme argument

```java
// Directement dans un appel de méthode
System.out.println(switch (jour) {
    case 1 -> "Lundi";
    case 2 -> "Mardi";
    default -> "Autre";
});

// Dans une affectation conditionnelle
double tarif = switch (categorie) {
    case "VIP"      -> 0.0;
    case "PREMIUM"  -> 0.1;
    case "STANDARD" -> 0.2;
    default         -> 0.25;
};
```

## Pattern Matching dans switch (Java 21+)

Java 21 ajoute le pattern matching pour les types dans `switch`. Combiné avec les classes scellées (sealed), il permet un dispatch exhaustif et type-safe.

```java
// Pattern matching sur le type
Object obj = "Bonjour";

String resultat = switch (obj) {
    case Integer i -> "Entier : " + i;
    case String s  -> "Chaîne de " + s.length() + " caractères";
    case null      -> "Valeur nulle";
    default        -> "Type inconnu : " + obj.getClass().getSimpleName();
};
```

### Avec classes scellées

```java
sealed interface Forme permits Cercle, Rectangle, Triangle {}
record Cercle(double rayon) implements Forme {}
record Rectangle(double largeur, double hauteur) implements Forme {}
record Triangle(double base, double hauteur) implements Forme {}

double surface(Forme f) {
    return switch (f) {
        case Cercle c       -> Math.PI * c.rayon() * c.rayon();
        case Rectangle r    -> r.largeur() * r.hauteur();
        case Triangle t     -> 0.5 * t.base() * t.hauteur();
        // Pas de default nécessaire : le compilateur sait que tous les cas sont couverts
    };
}
```

### Avec guards (when)

```java
int n = 42;

String categorie = switch (n) {
    case int i when i < 0  -> "Négatif";
    case int i when i == 0 -> "Zéro";
    case int i when i < 10 -> "Petit";
    case int i when i < 100 -> "Moyen";
    default                 -> "Grand";
};
```

## Switch sur types primitifs et wrappers supportés

| Supporté | Non supporté |
|---|---|
| `byte`, `short`, `char`, `int` | `long`, `float`, `double`, `boolean` |
| `Byte`, `Short`, `Character`, `Integer` (wrappers) | `Long`, `Float`, `Double` |
| `String` (depuis Java 7) | |
| `enum` | |
| Tout objet (pattern matching, Java 21+) | |

## Comparaison if-else vs switch vs switch expression

```java
// if-else : toujours applicable, mais verbeux pour de nombreuses valeurs
if (jour == 1)      nom = "Lundi";
else if (jour == 2) nom = "Mardi";
else                nom = "Autre";

// switch classique : lisible pour de nombreux cas, mais risque de fall-through
switch (jour) {
    case 1: nom = "Lundi"; break;
    case 2: nom = "Mardi"; break;
    default: nom = "Autre";
}

// switch expression (Java 14+) : concis, pas de fall-through, retourne une valeur
String nom = switch (jour) {
    case 1 -> "Lundi";
    case 2 -> "Mardi";
    default -> "Autre";
};
```

**Règle** : préférer le switch expression (Java 14+) quand on retourne une valeur selon un discriminant. Utiliser if-else pour des conditions complexes avec intervalles ou plusieurs variables.
