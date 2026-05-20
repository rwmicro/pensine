---
title: "React.js"
domain: "Applied Sciences"
subdomain: "Computer Science > Web"
tags: [sciences-appliquées, informatique, web, react, javascript, frontend]
date: "2026-04-07"
---

# React.js

React (ou React.js) est une bibliothèque JavaScript open-source créée par Meta (Facebook) en 2013 pour construire des interfaces utilisateur composables et réactives. Elle repose sur un modèle de composants et sur un DOM virtuel (Virtual DOM).

## Concepts fondamentaux

### JSX

JSX (JavaScript XML) est une syntaxe qui permet d'écrire du HTML dans du JavaScript. Babel le transforme en appels `React.createElement()` lors de la compilation.

```jsx
// JSX
const element = <h1 className="titre">Bonjour {prenom} !</h1>;

// Équivalent compilé
const element = React.createElement('h1', { className: 'titre' }, `Bonjour ${prenom} !`);

// Expressions JavaScript dans JSX (entre accolades)
const liste = (
    <ul>
        {items.map((item) => (
            <li key={item.id}>{item.nom}</li>  // key obligatoire dans les listes
        ))}
    </ul>
);

// Rendu conditionnel
const connexion = estConnecte ? <Profil /> : <ConnexionBouton />;
const message = estCharge && <Message texte="Chargement..." />;
```

### Composants

Un composant React est une fonction (ou classe) qui prend des **props** en entrée et retourne du JSX.

```jsx
// Composant fonctionnel (recommandé depuis React 16.8)
function Carte({ titre, description, image }) {
    return (
        <div className="carte">
            <img src={image} alt={titre} />
            <h2>{titre}</h2>
            <p>{description}</p>
        </div>
    );
}

// Utilisation (les props sont passées comme des attributs HTML)
<Carte
    titre="Introduction à React"
    description="Apprendre les bases de React.js"
    image="/img/react.png"
/>

// Props avec valeurs par défaut
function Bouton({ texte = "Cliquer", variante = "primaire", onClick }) {
    return (
        <button className={`btn btn-${variante}`} onClick={onClick}>
            {texte}
        </button>
    );
}

// Prop children (contenu imbriqué)
function Conteneur({ children, className }) {
    return <div className={`conteneur ${className}`}>{children}</div>;
}
// Utilisation :
<Conteneur className="large">
    <h1>Titre</h1>
    <p>Contenu...</p>
</Conteneur>
```

## Hooks

Les hooks permettent aux composants fonctionnels d'utiliser l'état et d'autres fonctionnalités React. Ils ne fonctionnent qu'à l'intérieur de composants React (ou de hooks personnalisés). Règle : toujours les appeler au niveau supérieur (jamais dans des conditions ou boucles).

### useState

Gère l'état local d'un composant.

```jsx
import { useState } from 'react';

function Compteur() {
    const [compte, setCompte] = useState(0);     // valeur initiale = 0
    const [texte, setTexte]   = useState('');

    return (
        <div>
            <p>Compte : {compte}</p>
            <button onClick={() => setCompte(compte + 1)}>Incrémenter</button>
            <button onClick={() => setCompte(c => c - 1)}>Décrémenter</button>
            {/* Forme fonctionnelle — recommandée quand le nouvel état dépend de l'ancien */}

            <input
                value={texte}
                onChange={(e) => setTexte(e.target.value)}
            />
        </div>
    );
}

// État avec objet
function Formulaire() {
    const [champs, setChamps] = useState({ nom: '', email: '' });

    const handleChange = (e) => {
        setChamps(prev => ({ ...prev, [e.target.name]: e.target.value }));
    };

    return (
        <form>
            <input name="nom" value={champs.nom} onChange={handleChange} />
            <input name="email" value={champs.email} onChange={handleChange} />
        </form>
    );
}
```

### useEffect

Gère les effets de bord : appels API, abonnements, timers, manipulation du DOM.

```jsx
import { useState, useEffect } from 'react';

function ProfilUtilisateur({ userId }) {
    const [utilisateur, setUtilisateur] = useState(null);
    const [chargement, setChargement]   = useState(true);
    const [erreur, setErreur]           = useState(null);

    useEffect(() => {
        let annule = false;  // Éviter les mises à jour après démontage

        const charger = async () => {
            try {
                setChargement(true);
                const res = await fetch(`/api/utilisateurs/${userId}`);
                if (!res.ok) throw new Error('Erreur réseau');
                const data = await res.json();
                if (!annule) setUtilisateur(data);
            } catch (e) {
                if (!annule) setErreur(e.message);
            } finally {
                if (!annule) setChargement(false);
            }
        };

        charger();

        return () => { annule = true; };  // Fonction de nettoyage
    }, [userId]);  // Se ré-exécute quand userId change

    if (chargement) return <p>Chargement...</p>;
    if (erreur)     return <p>Erreur : {erreur}</p>;
    return <div>{utilisateur?.nom}</div>;
}

// Tableau de dépendances :
useEffect(() => { ... });         // S'exécute après chaque rendu
useEffect(() => { ... }, []);     // S'exécute une seule fois au montage
useEffect(() => { ... }, [id]);   // S'exécute quand id change
```

### useContext

Partage des données sans passer des props à travers tous les niveaux (prop drilling).

```jsx
import { createContext, useContext, useState } from 'react';

// Créer le contexte
const ThemeContexte = createContext({ theme: 'clair', toggleTheme: () => {} });

// Provider — envelopper l'arbre de composants
function AppProviders({ children }) {
    const [theme, setTheme] = useState('clair');

    return (
        <ThemeContexte.Provider value={{ theme, toggleTheme: () =>
            setTheme(t => t === 'clair' ? 'sombre' : 'clair')
        }}>
            {children}
        </ThemeContexte.Provider>
    );
}

// Consommer le contexte dans n'importe quel composant enfant
function BoutonTheme() {
    const { theme, toggleTheme } = useContext(ThemeContexte);
    return (
        <button onClick={toggleTheme}>
            Mode : {theme}
        </button>
    );
}
```

### useReducer

Alternative à useState pour une logique d'état complexe.

```jsx
import { useReducer } from 'react';

const etatInitial = { items: [], total: 0 };

function reducerPanier(etat, action) {
    switch (action.type) {
        case 'AJOUTER_ITEM':
            return {
                ...etat,
                items: [...etat.items, action.item],
                total: etat.total + action.item.prix
            };
        case 'SUPPRIMER_ITEM':
            const item = etat.items.find(i => i.id === action.id);
            return {
                ...etat,
                items: etat.items.filter(i => i.id !== action.id),
                total: etat.total - (item?.prix ?? 0)
            };
        case 'VIDER':
            return etatInitial;
        default:
            return etat;
    }
}

function Panier() {
    const [etat, dispatch] = useReducer(reducerPanier, etatInitial);

    return (
        <div>
            <p>Total : {etat.total} €</p>
            <button onClick={() => dispatch({ type: 'AJOUTER_ITEM', item: { id: 1, nom: 'Livre', prix: 15 } })}>
                Ajouter
            </button>
        </div>
    );
}
```

### useMemo et useCallback

Optimisent les performances en mémorisant des valeurs et des fonctions.

```jsx
import { useMemo, useCallback } from 'react';

function ListeFiltree({ items, filtre }) {
    // useMemo : recalcule seulement si items ou filtre change
    const itemsFiltres = useMemo(
        () => items.filter(item => item.nom.includes(filtre)),
        [items, filtre]
    );

    // useCallback : renvoie la même référence de fonction si les dépendances n'ont pas changé
    const handleClick = useCallback((id) => {
        console.log('Clicked:', id);
    }, []);  // Ne change jamais

    return (
        <ul>
            {itemsFiltres.map(item => (
                <li key={item.id} onClick={() => handleClick(item.id)}>
                    {item.nom}
                </li>
            ))}
        </ul>
    );
}
```

## Gestion des formulaires

```jsx
function FormulaireInscription() {
    const [champs, setChamps] = useState({ nom: '', email: '', motDePasse: '' });
    const [erreurs, setErreurs] = useState({});
    const [envoi, setEnvoi] = useState(false);

    const valider = () => {
        const nouvellesErreurs = {};
        if (!champs.nom) nouvellesErreurs.nom = 'Nom requis';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(champs.email)) {
            nouvellesErreurs.email = 'Email invalide';
        }
        if (champs.motDePasse.length < 8) {
            nouvellesErreurs.motDePasse = 'Minimum 8 caractères';
        }
        return nouvellesErreurs;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const errs = valider();
        if (Object.keys(errs).length > 0) {
            setErreurs(errs);
            return;
        }
        setEnvoi(true);
        try {
            await inscrireUtilisateur(champs);
        } finally {
            setEnvoi(false);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={champs.nom}
                onChange={e => setChamps(p => ({ ...p, nom: e.target.value }))}
            />
            {erreurs.nom && <span className="erreur">{erreurs.nom}</span>}

            <button type="submit" disabled={envoi}>
                {envoi ? 'Envoi...' : "S'inscrire"}
            </button>
        </form>
    );
}
```

## Hooks personnalisés

Un hook personnalisé est une fonction dont le nom commence par `use` et qui peut appeler d'autres hooks.

```jsx
// Hook pour les appels API
function useApi(url) {
    const [data, setData]         = useState(null);
    const [chargement, setLoad]   = useState(true);
    const [erreur, setErreur]     = useState(null);

    useEffect(() => {
        let annule = false;
        fetch(url)
            .then(r => r.json())
            .then(d => { if (!annule) { setData(d); setLoad(false); } })
            .catch(e => { if (!annule) { setErreur(e); setLoad(false); } });
        return () => { annule = true; };
    }, [url]);

    return { data, chargement, erreur };
}

// Hook pour le localStorage
function useLocalStorage(cle, valeurDefaut) {
    const [valeur, setValeur] = useState(() => {
        try {
            const stocke = localStorage.getItem(cle);
            return stocke ? JSON.parse(stocke) : valeurDefaut;
        } catch { return valeurDefaut; }
    });

    const setter = (nouvelleValeur) => {
        setValeur(nouvelleValeur);
        localStorage.setItem(cle, JSON.stringify(nouvelleValeur));
    };

    return [valeur, setter];
}

// Utilisation
function App() {
    const { data: utilisateurs, chargement } = useApi('/api/utilisateurs');
    const [theme, setTheme] = useLocalStorage('theme', 'clair');

    if (chargement) return <Spinner />;
    return <div className={theme}>{/* ... */}</div>;
}
```

## React Router

```jsx
import { BrowserRouter, Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';

function App() {
    return (
        <BrowserRouter>
            <nav>
                <Link to="/">Accueil</Link>
                <Link to="/clients">Clients</Link>
            </nav>
            <Routes>
                <Route path="/" element={<Accueil />} />
                <Route path="/clients" element={<ListeClients />} />
                <Route path="/clients/:id" element={<DetailClient />} />
                <Route path="*" element={<PageNonTrouvee />} />
            </Routes>
        </BrowserRouter>
    );
}

function DetailClient() {
    const { id } = useParams();        // Lire :id depuis l'URL
    const navigate = useNavigate();    // Navigation programmatique

    return (
        <div>
            <h1>Client {id}</h1>
            <button onClick={() => navigate(-1)}>Retour</button>
            <button onClick={() => navigate('/clients')}>Liste</button>
        </div>
    );
}
```

## Architecture et bonnes pratiques

```
src/
├── components/         # Composants réutilisables (Button, Card, Modal...)
│   ├── ui/             # Composants purement visuels
│   └── features/       # Composants liés à une fonctionnalité
├── pages/              # Composants de page (une par route)
├── hooks/              # Hooks personnalisés
├── services/           # Appels API, logique externe
├── context/            # Contextes React
├── utils/              # Fonctions utilitaires
└── App.jsx             # Composant racine + routage
```

**Bonnes pratiques** :
- Un composant = une responsabilité unique (Single Responsibility)
- Remonter l'état (lift state up) au plus proche ancêtre commun qui en a besoin
- Préférer les composants stateless (sans état) quand possible
- Éviter la mutation directe de l'état (toujours utiliser la fonction setter)
- Fournir des `key` uniques et stables dans les listes (jamais l'index si la liste peut changer)
- Extraire la logique dans des hooks personnalisés pour la réutiliser

## Comparaison React vs alternatives

| Critère | React | Vue.js | Angular |
|---------|-------|--------|---------|
| Type | Bibliothèque UI | Framework progressif | Framework complet |
| Courbe d'apprentissage | Moyenne | Douce | Élevée |
| Langage | JS/JSX/TSX | HTML templates | TypeScript |
| Taille initiale | ~45 kB | ~34 kB | ~130 kB |
| Popularité | Très élevée | Élevée | Élevée |
| État global | Context / Redux / Zustand | Pinia / Vuex | NgRx / Services |
| Créateur | Meta | Evan You | Google |
