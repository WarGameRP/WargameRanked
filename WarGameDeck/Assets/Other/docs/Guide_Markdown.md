# Guide de Rédaction Markdown pour WarGameDeck

Ce guide explique comment utiliser les différents éléments Markdown pour créer des notes de mise à jour ou des explications de points.

## Structure de Base

### Titres
Utilisez le caractère `#` suivi d'un espace pour les titres.
```md
# Titre Principal (H1)
## Sous-titre (H2)
### Sous-sous-titre (H3)
```

### Mise en forme du texte
- **Gras** : `**texte**`
- *Italique* : `*texte*`
- ~~Barré~~ : `~~texte~~`

---

## Éléments Avancés

### Listes
**Liste à puces :**
- Élément 1
- Élément 2
  - Sous-élément

**Liste numérotée :**
1. Premier
2. Deuxième

### Citations (Blocks)
Utile pour mettre en avant une règle ou une doctrine :
`> Ceci est une citation ou une règle importante.`

### Séparateurs
Utilisez `---` sur une ligne vide pour créer une ligne horizontale.

### Tableaux
```md
| Catégorie | Crédits |
| :--- | :---: |
| Infanterie | 12 |
| Blindés | 0 |
```

### Code et Syntaxe
Pour du texte en chasse fixe (comme un nom de fichier) : `` `mon_fichier.html` ``.

---

## Où placer les fichiers ?

1. **Dernière MAJ** : Placez votre fichier dans `Assets/Other/Update/LastUpdate/whatsnew.md`.
2. **Archives** : Déplacez les anciens fichiers dans `Assets/Other/Update/OldUpdate/` (ex: `v1.0.9.md`).
3. **Points** : Modifiez directement `Assets/Other/Point.md`.

*Note : N'oubliez pas de lancer `Lancer_WarGame.bat` pour que l'application détecte les nouveaux fichiers !*
