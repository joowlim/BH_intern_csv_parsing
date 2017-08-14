import pymysql, configparser

config = configparser.ConfigParser()
config.read("./user_config.ini")

server = config.get("DATABASE", "server")
user = config.get("DATABASE", "user")
password = config.get("DATABASE", "password")
schema = config.get("DATABASE", "schema")

conn = pymysql.connect(host = server, user = user, password = password, db = schema, charset='utf8')
curs = conn.cursor()

# content

conn.commit()
conn.close()
