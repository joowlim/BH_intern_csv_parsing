import pymysql, configparser

class ParsedValue:
	def __init__(self, file_name):
		self.rows = list()
		self.open_file(file_name)

	def wrong_extension_error():
		print("Invalid extension")
		exit()

	def add_column(self, line):
		self.column = line.split(self.delimiter)

	def add_row(self, line):
		self.rows.append(line.split(self.delimiter))

	def open_file(self, file_name):
		# open given file
		input_file = open(file_name, "r")

		# read given file
		file_lines = input_file.readlines()
		input_file.close()

		# detect extension
		input_file_extension = file_name.split(".")[-1]

		# set delimiter
		if input_file_extension == "csv":
			self.delimiter = ';'
		elif input_file_extension == "tsb":
			self.delimiter = '\t'
		else:
			wrong_extension_error()

		# parse contents
		self.add_column(file_lines[0].strip("\n"))
		for line in file_lines[1:]:
			self.add_row(line.strip("\n"))
	def db_connection(self):
		config = configparser.ConfigParser()
		config.read("./user_config.ini")

		server = config.get("DATABASE", "server")
		user = config.get("DATABASE", "user")
		password = config.get("DATABASE", "password")
		schema = config.get("DATABASE", "schema")

		self.conn = pymysql.connect(host = server, user = user, password = password, db = schema, charset = 'utf8')
		self.curs = self.conn.cursor()

