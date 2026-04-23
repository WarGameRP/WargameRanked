#!/usr/bin/env python3
"""
Script pour télécharger les images depuis i.imgur.com et les placer dans les dossiers appropriés.
Ce script parcourt tous les fichiers HTML, extrait les URLs imgur, et télécharge les images
dans le dossier Assets/Image/[nom_du_pays]/ avec les noms de véhicules.
"""

import os
import re
import requests
import time
import json
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import sys

# Ensure utf-8 output for emojis in Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_image_name_from_url(url):
    """Extrait le nom de l'image depuis l'URL imgur."""
    parsed = urlparse(url)
    path = parsed.path
    # Supprimer l'extension si elle existe
    name = path.rstrip('.png').rstrip('.jpg').rstrip('.jpeg').rstrip('.gif')
    # Extraire juste le nom de fichier
    name = name.split('/')[-1]
    return name + '.png'

def sanitize_filename(name):
    """Nettoie le nom du véhicule pour l'utiliser comme nom de fichier."""
    # Remplacer les caractères invalides par des underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Remplacer les espaces par des underscores
    sanitized = sanitized.replace(' ', '_')
    # Supprimer les caractères non alphanumériques sauf underscore et tiret
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', sanitized)
    return sanitized

def extract_vehicle_data(html_content):
    """Extrait les noms de véhicules et leurs URLs imgur depuis le HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    vehicle_data = []
    
    # Trouver tous les éléments vehicleBadge
    badges = soup.find_all('td', class_='vehicleBadge')
    
    for badge in badges:
        # Extraire le nom du véhicule
        name_span = badge.find('span', class_='vehicleName')
        if name_span:
            vehicle_name = name_span.get_text(strip=True)
        else:
            continue
        
        # Extraire l'URL de l'image
        img = badge.find('img')
        if img and img.get('src'):
            img_url = img['src']
            if 'i.imgur.com' in img_url:
                vehicle_data.append({
                    'name': vehicle_name,
                    'url': img_url
                })
    
    return vehicle_data

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

def process_html_file(html_file_path, image_base_dir):
    """Traite un fichier HTML et télécharge ses images avec les noms de véhicules."""
    with open(html_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Déterminer le nom du dossier basé sur le nom du fichier HTML
    html_name = html_file_path.stem
    # Normaliser le nom pour le dossier
    folder_name = html_name.lower().replace(' ', '_').replace('-', '_')
    
    # Créer le dossier de destination
    dest_dir = image_base_dir / folder_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Extraire les données de véhicules (nom + URL)
    vehicle_data = extract_vehicle_data(content)
    
    if not vehicle_data:
        print(f"⚠ Aucune image imgur trouvée dans {html_file_path.name}")
        return {'file': html_file_path.name, 'country': folder_name, 'total': 0, 'downloaded': 0, 'skipped': 0, 'errors': [], 'vehicles': []}
    
    print(f"\nTraitement de {html_file_path.name}:")
    print(f"  {len(vehicle_data)} véhicule(s) trouvé(s)")
    
    downloaded = 0
    skipped = 0
    errors = []
    vehicles = []
    
    # Préparer la liste des téléchargements
    download_tasks = []
    for vehicle in vehicle_data:
        vehicle_name = vehicle['name']
        url = vehicle['url']
        
        # Sanitizer le nom du véhicule pour le nom de fichier
        sanitized_name = sanitize_filename(vehicle_name)
        image_name = f"{sanitized_name}.png"
        dest_path = dest_dir / image_name
        
        # Ne pas télécharger si le fichier existe déjà
        if dest_path.exists():
            print(f"  ⊘ {vehicle_name} ({image_name}) existe déjà")
            downloaded += 1
            skipped += 1
            vehicles.append({
                'name': vehicle_name,
                'image_path': 'Image/' + str(dest_path.relative_to(image_base_dir))
            })
            continue
        
        # Si l'URL n'est pas imgur, essayer de trouver l'image locale correspondante
        if 'i.imgur.com' not in url:
            # Chercher si une image avec le nom du véhicule existe déjà
            existing_images = list(dest_dir.glob('*.png'))
            for existing_img in existing_images:
                if sanitized_name in existing_img.stem:
                    vehicles.append({
                        'name': vehicle_name,
                        'image_path': 'Image/' + str(existing_img.relative_to(image_base_dir))
                    })
                    downloaded += 1
                    skipped += 1
                    print(f"  ⊘ {vehicle_name} utilise image existante: {existing_img.name}")
                    break
            continue
        
        download_tasks.append((url, dest_path, vehicle_name, image_name))
    
    # Télécharger en parallèle avec ThreadPoolExecutor
    if download_tasks:
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_vehicle = {executor.submit(download_image, url, dest_path): (name, img_name) for url, dest_path, name, img_name in download_tasks}
            for future in as_completed(future_to_vehicle):
                vehicle_name, image_name = future_to_vehicle[future]
                try:
                    if future.result():
                        downloaded += 1
                        # Trouver le chemin relatif depuis image_base_dir
                        dest_path = dest_dir / image_name
                        vehicles.append({
                            'name': vehicle_name,
                            'image_path': 'Image/' + str(dest_path.relative_to(image_base_dir))
                        })
                    else:
                        errors.append(vehicle_name)
                except Exception as e:
                    errors.append(vehicle_name)
                    print(f"  ✗ Erreur pour {vehicle_name}: {e}")
    
    print(f"  Téléchargement terminé: {downloaded}/{len(vehicle_data)} images")
    return {'file': html_file_path.name, 'country': folder_name, 'total': len(vehicle_data), 'downloaded': downloaded, 'skipped': skipped, 'errors': errors, 'vehicles': vehicles}

def main():
    """Fonction principale."""
    assets_dir = Path(__file__).parent.parent.parent
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
    all_vehicles_by_country = {}
    
    for html_path in html_files:
        try:
            stats = process_html_file(html_path, image_base_dir)
            download_stats.append(stats)
            total_downloaded += stats['downloaded']
            total_skipped += stats['skipped']
            total_errors += len(stats['errors'])
            
            # Collecter les véhicules par pays
            if 'country' in stats and stats['vehicles']:
                country = stats['country']
                if country not in all_vehicles_by_country:
                    all_vehicles_by_country[country] = []
                all_vehicles_by_country[country].extend(stats['vehicles'])
        except Exception as e:
            print(f"✗ Erreur lors du traitement de {html_path.name}: {e}")
            download_stats.append({'file': html_path.name, 'country': 'unknown', 'total': 0, 'downloaded': 0, 'skipped': 0, 'errors': [str(e)], 'vehicles': []})
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
    
    # Save or Merge JSON
    json_file = assets_dir / 'vehicles.json'
    existing_data = {}
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"⚠ Impossible de lire le JSON existant: {e}")

    # Merge new vehicle image paths into existing data
    for country, vehicles in all_vehicles_by_country.items():
        # Match country name (some might be slightly different in case or underscores)
        # We try to find the best match in existing_data
        target_country = country
        for existing_country in existing_data.keys():
            if existing_country.lower().replace(' ', '_') == country.lower().replace(' ', '_'):
                target_country = existing_country
                break
        
        if target_country not in existing_data:
            existing_data[target_country] = []
        
        # For each vehicle found in this country
        for new_v in vehicles:
            found = False
            for old_v in existing_data[target_country]:
                if old_v['name'] == new_v['name']:
                    old_v['image_path'] = new_v['image_path']
                    found = True
                    break
            if not found:
                # Add new vehicle if not exists
                existing_data[target_country].append(new_v)
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    # Also update vehicles.js for the web app
    js_file = assets_dir / 'vehicles.js'
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write("window.VEHICLES_DATA = " + json.dumps(existing_data, ensure_ascii=False, indent=2) + ";")

    print(f"✓ JSON et JS mis à jour: {json_file}, {js_file}")
    print(f"  {sum(len(v) for v in existing_data.values())} véhicules au total")

if __name__ == '__main__':
    main()
