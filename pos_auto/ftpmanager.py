import ftplib
import os
import datetime
import aurora
import re
import tqdm
from fileUploader import FileUploader
from reminders import Reminders

def check_ftp(all_distributors):
	# connect to aurora
	cnx = aurora.aurora_connect()
	# create cursor
	#use dictionary parameter to return results as dictionary
	cursor = cnx.cursor(dictionary=True)


	for d in all_distributors.values():
		# fetch ftp login info
		ftp_info = d.ftp_info
		rules = d.rules

		if not ftp_info or not rules:
			continue

		#check if we already received data from them
		cursor.execute('select received_data from distributors where id = %s', (d.relationship_id, ))
		result = cursor.fetchall()[0]
		if not result or result['received_data']:
			continue
		

		# connect to ftp
		try:
			ftp_conn = ftplib.FTP(ftp_info['url'], ftp_info['username'], ftp_info['password'])
			
			# change to subdirectory if needed
			if ftp_info['path'] != '/':
				ftp_conn.cwd(ftp_info['path'])
			
			# retrieve list of files
			# NOTE: can use mlsd() to get other info besides file name (like size and update time)
			files = ftp_conn.nlst()
			
			
			for f in files:
				# loop over file rules
				rule = None
				for r in rules:
					if re.search(r['regex'], f):					
						fpath = r['save_to_path']
						rule = r
						break			
				
				# need to add some testing to ensure a rule is found
				

				date = datetime.datetime.now()
				months = ["12 - Dec", "01 - Jan", "02 - Feb", "03 - Mar", "04 - Apr", "05 - May", "06 - Jun"
				, "07 - Jul", "08 - Aug", "09 - Sep", "10 - Oct", "11 - Nov", "12 - Dec"]
		
				prevMonthFolder = months[(date.month - 1) % 12]
				year = str(date.year)

			
				full_dir_path = os.path.join(fpath, year, prevMonthFolder)
				os.makedirs(full_dir_path, exist_ok=True)
				full_path = os.path.join(full_dir_path, f)
				# save file down based on first matched rule
				print('Saving {} to {}...'.format(f, full_dir_path))
				
				with open(full_path, 'wb') as outfile:
					def cb(data):
						outfile.write(data)
							
					ftp_conn.retrbinary('RETR ' + f, cb)

					# notify that system downloaded file
					if d.notify:
						Reminders.notify_downloaded_file(d, f, full_path)
					
					print("Downloaded: " + f + "\nTo: " + full_path + "\nFrom: " + d.name)	
					
					# upload the file to the database using the rule that matched
					if d.data_import:
						FileUploader.upload_file_to_server(d, full_path, rule)
			
			# if there was a file uploaded then tell database that the distributor sent data
			if len(files) > 0:
				Reminders.update_received_data(d, 1)

											
			ftp_conn.quit()
			
		except ftplib.all_errors as e:
			print(e)

	# cleanup
	cursor.close()
	cnx.close()
