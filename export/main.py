import os.path
import requests
import urllib3

from datetime import datetime
import json
from lxml import html
from typing import Dict

from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.session()
session.verify = False


URL = 'https://www.fftt.com/site/ajax1?plugins_controller=personsRemoteClassement&plugins_action=plugin_index_ajax'
PLAYER_URL = 'https://www.fftt.com/site/personnes/by-number'

SEX_OPTIONS = [
    'Hommes',
    'Femmes'
]

CATEGORIES = {
    "P": "Poussin",
    "B": "Benjamin",
    "M": "Minimes",
    "C": "Cadets",
    "J": "Juniors",
    "S": "Séniors",
    "V": "Vétérans",
}
CATEGORIES = [cat.lower() for cat in CATEGORIES.keys()]

# if no more option: nat
# optional field for reg  # ligues	"L01"
REGS = {
    "L01": "AUVERGNE RHONE ALPES",
    "L02": "BOURGOGNE FRANCHE COMTE",
    "L03": "BRETAGNE",
    "L04": "CENTRE VAL DE LOIRE",
    "L05": "CORSE",
    "L06": "GRAND EST",
    "L33": "GUADELOUPE.L",
    "L30": "GUYANE.L",
    "L07": "HAUTS DE FRANCE",
    "L08": "ILE DE FRANCE",
    "L34": "LIGUE MARTINIQUE",
    "L36": "MAYOTTE.L",
    "L09": "NORMANDIE",
    "L10": "NOUVELLE AQUITAINE",
    "L32": "NOUVELLE CALEDONIE",
    "L11": "OCCITANIE",
    "L13": "PACA",
    "L12": "PAYS DE LA LOIRE",
    "L31": "REUNION.L",
    "L37": "TAHITI",
    "L38": "WALLIS ET FUTUNA L",
}
# optional field for dep  # departements	"D77"
DEPTS = {
    "D01": "Ain",
    "D02": "Aisne",
    "D03": "Allier",
    "D04": "Alpes Hte Provence",
    "D06": "Alpes Maritimes",
    "D08": "Ardennes",
    "D09": "Ariege",
    "D10": "Aube",
    "D11": "Aude",
    "D12": "Aveyron",
    "D67": "Bas Rhin",
    "D90": "Belfort",
    "D13": "Bouches Du Rhone",
    "D14": "Calvados",
    "D15": "Cantal",
    "D16": "Charente",
    "D17": "Charente Maritime",
    "D18": "Cher",
    "D9B": "Comite Martinique",
    "D9E": "Comite Provincial Nord",
    "D9F": "Comite Provincial Sud",
    "D19": "Correze",
    "D99": "Corse Du Sud",
    "D21": "Cote D'or",
    "D22": "Cotes D Armor",
    "D23": "Creuse",
    "D79": "Deux Sevres",
    "D24": "Dordogne",
    "D25": "Doubs",
    "D26": "Drome/ardeche",
    "D91": "Essonne",
    "D27": "Eure",
    "D28": "Eure Et Loir",
    "D29": "Finistere",
    "D30": "Gard",
    "D32": "Gers",
    "D33": "Gironde",
    "D9A": "Guadeloupe",
    "D9C": "Guyane",
    "D68": "Haut Rhin",
    "D98": "Haute Corse",
    "D31": "Haute Garonne",
    "D70": "Haute Saone",
    "D74": "Haute Savoie",
    "D87": "Haute Vienne",
    "D52": "Haute-marne",
    "D05": "Hautes Alpes",
    "D65": "Hautes Pyrenees",
    "D92": "Hauts De Seine",
    "D34": "Herault",
    "D35": "Ille Et Vilaine",
    "D36": "Indre",
    "D37": "Indre Et Loire",
    "D38": "Isere",
    "D39": "Jura",
    "D40": "Landes",
    "D41": "Loir Et Cher",
    "D44": "Loire Atlantique",
    "D42": "Loire Haute-loire",
    "D45": "Loiret",
    "D46": "Lot",
    "D47": "Lot Et Garonne",
    "D48": "Lozere",
    "D49": "Maine Et Loire",
    "D50": "Manche",
    "D51": "Marne",
    "D53": "Mayenne",
    "D9G": "Mayotte",
    "D54": "Meurthe Et Moselle",
    "D55": "Meuse",
    "D56": "Morbihan",
    "D57": "Moselle",
    "D58": "Nievre",
    "D59": "Nord",
    "D60": "Oise",
    "D61": "Orne",
    "D75": "Paris",
    "D62": "Pas De Calais",
    "D63": "Puy De Dome",
    "D64": "Pyrenees Atlantiques",
    "D66": "Pyrenees Orientales",
    "D9D": "Reunion",
    "D69": "Rhone-lyon Tt",
    "D71": "Saone Et Loire",
    "D72": "Sarthe",
    "D73": "Savoie",
    "D77": "Seine Et Marne",
    "D76": "Seine Maritime",
    "D93": "Seine-saint-denis",
    "D80": "Somme",
    "D9H": "Tahiti",
    "D81": "Tarn",
    "D82": "Tarn Et Garonne",
    "D95": "Val D Oise",
    "D94": "Val De Marne",
    "D83": "Var",
    "D84": "Vaucluse",
    "D85": "Vendee",
    "D86": "Vienne",
    "D88": "Vosges",
    "D9W": "Wallis Et Futuna",
    "D89": "Yonne",
    "D78": "Yvelines",
}

"""
PROGRESS_BAR = tqdm(organisme_ids)
for organisme_id in PROGRESS_BAR:
    update_map_by_organisme_id(organisme_id)

output_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../backend/ranks.json'
)
with open(output_path, 'wb') as f:
    f.write(json.dumps(MAP_RANKS).encode())

"""

def fill_map(map_ranks: Dict, options: Dict[str, str]):
    pagination_current = 1
    pagination_total=None
    if map_ranks.get('stats') is None:
        map_ranks['stats'] = {}
    map_ranks['stats'][json.dumps(options)]=0
    #  rank = 1
    while pagination_total is None or pagination_current <= int(pagination_total):
        data = {
            'pagination-current': pagination_current,
            'classement_type': 'cl',
            'pagination-order': 'CLGLOB ASC',
            'pagination-items': 58,
        }
        for k,v in options.items():
            data[k] = v

        response = session.post(URL, data=data)
        tree = html.fromstring(response.content)

        pagination_total = tree.xpath('//input[@name="pagination-total"]/@value')[0]

        for player in tree.xpath('//ul[@class="plugin-list-large"]/li[contains(@class, "player-view")]'):
            rank = player.xpath('.//div[@class="col-smaller col-flex desktop-display mobile-hide"]/span/text()')[0].strip()
            license_id = player.xpath(
                './/div[@class="col-medium col-flex desktop-hide mobile-display"]/a[contains(@href, "personnes/by-number?number_id=")]/@href'
            )[0].split('=')[-1]

            nom = player.xpath('.//div[@class="col-medium col-flex desktop-display mobile-hide"]/a/text()')[0].strip()
            points = player.xpath('.//div[@class="col-small col-flex"]/div[@class="txt-bold-blue"]/text()')[1].strip()

            """
            if int(points) <= 500:
                continue
            """

            if map_ranks.get(license_id) is not None:
                continue

            map_ranks[license_id] = {
                'options': options,
                'rank': rank,
                'points': int(points),
                'cat': options['categorie'],
                'sex': options['persons_sexe'],
                'page': pagination_current,
                'nom': nom,
            }

            map_ranks['stats'][json.dumps(options)]+=1
            #  rank += 1

        pagination_current += 1
    return map_ranks


if not os.path.exists('../backend/ranks.json'):
    with open('../backend/ranks.json', 'w+') as f:
        f.write('{}')
with open('../backend/ranks.json', 'rb') as f:
    MAP_RANKS = json.loads(f.read())
MAP_RANKS_NAT = MAP_RANKS.get('National', {})
MAP_RANKS_REG = MAP_RANKS.get('Regional', {})
MAP_RANKS_DEP = MAP_RANKS.get('Departemental', {})


print('National')
for sex in SEX_OPTIONS:
    for cat in CATEGORIES:
        options = {
            'persons_sexe': sex,
            'categorie': cat,
        }
        fill_map(MAP_RANKS_NAT, options)
        print((sex, cat, len(MAP_RANKS_NAT)))

print('Régional')
for sex in SEX_OPTIONS:
    for cat in CATEGORIES:
        for ligue_key, ligue_value in REGS.items():
            options = {
                'persons_sexe': sex,
                'categorie': cat,
                'ligues': ligue_key,
            }
            fill_map(MAP_RANKS_REG, options)
            print((sex, cat, ligue_key, ligue_value, len(MAP_RANKS_REG)))

print('Départemental')
for sex in SEX_OPTIONS:
    for cat in CATEGORIES:
        for dep_key, dep_value in DEPTS.items():
            options = {
                'persons_sexe': sex,
                'categorie': cat,
                'departements': dep_key,
            }
            fill_map(MAP_RANKS_DEP, options)
            print((sex, cat, dep_key, dep_value, len(MAP_RANKS_DEP)))

MAP_RANKS = {
    'Date': datetime.now().strftime('%Y-%m-%d-%H-%%M-%S'),
    'National': MAP_RANKS_NAT,
    'Regional': MAP_RANKS_REG,
    'Departemental': MAP_RANKS_DEP,
}
with open('../backend/ranks.json', 'wb') as f:
    f.write(json.dumps(MAP_RANKS).encode())

"""
for license_id in MAP_RANKS_DEP.keys():
    if license_id not in MAP_RANKS_NAT.keys():
        print(license_id)

"""

all_keys = list(set(list(MAP_RANKS_DEP.keys()) + list(MAP_RANKS_REG.keys()) + list(MAP_RANKS_NAT.keys())))
keys_not_in_all = [k for k in all_keys if k not in MAP_RANKS_DEP.keys() or k not in MAP_RANKS_REG.keys() or k not in MAP_RANKS_NAT.keys()]
print("Keys not present in all three dictionaries:")
for i in list(keys_not_in_all)[:5]:
    if MAP_RANKS_DEP.get(i, {}).get('points', 0) <= 500:
        continue
    if MAP_RANKS_REG.get(i, {}).get('points', 0) <= 500:
        continue
    if MAP_RANKS_NAT.get(i, {}).get('points', 0) <= 500:
        continue
    print(i, i in MAP_RANKS_DEP, i in MAP_RANKS_REG, i in MAP_RANKS_NAT)
#  print(keys_not_in_all)