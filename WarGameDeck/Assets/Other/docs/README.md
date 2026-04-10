# 📄 Guide des Mises à Jour (Patch Notes)

Ce dossier gère le contenu dynamique du Dashboard (Boutons "Explication des Points" et "Nouveautés").

## 📁 Structure des dossiers

### 1. `Point.md`
Ce fichier contient les règles de doctrine. Il est affiché quand on clique sur **"Explication des Points"**.
- Utilisez du Markdown standard.
- Vous pouvez utiliser des icônes et des listes.

### 2. `Update/LastUpdate/whatsnew.md`
C'est le message qui s'affiche automatiquement à l'ouverture du site pour la version actuelle (Bouton **"Nouveautés"**).
- Modifiez ce fichier pour annoncer votre dernière version.

### 3. `Update/OldUpdate/`
Mettez ici vos anciens fichiers `.md` (ex: `v1.0.4.md`, `v1.0.3.md`).
- Ces fichiers sont **automatiquement détectés** par l'indexeur.
- Ils apparaissent dans la liste "Voir les anciennes mises à jour".
- Pas besoin de modifier manuellement de fichiers JSON.

---

## 🛠️ Comment faire une mise à jour ?

1.  **Nouveautés** : Modifiez `LastUpdate/whatsnew.md` avec votre nouveau contenu.
2.  **Archive** : Si vous voulez garder une trace de l'ancienne version, copiez son contenu dans un nouveau fichier (ex: `v1.1.0.md`) dans le dossier `OldUpdate`.
3.  **Lancement** : Double-cliquez sur `Lancer_WarGame.bat` à la racine pour mettre à jour l'affichage.

---
*Note : Le fichier `updates_list.json` n'est plus utilisé par le nouveau système d'indexation automatique, vous pouvez l'ignorer.*
