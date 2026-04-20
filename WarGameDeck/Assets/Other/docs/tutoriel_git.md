# Tutoriel Git Complet

Guide complet pour maîtriser Git et GitHub.

---

## Table des matières

1. [Concepts de base](#concepts-de-base)
2. [Configuration initiale](#configuration-initiale)
3. [Commandes essentielles](#commandes-essentielles)
4. [Branches](#branches)
5. [Merge et conflits](#merge-et-conflits)
6. [Stash](#stash)
7. [Annuler des modifications](#annuler-des-modifications)
8. [Travailler avec GitHub](#travailler-avec-github)
9. [Bonnes pratiques](#bonnes-pratiques)

---

## Concepts de base

### Qu'est-ce que Git ?

Git est un système de contrôle de version distribué qui permet de :
- Suivre les modifications de votre code
- Revenir à des versions précédentes
- Travailler en équipe sur le même projet
- Créer des branches pour expérimenter

### Vocabulaire essentiel

- **Repository (repo)** : Dossier contenant votre projet et l'historique Git
- **Commit** : Sauvegarde d'un état du projet
- **Branch** : Version parallèle du projet
- **Merge** : Fusion de deux branches
- **Pull** : Récupérer les modifications d'un serveur distant
- **Push** : Envoyer vos modifications vers un serveur distant
- **Stash** : Mettre de côté temporairement des modifications

---

## Configuration initiale

### Première configuration

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
```

### Vérifier la configuration

```bash
git config --list
```

---

## Commandes essentielles

### Initialiser un repository

```bash
# Créer un nouveau repository Git
git init

# Cloner un repository existant
git clone https://github.com/username/repo.git
```

### Vérifier l'état

```bash
# Voir les fichiers modifiés
git status

# Voir l'historique des commits
git log

# Voir l'historique en mode compact
git log --oneline

# Voir les différences
git diff
```

### Ajouter et commit

```bash
# Ajouter un fichier spécifique
git add fichier.txt

# Ajouter tous les fichiers modifiés
git add .

# Ajouter tous les fichiers (y compris ceux supprimés)
git add -A

# Commiter avec un message
git commit -m "Description des modifications"

# Ajouter et committer en une commande
git commit -am "Message"
```

### Ignorer des fichiers

Créez un fichier `.gitignore` à la racine :

```
# Fichiers système
.DS_Store
Thumbs.db

# Fichiers de configuration
config.local.json
.env

# Dossiers
node_modules/
__pycache__/
*.pyc

# Logs
*.log
```

---

## Branches

### Créer et gérer des branches

```bash
# Créer une nouvelle branche
git branch nom-branche

# Basculer sur une branche
git checkout nom-branche

# Créer et basculer en une commande
git checkout -b nom-branche

# Voir toutes les branches
git branch

# Voir toutes les branches (y compris distantes)
git branch -a

# Renommer la branche actuelle
git branch -m nouveau-nom

# Supprimer une branche locale
git branch -d nom-branche

# Supprimer une branche distante
git push origin --delete nom-branche
```

### Workflow avec branches

```bash
# 1. Créer une branche pour une nouvelle fonctionnalité
git checkout -b feature/nouvelle-fonction

# 2. Travailler et committer
git add .
git commit -m "Ajout de la fonctionnalité"

# 3. Revenir sur main
git checkout main

# 4. Fusionner la branche
git merge feature/nouvelle-fonction

# 5. Supprimer la branche fusionnée
git branch -d feature/nouvelle-fonction
```

---

## Merge et conflits

### Fusionner des branches

```bash
# Fusionner une branche dans la branche actuelle
git merge nom-branche

# Fusionner en créant un commit de fusion
git merge --no-ff nom-branche

# Annuler une fusion (avant commit)
git merge --abort
```

### Résoudre les conflits

Quand un conflit survient, Git marque les fichiers avec des conflits :

```
<<<<<<< HEAD
Votre modification
=======
Modification de l'autre branche
>>>>>>> nom-branche
```

**Comment résoudre :**

1. Ouvrez le fichier en conflit
2. Cherchez les marqueurs `<<<<<<<`, `=======`, `>>>>>>>`
3. Choisissez quelle version garder ou combinez-les
4. Supprimez les marqueurs
5. Sauvegardez le fichier

```bash
# Après résolution
git add fichier-resolu
git commit
```

### Outils pour les conflits

```bash
# Voir les fichiers en conflit
git status

# Utiliser votre version
git checkout --ours fichier

# Utiliser leur version
git checkout --theirs fichier

# Voir les différences
git diff --ours fichier
git diff --theirs fichier
```

---

## Stash

Le stash permet de mettre de côté temporairement des modifications.

```bash
# Stasher les modifications non commitées
git stash

# Stasher avec un message
git stash save "Message descriptif"

# Voir la liste des stashes
git stash list

# Appliquer le dernier stash
git stash pop

# Appliquer un stash spécifique
git stash apply stash@{0}

# Supprimer un stash
git stash drop stash@{0}

# Supprimer tous les stashes
git stash clear

# Créer une branche depuis un stash
git stash branch nom-branche stash@{0}
```

---

## Annuler des modifications

### Annuler des modifications non commitées

```bash
# Annuler les modifications d'un fichier (revenir au dernier commit)
git checkout fichier.txt

# Annuler toutes les modifications
git checkout .

# Annuler les modifications dans le répertoire de travail
git restore fichier.txt
```

### Annuler des commits

```bash
# Annuler le dernier commit (garder les modifications)
git reset --soft HEAD~1

# Annuler le dernier commit (supprimer les modifications)
git reset --hard HEAD~1

# Annuler plusieurs commits
git reset --hard HEAD~3

# Annuler un commit spécifique (garder l'historique)
git revert <hash-du-commit>
```

### Modifier le dernier commit

```bash
# Modifier le message du dernier commit
git commit --amend

# Ajouter des fichiers au dernier commit
git add fichier
git commit --amend --no-edit
```

### Récupérer un commit supprimé

```bash
# Voir les commits supprimés
git reflog

# Récupérer un commit
git reset --hard <hash-du-commit>
```

---

## Travailler avec GitHub

### Cloner un repository

```bash
git clone https://github.com/username/repo.git
```

### Ajouter un remote

```bash
# Ajouter un remote
git remote add origin https://github.com/username/repo.git

# Voir les remotes
git remote -v

# Changer l'URL du remote
git remote set-url origin https://github.com/username/nouveau-repo.git
```

### Push

```bash
# Pousser la branche actuelle
git push

# Pousser une branche spécifique
git push origin nom-branche

# Première poussée d'une nouvelle branche
git push -u origin nom-branche

# Pousser toutes les branches
git push --all

# Forcer le push (attention !)
git push --force
git push --force-with-lease (plus sûr)
```

### Pull

```bash
# Récupérer et fusionner
git pull

# Récupérer sans fusionner
git fetch

# Récupérer et rebase
git pull --rebase
```

### Pull Requests (sur GitHub)

1. Poussez votre branche :
   ```bash
   git push -u origin feature/nouvelle-fonction
   ```

2. Allez sur GitHub et créez une Pull Request

3. Discutez et modifiez si nécessaire

4. Fusionnez la PR

5. Mettez à jour votre local :
   ```bash
   git checkout main
   git pull
   git branch -d feature/nouvelle-fonction
   ```

---

## Bonnes pratiques

### Messages de commit

**Bon format :**
```
Type: description courte

Description détaillée optionnelle

- Point 1
- Point 2
```

**Types courants :**
- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `style:` formatage
- `refactor:` refactoring
- `test:` tests
- `chore:` maintenance

**Exemples :**
```
feat: ajouter la pagination

- Ajout de la pagination sur la liste des decks
- Limite à 20 items par page
```

```
fix: corriger le bug d'affichage des drapeaux

Le problème venait de l'encodage des caractères
```

### Workflow recommandé

1. **Créez une branche par fonctionnalité**
   ```bash
   git checkout -b feature/ma-fonction
   ```

2. **Commitez souvent**
   ```bash
   git add .
   git commit -m "progression"
   ```

3. **Pussez régulièrement**
   ```bash
   git push -u origin feature/ma-fonction
   ```

4. **Synchronisez avec main**
   ```bash
   git checkout main
   git pull
   git checkout feature/ma-fonction
   git merge main
   ```

5. **Créez une Pull Request**
   - Revue de code
   - Tests
   - Fusion

### Éviter

- ❌ Commits trop grands
- ❌ Messages vides ("fix", "update")
- ❌ Force push sur des branches partagées
- ❌ Ignorer les conflits
- ❌ Committer des fichiers temporaires

---

## Commandes rapides

| Action | Commande |
|--------|----------|
| Statut | `git status` |
| Ajouter tout | `git add .` |
| Commit | `git commit -m "msg"` |
| Push | `git push` |
| Pull | `git pull` |
| Nouvelle branche | `git checkout -b nom` |
| Fusionner | `git merge nom` |
| Stash | `git stash` |
| Annuler fichier | `git checkout fichier` |
| Annuler commit | `git reset --hard HEAD~1` |

---

## Ressources utiles

- [Documentation officielle Git](https://git-scm.com/doc)
- [GitHub Learning Lab](https://lab.github.com/)
- [Learn Git Branching](https://learngitbranching.js.org/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

*Document créé pour le projet Wargame Ranked*
