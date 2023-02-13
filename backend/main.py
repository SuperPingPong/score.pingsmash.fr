from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import codecs
import requests
from lxml.html import fromstring
import random
import json
import urllib3
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxy = "https://mute-hill-43b6.cryptoshotgun.workers.dev/"
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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
@cross_origin(origin='*', headers=['Content-Type'])
def get_player():
    license_number = request.args.get("license_number", "")
    url = f"https://fftt.dafunker.com/v1/joueur/{license_number}"
    response = session.get(url)
    content = response.json()
    return json.dumps(content), response.status_code, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
