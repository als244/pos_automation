# -*- coding: utf-8 -*-

import os
import re
import aurora
import datetime
from distributor import Distributor
from postmarker.core import PostmarkClient
from reminders import Reminders


class EmailAttachment():

	file_types = {".txt" : "text", 
				  ".xls":"excel", ".xlsx": "excel", ".xlsb":"excel", ".xlsm":"excel", ".xlt":"excel", ".xltx":"excel", ".xltm":"excel", ".xlv":"excel", ".xlw": "excel",
				  ".xlm":"xml",
				  ".pdf":"pdf",
				  ".csv":"csv"}

	def __init__(self, email, distributor):
		self.email = email
		self.distributor = distributor
		self.attachments = []

	def download_attachments(self):
		"""
		Given a message, save its attachments to the specified
		download folder (default is /tmp)

		return: file path to attachment
		"""
		#postmark = PostmarkClient(server_token = self.postmark_token)

		msg = self.email
		has_pos_data = False
		att_path = "No attachment found."
		for part in msg.walk():
			if part.get_content_maintype() == 'multipart': continue
			if part.get_content_maintype() == 'text': continue
			if part.get('Content-Disposition') == 'inline': continue
			if part.get('Content-Disposition') is None: continue

			filename = part.get_filename()
			print(filename)
						
			# TODO, work on without distributor
			if self.distributor == None:
				return False
			
			download_folder = None
			# check which rule the filename matches
			for r in self.distributor.rules:
				pattern = re.compile(r['regex'])
				if pattern.match(filename):
					download_folder = r['save_to_path']
					attach_rule = r 
					break
			
			if download_folder == None:
				print("No regex matched the filename ", filename)
				continue

			# open the attachment and write it to the location
			# of the download_folder + filename
			
			date = datetime.datetime.now()
			months = ["12 - Dec", "01 - Jan", "02 - Feb", "03 - Mar", "04 - Apr", "05 - May", "06 - Jun"
			, "07 - Jul", "08 - Aug", "09 - Sep", "10 - Oct", "11 - Nov", "12 - Dec"]
		
			prevMonthFolder = months[(date.month - 1) % 12]
			year = str(date.year)

			
			full_dir_path = os.path.join(download_folder, year, prevMonthFolder)
			os.makedirs(full_dir_path, exist_ok=True)
			att_path = os.path.join(full_dir_path, filename)
			name, file_extension = os.path.splitext(att_path)
			
			# DON"T OVERWRITE, but maybe we want to...?
			if not os.path.isfile(att_path):
				fp = open(att_path, 'wb+')
				fp.write(part.get_payload(decode=True))
				fp.close()

				# only send internal notifiations if actually POS data
				if attach_rule['is_pos_data']:
					has_pos_data = True
					if self.distributor.notify:
						Reminders.notify_downloaded_file(self.distributor, filename, att_path)
					print("Downloaded: " + filename + "\nTo: " + att_path + "\nFrom: " + self.distributor.name + "\n")
			

			# maybe a better way to structure rules...?
			if att_path != "No attachment found.":
				self.attachments.append((att_path, attach_rule))

		return has_pos_data

