import pymysql, configparser, os, sys, openpyxl

class ParsedValue:
	"""
	Class attributes : 
	self.rows / self.columns / self.delimiter / self.conn / self.curs
	"""
	def __init__(self, file_name):
		self.rows = list()
		self.open_file(file_name)
		self.connect_db()

	def wrong_extension_error():
		print("Invalid extension")
		exit()

	def add_column(self, line):
		self.columns = line.split(self.delimiter)

	def add_row(self, line):
		self.rows.append(line.split(self.delimiter))

	
	def open_file(self, file_name):

		# detect extension
		input_file_extension = file_name.split(".")[-1]

		# set delimiter
		if input_file_extension == "csv":
			self.delimiter = ';'
			self.open_normal_file(file_name)
		elif input_file_extension == "tsb":
			self.delimiter = '\t'
			self.open_normal_file(file_name)
			
		elif input_file_extension == "xlsx":
			self.delimiter = ';'
			self.open_excel_file(file_name)
			
		else:
			wrong_extension_error()

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
			if idx != len(first_row_as_list) -1 :
				first_row += ';'
				
		self.add_column(first_row)
		
		for each_row in rows[1:]:
			temp_each_row = ''
			for idx in range(len(each_row)):
				temp_each_row += str(each_row[idx].value)
				if idx != len(each_row) -1:
					temp_each_row += '; '
			self.add_row(temp_each_row)
		

	def connect_db(self):
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
		
		if current_num_of_column < len(self.columns):
			column_add_sql = "ALTER TABLE FILE_DATA "
			
			for i in range(current_num_of_column,len(self.columns)):
				column_add_sql += "ADD COLUMN column" + str(i+1) + " VARCHAR(100)"
				if i != len(self.columns)-1:
					column_add_sql+=", "
					
			num_of_column_update_sql = "UPDATE TABLE_INFO SET num_of_column = " + str(len(self.columns)) +" WHERE table_info_id=1"
			self.curs.execute(column_add_sql)
			self.curs.execute(num_of_column_update_sql)
			self.conn.commit()

	def insert_column_to_db(self):
		sql = "INSERT INTO COLUMN_INFO (column_info, delimiter) VALUES (%s, %s)"
		self.curs.execute(sql, (self.delimiter.join(self.columns), self.delimiter))
		
		self.conn.commit()
		return self.curs.lastrowid

	def insert_rows_to_db(self, column_id):
		for row in self.rows:
			sql = "INSERT INTO FILE_DATA (column_info_id"
			for i in range(len(row)):
				sql = sql + ", column" + str(i+1)
			sql = sql + ") VALUES ("
			for i in range(len(row)):
				sql = sql + "%s, "
			sql = sql + "%s)"
			self.curs.execute(sql, tuple([column_id]+row))

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

parsed_value = ParsedValue(file_name)
col_id = parsed_value.insert_column_to_db()
parsed_value.insert_rows_to_db(col_id)
# column_id = parsed_value.insert_column_to_db()
# parsed_value.insert_rows_to_db(column_id)
	
