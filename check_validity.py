import json
import re
import os

def check_set_validity(set_data):
    sheets = set_data['data']['booster']['arena']['sheets']
    arena_pack_possible_uuids = []
    for _, sheet in sheets.items():
        arena_pack_possible_uuids.extend(sheet['cards'].keys())

    cards = set_data['data']['cards']
    set_cards_uuids = [card['uuid'] for card in cards]

    verdict = set(arena_pack_possible_uuids).issubset(set(set_cards_uuids))
    return verdict

path = os.path.join('sets', 'DMU.json')



for set_json_path in os.listdir('sets'):
    path = os.path.join('sets', set_json_path)
    with open(path, 'r', encoding = 'utf-8') as f:
        set_data = json.loads(f.read())
    validity = check_set_validity(set_data)
    set_name = set_json_path.split('.')[0]
    print(set_name, validity)
