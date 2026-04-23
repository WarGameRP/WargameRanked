#!/usr/bin/env python3
"""
Script pour mettre à jour le style des fichiers HTML des decks Wargame Ranked.
Ce script ajoute les liens CSS manquants, l'en-tête avec le logo et le bouton de retour,
et met à jour le padding de la description.
"""

import os
import sys
from pathlib import Path

def update_html_style(html_file_path):
    """Met à jour un fichier HTML pour avoir le même style que les autres fichiers."""

    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remplacer le favicon War Thunder par le logo local
    old_favicon = '<link rel="icon" href="https://warthunder.com/i/favicons/mstile-144x144.png" />'
    new_favicon = '<link rel="icon" href="Other/img/Logo_Ranked.png" />'
    favicon_replaced = False
    if old_favicon in content:
        content = content.replace(old_favicon, new_favicon)
        favicon_replaced = True
        print(f"✓ Remplacé le favicon à {html_file_path}")

    # Vérifier si le fichier a déjà le style
    if 'Other/css/deck_style.css' in content and '<header>' in content and new_favicon in content and not favicon_replaced:
        print(f"✓ {html_file_path} a déjà le bon style")
        return

    # Ajouter les liens CSS dans le head s'ils manquent
    if 'Other/css/deck_style.css' not in content:
        # Trouver la ligne avec le viewport
        viewport_pattern = '<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />'
        css_links = '''    <link rel="stylesheet" href="Other/css/deck_style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'''

        if viewport_pattern in content:
            content = content.replace(viewport_pattern, viewport_pattern + '\n' + css_links)
            print(f"✓ Ajouté les liens CSS à {html_file_path}")

    # Remplacer l'ancien titre par le header si nécessaire
    old_title_pattern = r'<h1 style="text-align: center; border-bottom: 1px solid black; padding: 5px">([^<]+)</h1>'
    old_desc_pattern = r'<div style="max-width: 1000px; margin: auto; padding: 0 3px 0 3px"><p>([^<]+)</p>\n</div>'
    
    import re
    
    # Extraire le nom du pays depuis le titre
    title_match = re.search(old_title_pattern, content)
    desc_match = re.search(old_desc_pattern, content)
    
    if title_match and desc_match and '<header>' not in content:
        country_name = title_match.group(1)
        desc_text = desc_match.group(1)
        
        # Créer le nouveau header et la nouvelle description
        new_header = f'''    <header>
        <div class="header-title">
            <img src="Other/img/Logo_Ranked.png" alt="Logo">
            <h1>Deck : {country_name}</h1>
        </div>
        <a href="../index.html" class="back-btn">&#8592; Retour au Portail</a>
    </header>

    <div style="max-width: 1000px; margin: auto; padding: 20px 3px 0 3px">
        <p style="color: var(--text-muted); text-align: center;">{desc_text}</p>
    </div>'''
        
        # Remplacer l'ancien titre et description
        old_section = f'''<h1 style="text-align: center; border-bottom: 1px solid black; padding: 5px">{country_name}</h1>
        <div style="max-width: 1000px; margin: auto; padding: 0 3px 0 3px"><p>{desc_text}</p>
</div>'''
        
        content = content.replace(old_section, new_header)
        print(f"✓ Ajouté le header à {html_file_path}")
    
    # Écrire le contenu modifié
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ {html_file_path} mis à jour avec succès")

def main():
    """Fonction principale."""
    assets_dir = Path(__file__).parent.parent.parent
    
    # Détecter automatiquement tous les fichiers HTML dans le dossier Assets
    html_files = list(assets_dir.glob('*.html'))
    
    if not html_files:
        print("⚠ Aucun fichier HTML trouvé dans le dossier Assets")
        return
    
    print("Mise à jour du style des fichiers HTML...")
    print("=" * 50)
    print(f"{len(html_files)} fichier(s) HTML trouvé(s)")
    
    for html_path in html_files:
        try:
            update_html_style(html_path)
        except Exception as e:
            print(f"✗ Erreur lors de la mise à jour de {html_path.name}: {e}")
    
    print("=" * 50)
    print("Mise à jour terminée!")

if __name__ == '__main__':
    main()
