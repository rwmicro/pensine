---
title: "Exercices : auditer l'exposition de son propre labo"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Exposition Internet"
tags: [sciences-appliquées, informatique, sécurité, exposition, exercices, labo, purple-team]
date: "2026-11-25"
prerequis: ["[[Surveillance continue de l'exposition]]"]
---

# Exercices : auditer l'exposition de son propre labo

Lire comment fonctionne masscan n'apprend pas à interpréter un scan qui contredit sa propre configuration. Ces exercices reprennent tout le parcours sur un terrain où l'on a le droit de tout faire : son propre serveur et des machines virtuelles locales. Ils sont pensés pour un labo typique, un serveur qui héberge quelques applications web derrière un reverse proxy, publie certaines d'entre elles sur internet, en réserve d'autres au VPN, garde ses bases de données sur des réseaux internes et fait tourner quelques outils de détection (Wazuh, Suricata, Fail2Ban ou équivalents). Adaptez les commandes à votre propre installation.

Chaque exercice donne un objectif, la démarche et ce qu'on doit en retirer. Notez vos résultats au fur et à mesure dans une fiche d'audit, décrite à la fin.

> [!warning] Le cadre avant tout
> Tous les scans actifs portent uniquement sur des adresses et des domaines qui vous appartiennent. N'écrivez jamais un préfixe plus large que votre propre adresse, et vérifiez les conditions de votre hébergeur avant de scanner, même vos propres machines. Les recherches passives (crt.sh, Shodan) restent permises sur tout domaine, mais ce parcours ne les applique qu'au vôtre.

## Exercice 0 : poser le périmètre et la sortie de secours

**Objectif.** Écrire noir sur blanc ce qu'on a le droit de toucher, et prévoir le cas où l'on se bloque soi-même.

Créez un fichier `perimetre.txt` qui contient vos noms de domaine et vos adresses publiques, et seulement eux. Tous les outils de la suite liront leurs cibles dans ce fichier, jamais dans une saisie à la main : une faute de frappe dans un préfixe est la manière la plus courante de scanner quelqu'un d'autre. Prévoyez ensuite comment reprendre la main si Fail2Ban ou le pare-feu bannit l'adresse depuis laquelle vous scannez : console de l'hébergeur, accès par le VPN depuis une autre connexion, ou adresse de scan ajoutée temporairement à la liste blanche.

**À retenir.** Un audit professionnel commence par les mêmes deux documents : le périmètre autorisé et les règles d'engagement, décrits dans [[Test d'intrusion web — cadre et ROE]].

## Exercice 1 : l'inventaire attendu

**Objectif.** Écrire ce que vous croyez exposer, avant de regarder.

Sans lancer aucun outil externe, dressez le tableau de vos services à partir de la configuration : fichiers compose, vhosts du reverse proxy, zone DNS, règles du pare-feu. Pour chacun, notez l'exposition attendue : public, VPN uniquement, interne. Complétez ensuite avec les commandes locales vues dans [[Inventaire des actifs]] (`podman ps` ou `docker ps`, `ss -tulpn`).

| Service | Nom | Port | Exposition attendue |
|---|---|---|---|
| Site statique | `www.example.org` | 443 via tunnel ou proxy | Public |
| Galerie de photos | aucun nom public | 2283 | VPN uniquement |
| Base de données | aucun | 5432 | Interne aux conteneurs |
| SSH | aucun | 22 | VPN uniquement |

**À retenir.** Comparez `ss -tulpn` aux fichiers compose : tout service en écoute sur `0.0.0.0` qui n'apparaît pas dans votre tableau est une première trouvaille.

## Exercice 2 : ce que le monde sait déjà

**Objectif.** Mesurer ce qu'un inconnu apprend de vous sans envoyer un paquet.

1. Listez les noms publiés dans les journaux de certificats pour votre domaine (commande crt.sh de [[Empreinte externe]]). Repérez les noms que vous croyiez internes.
2. Lancez `subfinder -d votre-domaine -all -silent` et comparez avec la liste précédente.
3. Interrogez InternetDB sur chacune de vos adresses publiques : `curl -s https://internetdb.shodan.io/VOTRE_IP | jq`.
4. Si vous utilisez un CDN ou un tunnel, cherchez votre nom de domaine dans Censys et Shodan : l'une de vos adresses réelles apparaît-elle ?

**À retenir.** Chaque nom trouvé dans les certificats mais absent de votre tableau est un écart. Une adresse réelle associée à votre nom alors qu'elle devait rester cachée est une fuite d'origine, à traiter selon [[Réduire son exposition]].

## Exercice 3 : le scan externe, puis le scan par le VPN

**Objectif.** Comparer ce que voit internet et ce que voit le VPN.

Depuis une machine extérieure (une petite machine louée ailleurs, ou un ordinateur sur le partage de connexion d'un téléphone, VPN coupé), scannez tous les ports de votre adresse publique. Sur une seule adresse, nmap suffit :

```bash
nmap -Pn -p- --min-rate 500 -oA externe VOTRE_IP
```

Recommencez la même commande **connecté au VPN**, vers l'adresse du serveur dans le VPN, en enregistrant dans `-oA vpn`. Comparez les deux listes de ports.

**À retenir.** Tout port ouvert dans le scan externe doit être « public » dans votre tableau. Un port « VPN uniquement » visible de l'extérieur est l'anomalie la plus grave de tout l'audit. Si un conteneur publie un port alors que le pare-feu est fermé, vous venez de reproduire le piège décrit dans [[Réduire son exposition]].

## Exercice 4 : identifier, et tester le site par défaut

**Objectif.** Savoir ce qui répond, et ce qui répond quand on ne donne pas de nom.

1. Passez vos noms publics dans httpx : `httpx -l noms.txt -sc -title -td -server -cdn -silent`.
2. Interrogez votre adresse publique **sans nom** : `curl -skI https://VOTRE_IP/`. Le reverse proxy doit renvoyer une erreur, pas l'un de vos services.
3. Forcez un nom réservé au VPN sur l'adresse publique : `curl -skI --resolve galerie.example.org:443:VOTRE_IP https://galerie.example.org/`. Ce service doit rester inaccessible.
4. Regardez l'en-tête `Server` : affiche-t-il une version ?

**À retenir.** Le test 3 vérifie que la restriction au VPN repose sur l'adresse source et pas seulement sur l'absence de nom public : un attaquant qui devine le nom ne doit rien obtenir.

## Exercice 5 : chercher les expositions connues

**Objectif.** Lancer nuclei proprement et trier ses résultats.

```bash
nuclei -l urls.txt -as -etags intrusive,dos,fuzz -severity low,medium,high,critical -rl 20 -o nuclei.txt
```

Pour chaque résultat, vérifiez à la main s'il est réel (requête `curl`, version du paquet installé), puis classez-le avec la grille de [[Expositions et failles connues]] : exploité ou non, exposé ou non, critique ou non. Écrivez ensuite un modèle nuclei personnel pour une erreur que vous ne voulez jamais voir revenir chez vous (un fichier `.env`, un dossier `.git`, une page d'administration).

**À retenir.** Attendez-vous surtout à des résultats d'information (en-têtes manquants, technologies détectées). Une absence de résultat critique ne signifie pas absence de faille, seulement absence de faille connue de la bibliothèque.

## Exercice 6 : votre SOC vous a-t-il vu ?

**Objectif.** Retourner l'exercice : vérifier que vos outils de détection ont repéré vos propres scans.

Pendant les exercices 3 à 5, vous avez scanné votre serveur comme le ferait un attaquant. Consultez maintenant vos outils de détection : quelles alertes Suricata a-t-il levées sur le scan de ports ? Fail2Ban a-t-il banni votre adresse, et au bout de combien de requêtes ? Le pare-feu applicatif (ModSecurity, par exemple) a-t-il bloqué des requêtes de nuclei ? Wazuh a-t-il remonté ces événements, et avec quel niveau ?

**À retenir.** Un scan complet de tous les ports qui ne déclenche aucune alerte signale un angle mort de détection. C'est l'esprit du *purple teaming* : l'attaque sert à éprouver la défense.

## Exercice 7 : corriger, puis revérifier

**Objectif.** Fermer chaque écart et prouver qu'il est fermé.

Pour chaque écart des exercices précédents, appliquez la mesure la plus forte possible dans la hiérarchie supprimer, restreindre, durcir, masquer. Puis relancez le scan externe de l'exercice 3 et comparez au premier. Un écart n'est clos que lorsque le scan externe le confirme.

## Exercice 8 : automatiser et mesurer le délai de détection

**Objectif.** Mettre en place la surveillance continue, puis la tester par une erreur volontaire.

1. Installez le script de [[Surveillance continue de l'exposition]] sur une machine extérieure, planifiez-le chaque nuit et laissez-le tourner une première fois pour constituer la référence.
2. Commettez une erreur contrôlée et inoffensive : publiez un conteneur de test sur toutes les interfaces, par exemple `podman run -d --rm --name test-exposition -p 8081:80 docker.io/library/nginx:alpine`.
3. Notez l'heure, puis l'heure de la notification.
4. Arrêtez le conteneur (`podman stop test-exposition`) et vérifiez que le passage suivant le classe parmi les services disparus.

**À retenir.** Le délai mesuré est la durée pendant laquelle une vraie erreur resterait exposée sans que vous le sachiez. Si elle dépasse une journée, augmentez la fréquence.

## Exercice 9 : s'entraîner à grande vitesse, en local

**Objectif.** Pratiquer masscan, ZMap et nuclei sur des cibles vulnérables, sans jamais toucher internet.

Les débits élevés et les modèles qui détectent de vraies failles ne s'essaient pas sur un serveur en production. Créez un réseau de conteneurs local et lancez-y quelques services, dont une version volontairement vulnérable. Le seul port publié l'est sur l'interface locale `127.0.0.1` : rien n'est joignable depuis un autre ordinateur.

```bash
podman network create labo
podman run -d --rm --name vieux-grafana --network labo -p 127.0.0.1:3000:3000 docker.io/grafana/grafana:8.3.0
podman run -d --rm --name web --network labo docker.io/library/nginx:alpine
```

Grafana 8.3.0 est touché par CVE-2021-43798, une traversée de répertoires qui permet de lire des fichiers du serveur sans authentification. Lancez nuclei sur `http://127.0.0.1:3000` avec `-tags cve` et vérifiez qu'il la détecte. Entraînez-vous ensuite à masscan avec un débit élevé sur la plage du réseau `labo` (`podman network inspect labo` la donne), depuis un conteneur rattaché à ce réseau. Supprimez tout à la fin (`podman stop vieux-grafana web && podman network rm labo`).

**À retenir.** C'est ici, et seulement ici, qu'on pousse les outils à fond. Observez combien de ports masscan manque quand on augmente trop le débit.

## La fiche d'audit

Consignez les résultats dans un tableau unique, versionné à côté de votre configuration. Il devient la mémoire de vos audits et la référence du suivant.

| Date | Constat | Source | Exposition attendue | Gravité | Mesure | Vérifié par |
|---|---|---|---|---|---|---|
| Jour 1 | Nom interne dans les certificats | crt.sh | Interne | Faible | Certificat d'une autorité interne | crt.sh, plus aucun nouveau nom |
| Jour 1 | Port de la galerie ouvert sur internet | Scan externe | VPN uniquement | Critique | Port publié sur `127.0.0.1` seulement | Scan externe : port fermé |

> [!quiz] Pourquoi les cibles des outils doivent-elles venir d'un fichier de périmètre plutôt que d'une saisie à la main ?
> Parce qu'une faute de frappe dans une adresse ou un préfixe (un `/16` au lieu d'un `/26`) suffit à scanner des machines qui ne vous appartiennent pas. Un fichier relu une fois et réutilisé partout supprime ce risque.

> [!quiz] Lors de l'exercice 3, le port 2283, prévu « VPN uniquement », apparaît ouvert dans le scan externe. Que faire en premier ?
> Le restreindre immédiatement, par exemple en publiant le port uniquement sur l'interface locale ou sur l'interface du VPN, puis relancer le scan externe pour confirmer la fermeture. Il faut ensuite chercher pourquoi le pare-feu ne l'a pas bloqué (règles ajoutées par les conteneurs) et vérifier dans les journaux si des connexions extérieures ont déjà eu lieu.

> [!quiz] Lesquelles de ces actions restent permises sur un domaine qui ne vous appartient pas ?
> - [x] Consulter les journaux de certificats sur crt.sh.
>   Ce sont des données publiques ; on ne touche aucun système de la cible.
> - [ ] Lancer nuclei pour vérifier qu'il n'a pas de faille.
>   C'est un test actif, parfois intrusif, qui exige une autorisation.
> - [ ] Scanner ses ports avec masscan à faible débit.
>   Le débit ne change rien : un scan actif sans autorisation sort du cadre, et la plupart des hébergeurs l'interdisent.

> [!ordre] Les étapes d'un audit d'exposition, dans l'ordre
> 1. Poser le périmètre autorisé
> 2. Écrire l'inventaire attendu
> 3. Rassembler les traces passives
> 4. Scanner depuis l'extérieur
> 5. Identifier les services
> 6. Chercher les expositions et les failles
> 7. Corriger et revérifier
> 8. Automatiser la surveillance
