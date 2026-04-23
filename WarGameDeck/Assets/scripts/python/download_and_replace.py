#!/usr/bin/env python3
"""
Script combiné qui télécharge les images depuis imgur puis remplace les liens dans les fichiers HTML.
Ce script exécute successivement download_images.py et replace_imgur_links.py.
"""

import subprocess
import sys
from pathlib import Path

# Ensure utf-8 output for emojis in Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_script(script_name):
    """Exécute un script Python et retourne le code de sortie."""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ Erreur: Le script {script_name} n'existe pas")
        return False
    
    print(f"\n{'=' * 60}")
    print(f"Exécution de {script_name}...")
    print('=' * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {script_name}: {e}")
        return False

def main():
    """Fonction principale."""
    print("Script combiné: Téléchargement des images + Remplacement des liens imgur")
    print("=" * 60)
    
    # Étape 1: Télécharger les images
    download_success = run_script('download_images.py')
    
    if not download_success:
        print("\n❌ Le téléchargement des images a échoué")
        print("Arrêt du script")
        return
    
    print("\n✓ Téléchargement des images terminé")
    
    # Étape 2: Remplacer les liens imgur
    replace_success = run_script('replace_imgur_links.py')
    
    if not replace_success:
        print("\n❌ Le remplacement des liens a échoué")
        return
    
    print("\n✓ Remplacement des liens terminé")
    
    # Étape 3: Mettre à jour les données du Deck Builder
    print(f"\n{'=' * 60}")
    print("Mise à jour des données du Deck Builder...")
    print('=' * 60)
    try:
        subprocess.run(['node', 'scripts/js/extract_vehicles.js'], cwd=Path(__file__).parent.parent.parent)
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour des données: {e}")

    # Résumé
    print("\n" + "=" * 60)
    print("✓ Opérations terminées avec succès!")
    print("  - Images téléchargées")
    print("  - Liens imgur remplacés par les chemins locaux")
    print("=" * 60)

if __name__ == '__main__':
    main()
