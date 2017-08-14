import sys, pymysql, configparser

class ParsedValue:
	def __init__(self, delimiter):
		self.delimiter = delimiter
		self.rows = list()
	def add_column(self, line):
		self.column = line.split(self.delimiter)
	def add_row(self, line):
		self.rows.append(line.split(self.delimiter))

def wrong_extension_error():
	print("Invalid extension")
	exit()

config = configparser.ConfigParser()
config.read("./user_config.ini")

server = config.get("DATABASE", "server")
user = config.get("DATABASE", "user")
password = config.get("DATABASE", "password")
schema = config.get("DATABASE", "schema")
  
conn = pymysql.connect(host = server, user = user, password = password, db = schema, charset='utf8')
curs = conn.cursor()

# content
# conn.commit()
# conn.close()

# open given file
input_file_name = sys.argv[1]
input_file = open(input_file_name, "r")

# read given file
file_lines = input_file.readlines()
input_file.close()

# detect extension
input_file_extension = input_file_name.split(".")[-1]

# set delimiter
if input_file_extension == "csv":
	delimiter = ';'
elif input_file_extension == "tsb":
	delimiter = '\t'
else:
	wrong_extension_error()

# create new instance
parsed_value = ParsedValue(delimiter)

# add properties to the instance
parsed_value.add_column(file_lines[0].strip("\n"))
for line in file_lines[1:]:
	parsed_value.add_row(line.strip("\n"))
