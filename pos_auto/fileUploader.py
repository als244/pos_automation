import os
import aurora
import re
import xlrd
import pandas as pd
from reminders import Reminders



class FileUploader:

	# should return true if uploaded file to database
	def upload_file_to_server(distributor, fpath, rule):
		# TODO, work on error checking

		
		# determine what to do about default downloads
		# only have sql script for Massco
		if fpath is None or rule is None or distributor is None:
			return False

		if rule['sql_template_path'] is None:
			print("ERROR: The parsing rule for " + fpath + " has no sql template associated with it.")
			Reminders.notify_error_uploading(distributor, fpath)
			return False
		
		# want to make sure sql file to upload actually exists
		try:
			sql_file = open(rule['sql_template_path'], 'r')
			sql_text = sql_file.read()
			sql_file.close()
		except Exception:
			print("Error opening SQL file used to upload data")
				
		# EXCEL FILES NEED TO BE CONVERTED TO CSV BEFORE THEY CAN BE LOADED
		
		filename, file_extension = os.path.splitext(fpath)
		file_extension = file_extension.lower()

		file_type = rule['file_type']

		if not file_type:
			if file_extension == ".xls"  or file_extension == ".xlsx":
				file_type = "excel"
			elif file_extension == ".csv":
				file_type = "csv"
			elif file_extension == ".txt":
				file_type = "text"

		if file_type == "excel":
			workbook = xlrd.open_workbook(fpath)
			sheet = workbook.sheet_names()[0]
			data_xls = pd.read_excel(fpath, sheet, index_col=None)
			data_xls.to_csv(filename + ".csv", encoding='utf-8', index=False, header=None)
			data_path = filename + ".csv"
			print("CONVERTED TO CSV, path: ", data_path)
		else:
			data_path = fpath
		

		# NEED TO DETERMINE WHICH ATTACHMENT TO UPLOAD, assume that
		# the sql file has <{file}> in the proper replacement location

		if os.path.exists(data_path):
			data_path = data_path.replace('\\', '/')
			sql_to_exec = sql_text.format(file=" \'" + data_path + "\'")
			print(sql_to_exec)
		else:
			print("ERROR: data file not saved")
			return False
	
		commands = sql_to_exec.split(";")

		cn = aurora.aurora_connect()
		cur = cn.cursor(dictionary=True)
		
		for command in commands:
			command = command.strip()
			if command:
				cur.execute(command)
		
		row_count = cur.rowcount
		if distributor.notify:
			Reminders.notify_uploaded_to_server(distributor, fpath, row_count)

		cur.close()
		cn.close()

		return True
