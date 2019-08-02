import os
import mysql.connector
import xlrd
import pandas as pd

def aurora_connect(user = 'a.sheinberg', password = 'SaN#$PttW387', host = 'pre-aurora1.c8ueqdj3eykb.us-west-2.rds.amazonaws.com', database = 'ftp_auto'):
	return mysql.connector.connect(user=user, password=password, host=host, database=database, allow_local_infile=True, autocommit=True, compress=True)

def uploadFile(local_sql_template, local_data_file):
	
	
	try:
		sql_file = open(os.path.expanduser(local_sql_template), 'r')
		sql_text = sql_file.read()
		sql_file.close()
	except Exception:
		print("Error opening SQL file used to upload data")
				
		
	# NEED TO DETERMINE WHICH ATTACHMENT TO UPLOAD, assume that
	# the sql file has <{file}> in the proper replacement location

	expandedFpath = os.path.expanduser(local_data_file)
	filename, file_extension = os.path.splitext(expandedFpath)

	if file_extension == ".xls" or file_extension == ".xlsx":
		workbook = xlrd.open_workbook(expandedFpath)
		sheet = workbook.sheet_names()[0]
		data_xls = pd.read_excel(expandedFpath, sheet, index_col=None)
		data_xls.to_csv(filename + ".csv", encoding='utf-8', index=False, header=None)
		fpath = filename + ".csv"
		print("FILEPATH", fpath)
	else:
		fpath = expandedFpath


	if os.path.exists(fpath):
		sql_to_exec = sql_text.format(file=" \'" + fpath + "\'")
	else:
		print("ERROR: data file not saved")
		return False

	commands = sql_to_exec.split(";")

	cn = aurora_connect()
	cur = cn.cursor(dictionary=True)
		

	for c in commands:
		command = c.strip()
		print(command)
		if len(command) > 0:
			cur.execute(command)
		
	# MAKE EMAIL MORE SUITED TO SPECIFIC EMAIL / FILE.
	# need to think about organization of this class with emailHandler
	# postmark.emails.send(From='posauto@precisioncorp.net', To='cpitsenbarger@precisioncorp.net', Subject='Uploaded File to Database', HtmlBody='Uploaded file: ' + att_path + ' to database')

	# work out closing connection
	cur.close()
	cn.close()

uploadFile("~/Desktop/testTemplates/cole.sql", "~/Desktop/distributor_test_data/Cole.xlsx")

