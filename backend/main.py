from flask import Flask, request
from flask_cors import CORS

from os import environ
import requests
import json
import urllib3
import xml.etree.ElementTree as ET

from utils import replace_empty_epreuve

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxy = "https://mute-hill-43b6.cryptoshotgun.workers.dev/"
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
debug = environ.get('DEBUG', False)

session = requests.session()
session.verify = False
session.proxies = {"http": proxy}


@app.route("/api/search", methods=['GET', 'OPTIONS'])
def search():
    surname = request.args.get("surname", "")
    name = request.args.get("name", "")
    url = "https://fftt.dafunker.com/v1//proxy/xml_liste_joueur_o.php"
    response = session.get(url, params={"nom": surname, "prenom": name})
    root = ET.fromstring(response.content)
    players = root.findall('joueur')
    result = []
    for player in players:
        nclub = player.find('nclub').text
        if nclub is None:
            continue
        surname = player.find('nom').text
        name = player.find('prenom').text
        score = player.find('points').text
        license_number = player.find('licence').text
        player_result = {
            'surname': surname,
            'name': name,
            'nclub': nclub,
            'score': score,
            'license': license_number
        }
        # Fix latin-1 encoding
        for k, v in player_result.items():
            player_result[k] = v.replace('’', '\'')
        for k, v in player_result.items():
            if k in ['surname', 'name', 'nclub']:
                player_result[k] = v.encode('iso-8859-1').decode('utf-8')
        result.append(player_result)
    return json.dumps(result[:10]), response.status_code, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/api/player", methods=['GET', 'OPTIONS'])
def get_player_infos():
    license_number = request.args.get("license_number", "")
    url = f"https://fftt.dafunker.com/v1/joueur/{license_number}"
    response = session.get(url)
    content = response.json()
    return json.dumps(content), response.status_code, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/api/matchs", methods=['GET', 'OPTIONS'])
def get_player_matchs():
    license_number = request.args.get("license_number", "")
    url = f"https://fftt.dafunker.com/v1/parties/{license_number}"
    response = session.get(url)
    content = response.json()
    matches_by_epreuve_and_date = replace_empty_epreuve(content)
    return json.dumps(matches_by_epreuve_and_date), response.status_code, \
           {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/api/virtual_score", methods=['GET', 'OPTIONS'])
def get_player_virtual_score():
    license_number = request.args.get("license_number", "")
    url = f"https://fftt.dafunker.com/v1/joueur/{license_number}"
    response = session.get(url)
    content = response.json()
    return json.dumps(
        dict(
            score=round(content.get('pointm')),
        )), response.status_code, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=debug)
