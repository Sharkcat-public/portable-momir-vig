import requests
import os
import time
from PIL import Image
from io import BytesIO
from urllib import request
# thank you ijson https://github.com/ICRAR/ijson
import ijson

log = open('log.log', 'a')
log.write(f"\n{time.strftime("%Y-%m-%d %H:%M:%S")} Setup\n")
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
            card_path = os.path.join("cards", str(converted_mana_cost), card['name']+'.jpg')
            if os.path.exists(card_path):
                continue
            print(f"Adding {card['name']}")
            os.makedirs(os.path.dirname(card_path), exist_ok=True)
            if card.get('card_faces') and card.get('card_faces')[0].get('image_uris') and card.get('card_faces')[1].get('image_uris'):
                front_img_uri = card.get('card_faces')[0]['image_uris']['normal']
                back_img_uri = card.get('card_faces')[1]['image_uris']['normal']
                resp = requests.get(front_img_uri)
                front_img = Image.open(BytesIO(resp.content))
                resp = requests.get(back_img_uri)
                back_img = Image.open(BytesIO(resp.content))
                front_img = front_img.convert('L').resize((360,int((360/front_img.width)*front_img.height)))
                back_img = back_img.convert('L').resize((360,int((360/back_img.width)*back_img.height)))
                img = Image.new('L', (front_img.width, front_img.height+back_img.height),'white')
                img.paste(front_img, (0,0))
                img.paste(back_img, (0, front_img.height))
                img.save(card_path)
            elif card.get('image_uris'):
                img_uri = card['image_uris']['normal']
                resp = requests.get(img_uri)
                resp.raise_for_status()
                img = Image.open(BytesIO(resp.content))
                img = img.convert('L').resize((360,int((360/img.width)*img.height)))
                img.save(card_path)
            else:
                print(f"This is a weird card {i} {card.get('name')} Can't add")
            i = i + 1
        except Exception as e:
            log.write(f"{time.strftime("%Y-%m-%d %H:%M:%S")} Unable to add creature {card.get('name')}\n")
            log.write(str(e))
            log.write('\n')
