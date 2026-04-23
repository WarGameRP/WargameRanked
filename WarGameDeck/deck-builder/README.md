# Wargame Ranked - Deck Builder avec Signature Sécurisée

Ce deck-builder utilise une architecture sécurisée où les signatures SHA-256 sont générées par une API Cloudflare Workers, rendant impossible la triche côté client.

## Architecture

1. **script.js** génère le deck JSON
2. Le JSON est envoyé à l'API Cloudflare Workers
3. L'API (qui possède le secret caché) calcule la signature SHA-256
4. L'API renvoie la signature au navigateur
5. Le script télécharge le fichier avec la signature officielle

**Résultat :** Impossible de tricher, le secret est invisible côté client.

## Déploiement de l'API Cloudflare Workers

### Prérequis
- Un compte Cloudflare (gratuit)
- Node.js installé sur votre machine

### Étapes

1. **Installer Wrangler (CLI Cloudflare Workers)**
   ```bash
   npm install -g wrangler
   ```

2. **Se connecter à Cloudflare**
   ```bash
   wrangler login
   ```
   Suivez les instructions dans le navigateur.

3. **Créer un nouveau Worker**
   ```bash
   wrangler init wargame-api
   ```
   Choisissez "Hello World" Worker lors de la création.

4. **Configurer le Worker**
   Ouvrez le fichier `wargame-api/wrangler.toml` et configurez-le :
   ```toml
   name = "wargame-api"
   main = "index.js"
   compatibility_date = "2024-01-01"
   
   [vars]
   # Variables d'environnement si nécessaires
   ```

5. **Copier le code du Worker**
   Copiez le contenu de `cloudflare-worker.js` dans `wargame-api/index.js`.

6. **Définir le secret de signature**
   ```bash
   cd wargame-api
   wrangler secret put DECK_SIGNATURE_SALT
   ```
   Entrez votre secret quand demandé (ex: `WargameRankedSecretSalt`)
   **Important :** Choisissez un secret complexe et unique !

7. **Déployer le Worker**
   ```bash
   wrangler deploy
   ```
   Notez l'URL obtenue (ex: `https://wargame-api.votre-pseudo.workers.dev`)

## Configuration du Deck Builder

1. **Ouvrir `script.js`**
   Modifiez la constante `SIGNATURE_API_URL` avec l'URL de votre Worker :
   ```javascript
   const SIGNATURE_API_URL = "https://wargame-api.votre-pseudo.workers.dev/sign";
   ```

2. **Tester**
   Ouvrez `index.html` dans votre navigateur, créez un deck et exportez-le.
   Le fichier devrait être téléchargé avec une signature valide.

## Vérification des Decks

La vérification des signatures peut être faite par :
- Un bot Discord (en utilisant la même logique de signature)
- Un serveur backend
- L'API Cloudflare Workers peut être étendue avec un endpoint `/verify`

## Sécurité

- ✅ Le secret de signature est stocké dans les variables d'environnement de Cloudflare Workers
- ✅ Impossible de récupérer le secret côté client
- ✅ Les signatures sont calculées côté serveur
- ✅ CORS configuré pour autoriser les requêtes depuis votre domaine

## Structure des fichiers

```
deck-builder/
├── index.html              # Interface du deck-builder
├── script.js              # Logique JS (modifiée pour utiliser l'API)
├── style.css              # Styles
├── verify.html            # Page de vérification (à adapter)
├── cloudflare-worker.js   # Code du Worker Cloudflare
└── README.md              # Ce fichier
```

## Dépannage

### Erreur "Erreur API: 404"
- Vérifiez que l'URL dans `SIGNATURE_API_URL` est correcte
- Vérifiez que le Worker est bien déployé

### Erreur "Secret not configured"
- Assurez-vous d'avoir exécuté `wrangler secret put DECK_SIGNATURE_SALT`
- Vérifiez que le secret est bien défini dans le dashboard Cloudflare

### Erreur CORS
- Le Worker inclut déjà les headers CORS
- Vérifiez que votre domaine est autorisé si vous avez restreint CORS

## Notes

- La fonction `stableStringify` doit être identique côté client et côté serveur pour garantir que les signatures correspondent
- Le secret ne doit jamais être partagé ou commité dans un repository public
- Vous pouvez ajouter un rate limiting sur le Worker pour éviter les abus
