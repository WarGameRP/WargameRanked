# 🔍 Audit Complet — WargameRanked

> **Projet audité** : `WargameRanked/`
> **Date** : 23 avril 2026
> **Portée** : Sécurité · Architecture · Code · UX/UI · Performance · Déploiement

---

## Table des matières

1. [Vue d'ensemble du projet](#vue-densemble)
2. [🔴 Failles de sécurité critiques](#failles-de-sécurité-critiques)
3. [🟠 Problèmes majeurs](#problèmes-majeurs)
4. [🟡 Améliorations recommandées](#améliorations-recommandées)
5. [🟢 Points positifs](#points-positifs)
6. [📋 Tableau récapitulatif](#tableau-récapitulatif)

---

## Vue d'ensemble

Le projet **WargameRanked** est un portail web statique permettant de :
- Consulter des decks de véhicules (Tech Trees exportés)
- Construire des decks avec un Deck Builder interactif
- Vérifier l'intégrité d'un deck exporté via signature SHA-256
- Gérer les liens Discord communautaires

**Stack** : HTML/CSS/JS vanilla (front), PowerShell + Python + Node.js (tooling), GitHub Pages (déploiement)

---

## 🔴 Failles de sécurité critiques

### 1. Secret SHA-256 exposé côté client

> [!CAUTION]
> **Sévérité : CRITIQUE** — Le sel cryptographique est visible publiquement dans le code source.

| Fichier | Ligne | Code problématique |
|---------|-------|--------------------|
| [script.js](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/script.js#L326) | 326 | `sha256(dataString + "WargameRankedSecretSalt")` |
| [verify.html](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/verify.html#L186) | 186 | `sha256(stableStringify(rest) + "WargameRankedSecretSalt")` |

**Problème** : Le sel `"WargameRankedSecretSalt"` est en clair dans le JavaScript client. N'importe qui peut :
1. Ouvrir les DevTools
2. Copier la fonction `stableStringify` + le sel
3. Modifier le JSON du deck et recalculer une signature valide

**Impact** : Le mécanisme anti-triche est totalement contournable. Un joueur peut se créer un deck invalide (dépassant les crédits) avec une signature valide.

**Solution recommandée** :
- **Court terme** : Accepter que la vérification côté client est un simple garde-fou (pas une vraie sécurité). Renommer le système en "vérification d'intégrité" plutôt que "anti-triche".
- **Long terme** : Implémenter un serveur (API) qui signe les decks avec une clé secrète côté serveur. Ou utiliser un bot Discord pour la signature.

---

### 2. Injection XSS via les données de véhicules

> [!CAUTION]
> **Sévérité : HAUTE** — Utilisation de `innerHTML` avec des données non-sanitisées.

| Fichier | Lignes | Vecteur d'attaque |
|---------|--------|-------------------|
| [script.js](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/script.js#L63-L69) | 63-69 | `card.innerHTML` avec `v.name` non-échappé |
| [script.js](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/script.js#L244-L256) | 244-256 | `div.innerHTML` avec `v.name` et `v.selectedEmport._text` |
| [verify.html](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/verify.html#L228-L238) | 228-238 | `div.innerHTML` avec `u.name`, `u.country`, `emport._text` |
| [index.html (root)](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/index.html#L339-L348) | 339-348 | `dropdown.innerHTML` avec `server.name`, `server.description` |

**Problème** : Les noms de véhicules, pays, et descriptions sont injectés directement dans le DOM sans échappement HTML. Un fichier JSON malveillant importé pourrait contenir :
```json
{ "name": "<img src=x onerror=alert(document.cookie)>" }
```

**Solution** :
```javascript
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
// Puis utiliser : ${escapeHtml(v.name)} au lieu de ${v.name}
```

---

### 3. Injection XSS via le Markdown (marked.js)

> [!WARNING]
> **Sévérité : MOYENNE** — Le rendu Markdown pourrait exécuter du JavaScript.

| Fichier | Ligne |
|---------|-------|
| [index.html (WarGameDeck)](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/index.html#L120) | 120 |

**Problème** : `marked.parse(content)` est utilisé sans option de sanitisation. Si les fichiers Markdown contiennent du HTML brut ou des scripts, ils seront rendus tels quels.

**Solution** :
```javascript
marked.setOptions({ sanitize: true }); // deprecated, utiliser DOMPurify
// Ou mieux :
import DOMPurify from 'dompurify';
target.innerHTML = DOMPurify.sanitize(marked.parse(content));
```

---

### 4. Chemin absolu en dur dans le script Node.js

> [!WARNING]
> **Sévérité : MOYENNE** — Le script ne fonctionne que sur votre machine.

| Fichier | Lignes |
|---------|--------|
| [extract_vehicles.js](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/Assets/scripts/js/extract_vehicles.js#L4-L6) | 4-6 |

```javascript
const assetsPath = 'e:/Travaille/CodageAutres/Projets Web/Wargame/WGD/WargameRanked/WarGameDeck/Assets';
```

**Problème** : Chemin absolu = ne fonctionne pas sur un autre PC, ni en CI/CD.

**Solution** :
```javascript
const assetsPath = path.join(__dirname, '..', '..');
```

---

### 5. `ExecutionPolicy Bypass` dans les scripts batch

> [!WARNING]
> **Sévérité : BASSE** (intentionnel, mais à noter)

| Fichier | Ligne |
|---------|-------|
| [Lancer_WarGame.bat](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/Lancer_WarGame.bat#L3) | 3 |

`powershell -ExecutionPolicy Bypass` contourne les politiques de sécurité PowerShell. C'est une pratique courante pour des scripts personnels, mais cela pourrait être un vecteur d'attaque si le dépôt est cloné par un utilisateur.

---

## 🟠 Problèmes majeurs

### 6. Duplication de code massive

| Élément dupliqué | Occurrences | Fichiers |
|------------------|-------------|----------|
| `DOCTRINES` (données) | 2 | `script.js` L1-8, `verify.html` L126-133 |
| `translateType()` | 2 | `script.js` L80-91, `verify.html` L135-146 |
| `stableStringify()` | 2 | `script.js` L297-305, `verify.html` L148-156 |
| `getVehicleImage()` | 2 | `script.js` L184-201, `verify.html` L158-175 |
| Variables CSS (`--bg-color`, etc.) | 4 | `index.html (root)`, `index.css`, `deck_style.css`, `style.css` |
| Sel cryptographique | 2 | `script.js`, `verify.html` |

**Solution** : Créer un fichier `shared.js` contenant les fonctions et constantes communes, puis l'inclure dans les deux pages.

---

### 7. Gestion fragile des IDs d'instance

| Fichier | Ligne | Code |
|---------|-------|------|
| [script.js](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/script.js#L172) | 172 | `instanceId: Date.now() + Math.random()` |

**Problèmes** :
- `Date.now() + Math.random()` produit un float (ex: `1745451234567.8901`), ce qui peut causer des problèmes de précision avec les opérations JavaScript sur les grands nombres
- Utilisé directement dans un `onclick` inline : `onclick="removeVehicle(${v.instanceId})"` — si l'ID a trop de décimales, il sera tronqué et ne correspondra à aucun élément

**Solution** :
```javascript
instanceId: crypto.randomUUID() // string unique, pas de problème de précision
```

---

### 8. Pas de validation des données importées

| Fichier | Lignes |
|---------|--------|
| [script.js](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/script.js#L341-L396) | 341-396 |

**Problème** : Lors de l'import d'un deck JSON, seule une vérification basique est faite (`!data.doctrine || !data.units`). Aucune validation de :
- Type des champs (string vs number)
- Valeurs des crédits (négatifs ? NaN ?)
- Taille du tableau `units` (DoS avec un fichier de 10M d'unités ?)
- Doctrine valide (est-ce que `data.doctrine` existe dans `DOCTRINES` ?)

---

### 9. Dépendance externe non-épinglée via CDN

| Fichier | Ligne | Dépendance |
|---------|-------|------------|
| [deck-builder/index.html](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/index.html#L9) | 9 | `cdnjs.cloudflare.com/.../sha256.min.js` |
| [verify.html](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/verify.html#L9) | 9 | Idem |

**Problème** : 
- Si cdnjs est down → l'export/vérification ne fonctionne plus
- Pas de SRI (Subresource Integrity) : si le CDN est compromis, du code malveillant pourrait être injecté

**Solution** : Ajouter l'attribut `integrity` et un `crossorigin` :
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-sha256/0.9.0/sha256.min.js"
        integrity="sha512-xxxxx" crossorigin="anonymous"></script>
```
Ou mieux : télécharger le fichier localement (comme `marked.min.js` qui est déjà local).

---

### 10. Image externe sur verify.html

| Fichier | Ligne |
|---------|-------|
| [verify.html](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/deck-builder/verify.html#L33) | 33 |

```html
<img src="https://www.svgrepo.com/show/486241/upload-file.svg">
```

**Problème** : Dépendance à un serveur externe pour une icône. Si svgrepo est down, l'icône est cassée.

**Solution** : Utiliser un SVG inline ou télécharger le fichier localement.

---

## 🟡 Améliorations recommandées

### 11. Architecture — Pas de séparation des données et de la vue

Les doctrines sont dupliquées en dur dans le HTML (cartes de sélection L46-112 de `deck-builder/index.html`) ET dans le JS (`DOCTRINES` L1-8 de `script.js`). Si une doctrine change, il faut modifier les deux endroits.

**Solution** : Générer les cartes de doctrine dynamiquement depuis l'objet `DOCTRINES`.

---

### 12. SEO & Meta — Manquant

Aucun des fichiers HTML n'a :
- `<meta name="description">`
- Open Graph tags (`og:title`, `og:image`, etc.)
- Structured data

Cela impacte le partage sur Discord (pas de preview card riche).

---

### 13. Accessibilité (a11y)

| Problème | Fichier | Détail |
|----------|---------|--------|
| Pas de `alt` descriptif sur les images de véhicules | `script.js` L64 | `alt=""` vide |
| Navigation au clavier impossible | `index.html (root)` L281 | `onclick` sur `div` au lieu de `<a>` ou `<button>` |
| Pas de rôles ARIA | Tous | Modales sans `role="dialog"` ni `aria-modal="true"` |
| Pas de gestion du focus | `index.html`, `verify.html` | Le focus n'est pas piégé dans les modales |
| Contraste potentiellement insuffisant | CSS | `--text-muted: #8b949e` sur fond sombre |

---

### 14. Responsive Design — Deck Builder

Le layout `grid-template-columns: 350px 1fr 350px` est rigide. Le breakpoint 1200px passe à 2 colonnes mais le panneau Actions disparaît de la vue. Le fallback mobile (`display: block`) rend l'interface difficile à utiliser sur téléphone.

**Solution** : Repenser le layout mobile avec un système de tabs ou d'accordéon.

---

### 15. Performance — vehicles.js chargé globalement

| Fichier | Taille |
|---------|--------|
| `vehicles.js` | 44 KB |
| `vehicles.json` | 44 KB |

Ces 44 KB sont chargés à chaque page, même quand non nécessaires (ex: page d'accueil, page verify avant import).

**Solution** : Charger les données à la demande (`fetch()` au moment nécessaire).

---

### 16. PowerShell Indexer — Regex fragile

Le fichier [Indexer.ps1](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/Indexer.ps1) utilise des regex complexes pour modifier le HTML :

```powershell
$content = $content -replace '(?s)<header>.*?</header>\s*(<div style="max-width: 1000px;...)', $headerHtml
```

C'est extrêmement fragile — un simple changement de whitespace peut casser le matching.

**Solution** : Utiliser un parseur HTML (comme un script Python avec BeautifulSoup, qui est déjà dans les dépendances du projet).

---

### 17. Fichier `.lnk` dans le dépôt

[WarGameDeck.lnk](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/WarGameDeck.lnk) est un raccourci Windows. 

**Problèmes** :
- Inutile pour les non-Windows
- Contient potentiellement des chemins absolus de votre machine
- Peut être un vecteur d'attaque (les `.lnk` peuvent exécuter des commandes)

**Solution** : Supprimer du dépôt et ajouter `*.lnk` au `.gitignore`.

---

### 18. Pas de `.gitignore`

Aucun `.gitignore` visible dans le projet. Cela risque de versionner :
- `node_modules/`
- Fichiers temporaires Python (`__pycache__/`, `*.pyc`)
- `download_log.txt`
- Fichiers `.lnk`

---

### 19. Gestion d'erreurs insuffisante

| Fichier | Ligne | Problème |
|---------|-------|----------|
| `script.js` L20 | `console.error` mais pas de fallback UI | L'utilisateur ne comprend pas l'erreur |
| `verify.html` L242 | `alert()` pour les erreurs | Mauvaise UX, bloquant |
| `Indexer.ps1` | Aucun `try/catch` sur les opérations fichier | Un fichier corrompu peut crasher tout l'indexeur |

---

### 20. Config.json inutilisé

Le fichier [config.json](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/config.json) définit les types de crédits mais n'est importé par aucun fichier JS ou HTML.

---

### 21. Pas de gestion de version cohérente

La version `1.1.0` est définie en deux endroits non-synchronisés :
- HTML : `<span class="version-tag" id="current-version">v1.1.0</span>` (L26 de `WarGameDeck/index.html`)
- JS : `const APP_VERSION = "1.1.0";` (L68)

**Solution** : Définir la version dans un seul endroit (`config.json` ou un `version.js`) et la consommer partout.

---

### 22. CSS — Usage excessif de `!important`

Le fichier [deck_style.css](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/WarGameDeck/Assets/Other/css/deck_style.css) contient **31 occurrences de `!important`**. Cela rend le CSS difficile à maintenir et à surcharger.

**Solution** : Augmenter la spécificité des sélecteurs au lieu d'utiliser `!important`.

---

### 23. Déploiement — Le workflow copie tout le dossier WarGameDeck

Le workflow [deploy.yml](file:///e:/Travaille/CodageAutres/Projets%20Web/Wargame/WGD/WargameRanked/.github/workflows/deploy.yml#L38) copie tout le dossier `WarGameDeck/` y compris :
- Les scripts PowerShell (`Indexer.ps1`)
- Les scripts Python (`scripts/python/`)
- Les fichiers `.bat`
- Le fichier `.lnk`

Ces fichiers sont inutiles sur le site web déployé et exposent de l'information interne.

**Solution** : Exclure les fichiers de tooling du déploiement :
```yaml
- name: Prepare deployment files
  run: |
    cp -r WarGameDeck deploy/
    rm -rf deploy/WarGameDeck/Assets/scripts
    rm -f deploy/WarGameDeck/*.bat deploy/WarGameDeck/*.ps1 deploy/WarGameDeck/*.lnk
```

---

## 🟢 Points positifs

| Aspect | Détail |
|--------|--------|
| ✅ Design cohérent | Thème sombre premium unifié avec variables CSS, palette accent doré |
| ✅ Responsive partiel | Breakpoints présents pour mobile (même si améliorables) |
| ✅ Animations soignées | Transitions `cubic-bezier`, hover effects, `slideUp` modal |
| ✅ Architecture modulaire des scripts | Pipeline clair : `download_images → replace_imgur → extract_vehicles` |
| ✅ Documentation README | README bien structuré avec instructions d'utilisation |
| ✅ CI/CD GitHub Actions | Déploiement automatique sur GitHub Pages |
| ✅ Système de versions/changelog | Modal de nouveautés avec historique des anciennes mises à jour |
| ✅ Drag & Drop | Vérification de deck avec glisser-déposer de fichier |

---

## 📋 Tableau récapitulatif

| # | Sévérité | Catégorie | Description | Effort |
|---|----------|-----------|-------------|--------|
| 1 | 🔴 Critique | Sécurité | Secret SHA-256 exposé côté client | ⚡ Moyen |
| 2 | 🔴 Critique | Sécurité | XSS via innerHTML non-sanitisé | ⚡ Facile |
| 3 | 🟠 Haute | Sécurité | XSS via Markdown (marked.js) | ⚡ Facile |
| 4 | 🟠 Haute | Portabilité | Chemins absolus dans extract_vehicles.js | ⚡ Facile |
| 5 | 🟡 Basse | Sécurité | ExecutionPolicy Bypass | 📝 Note |
| 6 | 🟠 Haute | Architecture | Duplication de code massive | 🔨 Moyen |
| 7 | 🟠 Haute | Bug potentiel | IDs d'instance float fragiles | ⚡ Facile |
| 8 | 🟠 Haute | Robustesse | Pas de validation des imports JSON | 🔨 Moyen |
| 9 | 🟡 Moyenne | Sécurité | CDN sans SRI (Subresource Integrity) | ⚡ Facile |
| 10 | 🟡 Basse | Résilience | Image externe (svgrepo.com) | ⚡ Facile |
| 11 | 🟡 Moyenne | Architecture | Données dupliquées HTML/JS (doctrines) | 🔨 Moyen |
| 12 | 🟡 Basse | SEO | Pas de meta descriptions / Open Graph | ⚡ Facile |
| 13 | 🟡 Moyenne | Accessibilité | Navigation clavier, ARIA, focus trap | 🔨 Moyen |
| 14 | 🟡 Moyenne | UX | Deck Builder difficilement utilisable mobile | 🔨 Long |
| 15 | 🟡 Basse | Performance | vehicles.js chargé globalement (44KB) | 🔨 Moyen |
| 16 | 🟡 Moyenne | Maintenabilité | Regex fragiles dans Indexer.ps1 | 🔨 Long |
| 17 | 🟡 Basse | Hygiène | Fichier .lnk dans le dépôt | ⚡ Facile |
| 18 | 🟡 Basse | Hygiène | Pas de .gitignore | ⚡ Facile |
| 19 | 🟡 Moyenne | UX | Gestion d'erreurs insuffisante | 🔨 Moyen |
| 20 | 🟡 Basse | Architecture | config.json inutilisé | ⚡ Facile |
| 21 | 🟡 Basse | Maintenabilité | Version dupliquée HTML/JS | ⚡ Facile |
| 22 | 🟡 Moyenne | Maintenabilité | 31x `!important` dans deck_style.css | 🔨 Moyen |
| 23 | 🟡 Moyenne | Déploiement | Scripts de tooling déployés publiquement | ⚡ Facile |

---

> **Priorisation suggérée** : Commencer par les items **🔴 1-2** (sécurité), puis **🟠 4, 6, 7** (qualité), puis les items **🟡** selon le temps disponible.
