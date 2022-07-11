from crypt import methods
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
from pokemons import *


#postgres://<user>:<password>@localhost/<database>
app.config["SQLALCHEMY_DATABASE_URI"]='postgres://postgres:postgres@localhost/pokemon'

db=SQLAlchemy(app)

CORS(app)



@app.route("/")
def hello():
  return "Hello World!"

@app.route("/habitats")
def requestGetHabitats():
  habitats = getHabitats()
  print(habitats)
  return jsonify(habitats)

@app.route("/types")
def requestGetTypes():
  print("deu bom?")
  return jsonify(getTypes())

@app.route("/pokemon_from_type", methods=["POST"])
# def requestGetPokemonsFromArea()

@app.route("/create_trainer", methods=["POST"])
def requestMakeTrainer():
  data = request.get_json()
  name = data["name"].title()
  area = data["area"].title()
  createTrainer(name, area)

@app.route("/create_area", methods=["POST"])
def requestMakeArea():
  data = request.get_json()
  name = data["name"].title()
  habitat = data["habitat"].title()
  game = data["game"]
  is_city = data["is_city"]
  surroundings = data["surroundings"]
  createNewArea(name, habitat, game, is_city, surroundings)

@app.route("/get_trainer", methods=["POST"])
def requestGetTrainer():
  data = request.get_json()
  name = data["name"].title()
  getTrainer(name)

@app.route("/get_pokemons_from_area", methods=["POST"])
def requestGetPokemonsFromArea():
  data = request.get_json()
  area = data["area"].title()
  number = data["number"]
  pokemons = generateGroupOfArea(area,int(number))

@app.route("/generate_area_pokemons", methods=["POST"])
def requestMakePokemonOfAreas():
  data = request.get_json()
  number = data["number"]
  level = data["level"]
  area = data["area"].title()
  ids = registerPokemonsOfArea(number, area)
  pkmns = []
  for id in ids:
    name = generatePokemonById(id)
    pkmn = createPokemonStatsOnLevel(name, level)
    pkmns.append((name, pkmn))
  return pkmns

@app.route("/register_pokemons_of_area", methods=["POST"])
def requestRegisterPokemonsOfArea():
  data = request.get_json()
  number = data["number"]
  area = data["area"]
  try:
    registerPokemonsOfArea(number, area)
    return jsonify("Deu certo")
  except Exception as e:
    print(e)
    return jsonify(e)

@app.route("/get_areas/<game>")
def requestGetAreas(game):
  game_id = int(game)
  return jsonify(getAreas(game_id))

@app.route("/pokemons_from_habitat", methods=["POST"])
def requestGetPokemonsFromHabitat():
  data = request.get_json()
  habitat = data["habitat"]
  level = data["level"]
  number = data["number"]
  pkmns = createPokemonByHabitat(number, habitat, level)
  print((type(pkmns)))
  return jsonify(pkmns)

@app.route("/pokemons_from_area", methods=["POST"])
def requestGetGroupPokemonsFromArea():
  data = request.get_json()
  area = data["area"]
  level = data["level"]
  number = data["number"]
  pkmns = createGroupPokemonByArea(number, area, level)
  print((type(pkmns)))
  return jsonify(pkmns)


@app.route("/pokemon/get_image/<pokemon>")
def requestGetPokemonImage(pokemon):
  try:
    name = pokemon.lower()
    res = requests.get("https://pokeapi.co/api/v2/pokemon/"+name)
    data = res.json()
    req_res = jsonify(data["sprites"]["front_default"])
    return req_res
  except Exception as e:
    print("deu ruim")
    print(e)


if __name__ == "__main__":
  app.run(debug=True)