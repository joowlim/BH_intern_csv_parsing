import pymysql, configparser, os, sys, openpyxl

class ParsedValue:
	"""
	Class attributes : 
	self.rows / self.columns / self.delimiter / self.conn / self.curs / self.config
	"""
	def __init__(self):
		
		self.rows = list()
		
	def wrong_extension_error(self):
		print("Invalid extension")
		exit()
		
	# database relative function -----
	def connect_db(self, server, user, password, schema):

		self.conn = pymysql.connect(host = server, user = user, password = password, charset = 'utf8')
		self.curs = self.conn.cursor()
		self.init_all_database_if_not_exists(schema)
		
	def check_db_exists(self, schema):
		sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '" + schema + "'"
		self.curs.execute(sql)
		
		if self.curs.fetchone() == None:
			return False
		
		use_database_sql = "USE " + schema
		self.curs.execute(use_database_sql)
		self.conn.commit()
		return True
		
	def table_init_if_not_exist(self):
		create_column_info_table_sql = "CREATE TABLE IF NOT EXISTS COLUMN_INFO("\
											"column_info_id INT(11) NOT NULL primary key auto_increment,"\
											"column_info VARCHAR(500) NOT NULL,"\
											"`delimiter` VARCHAR(5) NOT NULL"\
										");"
										
		create_file_data_table_sql = "CREATE TABLE IF NOT EXISTS FILE_DATA("\
										"file_data_id INT(11) NOT NULL primary key auto_increment,"\
										"column_info_id INT(11) NOT NULL,"\
										"column1 varchar(100)"\
									");"
									
		create_table_info_table_sql = "CREATE TABLE IF NOT EXISTS  TABLE_INFO("\
											"table_info_id INT(11) NOT NULL primary key auto_increment,"\
											"num_of_column INT(11)"\
											");"
		self.curs.execute(create_column_info_table_sql)
		self.curs.execute(create_file_data_table_sql)
		self.curs.execute(create_table_info_table_sql)
		self.conn.commit()
		
		select_table_info_sql = "SELECT * FROM TABLE_INFO"
		self.curs.execute(select_table_info_sql)
		result = self.curs.fetchone()
		
		if result == None:
			insert_table_info_sql = "INSERT INTO TABLE_INFO(num_of_column) VALUES(1)"
			self.curs.execute(insert_table_info_sql)
		self.conn.commit()
		
	def initialize_db_schema(self, schema):
		
		create_schema_sql = "CREATE SCHEMA " + schema + " DEFAULT CHARACTER SET utf8 "
		use_database_sql = "USE " + schema
		self.curs.execute(create_schema_sql)
		self.curs.execute(use_database_sql)
		self.conn.commit()
		
		
	def connect_db_by_file(self, file_path):
		
		# create config parser
		self.config = configparser.ConfigParser()
		self.config.read(file_path)
		
		server = self.config.get("DATABASE", "server")
		user = self.config.get("DATABASE", "user")
		password = self.config.get("DATABASE", "password")
		schema = self.config.get("DATABASE", "schema")
		
		self.connect_db(server, user, password, schema)

	def init_all_database_if_not_exists(self,schema):
	
		if self.check_db_exists(schema) == False:
			self.initialize_db_schema(schema)
		self.table_init_if_not_exist()
		
	def connect_db_by_argument(self, server, user, password, schema):
		self.connect_db(server,user,password,schema)
	
	# end database relative function -----
	
	
	def add_column(self, line):
		self.columns = line.split(self.delimiter)

	def add_row(self, line):
		self.rows.append(line.split(self.delimiter))

	def open_file_and_set_delimiter(self, file_name, delimiter = None):
		# detect extension
		input_file_extension = file_name.split(".")[-1]

		# set delimiter
		if delimiter == None:
			if hasattr(self,'config') == False:
				print("input your delimiter >> ", end='')
				self.delimiter = input()
			else:
				self.delimiter = self.config.get("DELIMITER", input_file_extension)
		else:
			self.delimiter = delimiter

		# set delimiter
		if input_file_extension == "csv":
			self.open_normal_file(file_name)

		elif input_file_extension == "tsv":
			self.open_normal_file(file_name)
			
		elif input_file_extension == "xlsx":
			self.open_excel_file(file_name)
			
		else:
			self.wrong_extension_error()

	def open_normal_file(self, file_name):
		# open given file
		input_file = open(file_name, "r")

		# read given file
		file_lines = input_file.readlines()
		input_file.close()
		
		# parse contents
		self.add_column(file_lines[0].strip("\n"))
		for line in file_lines[1:]:
			self.add_row(line.strip("\n"))

	def open_excel_file(self, file_name):
		excel_document = openpyxl.load_workbook(file_name)
		sheet_name = excel_document.get_sheet_names()[0]
		sheet = excel_document.get_sheet_by_name(sheet_name)
		rows = list(sheet.rows)
		first_row_as_list = rows[0]
		num_of_column = len(first_row_as_list)
		
		first_row = ''
		for idx in range(len(first_row_as_list)):
			first_row += str(first_row_as_list[idx].value)
			if idx != len(first_row_as_list) - 1:
				first_row += self.delimiter
				
		self.add_column(first_row)
		
		for each_row in rows[1:]:
			temp_each_row = ''
			for idx in range(len(each_row)):
				temp_each_row += str(each_row[idx].value)
				if idx != len(each_row) - 1:
					temp_each_row += self.delimiter
			self.add_row(temp_each_row)


	
	def get_current_num_of_column(self):
		sql = "SELECT num_of_column FROM TABLE_INFO"
		self.curs.execute(sql)
		num_of_column = self.curs.fetchone()[0]
		return num_of_column
	
	def add_column_if_needed(self):
		current_num_of_column = self.get_current_num_of_column()
		
		if current_num_of_column < len(self.columns):
			column_add_sql = "ALTER TABLE FILE_DATA "
			
			for i in range(current_num_of_column, len(self.columns)):
				column_add_sql += "ADD COLUMN column" + str(i + 1) + " VARCHAR(100)"
				if i != len(self.columns) - 1:
					column_add_sql += ", "
					
			num_of_column_update_sql = "UPDATE TABLE_INFO SET num_of_column = " + str(len(self.columns)) + " WHERE table_info_id=1"
			self.curs.execute(column_add_sql)
			self.curs.execute(num_of_column_update_sql)
			self.conn.commit()

	def insert_column_to_db(self):
		# check if there already exist column in db
		sql = "SELECT column_info_id, column_info FROM COLUMN_INFO WHERE column_info = \"" + self.delimiter.join(self.columns) + "\""
		self.curs.execute(sql)
		column = self.curs.fetchone()

		if column == None:
			sql = "INSERT INTO COLUMN_INFO (column_info, delimiter) VALUES (%s, %s)"
			self.curs.execute(sql, (self.delimiter.join(self.columns), self.delimiter))
			result = self.curs.lastrowid
		else:
			(column_info_id, column_info) = column
			result = column_info_id
	
		self.conn.commit()

		return result

	def insert_rows_to_db(self, column_id):
		for row in self.rows:
			sql = "INSERT INTO FILE_DATA (column_info_id"
			for i in range(len(row)):
				sql = sql + ", column" + str(i + 1)
			sql = sql + ") VALUES ("
			for i in range(len(row)):
				sql = sql + "%s, "
			sql = sql + "%s)"
			self.curs.execute(sql, tuple([column_id] + row))

		self.conn.commit()

	def parse_to_insert(self):
		self.add_column_if_needed()
		column_id = self.insert_column_to_db()
		self.insert_rows_to_db(column_id)

if __name__ == "__main__":
	# without argument
	"""
	if len(sys.argv) != 2:
		print("call like")	
		print("python3 csv_parsing.py your_file")
		exit()

	file_name = sys.argv[1]

	if os.path.exists(file_name) is False:
		print("the file is not exist")
		print("check your file")
		exit()
	"""
	# by file
	parsed_value = ParsedValue()
	parsed_value.connect_db_by_file("./user_config.ini")
	parsed_value.open_file_and_set_delimiter("./report.csv")
	parsed_value.parse_to_insert()
	
	# by argument
	#parsed_value2 = ParsedValue()
	#parsed_value2.connect_db_by_argument("localhost", "root", "root", "name")
	#parsed_value2.open_file_and_set_delimiter("./report.csv",';')
	#parsed_value2.parse_to_insert()
	
	

