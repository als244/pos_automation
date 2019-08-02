import pandas as pd
from pathlib import Path
import os
import xlrd

def convToExcel(fpath_excel):

	filepath = Path(fpath_excel)
	filename, file_extension = os.path.splitext(filepath)
	workbook = xlrd.open_workbook(filepath)
	sheet = workbook.sheet_names()[0]
	data_xls = pd.read_excel(filepath, sheet, index_col=None)
	data_xls.to_csv(filename + ".csv", encoding='utf-8', index=False, header=None)
	fpath = filename + ".csv"
	print("FILEPATH", filepath)

convToExcel("G:/Data/Source Data (all)/pos_auto_trial/rcp/rcp_data/American_Hotel.xlsx")