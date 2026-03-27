import requests
import os
from PIL import Image
from io import BytesIO

# get bulk data (metadata about all bulk data jsons)
# https://scryfall.com/docs/api/bulk-data
print("getting bulk data")
resp = requests.get("https://api.scryfall.com/bulk-data")
resp.raise_for_status()
bulk_data = resp.json()
# get uri for oracle cards
# A JSON file containing one Scryfall card object for each Oracle ID on Scryfall. The chosen sets for the cards are an attempt to return the most up-to-date recognizable version of the card
oracle_cards_uri = ""
for data in bulk_data['data']:
    if data['name'] == 'Oracle Cards':
        oracle_cards_uri = data['download_uri']
        break
        

print("Getting oracle cards")
resp = requests.get(oracle_cards_uri)
resp.raise_for_status()
oracle_cards = resp.json()
resp = None

for card in oracle_cards[:50]:
    if 'Creature' in card['type_line']:
        print(f"Adding {card['name']}")
        converted_mana_cost = int(card['cmc'])
        img_uri = card['image_uris']['normal']
        card_path = os.path.join("cards", str(converted_mana_cost), card['name']+'.jpg')
        os.makedirs(os.path.dirname(card_path), exist_ok=True)
        resp = requests.get(img_uri)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        img = img.convert('L').resize((360,int((360/img.width)*img.height)))
        img.save(card_path)
        
        
        