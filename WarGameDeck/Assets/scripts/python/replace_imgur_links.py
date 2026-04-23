#!/usr/bin/env python3
"""
Script pour remplacer les liens imgur par les chemins d'images locaux
en utilisant le fichier vehicles.json comme référence.
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import sys

# Ensure utf-8 output for emojis in Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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
            print(f"  ✓ Remplacé (HTML): {vehicle_name} -> {new_path}")
        else:
            print(f"  ⚠ Véhicule non trouvé dans le mapping: {vehicle_name}")
    
    # Remplacer aussi les liens imgur dans la constante JavaScript vehicleList
    # Trouver le script contenant vehicleList
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'const vehicleList' in script.string:
            script_content = script.string
            
            # Extraire le JSON vehicleList du script
            # Chercher le début et la fin du tableau JSON
            start_idx = script_content.find('const vehicleList = [')
            if start_idx == -1:
                continue
            
            # Trouver la fin du tableau JSON (le crochet fermant correspondant)
            # Utiliser une approche plus robuste avec comptage de crochets
            bracket_count = 0
            in_string = False
            escape_next = False
            end_idx = start_idx + len('const vehicleList = ')
            
            for i, char in enumerate(script_content[end_idx:], start=end_idx):
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"':
                    in_string = not in_string
                    continue
                if not in_string:
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_idx = i + 1
                            break
            
            if bracket_count != 0:
                print(f"  ⚠ Impossible de trouver la fin du tableau JSON")
                continue
            
            json_str = script_content[start_idx + len('const vehicleList = '):end_idx]
            
            # Nettoyer les entités HTML qui pourraient causer des problèmes de parsing JSON
            # Remplacer les entités HTML courantes par leurs caractères réels
            import html
            json_str = html.unescape(json_str)
            
            try:
                vehicle_list_json = json.loads(json_str)
                
                vehiclelist_replaced_count = 0
                # Pour chaque véhicule dans le JSON, remplacer ses liens imgur
                for vehicle in vehicle_list_json:
                    vehicle_name = vehicle.get('name')
                    if vehicle_name in vehicle_mapping:
                        local_path = vehicle_mapping[vehicle_name]
                        
                        # Remplacer thumbnail
                        if 'thumbnail' in vehicle and 'i.imgur.com' in vehicle['thumbnail']:
                            vehicle['thumbnail'] = local_path
                            vehiclelist_replaced_count += 1
                            print(f"  ✓ Remplacé (vehicleList thumbnail): {vehicle_name}")
                        
                        # Remplacer dans images array
                        if 'images' in vehicle:
                            for img in vehicle['images']:
                                if 'image' in img and 'i.imgur.com' in img['image']:
                                    img['image'] = local_path
                                    vehiclelist_replaced_count += 1
                                if 'thumb' in img and 'i.imgur.com' in img['thumb']:
                                    img['thumb'] = local_path
                                    vehiclelist_replaced_count += 1
                                if 'big' in img and 'i.imgur.com' in img['big']:
                                    img['big'] = local_path
                                    vehiclelist_replaced_count += 1
                
                if vehiclelist_replaced_count > 0:
                    # Replacer le JSON modifié dans le script
                    new_json = json.dumps(vehicle_list_json, ensure_ascii=False)
                    script_content = script_content[:start_idx + len('const vehicleList = ')] + new_json + script_content[end_idx:]
                    script.string = script_content
                    print(f"  ✓ {vehiclelist_replaced_count} lien(s) remplacé(s) dans vehicleList (JavaScript)")
                    replaced_count += vehiclelist_replaced_count
            except json.JSONDecodeError as e:
                print(f"  ⚠ Erreur lors du parsing du JSON vehicleList: {e}")
            break
    
    if replaced_count == 0:
        print(f"  Aucun remplacement effectué dans {html_file.name}")
        return False
    
    # Sauvegarder le fichier modifié
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"  ✓ {replaced_count} lien(s) remplacé(s) dans {html_file.name}")
    return True

def main():
    """Fonction principale."""
    assets_dir = Path(__file__).parent.parent.parent
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
    
    # Update vehicles.json and vehicles.js with new paths
    if total_replaced > 0:
        print("\nMise à jour de vehicles.json et vehicles.js...")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update paths in data
            for country, vehicles in data.items():
                for v in vehicles:
                    if v['name'] in vehicle_mapping:
                        v['image_path'] = vehicle_mapping[v['name']]
            
            # Save JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Save JS
            js_file = assets_dir / 'vehicles.js'
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write("window.VEHICLES_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
            
            print("✓ Fichiers de données mis à jour.")
        except Exception as e:
            print(f"⚠ Erreur lors de la mise à jour des données: {e}")

if __name__ == '__main__':
    main()
