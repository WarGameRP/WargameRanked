# Dashboard WarGameDeck v1.1.1

Mise a jour mineure avec de nouveaux outils d'automatisation.

## Nouveaux outils

### Script de mise a jour du style
- Creation du script Python `update_style.py` pour standardiser le style des fichiers HTML
- Ajout du fichier batch `update_style.bat` pour un lancement simplifie
- Le script detecte automatiquement les fichiers qui necessitent une mise a jour et applique le style uniforme (CSS, en-tete, padding)

### Documentation
- Mise a jour du README.md avec les instructions pour utiliser le script de mise a jour du style
- Creation d'un guide de documentation dans `Other/docs/README.md` pour expliquer le systeme de mises a jour

## Fonctionnalites

Le script `update_style.py` effectue les actions suivantes :
- Ajoute les liens CSS manquants (deck_style.css et Google Fonts)
- Ajoute l'en-tete avec le logo et le bouton de retour au portail
- Met a jour le padding de la description
- Traite automatiquement tous les fichiers HTML du dossier Assets

---
*Le systeme continue d'evoluer pour une experience utilisateur optimisee.*
