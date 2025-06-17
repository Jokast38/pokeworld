from flask import Flask, render_template, request, flash
from flask_caching import Cache
import os
import requests
from dotenv import load_dotenv
import random

# Charger les variables d'environnement
load_dotenv()

# Vérification de la variable POKEAPI_URL
POKEAPI_URL = os.getenv("POKEAPI_URL")
if not POKEAPI_URL:
    raise ValueError("❌ ERREUR: La variable d'environnement POKEAPI_URL est absente du fichier .env !")

# Initialisation de l'application Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "my_secret_key")  # Clé secrète pour flash()

# Configuration du cache
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

# Cache les résultats des requêtes pendant 5 minutes
@cache.memoize(timeout=300)
def get_pokemon_details(pokemon_name):
    """Récupère les détails d'un Pokémon depuis l'API avec mise en cache."""
    try:
        url = f"{POKEAPI_URL}/pokemon/{pokemon_name.lower()}"
        response = requests.get(url, timeout=5)  # Timeout après 5 secondes

        if response.status_code == 200:
            data = response.json()
            pokemon_data = {
                "name": data["name"].capitalize(),
                "hp": data["stats"][0]["base_stat"],
                "attack": data["stats"][1]["base_stat"],
                "defense": data["stats"][2]["base_stat"],
                "types": [t["type"]["name"].capitalize() for t in data["types"]],
                "sprite": data["sprites"]["front_default"]
            }
            return pokemon_data
        else:
            flash(f"❌ Erreur: Pokémon {pokemon_name} non trouvé.", "danger")
            return None
    except requests.RequestException as e:
        flash(f"❌ Erreur réseau: {e}", "danger")
        return None
    except Exception as e:
        flash(f"❌ Une erreur inconnue est survenue: {e}", "danger")
        return None

@cache.memoize(timeout=300)
def get_all_pokemons():
    """Récupère la liste des 151 premiers Pokémon avec leurs détails."""
    try:
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=151")
        response.raise_for_status()
        data = response.json()
        
        pokemons = []
        for item in data["results"]:
            details = requests.get(item["url"]).json()
            pokemons.append({
                "name": details["name"].capitalize(),
                "hp": details["stats"][0]["base_stat"],
                "attack": details["stats"][1]["base_stat"],
                "defense": details["stats"][2]["base_stat"],
                "types": [t["type"]["name"].capitalize() for t in details["types"]],
                "sprite": details["sprites"]["front_default"]
            })
        return pokemons
    except requests.RequestException as e:
        flash(f"❌ Erreur réseau lors de la récupération des Pokémon: {e}", "danger")
        return []

def get_pokemon_by_type(type_name):
    """Récupère les Pokémon d'un type donné avec leurs statistiques."""
    try:
        url = f"{POKEAPI_URL}/type/{type_name.lower()}"
        response = requests.get(url, timeout=5)  # Timeout après 5 secondes
        if response.status_code == 200:
            data = response.json()
            pokemon_list = data["pokemon"]
            total_hp = 0
            count = len(pokemon_list)

            for p in pokemon_list:
                pokemon_details = get_pokemon_details(p["pokemon"]["name"])
                if pokemon_details:
                    total_hp += pokemon_details["hp"]

            avg_hp = total_hp / count if count > 0 else 0
            return {"count": count, "avg_hp": avg_hp}
        else:
            flash(f"❌ Erreur: Type {type_name} non trouvé.", "danger")
            return None
    except requests.RequestException as e:
        flash(f"❌ Erreur réseau: {e}", "danger")
        return None
    except Exception as e:
        flash(f"❌ Une erreur inconnue est survenue: {e}", "danger")
        return None

@app.route("/", methods=["GET", "POST"])
@cache.cached(timeout=300, query_string=True)
def home():
    """Affiche la page d'accueil avec la liste des Pokémon et leurs détails."""
    pokemon, comparison, type_info = None, None, None
    
    # Gestion de la pagination
    page = request.args.get("page", 1, type=int)
    per_page = 10
    all_pokemons = get_all_pokemons()
    total_pokemons = len(all_pokemons)
    total_pages = (total_pokemons + per_page - 1) // per_page

    paginated_pokemons = all_pokemons[(page - 1) * per_page : page * per_page]

    # Suggestions pour l'autocomplétion
    suggestions = [pokemon['name'] for pokemon in all_pokemons]

    # Gestion des actions du formulaire
    if request.method == "POST":
        if "pokemon_name" in request.form:
            pokemon = get_pokemon_details(request.form["pokemon_name"])
            if pokemon:
                flash(f"✅ Pokémon {pokemon['name']} récupéré avec succès !", "success")
            else:
                flash(f"❌ Pokémon non trouvé.", "danger")
        elif "pokemon1" in request.form and "pokemon2" in request.form:
            p1 = get_pokemon_details(request.form["pokemon1"])
            p2 = get_pokemon_details(request.form["pokemon2"])
            if p1 and p2:
                comparison = {
                    "pokemon1": p1,
                    "pokemon2": p2,
                    "stronger": p1["attack"] > p2["attack"]
                }
        elif "pokemon_type" in request.form:
            type_info = get_pokemon_by_type(request.form["pokemon_type"])
            if type_info:
                flash(f"✅ Pokémon de type {request.form['pokemon_type']} récupérés !", "success")
            else:
                flash(f"❌ Aucun Pokémon de type {request.form['pokemon_type']} trouvé.", "danger")

    return render_template(
        "index.html",
        pokemon=pokemon,
        comparison=comparison,
        type_info=type_info,
        pokemons=paginated_pokemons,
        page=page,
        total_pages=total_pages,
        total_pokemons=total_pokemons,
        suggestions=suggestions
    )

@app.route('/pokemon/<name>')
@cache.cached(timeout=300)
def pokemon_details(name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")
    if response.status_code == 200:
        data = response.json()
        pokemon = {
            "name": data["name"].capitalize(),
            "hp": data["stats"][0]["base_stat"],
            "attack": data["stats"][1]["base_stat"],
            "defense": data["stats"][2]["base_stat"],
            "types": [t["type"]["name"].capitalize() for t in data["types"]],
            "sprite": data["sprites"]["front_default"],
            "height": data["height"],
            "weight": data["weight"],
            "abilities": [a["ability"]["name"].capitalize() for a in data["abilities"]]
        }
        return render_template("pokemon_details.html", pokemon=pokemon)
    else:
        return "Pokémon non trouvé", 404

@app.route('/battle', methods=["GET", "POST"])
def battle():
    battle_result = None
    pokemon1_name = None
    pokemon2_name = None

    if request.method == "POST":
        pokemon1_name = request.form["pokemon1"]
        pokemon2_name = request.form["pokemon2"]
        p1 = get_pokemon_details(pokemon1_name)
        p2 = get_pokemon_details(pokemon2_name)

        if p1 and p2:
            battle_result = simulate_battle(p1, p2)

    return render_template("battle.html", battle_result=battle_result, pokemon1_name=pokemon1_name, pokemon2_name=pokemon2_name)

@app.route('/type-stats')
@cache.cached(timeout=300)
def type_stats():
    """Affiche les statistiques des types de Pokémon."""
    types = ["fire", "water", "grass", "electric", "ice", "fighting", "poison", "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"]
    type_stats = {type_name: get_pokemon_by_type(type_name) for type_name in types}
    type_emojis = {
        "fire": "🔥",
        "water": "💧",
        "grass": "🌿",
        "electric": "⚡",
        "ice": "❄️",
        "fighting": "🥊",
        "poison": "☠️",
        "ground": "🌍",
        "flying": "🕊️",
        "psychic": "🔮",
        "bug": "🐛",
        "rock": "🪨",
        "ghost": "👻",
        "dragon": "🐉",
        "dark": "🌑",
        "steel": "🔩",
        "fairy": "🧚"
    }
    return render_template("type_stats.html", type_stats=type_stats, type_emojis=type_emojis)

def simulate_battle(pokemon1, pokemon2):
    p1_hp = pokemon1["hp"]
    p2_hp = pokemon2["hp"]

    for _ in range(5):  # 5 tours de combat
        p2_hp -= max(1, pokemon1["attack"] - random.randint(0, 5))
        p1_hp -= max(1, pokemon2["attack"] - random.randint(0, 5))

        if p1_hp <= 0 or p2_hp <= 0:
            break

    winner = pokemon1["name"] if p1_hp > p2_hp else pokemon2["name"]
    return {"winner": winner, "p1_hp": p1_hp, "p2_hp": p2_hp}

if __name__ == "__main__":
    app.run(debug=True)