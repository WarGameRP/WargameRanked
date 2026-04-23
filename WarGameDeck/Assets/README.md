# Scripts Wargame Ranked Assets

Ce dossier contient des scripts Python pour automatiser la gestion des fichiers HTML et des images du projet Wargame Ranked.

## Script d'Installation

### `setup.bat`
Script d'installation qui vérifie Python et installe les dépendances nécessaires.

**Fonctionnalités:**
- Vérifie si Python est installé
- Installe Python automatiquement via winget si nécessaire
- Installe les dépendances Python (beautifulsoup4, requests)

**Usage:**
Double-cliquez sur `scripts/setup.bat`

## Scripts Individuels

### `download_images.py`
Télécharge les images depuis les URLs imgur dans les fichiers HTML et les organise dans des dossiers par pays.

**Fonctionnalités:**
- Parcourt tous les fichiers HTML du dossier Assets
- Extrait les noms de véhicules et leurs URLs imgur
- Télécharge les images dans `Image/[nom_du_pays]/`
- Crée un fichier `vehicles.json` avec le mapping véhicule → chemin image
- Utilise le téléchargement parallèle pour accélérer le processus
- Génère un fichier `download_log.txt` avec les statistiques

**Usage:**
```bash
python scripts/python/download_images.py
```

Ou double-cliquez sur `scripts/download_images.bat`

### `replace_imgur_links.py`
Remplace les liens imgur par les chemins d'images locaux dans les fichiers HTML.

**Fonctionnalités:**
- Charge le mapping des véhicules depuis `vehicles.json`
- Remplace les liens imgur dans les badges HTML (`<img src="...">`)
- Remplace les liens imgur dans la constante JavaScript `vehicleList` (thumbnail, images array)
- Gère les entités HTML dans le JSON
- Sauvegarde les fichiers modifiés

**Usage:**
```bash
python scripts/python/replace_imgur_links.py
```

Ou double-cliquez sur `scripts/replace_imgur_links.bat`

### `update_style.py`
Met à jour le style des fichiers HTML pour uniformiser l'apparence des decks.

**Fonctionnalités:**
- Ajoute les liens CSS manquants (`deck_style.css`, Google Fonts)
- Remplace l'ancien titre par un header avec logo
- Ajoute le bouton de retour au portail
- Met à jour le padding de la description

**Usage:**
```bash
python scripts/python/update_style.py
```

Ou double-cliquez sur `scripts/update_style.bat`

## Scripts Combinés

### `download_and_replace.py`
Combine le téléchargement des images et le remplacement des liens imgur en une seule opération.

**Fonctionnalités:**
- Exécute `download_images.py` pour télécharger les images et créer `vehicles.json`
- Exécute `replace_imgur_links.py` pour remplacer les liens imgur par les chemins locaux
- Affiche un résumé des opérations effectuées

**Usage:**
```bash
python scripts/python/download_and_replace.py
```

Ou double-cliquez sur `scripts/download_and_replace.bat`

### `full_update.py`
Script complet qui effectue toutes les mises à jour nécessaires: style, téléchargement d'images, et remplacement des liens.

**Fonctionnalités:**
- Exécute `update_style.py` pour uniformiser le style HTML
- Exécute `download_images.py` pour télécharger les images
- Exécute `replace_imgur_links.py` pour remplacer les liens imgur
- Affiche un rapport complet de toutes les opérations

**Usage:**
```bash
python scripts/python/full_update.py
```

Ou double-cliquez sur `scripts/full_update.bat`

## Flux de Travail Recommandé

Pour un nouveau deck ou une mise à jour complète:

1. **Créer/modifier le fichier HTML** avec les données du deck
2. **Exécuter `full_update.py`** pour:
   - Mettre à jour le style
   - Télécharger toutes les images
   - Remplacer les liens imgur par des chemins locaux

Pour une mise à jour rapide des images uniquement:

1. **Exécuter `download_and_replace.py`** pour:
   - Télécharger les nouvelles images
   - Mettre à jour les liens dans les fichiers HTML

## Dépendances

Tous les scripts nécessitent les packages Python suivants:
```bash
pip install beautifulsoup4 requests
```

## Structure des Dossiers

```
Assets/
├── scripts/                  # Dossier des scripts
│   ├── python/              # Scripts Python
│   │   ├── download_images.py
│   │   ├── replace_imgur_links.py
│   │   ├── update_style.py
│   │   ├── download_and_replace.py
│   │   └── full_update.py
│   ├── setup.bat            # Script d'installation
│   ├── download_images.bat
│   ├── replace_imgur_links.bat
│   ├── update_style.bat
│   ├── download_and_replace.bat
│   └── full_update.bat
├── Image/                    # Dossiers d'images par pays
│   ├── afrique_du_sud/
│   ├── chine/
│   ├── france/
│   ├── japon/
│   ├── ranked_basique/
│   └── south_korea/
├── Other/                    # Ressources partagées
│   ├── css/
│   └── img/
├── *.html                    # Fichiers HTML des decks
├── vehicles.json             # Mapping véhicule → chemin image
├── download_log.txt          # Log des téléchargements
└── README.md                 # Documentation des scripts
```
