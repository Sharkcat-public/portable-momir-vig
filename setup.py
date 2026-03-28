import requests
import os
import time
from PIL import Image
from io import BytesIO
from urllib import request
# thank you ijson https://github.com/ICRAR/ijson
import ijson

start_time = time.time()
log = open('log.log', 'a')
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

stream_cards = request.urlopen(oracle_cards_uri)
parser = ijson.parse(stream_cards)
i = 0
for card in ijson.items(parser, 'item'):
    if i == 10:
        break
    if ('Creature' in card['type_line']) and ('Token' not in card['type_line']):
        try:
            converted_mana_cost = int(card['cmc'])
            img_uri = card['image_uris']['normal']
            card_path = os.path.join("cards", str(converted_mana_cost), card['name']+'.jpg')
            if os.path.exists(card_path):
                continue
            print(f"Adding {card['name']}")
            os.makedirs(os.path.dirname(card_path), exist_ok=True)
            resp = requests.get(img_uri)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content))
            img = img.convert('L').resize((360,int((360/img.width)*img.height)))
            img.save(card_path)
            i = i + 1
        except Exception as e:
            log.write(f"{time.time()-start_time} Unable to add creature {card.get('name')}\n")
            log.write(str(e))
            log.write('\n')
