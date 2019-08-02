# -*- coding: utf-8 -*-
from collections import defaultdict
from email.utils import parseaddr
from emailAttachment import EmailAttachment
from reminders import Reminders
from fileUploader import FileUploader

class EmailManager:

	def __init__(self, all_distributors, email_server):
		self.all_distributors = all_distributors
		self.email_server = email_server
		self.email_to_distributor = defaultdict(list)
		self.populate_email_to_distrib()


	def populate_email_to_distrib(self):
		for d in self.all_distributors.values():
			
			# HERE WE CAN CHANGE IF THERE AR MULTIPLE CONTACTS
			s = None
			c = None
			for contact in d.contacts:
				if contact['is_data_contact']:
					self.email_to_distributor[contact['email']].append(d)
			

	

	# reads all undread messages asscoiated with self.email_server
	# we care about emails from a distributor data contact, with a valuable attachment (.csv, .txt, .xlsx, etc.)
	def parse_emails(self):
		emails = self.email_server.fetch_unread_messages()
		cnt = 0
		for email in emails:
			emailFrom = parseaddr(email['from'])[1]
			if emailFrom in self.email_to_distributor:

				# NEED TO DETERMINE THE ASSCOCIATED SUPPLIER IF EMAIL SI ASSOCIATED WITH MULTIPLE
				# NOT DOING THAT NOW
				associated_distrib = self.email_to_distributor[emailFrom][0]
				print(associated_distrib.name)

				print("Received email from " + emailFrom + " at " + associated_distrib.name)

				attach_obj = EmailAttachment(email, associated_distrib)
				has_pos_data = attach_obj.download_attachments()


				# set the value in the database of the associated distrib
				# to be that the distribute sent in POS data
				if has_pos_data:
					Reminders.update_received_data(associated_distrib, 1)


				# try to upload every attachment
				# assume the upload function in EmailAttachment will parse files and error check 

				if associated_distrib.data_import:
				# attach is a tuple of (fpath, rule)					
					for attach in attach_obj.attachments:
						if associated_distrib.data_import:
							FileUploader.upload_file_to_server(associated_distrib, attach[0], attach[1])
	
			
			# email from non-distributor
			
		return len(emails)


		