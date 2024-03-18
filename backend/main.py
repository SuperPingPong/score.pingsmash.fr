from flask import Flask, request
from flask_cors import CORS
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from os import environ
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import urllib3
import xml.etree.ElementTree as ET

from utils import replace_empty_epreuve, find_category

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
debug = environ.get('DEBUG', False)

SENTRY_DSN = environ.get('SENTRY_DSN')
if SENTRY_DSN is None:
    raise Exception('Please configure environment variable SENTRY_DSN')
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[FlaskIntegration()]
)
sentry_sdk.set_tag("app", "fftt-score")

with open('ranks.json', 'rb') as f:
    MAP_RANKS = json.loads(f.read())

# Error handler for other exceptions
@app.errorhandler(Exception)
def handle_exception(error):
    sentry_sdk.capture_exception(error)
    if debug:
        print(error)
    if not hasattr(error, 'code'):
        error_code = 500
    else:
        error_code = error.code
    if not hasattr(error, 'description'):
        error_description = ''
    else:
        error_description = error.description
    return error_description, error_code

retry_strategy = Retry(
    total=3, #  Maximum number of retries
    backoff_factor=0.3, #  Exponential backoff factor
    status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
)

session = requests.session()
session.verify = False
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('http://', adapter)
session.mount('https://', adapter)


@app.route("/api/search", methods=['GET', 'OPTIONS'])
def search():
    surname = request.args.get("surname", "")
    name = request.args.get("name", "")
    url = "https://fftt.dafunker.com/v1//proxy/xml_liste_joueur_o.php"
    response = session.get(url, params={"nom": surname, "prenom": name})
    root = ET.fromstring(response.content.replace(b'ISO-8859-1', b'UTF-8'))
    players = root.findall('joueur')
    result = []
    for player in players:
        nclub = player.find('nclub').text
        if nclub is None:
            continue
        surname = player.find('nom').text.strip()
        name = player.find('prenom').text.strip()
        score = player.find('points').text
        license_number = player.find('licence').text
        player_result = {
            'surname': surname,
            'name': name,
            'nclub': nclub,
            'score': score,
            'license': license_number
        }
        for k, v in player_result.items():
            if k in ['surname', 'name', 'nclub']:
                player_result[k] = v
        result.append(player_result)
    return json.dumps(result[:10]), response.status_code, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/api/player", methods=['GET', 'OPTIONS'])
def get_player_infos():
    license_number = request.args.get("license_number", "")
    url = f"https://fftt.dafunker.com/v1/joueur/{license_number}"
    response = session.get(url)

    content = response.json()
    content_category = content.get('cat')
    content['category'] = find_category(content_category)

    content['rangnat_cat'] = MAP_RANKS['National'].get(license_number, {}).get('rank')
    if content['rangnat_cat'] and isinstance(content['rangnat_cat'], str):
        rang_nat_options = MAP_RANKS['National'][license_number]['options']
        max_rank_nat = MAP_RANKS['National']['stats'][json.dumps(rang_nat_options)]
        content['rangnat_cat'] += '/' + str(max_rank_nat)
    content['rangreg_cat'] = MAP_RANKS['Regional'].get(license_number, {}).get('rank')
    if content['rangreg_cat'] and isinstance(content['rangreg_cat'], str):
        rang_reg_options = MAP_RANKS['Regional'][license_number]['options']
        max_rank_reg = MAP_RANKS['Regional']['stats'][json.dumps(rang_reg_options)]
        content['rangreg_cat'] += '/' + str(max_rank_reg)
    content['rangdep_cat'] = MAP_RANKS['Departemental'].get(license_number, {}).get('rank')
    if content['rangdep_cat'] and isinstance(content['rangdep_cat'], str):
        rang_dep_options = MAP_RANKS['Departemental'][license_number]['options']
        max_rank_dep = MAP_RANKS['Departemental']['stats'][json.dumps(rang_dep_options)]
        content['rangdep_cat'] += '/' + str(max_rank_dep)

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
