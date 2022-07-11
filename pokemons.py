from urllib import response
import psycopg2
from pprint import pprint
import numpy as np
from random import *

dbHost = "localhost"
dbName = "pokemon"
dbPort = 5432
dbUser = "postgres"
dbPass = "postgres"


def makeQuery(sqlString,args):
  conn = psycopg2.connect(host = dbHost, port = dbPort, dbname=dbName, user = dbUser, password = dbPass) 
  cur = conn.cursor()
  cur.execute(sqlString, args)  
  row_count = cur.rowcount
  print("row count: {}".format(row_count))
  records = cur.fetchall()
  cur.close()
  conn.close()
  return records

def rowCountQuery(sqlString, args):
  conn = psycopg2.connect(host = dbHost, port = dbPort, dbname=dbName, user = dbUser, password = dbPass) 
  cur = conn.cursor()
  cur.execute(sqlString, args)  
  row_count = cur.rowcount
  cur.close()
  conn.close()
  return row_count

def getTypes():
  return ["Bug", "Dark", "Dragon", "Electric", "Fairy", "Fighting", "Fire", "Flying", "Ghost", "Grass", "Ground", "Ice", "Normal", "Poison", "Psychic", "Rock", "Steel", "Water"]

def getAreas(game):
  sqlString = "select name from area where game_id = %s"
  areas = makeQuery(sqlString,[game])
  print(areas)
  return areas

def insertQuery(sqlString, args):
  conn = psycopg2.connect(host = dbHost, port = dbPort, dbname=dbName, user = dbUser, password = dbPass) 
  cursor = conn.cursor()
  cursor.execute(sqlString, args)
  conn.commit() # <- We MUST commit to reflect the inserted data
  cursor.close()
  conn.close()
  return 0

def getPokemon(pokemon):
  sqlString = "select hp, atk, def, spatk, spdef, spd from pokemon where name = %s"
  makeQuery(sqlString,[pokemon.title()])
  return 0

def getHabitats():
  sqlString = "select distinct habitat from pokemon_lives_in_habitat"
  habitats = makeQuery(sqlString, [])
  return habitats
  
def getPokemonsOfHabitat(habitat):
  sqlString = "select p.name from pokemon as p natural join pokemon_lives_in_habitat as h \
              where h.habitat = %s and (p.stage is null or p.stage = 1)"
  pokemons_from_habitat = makeQuery(sqlString,[habitat.title()])
  return pokemons_from_habitat

def getPokemonsOfType(tipe):
  sqlString = "select p.name from pokemon as p where p.type1 = %s or p.type2 = %s"
  pokemons_from_type = makeQuery(sqlString,[tipe.title(), tipe.title()])
  return pokemons_from_type

def getSpecificPokemon(pkmn):
  sqlString = 'select * from pokemon as p where p.name = %s'
  pokemon = makeQuery(sqlString,[pkmn.title()])
  return pokemon

def gerSpecificArea(area):
  sqlString = 'select * from area as a where a.name = %s'
  area_result = makeQuery(sqlString,[area.title()])
  return area_result

def getAllAreas(game):
  sqlString = 'select area_id, name, habitat from area as a where a.game_id = %s'
  areas = makeQuery(sqlString,[game])
  return areas  

def makeNewAreaLow(name, habitat, game, is_city):
  sqlString = "select count(*) from area"
  number = makeQuery(sqlString,[game])[0][0]
  sqlString2 = "select name from area where name = %s"
  exists = len(makeQuery(sqlString2,[name.title()]))
  if(exists >0):
    print("Already exists")
    return "area already exists"
  else:
    print("number: {}".format(number))
    sqlString3 = 'insert into "area" values (%s, %s, %s, %s, %s)'
    response = insertQuery(sqlString3,[number+1, name.title(), habitat.title(), is_city, game])
    return response

def makeNewGame(name, narrator):
  sqlString = "select count(*) from game"
  number = makeQuery(sqlString,[name])[0][0]
  sqlString2 = "select name from game where name = %s"
  exists = len(makeQuery(sqlString2,[name]))
  if(exists > 0):
    print("Game {} Already exists".format(name))
    return "game already exists"
  else:
    print("number: {}".format(number))
    sqlString3 = 'insert into game values (%s, %s, %s)'
    response = insertQuery(sqlString3,[number+1, name, narrator])
    return response

def registerNearAreasLow(area1,array):
  area1_id, game = makeQuery("select area_id,game_id from area where name = %s",[area1.title()])[0]
  print(game)
  for area in array:
    checkString = "select count(*) from area_near_area as aa where aa.area1_id in (%s, %s) and aa.area2_id in (%s, %s)"
    result = makeQuery(checkString,[area1_id,area["id"],area1_id,area["id"]])
    if (result[0][0] == 0):
      print("areas sem fronteira encontradas")
      insert_query = "insert into area_near_area values (%s, %s, %s)"
      try:
        insertQuery(insert_query,[area1_id,area["id"],game])
        insertQuery(insert_query,[area["id"],area1_id,game])
      except Exception as e:
        print(e)  
    else:
      print(" count: {}".format(result[0][0]))
      print(result)
      print("foi encontrada uma fronteira")
      
def createNewArea(name, habitat, game, is_city, surrounding):
  makeNewAreaLow(name,habitat,game, is_city)
  registerNearAreasLow(name, surrounding)

def getArea(area_name):
  sqlString = "select area_id, game_id from area where name = %s"
  id, game = makeQuery(sqlString,[area_name])[0]
  return id, game

def createTrainer(name, area):
  area_id, game_id = getArea(area)
  count = makeQuery("select count(*) from trainer",[])[0][0]
  print(count)
  sqlString = "insert into trainer values (%s,%s,%s,%s)"
  try:
    insertQuery(sqlString,[count+1,name,area_id,game_id])
  except Exception as e:
    print(e)
    
def getTrainerId(name):
  sqlString = "select trainer_id, game_id from trainer where name= %s"
  trainer_id, game_id = makeQuery(sqlString,[name.title()])[0]
  return trainer_id, game_id

def getTrainer(name):
  sqlString = "select * from trainer where name= %s"
  trainer = makeQuery(sqlString,[name.title()])[0]
  return trainer

def levelUpPokemon(stats, level):
  new_stats = stats
  for i in range(level):
    index = randrange(0,5)
    new_stats[index] = new_stats[index]+1
  return new_stats

def createPokemonLevel(pokemon, level,trainer=False):
  stats = createPokemonStatsOnLevel(pokemon, level)
  moves = createPokemonMoveset(pokemon, level, isTrained = False)
  return stats, moves
  
def createPokemonMoveset(pokemon, level, isTrained=False):
  sqlString = "select distinct l.move_id from pokemon_learns_move as l \
              inner join pokemon as p  on l.pokemon_id = p.pokemon_id \
              where l.pokemon_id in ( \
                select e.pokemon_id from pokemon as pp \
                inner join pokemon_evolves_to as e \
                on pp.evo_line_id = e.evo_line_id \
                where pp.name = %s \
                order by e.pokemon_id)and (l.level !=0 or l.egg) and l.level <= %s \
                "
  moves = makeQuery(sqlString,[pokemon.title() ,level])
  print(moves)
  print("no de moves: {}".format(len(moves)))
  if(isTrained):
    num_moves = 6
  else:
    num_moves = randrange(3,7)
  num_list = sample(range(0,len(moves)),num_moves)
  move_list = []
  for num in num_list:
    move_list.append(moves[num][0])
  return move_list
  
def createPokemonStatsOnLevel(pokemon, level):
  sqlString = "select hp,atk,def,spatk, spdef, spd from pokemon where name = %s"
  base_stats = makeQuery(sqlString,[pokemon.title()])
  print("base_stats: {}".format(np.array(base_stats)[0]))
  stats = levelUpPokemon(np.array(base_stats)[0], level)
  print("stats: {}".format(stats))
  return stats

def createPokemonFromTrainer(trainer, pokemon_name, pokemon, level):
  t_id, g_id = getTrainerId(trainer)
  stats, moves = createPokemonLevel(pokemon, level)
  count = makeQuery("select count(*) from pokemon_from_trainer",[])[0][0]
  species_id = makeQuery("select pokemon_id from pokemon where name = %s",[pokemon.title()])[0][0]
  sqlString = "insert into pokemon_from_trainer (pokemon_id, name, trainer_id, level, hp, atk, def, spatk, spdef, spd, species_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
  hp, atk, defe, spatk, spdef, spd = stats.tolist()
  repeat_count = makeQuery("select count(*) from pokemon_from_trainer where trainer_id = %s and name = %s",[t_id,pokemon_name.title()])[0][0]
  if(repeat_count == 0):  
    insertQuery(sqlString,[count, pokemon_name.title(), t_id, level, hp, atk, defe, spatk, spdef, spd, species_id])
    for move in moves:
      insertQuery("insert into pokemon_from_trainer_has_move (pokemon_id, move_id) values (%s, %s)",[count,int(move)])
  else:
    print("Pokemon ja cadastrado!")
    return
  
def getPokemonFromTrainer(trainer):
  sqlString = "select * from pokemon_from_trainer where trainer = %s"
  pokemons = makeQuery(sqlString,[trainer])
  return pokemons

def generateGroupPokemonByHabitat(number, habitat):
  sqlString = "select distinct p.evo_line_id from pokemon_lives_in_habitat as h inner join pokemon as p on h.pokemon_id = p.pokemon_id where habitat = %s and p.isLegendary = false and p.pokemon_id not in (select pokemon_id from pokemon_in_area)"
  pkmns = makeQuery(sqlString,[habitat.title()])
  pkmn_list = []
  num_list = []
  if(number > len(pkmns)):
    print("pouco pokemon")
    for pkmn in pkmns:
      num_list.append(pkmn[0])
  else:
    num_list = sample(range(0,len(pkmns)), number)
    for num in num_list:
      print(pkmns[num][0])
      pkmn_list.append(pkmns[num][0])
  return pkmn_list

def registerPokemonsOfArea(number, area):
  area_id, habitat = makeQuery("select area_id, habitat from area where name = %s",[area.title()])[0]
  pkmn_list = generateGroupPokemonByHabitat(number,habitat)
  chances = sample(range(0,99), number)
  sum = 0
  for i in range(len(pkmn_list)):
    sum = sum + chances[i]
  for i in range(len(pkmn_list)):
    insertQuery("insert into pokemon_in_area (area_id, pokemon_id, chance) values(%s,%s,%s)",[area_id, pkmn_list[i],chances[i]*100/sum])

def generateGroupOfArea(area, number):
  area_id = makeQuery("select area_id from area where name = %s",[area.title()])[0][0]
  sqlString = "select pokemon_id, chance from pokemon_in_area where area_id = %s"
  pkmns = makeQuery(sqlString,[area_id])
  pkmns_list = []
  weights_list = []
  for i in range(len(pkmns)):
    pkmns_list.append(pkmns[i][0])
    weights_list.append(pkmns[i][1])
  print("size of pkmn_list: {}".format(len(pkmns_list)))
  print("size of weights: {}".format(len(weights_list)))
  generated_pkmns = choices(pkmns_list, weights=tuple(weights_list),k=number)
  print(generated_pkmns)
  return generated_pkmns

def getPokemonById(id):
  name = makeQuery("select name from pokemon where pokemon_id = %s", [id])[0][0]
  return name

def getMoveById(id):
  sqlString = "select name, type, db, effects from move where move_id = %s"
  move = makeQuery(sqlString,[id])[0]
  return move

def createPokemonByHabitat(number, habitat, level):
  ids_list = generateGroupPokemonByHabitat(number, habitat)
  names = []
  for id in ids_list:
    name = getPokemonById(id)
    names.append(name)
  pkmns = []
  for name in names:
    pkmn = []
    pkmn.append(name)
    pkmn.append(level)
    stats = createPokemonStatsOnLevel(name, level)
    print(type(stats))
    pkmn.append(stats.tolist())
    moves = createPokemonMoveset(name,level)
    moveset = []
    for move in moves:
      print("move: {}".format(move))
      print(getMoveById(move))
      moveset.append(getMoveById(move))
    pkmn.append(moveset)
    pkmns.append(pkmn)
  return pkmns

def createGroupPokemonByArea(number,area, level):
  ids_list = generateGroupOfArea(area, number)
  names = []
  for id in ids_list:
    name = getPokemonById(id)
    names.append(name)
  pkmns = []
  for name in names:
    pkmn = []
    pkmn.append(name)
    pkmn.append(level)
    stats = createPokemonStatsOnLevel(name, level)
    print(type(stats))
    pkmn.append(stats.tolist())
    moves = createPokemonMoveset(name,level)
    moveset = []
    for move in moves:
      print("move: {}".format(move))
      print(getMoveById(move))
      moveset.append(getMoveById(move))
    pkmn.append(moveset)
    pkmns.append(pkmn)
  return pkmns

