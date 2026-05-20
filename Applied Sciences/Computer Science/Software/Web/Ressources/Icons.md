---
title: "Icônes pour le Web"
domain: "Applied Sciences"
subdomain: "Computer Science > Web > Ressources"
tags: [sciences-appliquées, informatique, web]
date: "2025-01-15"
---

# Icônes pour le Web

Ressources pour trouver et intégrer des icônes dans vos projets web.


## Bibliothèques React

| Bibliothèque | Lien | Description |
|-------------|------|-------------|
| **React Icons** | [react-icons.github.io](https://react-icons.github.io/react-icons/) | Regroupe Font Awesome, Material, Feather, etc. en un seul package |
| **Lucide React** | [lucide.dev](https://lucide.dev/) | Icônes propres et modernes, léger |
| **Heroicons** | [heroicons.com](https://heroicons.com/) | Par les créateurs de Tailwind, SVG |

```bash
# Installation React Icons
npm install react-icons

# Utilisation
import { FaHome } from 'react-icons/fa'
<FaHome size={24} color="blue" />
```


## SVG & Collections générales

| Site | Description |
|------|-------------|
| [Isocons](https://www.isocons.app/) | Icônes isométriques 3D, style unique |
| [Phosphor Icons](https://phosphoricons.com/) | Flexible, plusieurs styles (outline, fill, etc.) |
| [Tabler Icons](https://tabler-icons.io/) | +4000 icônes SVG open source |
| [Feather Icons](https://feathericons.com/) | Minimaliste, très propre |
| [Iconify](https://iconify.design/) | Accès à 200 000+ icônes de toutes les collections |


## Emojis comme icônes

| Site | Description |
|------|-------------|
| [Emojipedia](https://emojipedia.org/) | Référence complète des emojis |
| [OpenMoji](https://openmoji.org/) | Emojis open source en SVG |


## Favicon

| Site | Description |
|------|-------------|
| [favicon.io](https://favicon.io/) | Générer un favicon depuis texte, image ou emoji |
| [RealFaviconGenerator](https://realfavicongenerator.net/) | Générer pour toutes les plateformes |


## Formats et intégration

```html
<!-- SVG inline (le plus flexible) -->
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
  <path d="..."/>
</svg>

<!-- Via CDN (Font Awesome) -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<i class="fas fa-home"></i>
```
