---
title: "Bash — Scripts et Automatisation"
domain: "Applied Sciences"
subdomain: "Computer Science > Languages > Bash"
tags: [sciences-appliquées, informatique, bash]
date: "2026-03-20"
---

# Bash — Scripts et Automatisation

Un script Bash est un fichier texte exécutable contenant une séquence de commandes shell. L'automatisation de tâches répétitives (sauvegardes, déploiements, maintenance) est le principal cas d'usage.

### Structure d'un Script

```bash
#!/usr/bin/env bash
# Shebang : indique l'interpréteur à utiliser

set -euo pipefail
# -e : quitter si une commande échoue
# -u : erreur si variable non définie
# -o pipefail : le pipe échoue si une commande du pipe échoue

# Variables
NOM="monde"
echo "Bonjour, $NOM"
```

**Permissions d'exécution** :
```bash
chmod +x mon_script.sh
./mon_script.sh
```

### Variables et Paramètres

```bash
# Variables
MA_VAR="valeur"
echo "$MA_VAR"           # Bonne pratique : toujours entre guillemets
echo "${MA_VAR}_suffixe" # Délimiter le nom avec {}

# Variables spéciales
echo "$0"   # Nom du script
echo "$1"   # Premier argument
echo "$@"   # Tous les arguments (séparés)
echo "$#"   # Nombre d'arguments
echo "$?"   # Code de retour de la dernière commande
echo "$$"   # PID du shell courant

# Substitution de commande
DATE=$(date +%Y-%m-%d)
NB_LIGNES=$(wc -l < fichier.txt)

# Valeur par défaut
NOM="${1:-Martin}"  # Si $1 vide, utiliser "Martin"
```

### Conditions

```bash
# if / elif / else
if [[ -f "/etc/passwd" ]]; then
    echo "Fichier existe"
elif [[ -d "/etc/passwd" ]]; then
    echo "C'est un dossier"
else
    echo "N'existe pas"
fi

# Tests courants
[[ -f fichier ]]   # Fichier régulier existe
[[ -d dossier ]]   # Dossier existe
[[ -z "$var" ]]    # Variable vide
[[ -n "$var" ]]    # Variable non vide
[[ "$a" == "$b" ]] # Égalité de chaînes
[[ "$a" -eq "$b" ]] # Égalité numérique
[[ "$a" -gt "$b" ]] # a > b (numérique)

# Opérateurs logiques
[[ condition1 && condition2 ]]
[[ condition1 || condition2 ]]
```

### Boucles

```bash
# for sur liste
for fruit in pomme banane cerise; do
    echo "$fruit"
done

# for C-style
for ((i=0; i<10; i++)); do
    echo "$i"
done

# for sur fichiers
for fichier in /var/log/*.log; do
    echo "Traitement : $fichier"
done

# while
compteur=0
while [[ $compteur -lt 5 ]]; do
    echo "Compteur : $compteur"
    ((compteur++))
done

# Lire un fichier ligne par ligne
while IFS= read -r ligne; do
    echo "$ligne"
done < fichier.txt
```

### Fonctions

```bash
# Définition
saluer() {
    local prenom="$1"    # local : variable locale à la fonction
    local message="Bonjour, $prenom"
    echo "$message"
    return 0             # 0 = succès, 1-255 = erreur
}

# Appel
saluer "Martin"
resultat=$(saluer "Alice")  # Capturer la sortie
```

### Gestion des Erreurs

```bash
# Quitter avec message d'erreur
erreur() {
    echo "ERREUR : $1" >&2  # >&2 : rediriger vers stderr
    exit 1
}

# Vérifier code de retour
commande_risquee || erreur "La commande a échoué"

# Trap : exécuter une action sur signal ou erreur
nettoyer() {
    rm -f /tmp/fichier_temp_$$
    echo "Nettoyage effectué"
}
trap nettoyer EXIT          # Exécuter nettoyer à la sortie
trap 'erreur "Ligne $LINENO"' ERR  # Afficher la ligne d'erreur
```

### Exemples Pratiques

**Sauvegarde automatique**
```bash
#!/usr/bin/env bash
set -euo pipefail

SOURCE="/home/user/documents"
DEST="/backup"
DATE=$(date +%Y-%m-%d_%H-%M)
ARCHIVE="$DEST/backup_$DATE.tar.gz"

mkdir -p "$DEST"
tar -czf "$ARCHIVE" "$SOURCE"
echo "Sauvegarde créée : $ARCHIVE"

# Supprimer sauvegardes de plus de 30 jours
find "$DEST" -name "backup_*.tar.gz" -mtime +30 -delete
```

**Surveillance d'un service**
```bash
#!/usr/bin/env bash
SERVICE="nginx"

if ! systemctl is-active --quiet "$SERVICE"; then
    echo "$(date) : $SERVICE arrêté, redémarrage..." >> /var/log/watchdog.log
    systemctl restart "$SERVICE"
fi
```

**Traitement de fichiers CSV**
```bash
#!/usr/bin/env bash
# Traiter chaque ligne d'un CSV (skip header)
tail -n +2 données.csv | while IFS=',' read -r nom age ville; do
    echo "Nom: $nom | Age: $age | Ville: $ville"
done
```

### Bonnes Pratiques

| Pratique | Raison |
|---|---|
| `#!/usr/bin/env bash` | Portable (chemin de bash variable selon OS) |
| `set -euo pipefail` | Fail fast — évite les erreurs silencieuses |
| `"$var"` avec guillemets | Évite le word splitting et la glob expansion |
| `local` dans les fonctions | Évite la pollution des variables globales |
| `[[ ]]` plutôt que `[ ]` | Plus robuste, supporte `&&`, `||`, regex |
| Noms en MAJUSCULES pour constantes | Convention lisibilité |
| `mktemp` pour fichiers temporaires | Évite les conflits de noms |
| Commentaires au-dessus des blocs | Documenter l'intention, pas l'évidence |
