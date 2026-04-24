# Dashboard WarGameDeck v1.2.0

Mise à jour majeure avec l'ajout du Deck Builder et de l'API de signature sécurisée.

---

## 🆕 Nouvelles Fonctionnalités

### Deck Builder avec Signature Sécurisée
- **Deck Builder complet** avec interface moderne pour créer des decks
- **Système de doctrines** : Infanterie, Blindée, Mécanisée, Appui, CAS, Mixte
- **Signature SHA-256 sécurisée** via API Cloudflare Workers (anti-triche)
- **Import/Export de decks** en format JSON avec signature
- **Page de vérification** des decks (`verify.html`)
- **Gestion des crédits** par catégorie avec limites dynamiques selon la doctrine

**Architecture de sécurité :**
- Le secret de signature est stocké côté serveur (Cloudflare Workers)
- Impossible de tricher côté client
- CORS configuré pour autoriser les requêtes

---

### API Cloudflare Workers
- **`wargame-api/index.js`** : API pour la signature des decks
- **`wargame-api/package.json`** : Dépendances Node.js
- **`wargame-api/wrangler.toml`** : Configuration Cloudflare Workers
- **`deck-builder/cloudflare-worker.js`** : Code du Worker

---

### GitHub Actions
- **`.github/workflows/deploy.yml`** : Workflow de déploiement automatique
- **`.nojekyll`** : Désactivation de Jekyll pour GitHub Pages

---

## 🛠️ Outils d'Automatisation Ajoutés

### Scripts de Téléchargement d'Images
- **`download_images.py`** : Télécharge les images depuis les URLs
- **`run_download_images.bat`** : Lancement simplifié
- **`download_log.txt`** : Journal des téléchargements
- **`vehicles.json`** : Base de données des véhicules

### Script de Remplacement de Liens
- **`replace_imgur_links.py`** : Remplace les liens imgur par des liens locaux

---

## 📚 Documentation Ajoutée

### Guides Git
- **`git_basics.md`** : Bases de Git pour débutants
- **`tutoriel_git.md`** : Tutoriel Git détaillé

---

## 🔧 Fichiers de Configuration

- **`.gitignore`** : Fichiers ignorés par Git
- **`discord_servers.js`** : Configuration des serveurs Discord

---

## 📈 Améliorations

### Interface Deck Builder
- **Modale de sélection de crédit** : Ajout du scroll quand il y a beaucoup d'options (max-height: 50vh)
- **Tooltip sur les emport-label** : Affichage du texte complet au survol de la souris quand le label est tronqué

### Mises à jour des Decks
- **`france.html`** : Mise à jour du deck français
- **`corée_du_sud.html`** : Mise à jour du deck sud-coréen
- **`chine.html`** : Mise à jour du deck chinois
- **`afrique_du_sud.html`** : Mise à jour du deck sud-africain
- **`japon.html`** : Mise à jour du deck japonais
- **`ranked_basique.html`** : Mise à jour du deck ranked_basique

### Ajouts decks
- **`ukraine.html`** : Ajout du deck ukrainien

---

*Pour voir les modifications des versions précédentes, consultez `OldUpdate/v1.1.1.md`*
