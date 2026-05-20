---
title: "Scanner"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Java"
tags: [sciences-appliquées, informatique, java]
date: "2026-02-16"
---

# Scanner

`Scanner` est une classe de `java.util` qui permet d'analyser (parser) du texte provenant de différentes sources : entrée standard (`System.in`), fichiers, chaînes de caractères, flux. Elle découpe l'entrée en tokens selon un délimiteur (espace blanc par défaut) et fournit des méthodes de conversion vers les types primitifs.

```java
import java.util.Scanner;
```

## Sources d'entrée

```java
// Depuis l'entrée standard (clavier)
Scanner stdin = new Scanner(System.in);

// Depuis un fichier
import java.io.File;
import java.io.FileNotFoundException;
Scanner fichier = new Scanner(new File("donnees.txt"));

// Depuis une chaîne de caractères
Scanner chaine = new Scanner("42 3.14 hello");

// Depuis un InputStream quelconque
Scanner flux = new Scanner(System.in, "UTF-8");
```

## Méthodes principales

| Méthode | Type retourné | Description |
|---|---|---|
| `nextLine()` | `String` | Lit la ligne entière jusqu'au retour chariot |
| `next()` | `String` | Lit le prochain token (séparé par un délimiteur) |
| `nextInt()` | `int` | Lit le prochain token comme entier |
| `nextLong()` | `long` | Lit le prochain token comme long |
| `nextDouble()` | `double` | Lit le prochain token comme double |
| `nextFloat()` | `float` | Lit le prochain token comme float |
| `nextBoolean()` | `boolean` | Lit `true` ou `false` (insensible à la casse) |
| `nextByte()` | `byte` | Lit le prochain token comme byte |
| `nextShort()` | `short` | Lit le prochain token comme short |
| `hasNext()` | `boolean` | Vérifie s'il reste un token |
| `hasNextLine()` | `boolean` | Vérifie s'il reste une ligne |
| `hasNextInt()` | `boolean` | Vérifie si le prochain token est un entier |
| `hasNextDouble()` | `boolean` | Vérifie si le prochain token est un double |
| `skip(pattern)` | `Scanner` | Ignore le texte correspondant au pattern |
| `reset()` | `Scanner` | Réinitialise le délimiteur et la locale |

## Lecture depuis l'entrée standard

```java
import java.util.Scanner;

public class LectureStdin {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.print("Entrez votre prénom : ");
        String prenom = sc.nextLine();

        System.out.print("Entrez votre âge : ");
        int age = sc.nextInt();

        System.out.print("Entrez votre taille (en m) : ");
        double taille = sc.nextDouble();

        System.out.printf("Bonjour %s, %d ans, %.2f m%n", prenom, age, taille);

        sc.close();
    }
}
```

### Piège classique : nextInt() et nextLine()

`nextInt()` consomme le nombre mais laisse le caractère de fin de ligne (`\n`) dans le buffer. Le `nextLine()` suivant lira immédiatement cette ligne vide.

```java
Scanner sc = new Scanner(System.in);
int age = sc.nextInt();
sc.nextLine();            // consommer le \n résiduel
String nom = sc.nextLine(); // lit correctement la ligne suivante
```

## Lecture depuis un fichier

```java
import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class LectureFichier {
    public static void main(String[] args) {
        try {
            Scanner sc = new Scanner(new File("notes.txt"));
            while (sc.hasNextLine()) {
                String ligne = sc.nextLine();
                System.out.println(ligne);
            }
            sc.close();
        } catch (FileNotFoundException e) {
            System.err.println("Fichier introuvable : " + e.getMessage());
        }
    }
}
```

## Lecture d'un fichier CSV simple

```java
import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class LectureCSV {
    public static void main(String[] args) throws FileNotFoundException {
        Scanner sc = new Scanner(new File("etudiants.csv"));
        sc.useDelimiter("[,\n\r]+"); // délimiteur : virgule ou saut de ligne

        while (sc.hasNext()) {
            String nom   = sc.next();
            int    note  = sc.nextInt();
            System.out.printf("%-20s : %d%n", nom, note);
        }
        sc.close();
    }
}
```

## Délimiteurs personnalisés

```java
Scanner sc = new Scanner("rouge:vert:bleu");
sc.useDelimiter(":");
while (sc.hasNext()) {
    System.out.println(sc.next()); // rouge, puis vert, puis bleu
}

// Remettre le délimiteur par défaut (espace blanc)
sc.reset();
```

`useDelimiter` accepte une expression régulière, ce qui permet des cas complexes comme `[;,\t]+` pour des fichiers séparés par virgule, point-virgule ou tabulation.

## Gestion des exceptions

### InputMismatchException

Levée lorsque le token lu ne correspond pas au type demandé (par exemple, appeler `nextInt()` sur `"abc"`).

```java
Scanner sc = new Scanner(System.in);
try {
    int n = sc.nextInt();
} catch (java.util.InputMismatchException e) {
    System.err.println("Entrée invalide, un entier était attendu.");
    sc.next(); // consommer le token invalide pour ne pas boucler
}
```

### NoSuchElementException

Levée lorsque l'on demande un token alors qu'il n'en reste plus. Toujours vérifier avec `hasNext()` ou `hasNextLine()` avant d'appeler une méthode de lecture.

```java
Scanner sc = new Scanner("42");
sc.nextInt();           // ok
if (sc.hasNextInt()) {  // false → on n'appelle pas nextInt()
    sc.nextInt();
}
```

### IllegalStateException

Levée lorsqu'on utilise un scanner déjà fermé.

## Fermeture du scanner

Il est nécessaire de fermer le scanner pour libérer les ressources associées (surtout pour les fichiers). Le pattern `try-with-resources` est la méthode recommandée :

```java
try (Scanner sc = new Scanner(new File("data.txt"))) {
    while (sc.hasNextLine()) {
        System.out.println(sc.nextLine());
    }
} catch (FileNotFoundException e) {
    e.printStackTrace();
}
// sc.close() est appelé automatiquement
```

Attention : fermer un `Scanner` sur `System.in` ferme également le flux `System.in`, le rendant inutilisable pour le reste du programme.

## Comparaison Scanner vs BufferedReader vs Console

| Critère | `Scanner` | `BufferedReader` | `Console` |
|---|---|---|---|
| Import | `java.util` | `java.io` | `java.io` |
| Parsing intégré | Oui (nextInt, etc.) | Non (à faire manuellement) | Non |
| Performance | Modérée (regex) | Haute (buffer simple) | Modérée |
| Lecture de fichier | Oui | Oui | Non |
| Lecture mot par mot | Oui | Non natif | Non |
| Lecture sécurisée (mot de passe) | Non | Non | Oui (`readPassword()`) |
| Thread-safe | Non | Non | Oui |
| Disponible en IDE/redirect | Oui | Oui | Parfois non (retourne null) |

`BufferedReader` est préféré dans les contextes où la performance est critique (lecture de gros fichiers) car il n'applique pas de regex sur chaque token. `Console` est utile pour lire des mots de passe masqués en mode interactif mais n'est pas disponible dans tous les environnements.

## Exemple complet : validation en boucle

```java
import java.util.Scanner;

public class Validation {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int nombre = -1;

        while (true) {
            System.out.print("Entrez un entier entre 1 et 100 : ");
            if (sc.hasNextInt()) {
                nombre = sc.nextInt();
                if (nombre >= 1 && nombre <= 100) break;
                System.out.println("Hors intervalle, réessayez.");
            } else {
                System.out.println("Ce n'est pas un entier.");
                sc.next(); // consommer le token invalide
            }
        }

        System.out.println("Valeur acceptée : " + nombre);
        sc.close();
    }
}
```
