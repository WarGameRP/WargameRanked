#!/usr/bin/env python3
"""
Script pour remplacer les liens imgur par les chemins d'images locaux
en utilisant le fichier vehicles.json comme référence.
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

def load_vehicle_mapping(json_file):
    """Charge le mapping des véhicules depuis le fichier JSON."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Créer un mapping: nom du véhicule -> chemin image
    vehicle_mapping = {}
    for country, vehicles in data.items():
        for vehicle in vehicles:
            vehicle_name = vehicle['name']
            image_path = vehicle['image_path'].replace('\\', '/')  # Convertir les backslashes en forward slashes
            vehicle_mapping[vehicle_name] = image_path
    
    return vehicle_mapping

def replace_imgur_links_in_html(html_file, vehicle_mapping):
    """Remplace les liens imgur par les chemins locaux dans un fichier HTML."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Trouver tous les éléments vehicleBadge
    badges = soup.find_all('td', class_='vehicleBadge')
    
    replaced_count = 0
    for badge in badges:
        # Extraire le nom du véhicule
        name_span = badge.find('span', class_='vehicleName')
        if not name_span:
            continue
        
        vehicle_name = name_span.get_text(strip=True)
        
        # Trouver l'URL imgur actuelle
        img = badge.find('img')
        if not img or not img.get('src'):
            continue
        
        current_url = img['src']
        
        # Si ce n'est pas une URL imgur, passer
        if 'i.imgur.com' not in current_url:
            continue
        
        # Chercher le chemin local correspondant
        if vehicle_name in vehicle_mapping:
            new_path = vehicle_mapping[vehicle_name]
            img['src'] = new_path
            replaced_count += 1
            print(f"  ✓ Remplacé: {vehicle_name} -> {new_path}")
        else:
            print(f"  ⚠ Véhicule non trouvé dans le mapping: {vehicle_name}")
    
    if replaced_count == 0:
        print(f"  Aucun remplacement effectué dans {html_file.name}")
        return False
    
    # Sauvegarder le fichier modifié
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    
    print(f"  ✓ {replaced_count} lien(s) remplacé(s) dans {html_file.name}")
    return True

def main():
    """Fonction principale."""
    assets_dir = Path(__file__).parent
    json_file = assets_dir / 'vehicles.json'
    
    if not json_file.exists():
        print(f"❌ Erreur: Le fichier {json_file} n'existe pas")
        return
    
    print("Chargement du mapping des véhicules...")
    vehicle_mapping = load_vehicle_mapping(json_file)
    print(f"✓ {len(vehicle_mapping)} véhicules chargés")
    
    # Trouver tous les fichiers HTML
    html_files = list(assets_dir.glob('*.html'))
    
    if not html_files:
        print("⚠ Aucun fichier HTML trouvé")
        return
    
    print(f"\nTraitement de {len(html_files)} fichier(s) HTML...")
    print("=" * 60)
    
    total_replaced = 0
    for html_file in html_files:
        print(f"\nTraitement de {html_file.name}:")
        if replace_imgur_links_in_html(html_file, vehicle_mapping):
            total_replaced += 1
    
    print("\n" + "=" * 60)
    print(f"✓ Terminé! {total_replaced}/{len(html_files)} fichier(s) modifié(s)")

if __name__ == '__main__':
    main()
