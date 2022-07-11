import psycopg2
from pprint import pprint

dbHost = "localhost"
dbName = "pokemon"
dbPort = 5432
dbUser = "postgres"
dbPass = "postgres"

conn = psycopg2.connect(host = dbHost, port = dbPort, dbname=dbName, user = dbUser, password = dbPass) 


cur = conn.cursor()

# do stuff
# sqlString = "select * from pokemon_lives_in_habitat \
#              natural join pokemon \
#              where habitat = %s and isLegendary = False \
#              and "

# sqlString = "select p.name, c.evo_line_id, from pokemon_evolves_to as c, \
#   pokemon as p \
#   where p.pokemon_id = c.evo_line_id \
#   or p.pokemon_id = c.from_id \
#   or p.pokemon_id = c.current_id \
#   group by c.evo_line_id, p.name"

sqlString = "select p.name,p.hp, p.atk,p.def, p.spatk, p.spdef, p.spd \
              from pokemon as p, pokemon_lives_in_habitat as h \
              where h.habitat = 'Cave' and (p.type1 = 'Dragon' or p.type2 = 'Dragon') \
                and p.isLegendary = False"

# sqlString = "select type_id from type where type = 'dragon'"

cur.execute(sqlString)

row_count = cur.rowcount
print("row count {}".format(row_count))

records = cur.fetchall()
pprint(records)


cur.close()

conn.close()