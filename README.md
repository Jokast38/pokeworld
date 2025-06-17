# PokéWorld 🕹️✨

Bienvenue sur **PokéWorld** !  
Une application web Flask pour explorer, comparer et combattre avec vos Pokémon préférés grâce à la PokéAPI.  
Attrapez-les tous ! 🎒⚡

---

## 📁 Structure du projet

```
pokeworld/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── static/
│   └── style.css
├── templates/
│   ├── battle.html
│   ├── index.html
│   ├── pokemon_details.html
│   └── type_stats.html
└── __pycache__/
```

---

## ⚙️ Exemple de configuration `.env`

```
POKEAPI_URL=https://pokeapi.co/api/v2
SECRET_KEY='votre_clé_secrète_ici'
```

- `POKEAPI_URL` : URL de base de l'API PokéAPI (ne pas modifier sauf besoin spécifique)
- `SECRET_KEY` : Clé secrète Flask pour la gestion des sessions et des messages flash

---

## 🚀 Installation et démarrage

1. **Cloner le dépôt**  
   🧬

```sh
git clone <url-du-repo>
cd pokeworld
```

2. **Créer et activer un environnement virtuel**  
   🐍

```sh
python -m venv venv
# Sur Linux/Mac :
source venv/bin/activate
# Sur Windows :
venv\Scripts\activate
```

3. **Installer les dépendances**  
   📦

```sh
pip install -r requirements.txt
```

4. **Configurer le fichier `.env`**  
   📝  
   Crée un fichier `.env` à la racine du projet et copie la configuration d'exemple ci-dessus.

5. **Lancer l'application**  
   🏁

```sh
python app.py
```

L'application sera accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).  
Ouvre ton navigateur et commence l'aventure ! 🌍

---

## 🎮 Fonctionnalités

- 🔍 Recherche de Pokémon par nom ou ID
- 📋 Affichage détaillé des Pokémon
- 📚 Liste paginée des 151 premiers Pokémon
- 📊 Statistiques par type de Pokémon
- ⚔️ Simulation de combats entre deux Pokémon

---

## 🧑‍💻 Auteur
Par Jokast Kassa 

Projet de formation - Janvier 2025  
Fais équipe et deviens le meilleur dresseur ! 🏆

---

> Gotta catch 'em all! 🎉