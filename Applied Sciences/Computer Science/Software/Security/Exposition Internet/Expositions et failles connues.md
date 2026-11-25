---
title: "Expositions et failles connues : nuclei et priorisation"
domain: "Applied Sciences"
subdomain: "Computer Science > Security > Exposition Internet"
tags: [sciences-appliquées, informatique, sécurité, exposition, nuclei, cve, kev, epss, priorisation]
date: "2026-11-25"
prerequis: ["[[Identification des services]]"]
---

# Expositions et failles connues : nuclei et priorisation

Une fois les services identifiés, la question devient : lesquels présentent un risque réel, et dans quel ordre les traiter ? Un premier passage d'outil sur un périmètre même modeste renvoie facilement des dizaines de résultats, dont beaucoup sont des faux positifs ou des détails sans conséquence. Le danger n'est pas de manquer d'alertes, mais de s'y noyer et de laisser la seule qui compte au milieu des autres.

Cette note distingue d'abord deux familles de problèmes, les mauvaises configurations et les vulnérabilités logicielles, puis montre comment nuclei les détecte et comment décider quoi corriger en premier. Le cycle complet de gestion des vulnérabilités (CVE, CWE, CVSS en détail) est traité dans [[Gestion des Vulnérabilités]].

## Exposition ou vulnérabilité

Une **vulnérabilité** est un défaut du logiciel lui-même, généralement catalogué sous un identifiant CVE : une version de Confluence permet l'exécution de code à distance, une version d'OpenSSL lit au-delà d'un tampon. On la corrige en mettant à jour.

Une **exposition** est un défaut d'usage : le logiciel fonctionne comme prévu, mais il ne devrait pas être accessible ainsi. Une base Elasticsearch ouverte sans authentification, un tableau de bord Grafana avec le mot de passe par défaut, un dossier `.git` publié avec le site, un fichier `.env` qui contient des clés d'API, une interface d'administration de routeur joignable depuis internet. Aucune mise à jour ne corrige cela : il faut changer la configuration ou fermer l'accès.

Les deux familles sont aussi dangereuses l'une que l'autre, et la seconde est souvent la plus exploitée, parce qu'elle ne demande aucune compétence : il suffit de se connecter.

## nuclei : des tests décrits en YAML

**nuclei**, de ProjectDiscovery, est un moteur qui exécute des **modèles** (*templates*) écrits en YAML. Chaque modèle décrit une requête à envoyer et la condition qui signale un problème. La bibliothèque communautaire en compte plusieurs milliers, classés par étiquettes : `cve`, `exposure`, `misconfig`, `panel`, `default-login`, `takeover`. Son atout est la vitesse de réaction : un modèle pour une faille médiatisée paraît souvent dans les jours qui suivent sa publication. La note [[Nuclei]] détaille l'outil ; on s'en tient ici à son usage pour mesurer l'exposition.

```bash
nuclei -ut                                   # met à jour les modèles
nuclei -l web.txt -tags exposure,misconfig,panel,default-login,takeover \
       -severity medium,high,critical -rl 50 -o expositions.txt
nuclei -l web.txt -tags cve -severity high,critical -rl 50 -o cve.txt
```

`-rl 50` limite le débit à cinquante requêtes par seconde : même sur son propre serveur, il vaut mieux ne pas déclencher le pare-feu applicatif ni saturer une petite machine. L'option `-as` (scan automatique) détecte d'abord les technologies présentes et n'exécute que les modèles pertinents, ce qui réduit beaucoup le bruit.

> [!warning] Certains modèles ne sont pas anodins
> Une partie des modèles envoie de vraies charges d'exploitation, teste des identifiants par défaut ou provoque des requêtes coûteuses. Les étiquettes `intrusive`, `dos` et `fuzz` signalent les plus agressifs ; on peut les exclure avec `-etags intrusive,dos,fuzz`. Utiliser nuclei sur une cible sans autorisation n'est plus de la reconnaissance : c'est une tentative d'intrusion.

Écrire son propre modèle est simple, et c'est le meilleur moyen de surveiller une erreur qu'on ne veut jamais voir revenir. Celui-ci signale un dossier `.git` publié par erreur :

```yaml
id: git-config-expose-labo

info:
  name: Dossier .git publié
  author: moi
  severity: medium
  tags: exposure,git

http:
  - method: GET
    path:
      - "{{BaseURL}}/.git/config"
    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200
      - type: word
        words:
          - "[core]"
```

Les deux conditions sont liées par `and` : un code 200 seul ne suffit pas, car beaucoup de sites renvoient leur page d'accueil avec un code 200 pour n'importe quel chemin. Exiger la présence de `[core]`, qui ouvre tout fichier `.git/config`, élimine ces faux positifs.

## Faux positifs et vrais négatifs

Un résultat de scanner est une hypothèse. Les faux positifs viennent surtout de deux sources. La première est la détection par version : un modèle qui se fonde sur le numéro annoncé ignore les correctifs rétroportés par la distribution, comme on l'a vu pour OpenSSH dans [[Identification des services]]. La seconde est une condition trop lâche, comme le code 200 ci-dessus. À l'inverse, l'absence de résultat ne prouve pas l'absence de faille : aucun modèle n'existe pour une faille encore inconnue, et un service caché derrière une authentification n'est testé qu'en surface.

On vérifie donc chaque résultat important à la main, par une requête `curl` ou en consultant le paquet installé, avant de le traiter.

## Prioriser : au-delà du score CVSS

Le score **CVSS** mesure la gravité intrinsèque d'une faille, de 0 à 10. Il ne dit pas si quelqu'un l'exploite. Or, chaque année, des dizaines de milliers de CVE sont publiées et seule une petite fraction est exploitée en pratique. Deux sources répondent à cette question.

- Le catalogue **KEV** (*Known Exploited Vulnerabilities*) de la CISA, ouvert en novembre 2021, liste les failles dont l'exploitation réelle est avérée. Une faille au KEV sur un service exposé se traite immédiatement, quel que soit son score.
- L'**EPSS** (*Exploit Prediction Scoring System*), publié par le FIRST, estime pour chaque CVE la probabilité qu'elle soit exploitée dans les trente jours, à partir de données observées.

```bash
# Une CVE est-elle au KEV ?
curl -s https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json \
  | jq '.vulnerabilities[] | select(.cveID=="CVE-2023-22515") | {cveID, vulnerabilityName, dateAdded}'

# Son score EPSS
curl -s 'https://api.first.org/data/v1/epss?cve=CVE-2023-22515' | jq '.data[0]'
```

À ces deux signaux s'ajoutent les attributs de l'inventaire vus dans [[Inventaire des actifs]] : l'exposition (internet ou VPN) et la criticité de l'actif. On obtient une priorisation qui tient en quelques questions, dans l'esprit de la méthode SSVC promue par la CISA : la faille est-elle exploitée ? Le service est-il joignable depuis internet ? Que perdrait-on s'il était compromis ?

| Résultat | CVSS | Exploité (KEV) | Exposition | Priorité |
|---|---|---|---|---|
| Confluence vulnérable à CVE-2023-22515 | 10,0 | Oui | Internet | Immédiate, avant la fin de la journée |
| Dossier `.git` publié sur le site | Sans CVE | Exploitation triviale | Internet | Immédiate : fermer l'accès, puis vérifier les secrets du dépôt |
| Faille de gravité 9,8 dans un service | 9,8 | Non, EPSS faible | VPN uniquement | Planifiée, au prochain cycle de mises à jour |
| Version de nginx affichée dans l'en-tête | Sans CVE | Non | Internet | Faible : à corriger par hygiène |

Le troisième cas illustre la leçon principale : un score de 9,8 sur un service que seul le VPN atteint pèse moins qu'une mauvaise configuration banale sur internet. Réduire l'exposition fait souvent baisser le risque plus vite que corriger les failles une à une, ce qui mène à la note suivante, [[Réduire son exposition]].

> [!quiz] Quelle différence entre une exposition et une vulnérabilité ?
> Une vulnérabilité est un défaut du logiciel (souvent une CVE), qu'on corrige par une mise à jour. Une exposition est un défaut d'usage : le logiciel fonctionne comme prévu mais ne devrait pas être accessible ainsi (base sans authentification, mot de passe par défaut, fichier `.env` publié). On la corrige en changeant la configuration ou l'accès.

> [!quiz] Pourquoi un modèle nuclei qui ne vérifie qu'un code 200 produit-il des faux positifs ?
> Parce que beaucoup de sites renvoient une page (souvent l'accueil) avec un code 200 pour n'importe quel chemin. Il faut une seconde condition sur le contenu, propre au fichier recherché.

> [!quiz] Une faille notée 7,5 est au catalogue KEV, une autre notée 9,8 a un EPSS très faible. Les deux touchent des services exposés sur internet. Laquelle traiter d'abord ?
> - [x] Celle notée 7,5, parce qu'elle est exploitée.
>   Le KEV atteste une exploitation réelle ; le CVSS ne mesure que la gravité théorique.
> - [ ] Celle notée 9,8, parce que son score est plus élevé.
>   Un score élevé sans exploitation observée est moins urgent qu'une faille activement exploitée.
> - [ ] Aucune, tant qu'aucune alerte n'a été levée.
>   Attendre une alerte, c'est attendre la compromission.

> [!quiz] Que fait l'option `-etags intrusive,dos,fuzz` de nuclei ?
> Elle exclut les modèles qui portent ces étiquettes, c'est-à-dire ceux qui envoient des charges d'exploitation, peuvent dégrader le service ou génèrent un grand nombre de requêtes.
