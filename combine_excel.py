import pymysql, openpyxl, configparser, os, sys, progressbar

sheet_check = 1
config = configparser.ConfigParser()
config.read("./user_config.ini")
server = config.get("DATABASE", "server")
user = config.get("DATABASE", "user")
password = config.get("DATABASE", "password")
schema = config.get("DATABASE", "schema")

conn = pymysql.connect(host = server, user = user, password = password, db = schema, charset = 'utf8')
curs = conn.cursor()

num_of_column_select_sql = "SELECT num_of_column FROM TABLE_INFO"
curs.execute(num_of_column_select_sql)
num_of_column = curs.fetchone()[0]

combined_excel = openpyxl.Workbook()
sql_column_info = "SELECT column_info_id, column_info, delimiter FROM COLUMN_INFO"
curs.execute(sql_column_info)
columns = curs.fetchall()

sheet_idx = 1
for (column_info_id, column_info, delimiter) in columns:
    # use the first sheet which was already opened
	
	if sheet_check == 0:
		sheet = combined_excel.create_sheet()
	else:
		sheet = combined_excel.active
	column_name_list = column_info.split(delimiter)
	sql_file_data = "SELECT * FROM FILE_DATA WHERE column_info_id = " + str(column_info_id)
	curs.execute(sql_file_data)
	data_tuples = curs.fetchall()
	for column_name in column_name_list:
		sheet.cell(row = 1, column = column_name_list.index(column_name) + 1).value = column_name
		
	bar = progressbar.ProgressBar(maxval=len(data_tuples), widgets=[progressbar.Bar('=',"sheet : " + str(sheet_idx) + "/" + str(len(columns))+ ' [', ']'), ' ',progressbar.SimpleProgress()])
	bar.start()
	idx = 1
	for data_tuple in data_tuples:
		for j in range(1, len(column_name_list) + 1):
			sheet.cell(row = data_tuples.index(data_tuple) + 2, column = j).value = data_tuple[j+1]
		bar.update(idx)
		idx += 1
	sheet_check = 0
	sheet_idx += 1
	bar.finish()
print("now saving...")
combined_excel.save("combined_excel.xlsx")
