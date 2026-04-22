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
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        # Ajouter un user-agent pour éviter le blocage
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=30, headers=headers)
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
        return {'file': html_file_path.name, 'total': 0, 'downloaded': 0, 'skipped': 0, 'errors': []}
    
    print(f"\nTraitement de {html_file_path.name}:")
    print(f"  {len(imgur_urls)} image(s) trouvée(s)")
    
    downloaded = 0
    skipped = 0
    errors = []
    
    # Préparer la liste des téléchargements
    download_tasks = []
    for url in imgur_urls:
        image_name = get_image_name_from_url(url)
        dest_path = dest_dir / image_name
        
        # Ne pas télécharger si le fichier existe déjà
        if dest_path.exists():
            print(f"  ⊘ {image_name} existe déjà")
            downloaded += 1
            skipped += 1
            continue
        
        download_tasks.append((url, dest_path, image_name))
    
    # Télécharger en parallèle avec ThreadPoolExecutor
    if download_tasks:
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_name = {executor.submit(download_image, url, dest_path): name for url, dest_path, name in download_tasks}
            for future in as_completed(future_to_name):
                image_name = future_to_name[future]
                try:
                    if future.result():
                        downloaded += 1
                    else:
                        errors.append(image_name)
                except Exception as e:
                    errors.append(image_name)
                    print(f"  ✗ Erreur pour {image_name}: {e}")
    
    print(f"  Téléchargement terminé: {downloaded}/{len(imgur_urls)} images")
    return {'file': html_file_path.name, 'total': len(imgur_urls), 'downloaded': downloaded, 'skipped': skipped, 'errors': errors}

def main():
    """Fonction principale."""
    assets_dir = Path(__file__).parent
    image_base_dir = assets_dir / 'Image'
    
    # Détecter automatiquement tous les fichiers HTML dans le dossier Assets
    html_files = list(assets_dir.glob('*.html'))
    
    if not html_files:
        print("⚠ Aucun fichier HTML trouvé dans le dossier Assets")
        return
    
    print("Téléchargement des images depuis i.imgur.com...")
    print("=" * 60)
    print(f"{len(html_files)} fichier(s) HTML trouvé(s)")
    
    # Collecter les statistiques de téléchargement
    download_stats = []
    total_downloaded = 0
    total_skipped = 0
    total_errors = 0
    
    for html_path in html_files:
        try:
            stats = process_html_file(html_path, image_base_dir)
            download_stats.append(stats)
            total_downloaded += stats['downloaded']
            total_skipped += stats['skipped']
            total_errors += len(stats['errors'])
        except Exception as e:
            print(f"✗ Erreur lors du traitement de {html_path.name}: {e}")
            download_stats.append({'file': html_path.name, 'total': 0, 'downloaded': 0, 'skipped': 0, 'errors': [str(e)]})
            total_errors += 1
    
    print("=" * 60)
    print("Téléchargement terminé!")
    
    # Créer le fichier log
    log_file = assets_dir / 'download_log.txt'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"Rapport de téléchargement d'images\n")
        f.write(f"Date: {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total fichiers HTML traités: {len(html_files)}\n")
        f.write(f"Total images téléchargées: {total_downloaded}\n")
        f.write(f"Total images ignorées (existantes): {total_skipped}\n")
        f.write(f"Total erreurs: {total_errors}\n\n")
        f.write("=" * 60 + "\n")
        f.write("Détails par fichier:\n")
        f.write("=" * 60 + "\n\n")
        
        for stats in download_stats:
            f.write(f"Fichier: {stats['file']}\n")
            f.write(f"  Images trouvées: {stats['total']}\n")
            f.write(f"  Téléchargées: {stats['downloaded']}\n")
            f.write(f"  Ignorées: {stats['skipped']}\n")
            if stats['errors']:
                f.write(f"  Erreurs: {len(stats['errors'])}\n")
                for error in stats['errors']:
                    f.write(f"    - {error}\n")
            f.write("\n")
        
        f.write("=" * 60 + "\n")
        f.write("Fin du rapport\n")
    
    print(f"✓ Log créé: {log_file}")

if __name__ == '__main__':
    main()
