#!/usr/bin/env python3
"""
Script complet qui effectue toutes les mises à jour nécessaires pour les fichiers HTML.
Ce script exécute successivement:
1. update_style.py - Met à jour le style des fichiers HTML
2. download_images.py - Télécharge les images depuis imgur
3. replace_imgur_links.py - Remplace les liens imgur par des chemins locaux
"""

import subprocess
import sys
from pathlib import Path

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
            cwd=Path(__file__).parent,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {script_name}: {e}")
        return False

def main():
    """Fonction principale."""
    print("Script de mise à jour complète des fichiers HTML")
    print("=" * 60)
    print("Ce script va effectuer les opérations suivantes:")
    print("  1. Mettre à jour le style des fichiers HTML")
    print("  2. Télécharger les images depuis imgur")
    print("  3. Remplacer les liens imgur par des chemins locaux")
    print("=" * 60)
    
    results = {}
    
    # Étape 1: Mettre à jour le style
    results['style'] = run_script('update_style.py')
    
    if not results['style']:
        print("\n⚠ La mise à jour du style a échoué ou n'était pas nécessaire")
        print("Continuation avec les étapes suivantes...")
    else:
        print("\n✓ Mise à jour du style terminée")
    
    # Étape 2: Télécharger les images
    results['download'] = run_script('download_images.py')
    
    if not results['download']:
        print("\n❌ Le téléchargement des images a échoué")
        print("Arrêt du script")
        return
    
    print("\n✓ Téléchargement des images terminé")
    
    # Étape 3: Remplacer les liens imgur
    results['replace'] = run_script('replace_imgur_links.py')
    
    if not results['replace']:
        print("\n❌ Le remplacement des liens a échoué")
        return
    
    print("\n✓ Remplacement des liens terminé")
    
    # Résumé
    print("\n" + "=" * 60)
    print("✓ Mise à jour complète terminée avec succès!")
    print("Résumé des opérations:")
    print(f"  - Style HTML: {'✓ Succès' if results['style'] else '⚠ Échoué/Non nécessaire'}")
    print(f"  - Téléchargement images: {'✓ Succès' if results['download'] else '❌ Échoué'}")
    print(f"  - Remplacement liens: {'✓ Succès' if results['replace'] else '❌ Échoué'}")
    print("=" * 60)

if __name__ == '__main__':
    main()
