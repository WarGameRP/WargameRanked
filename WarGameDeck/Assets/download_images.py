#!/usr/bin/env python3
"""
Script pour télécharger les images depuis i.imgur.com et les placer dans les dossiers appropriés.
Ce script parcourt tous les fichiers HTML, extrait les URLs imgur, et télécharge les images
dans le dossier Assets/Image/[nom_du_pays]/.
"""

import os
import re
import requests
import time
from pathlib import Path
from urllib.parse import urlparse

def get_image_name_from_url(url):
    """Extrait le nom de l'image depuis l'URL imgur."""
    parsed = urlparse(url)
    path = parsed.path
    # Supprimer l'extension si elle existe
    name = path.rstrip('.png').rstrip('.jpg').rstrip('.jpeg').rstrip('.gif')
    # Extraire juste le nom de fichier
    name = name.split('/')[-1]
    return name + '.png'

def download_image(url, destination_path):
    """Télécharge une image depuis une URL et la sauvegarde."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Créer le dossier parent si nécessaire
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(destination_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Téléchargé: {destination_path.name}")
        return True
    except Exception as e:
        print(f"✗ Erreur lors du téléchargement de {url}: {e}")
        return False

def extract_imgur_urls(html_content):
    """Extrait toutes les URLs imgur d'un contenu HTML."""
    # Pattern pour trouver les URLs imgur dans les balises img
    pattern = r'https://i\.imgur\.com/[a-zA-Z0-9]+\.(?:png|jpg|jpeg|gif)'
    urls = re.findall(pattern, html_content)
    return list(set(urls))  # Supprimer les doublons

def process_html_file(html_file_path, image_base_dir):
    """Traite un fichier HTML et télécharge ses images."""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Déterminer le nom du dossier basé sur le nom du fichier HTML
    html_name = html_file_path.stem
    # Normaliser le nom pour le dossier
    folder_name = html_name.lower().replace(' ', '_').replace('-', '_')
    
    # Créer le dossier de destination
    dest_dir = image_base_dir / folder_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Extraire les URLs imgur
    imgur_urls = extract_imgur_urls(content)
    
    if not imgur_urls:
        print(f"⚠ Aucune image imgur trouvée dans {html_file_path.name}")
        return
    
    print(f"\nTraitement de {html_file_path.name}:")
    print(f"  {len(imgur_urls)} image(s) trouvée(s)")
    
    downloaded = 0
    for url in imgur_urls:
        image_name = get_image_name_from_url(url)
        dest_path = dest_dir / image_name
        
        # Ne pas télécharger si le fichier existe déjà
        if dest_path.exists():
            print(f"  ⊘ {image_name} existe déjà")
            downloaded += 1
            continue
        
        if download_image(url, dest_path):
            downloaded += 1
    
    print(f"  Téléchargement terminé: {downloaded}/{len(imgur_urls)} images")

def main():
    """Fonction principale."""
    assets_dir = Path(__file__).parent
    image_base_dir = assets_dir / 'Image'
    
    # Liste des fichiers HTML à traiter
    html_files = [
        'france.html',
        'japon.html',
        'South Korea.html',
        'ranked_basique.html',
        'afrique_du_sud.html',
        'chine.html'
    ]
    
    print("Téléchargement des images depuis i.imgur.com...")
    print("=" * 60)
    
    total_downloaded = 0
    for html_file in html_files:
        html_path = assets_dir / html_file
        if html_path.exists():
            try:
                process_html_file(html_path, image_base_dir)
            except Exception as e:
                print(f"✗ Erreur lors du traitement de {html_file}: {e}")
        else:
            print(f"⚠ {html_file} n'existe pas")
    
    print("=" * 60)
    print("Téléchargement terminé!")

if __name__ == '__main__':
    main()
