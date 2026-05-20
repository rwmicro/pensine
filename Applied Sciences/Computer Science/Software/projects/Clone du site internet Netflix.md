---
title: "Clone du site internet Netflix"
domain: "Applied Sciences"
subdomain: "Computer Science > projects"
tags: [sciences-appliquées, informatique]
date: "2025-02-15"
---

Ce projet avait pour but de refaire le site Netflix afin de m’entraîner de manière plus ludique que de suivre un cours en ligne.

![](sources/images/netflix.jpg)


Je me suis dans un premier temps demandé comment est-ce que je pourrais développer mes connaissances en du framework javscript Next.js d'une manière plus ludique que de suivre un cours en ligne. L'idée m'ait alors venue de refaire un site web. Je me suis donc mis au défis de refaire le site Netflix à ma manière. 

### Structuration du site

Avant de commencer à developer le site, une étape de structuration est nécessaire. Après reflection, j'en ai conclu que le site aura besoin de 3 pages principales. Une page **Accueil**, une page **Films** et un page **Series**. A cela s'ajoute deux pages suplémentaires qui serons generées automatiquement en fonction du nom du film ou de la serie.


![](sources/images/structure.jpg)

On retrouve ici tout l'intéret de NextJS. La possibilité de génerer des pages dynamiques en fonction d'une donnée passée en paramètre, dans notre cas le nom enfin plus particulièrement sont identifiant.

### Développement
Ma manière de travailler à était de coder chaque élement visuel. J'ai donc naturellement commencé par la page d'accueil. Cette page est composée de deux éléments principaux, un entête et une bar de recherche. L'entête sera lui commun à toutes les pages.

![Capture d'écran de la page d'accueil](sources/images/home.jpg)

La bar de recherche donne à l'utilisateur la possibilité de chercher n'importe quel film ou série présent sur le site et d'accéder directement à sa page correspondante.

### Les pages films et series
La page Films et Series sont composés d’énormément d'éléments. Premièrement, la présentation d'un film ou d'une série phare du moment, l'utilisateur à la possibilité de lire directement le film ou la série via le bouton *Lecture*.


![Capture d'écran de la page Films](sources/images/movies.jpg)

Juste en dessous se trouve tous les films et series disponibles sur le site. Il suffit juste à l'utilisateur de cliquer sur une des affiches et il sera renvoyé directement sur la page correspondante. Un fichier JSON contenant toutes les informations nécessaires sera alors chargé en fonction de l'identifiant du film ou de la série cliqué une page statique sera alors générée en fonction de toutes ces informations.


![Détails du film 'Mon Voisin Totoro'](sources/images/totoro.jpg)
### Ce que j'en retiens
Ce projet m'aura apporté beaucoup, non seulement sur l'aspect front-end et la connaissance de Next.js en soit mais aussi sur l'aspect back-end et les processus d'optimisations mis en places afin qu'une page web s'affiche le plus rapidement possible.
