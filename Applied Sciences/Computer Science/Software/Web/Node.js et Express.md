---
title: "Node.js et Express"
domain: "Applied Sciences"
subdomain: "Computer Science > Web"
tags: [sciences-appliquées, informatique, web, nodejs, express, backend, javascript]
date: "2026-04-07"
---

# Node.js et Express

## Node.js

Node.js est un environnement d'exécution JavaScript côté serveur, construit sur le moteur V8 de Chrome. Il permet d'exécuter du JavaScript en dehors du navigateur.

### Caractéristiques

**Architecture événementielle non-bloquante** : Node.js utilise un modèle d'I/O asynchrone basé sur une boucle d'événements (event loop). Au lieu de créer un thread par connexion, Node.js gère toutes les connexions dans un seul thread, en déléguant les opérations I/O au système d'exploitation.

```
Requêtes entrantes
        │
        ▼
   Event Loop (single thread)
        │
   ┌────┴────┐
   │         │
Callbacks  I/O Operations (async)
(sync)    ─────────────────────────
          File System, Network, DB
          (gérés par libuv en C++)
```

**Adapté pour** : APIs REST, applications temps réel (chat, streaming), microservices, outils CLI.

**Moins adapté pour** : calcul intensif CPU (bloque l'event loop), applications nécessitant du parallélisme natif.

### npm — Node Package Manager

```bash
# Initialiser un projet
npm init -y

# Installer une dépendance
npm install express
npm install -D nodemon   # dépendance de développement (-D = --save-dev)

# Désinstaller
npm uninstall express

# Lancer un script (défini dans package.json)
npm start
npm run dev

# Audit de sécurité
npm audit
npm audit fix
```

### Modules CommonJS et ESM

```javascript
// CommonJS (historique, .js par défaut si "type": "commonjs")
const fs = require('fs');
const { join } = require('path');
module.exports = { maFonction };

// ESM — ES Modules (.mjs ou "type": "module" dans package.json)
import fs from 'fs';
import { join } from 'path';
export { maFonction };
export default class MaClasse {}
```

### Modules natifs courants

```javascript
const fs = require('fs');           // Système de fichiers
const path = require('path');       // Manipulation de chemins
const http = require('http');       // Serveur HTTP natif
const https = require('https');     // Serveur HTTPS natif
const os = require('os');           // Informations système
const crypto = require('crypto');   // Cryptographie
const events = require('events');   // EventEmitter
const stream = require('stream');   // Streams
const url = require('url');         // Parsing d'URL
const querystring = require('querystring'); // Query strings
```

### Système de fichiers asynchrone

```javascript
const fs = require('fs').promises;  // API promises (Node 10+)
const path = require('path');

// Lire un fichier
const contenu = await fs.readFile(path.join(__dirname, 'data.txt'), 'utf8');

// Écrire un fichier
await fs.writeFile('output.txt', 'Hello World', 'utf8');

// Lire un répertoire
const fichiers = await fs.readdir('./');

// Vérifier l'existence
try {
    await fs.access('fichier.txt');
    console.log('Existe');
} catch {
    console.log("N'existe pas");
}

// Copier, renommer, supprimer
await fs.copyFile('src.txt', 'dest.txt');
await fs.rename('ancien.txt', 'nouveau.txt');
await fs.unlink('fichier.txt');
```

### Streams

Les streams permettent de traiter des données en flux continu sans charger tout le fichier en mémoire.

```javascript
const fs = require('fs');

// Lire un grand fichier par morceaux
const readable = fs.createReadStream('grand-fichier.csv', { encoding: 'utf8' });

readable.on('data', (chunk) => {
    console.log(`Reçu ${chunk.length} octets`);
});
readable.on('end', () => console.log('Lecture terminée'));
readable.on('error', (err) => console.error(err));

// Pipe : connecter readable → writable
const readStream = fs.createReadStream('input.txt');
const writeStream = fs.createWriteStream('output.txt');
readStream.pipe(writeStream);

// Transform stream (transformer à la volée)
const { Transform } = require('stream');
const majuscules = new Transform({
    transform(chunk, encoding, callback) {
        callback(null, chunk.toString().toUpperCase());
    }
});
fs.createReadStream('input.txt')
    .pipe(majuscules)
    .pipe(fs.createWriteStream('output.txt'));
```

### EventEmitter

```javascript
const EventEmitter = require('events');

class Serveur extends EventEmitter {
    demarrer(port) {
        // ... démarrage
        this.emit('demarrage', port);
    }
    arreter() {
        this.emit('arret');
    }
}

const serveur = new Serveur();
serveur.on('demarrage', (port) => console.log(`Serveur démarré sur :${port}`));
serveur.on('arret', () => console.log('Serveur arrêté'));
serveur.demarrer(3000);
```

## Express.js

Express est le framework web minimal pour Node.js. Il fournit un système de routage, un middleware pipeline et des utilitaires HTTP.

### Installation et serveur de base

```javascript
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware globaux
app.use(express.json());                    // Parser les corps JSON
app.use(express.urlencoded({ extended: true })); // Parser les form data
app.use(express.static('public'));          // Servir des fichiers statiques

// Route simple
app.get('/', (req, res) => {
    res.json({ message: 'Bienvenue sur l\'API' });
});

// Démarrer le serveur
app.listen(PORT, () => {
    console.log(`Serveur sur http://localhost:${PORT}`);
});
```

### Routage

```javascript
// Méthodes HTTP
app.get('/clients', listerClients);
app.post('/clients', creerClient);
app.get('/clients/:id', obtenirClient);
app.put('/clients/:id', remplacerClient);
app.patch('/clients/:id', modifierClient);
app.delete('/clients/:id', supprimerClient);

// Paramètres de route
app.get('/clients/:id/commandes/:commandeId', (req, res) => {
    const { id, commandeId } = req.params;
    res.json({ clientId: id, commandeId });
});

// Query parameters
app.get('/produits', (req, res) => {
    const { page = 1, limit = 20, categorie } = req.query;
    // GET /produits?page=2&limit=10&categorie=informatique
    res.json({ page, limit, categorie });
});

// Router modulaire
const router = express.Router();
router.get('/', listerClients);
router.post('/', creerClient);
router.get('/:id', obtenirClient);

app.use('/api/v1/clients', router);
```

### Middleware

Le middleware est une fonction `(req, res, next)` qui s'exécute dans le pipeline de traitement de la requête.

```javascript
// Middleware global (s'applique à toutes les routes)
app.use((req, res, next) => {
    console.log(`${req.method} ${req.path} - ${new Date().toISOString()}`);
    next(); // Passer au middleware suivant
});

// Middleware sur une route spécifique
const verifierAuthentification = (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
        return res.status(401).json({ erreur: 'Token manquant' });
    }
    try {
        req.utilisateur = jwt.verify(token, process.env.JWT_SECRET);
        next();
    } catch {
        res.status(401).json({ erreur: 'Token invalide' });
    }
};

app.get('/profil', verifierAuthentification, (req, res) => {
    res.json(req.utilisateur);
});

// Middleware de gestion des erreurs (4 paramètres)
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(err.status || 500).json({
        erreur: {
            message: err.message || 'Erreur interne du serveur',
            code: err.code || 'INTERNAL_ERROR'
        }
    });
});
```

### Architecture MVC avec Express

```
projet/
├── src/
│   ├── controllers/      # Logique de traitement des requêtes
│   │   └── clientController.js
│   ├── services/         # Logique métier
│   │   └── clientService.js
│   ├── models/           # Modèles de données (Mongoose, Sequelize...)
│   │   └── Client.js
│   ├── routes/           # Définition des routes
│   │   └── clientRoutes.js
│   ├── middlewares/      # Middlewares personnalisés
│   │   └── auth.js
│   └── app.js            # Configuration Express
├── .env                  # Variables d'environnement
└── server.js             # Point d'entrée
```

```javascript
// controllers/clientController.js
const clientService = require('../services/clientService');

exports.lister = async (req, res, next) => {
    try {
        const { page = 1, limit = 20 } = req.query;
        const clients = await clientService.lister({ page, limit });
        res.json({ data: clients });
    } catch (err) {
        next(err);  // Passer l'erreur au middleware d'erreur
    }
};

exports.creer = async (req, res, next) => {
    try {
        const client = await clientService.creer(req.body);
        res.status(201).json({ data: client });
    } catch (err) {
        next(err);
    }
};

// routes/clientRoutes.js
const router = require('express').Router();
const { lister, creer, obtenir, modifier, supprimer } = require('../controllers/clientController');
const { verifierToken } = require('../middlewares/auth');

router.get('/', lister);
router.post('/', verifierToken, creer);
router.get('/:id', obtenir);
router.patch('/:id', verifierToken, modifier);
router.delete('/:id', verifierToken, supprimer);

module.exports = router;
```

### Validation avec express-validator

```javascript
const { body, validationResult } = require('express-validator');

const reglesCréationClient = [
    body('nom')
        .notEmpty().withMessage('Le nom est requis')
        .isLength({ min: 2, max: 100 }).withMessage('2 à 100 caractères'),
    body('email')
        .isEmail().withMessage('Email invalide')
        .normalizeEmail(),
    body('age')
        .optional()
        .isInt({ min: 0, max: 150 }).withMessage('Âge entre 0 et 150')
];

const valider = (req, res, next) => {
    const erreurs = validationResult(req);
    if (!erreurs.isEmpty()) {
        return res.status(422).json({ erreurs: erreurs.array() });
    }
    next();
};

router.post('/', reglesCréationClient, valider, creerClient);
```

### Variables d'environnement avec dotenv

```bash
# .env (ne jamais committer)
PORT=3000
DATABASE_URL=postgresql://user:pass@localhost:5432/madb
JWT_SECRET=super_secret_key_changez_moi
NODE_ENV=development
```

```javascript
require('dotenv').config();  // À appeler le plus tôt possible

const port = process.env.PORT || 3000;
const dbUrl = process.env.DATABASE_URL;
```

### CORS

```javascript
const cors = require('cors');

// Autoriser toutes les origines (développement seulement)
app.use(cors());

// Configuration précise (production)
app.use(cors({
    origin: ['https://monsite.com', 'https://app.monsite.com'],
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    credentials: true  // Autoriser les cookies
}));
```

### Authentification JWT

```javascript
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

// Connexion
app.post('/auth/login', async (req, res) => {
    const { email, motDePasse } = req.body;
    const utilisateur = await trouverParEmail(email);

    if (!utilisateur || !await bcrypt.compare(motDePasse, utilisateur.motDePasse)) {
        return res.status(401).json({ erreur: 'Identifiants invalides' });
    }

    const token = jwt.sign(
        { id: utilisateur.id, email: utilisateur.email, role: utilisateur.role },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
    );

    res.json({ token });
});

// Inscription
app.post('/auth/inscription', async (req, res) => {
    const { email, motDePasse } = req.body;
    const hash = await bcrypt.hash(motDePasse, 12);  // 12 rounds
    const utilisateur = await creerUtilisateur({ email, motDePasse: hash });
    res.status(201).json({ id: utilisateur.id });
});
```

### Connexion à une base de données (PostgreSQL avec pg)

```javascript
const { Pool } = require('pg');

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    max: 20,              // Taille maximale du pool
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000
});

// Requête simple
const { rows } = await pool.query(
    'SELECT * FROM clients WHERE id = $1',
    [id]
);

// Transaction
const client = await pool.connect();
try {
    await client.query('BEGIN');
    await client.query('UPDATE comptes SET solde = solde - $1 WHERE id = $2', [montant, idSource]);
    await client.query('UPDATE comptes SET solde = solde + $1 WHERE id = $2', [montant, idDest]);
    await client.query('COMMIT');
} catch (err) {
    await client.query('ROLLBACK');
    throw err;
} finally {
    client.release();
}
```

### Middlewares tiers populaires

| Package | Usage |
|---------|-------|
| `cors` | Gestion du Cross-Origin Resource Sharing |
| `helmet` | En-têtes de sécurité HTTP |
| `express-rate-limit` | Limitation du nombre de requêtes |
| `morgan` | Logging des requêtes HTTP |
| `compression` | Compression gzip des réponses |
| `multer` | Upload de fichiers multipart |
| `express-validator` | Validation et sanitisation |
| `dotenv` | Variables d'environnement |
| `jsonwebtoken` | Création et vérification JWT |
| `bcrypt` | Hachage de mots de passe |
| `pg` | Client PostgreSQL |
| `mongoose` | ODM MongoDB |
| `sequelize` | ORM SQL |

```javascript
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');

// Sécurité
app.use(helmet());

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,  // 15 minutes
    max: 100,                    // 100 requêtes par fenêtre
    message: 'Trop de requêtes, réessayez dans 15 minutes'
});
app.use('/api/', limiter);

// Logging
app.use(morgan('combined'));   // Format Apache
app.use(morgan('dev'));        // Format compact coloré
```
