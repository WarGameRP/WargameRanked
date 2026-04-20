# Git - Les Bases Essentielles

Guide rapide pour comprendre Git et les commandes essentielles.

---

## Pourquoi utiliser Git ?

Git est un **système de contrôle de version** qui permet de :

- ✅ **Sauvegarder l'historique** de votre code (comme une machine à remonter le temps)
- ✅ **Travailler en équipe** sans écraser le travail des autres
- ✅ **Revenir en arrière** si une modification casse quelque chose
- ✅ **Créer des branches** pour expérimenter sans risquer le code principal
- ✅ **Collaborer** facilement via GitHub, GitLab, etc.

**En résumé :** Git est votre assurance-vie pour le code.

---

## Concepts fondamentaux

### Repository (Repo)
Dossier contenant votre projet et tout son historique Git.

### Commit
Une "photo" de votre projet à un moment donné. C'est une sauvegarde avec un message expliquant ce qui a changé.

### Branch
Une version parallèle de votre projet. Vous pouvez travailler sur une branche sans affecter le code principal.

### Merge
Action de fusionner deux branches ensemble.

### Stash
Mettre temporairement vos modifications de côté pour les récupérer plus tard.

---

## Les commandes essentielles

### 1. Commit (Sauvegarder)

```bash
# Voir ce qui a changé
git status

# Ajouter les fichiers à sauvegarder
git add fichier.txt
git add .  # Tous les fichiers

# Sauvegarder avec un message
git commit -m "Description de ce que j'ai fait"

# Ajouter et sauvegarder en une commande
git commit -am "Message"
```

**Quand commit ?**
- Après chaque fonctionnalité terminée
- Après avoir corrigé un bug
- Avant de faire quelque chose de risqué

---

### 2. Merge (Fusionner)

```bash
# Basculer sur la branche principale
git checkout main

# Fusionner une autre branche
git merge nom-branche
```

**À savoir :**
- Si des modifications conflictuelles existent, Git vous demandera de les résoudre
- Après résolution : `git add` puis `git commit`

---

### 3. Uncommit (Annuler un commit)

```bash
# Annuler le dernier commit mais GARDER les modifications
git reset --soft HEAD~1

# Annuler le dernier commit et SUPPRIMER les modifications
git reset --hard HEAD~1

# Annuler un commit spécifique (créer un nouveau commit inverse)
git revert <hash-du-commit>
```

**Quand utiliser ?**
- Si vous avez commit par erreur
- Si le message du commit est mauvais
- Si vous voulez corriger quelque chose

---

### 4. Stash (Mettre de côté)

```bash
# Mettre les modifications non commitées de côté
git stash

# Mettre avec un message
git stash save "Travail en cours"

# Voir les stashes
git stash list

# Récupérer le dernier stash
git stash pop

# Récupérer un stash spécifique
git stash apply stash@{0}

# Supprimer un stash
git stash drop stash@{0}
```

**Quand utiliser ?**
- Quand vous devez changer de branche mais avez des modifications non terminées
- Quand vous voulez tester quelque chose rapidement sans perdre votre travail actuel

---

### 5. Branch (Créer une branche)

```bash
# Créer une nouvelle branche
git branch nom-branche

# Basculer sur une branche
git checkout nom-branche

# Créer et basculer en une commande
git checkout -b nom-branche

# Supprimer une branche
git branch -d nom-branche
```

**Pourquoi utiliser des branches ?**
- Travailler sur une nouvelle fonctionnalité sans casser le code principal
- Tester des idées sans risques
- Travailler sur plusieurs choses en même temps

---

### 6. Push et Pull (GitHub)

```bash
# Envoyer vos commits vers GitHub
git push

# Récupérer les modifications de GitHub
git pull

# Première fois : créer la branche sur GitHub
git push -u origin nom-branche
```

---

## Workflow typique

```bash
# 1. Créer une branche pour votre travail
git checkout -b feature/ma-fonction

# 2. Travailler et commit régulièrement
git add .
git commit -m "Ajout de X"

# 3. Si besoin, mettre de côté et changer de branche
git stash
git checkout main
git checkout feature/ma-fonction
git stash pop

# 4. Quand terminé, fusionner
git checkout main
git merge feature/ma-fonction

# 5. Envoyer sur GitHub
git push

# 6. Si erreur, annuler
git reset --soft HEAD~1
```

---

## Commandes rapides

| Action | Commande |
|--------|----------|
| Voir l'état | `git status` |
| Ajouter tout | `git add .` |
| Commit | `git commit -m "msg"` |
| Annuler fichier | `git checkout fichier` |
| Annuler commit | `git reset --soft HEAD~1` |
| Stash | `git stash` |
| Récupérer stash | `git stash pop` |
| Nouvelle branche | `git checkout -b nom` |
| Fusionner | `git merge nom` |
| Push | `git push` |
| Pull | `git pull` |

---

## Erreurs courantes

### "Nothing to commit"
Vous n'avez pas de modifications à sauvegarder.

**Solution :** Vérifiez avec `git status` pour voir ce qui a changé.

### "Merge conflict"
Deux personnes ont modifié la même ligne du même fichier.

**Solution :**
1. Ouvrez le fichier en conflit
2. Choisissez quelle version garder
3. Supprimez les marqueurs `<<<<<<<`, `=======`, `>>>>>>>`
4. `git add fichier` puis `git commit`

### "Your branch is behind"
Votre branche locale est en retard sur GitHub.

**Solution :** `git pull` pour récupérer les modifications.

---

## Bonnes pratiques

- ✅ **Commitez souvent** - petits commits avec des messages clairs
- ✅ **Utilisez des branches** - une branche par fonctionnalité
- ✅ **Messages clairs** - "fix: corriger le bug X" au lieu de "fix"
- ✅ **Ne committez pas de secrets** - mots de passe, API keys
- ✅ **Pull avant de push** - évitez les conflits

---

## Pour aller plus loin

Voir le tutoriel complet : `tutoriel_git.md`

---

*Document créé pour le projet Wargame Ranked*
