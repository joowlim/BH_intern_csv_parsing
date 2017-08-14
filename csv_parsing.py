import pymysql, configparser, os, sys

class ParsedValue:
	"""
	Class attributes : 
	self.rows / self.column / self.delimiter / self.conn / self.curs
	"""
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
	
	def get_current_num_of_column(self):
		sql = "SELECT num_of_column FROM TABLE_INFO"
		self.curs.execute(sql)
		num_of_column = self.curs.fetchone()[0]
		return num_of_column
	
	def add_column_if_needed(self):
		current_num_of_column = self.get_current_num_of_column()
		
		if current_num_of_column < len(self.column):
			column_add_sql = "ALTER TABLE FILE_DATA "
			
			for i in range(current_num_of_column,len(self.column)):
				column_add_sql += "ADD COLUMN column" + str(i+1) + " VARCHAR(100)"
				if i != len(self.column)-1:
					column_add_sql+=", "
					
			num_of_column_update_sql = "UPDATE TABLE_INFO SET num_of_column = " + str(len(self.column)) +" WHERE table_info_id=1"
			self.curs.execute(column_add_sql)
			self.curs.execute(num_of_column_update_sql)
			self.conn.commit()

		
if len(sys.argv) != 2:
	print("call like")
	print("python3 csv_parsing.py your_file")
	exit()

file_name = sys.argv[1]
if os.path.exists(file_name) is False:
	print("the file is not exist")
	print("check your file")
	exit()


	
