import aurora
import numpy as np
import datetime
import postmark.config
from postmarker.core import PostmarkClient


class Reminders:


	holidays = np.array(['2019-07-04', '2019-09-02', '2019-10-14', '2019-11-11', '2019-11-28', '2019-12-25'], dtype='datetime64')
	POSTMARK_TOKEN = postmark.config.postmark_info["token"]
	
	def get_distributors_to_remind(date):
		start = date.strftime("%Y-%m-01")
		today = date.strftime("%Y-%m-%d")


		# might need to add one, depending on how business days are counted
		cur_bus_day = np.busday_count(start, today, holidays=Reminders.holidays)
		cn = aurora.aurora_connect()
		cur = cn.cursor()

		# ones to send first reminder
		cur.execute("select id from distributors where escalate = 'Y' && received_data = 0 && business_day_expected <= " + str(cur_bus_day)  + " && reminders_sent = 0 && (override_second_reminder_date is null || override_second_reminder_date > CONVERT(%s, DATE))", (today,))

		first_reminders = cur.fetchall()

		# ones to send final reminder
		cur.execute("select id from distributors where escalate = 'Y' && received_data = 0 && business_day_expected <= " + str(cur_bus_day) + " && reminders_sent = 1 && override_second_reminder_date is null")

		auto_second_reminders = cur.fetchall()

		cur.execute("select id from distributors where escalate = 'Y' && received_data = 0 && override_second_reminder_date is not null && override_second_reminder_date <= CONVERT(%s, DATE)", (today,))

		override_second_reminders = cur.fetchall()
		print(override_second_reminders)

		second_reminders = auto_second_reminders + override_second_reminders

		print(second_reminders)
		cur.close()
		cn.close()

		return first_reminders, second_reminders



	def send_reminder(distributor, send_to, to_name, cc, bcc, reminder_number, date):
		postmark = PostmarkClient(server_token = Reminders.POSTMARK_TOKEN)
		months = ["December", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
		
		prevMonth = months[(date.month - 1) % 12]
	

		supplier = distributor.supplier
		
		sender = supplier['sender_email']
		subject = supplier['subject_line']
		subject.format(prev_month = prevMonth)
		first_body_raw = supplier['first_email_body']

		first_body = first_body_raw.format(name=to_name, prev_month = prevMonth)
		second_body_raw = supplier['second_email_body']
		second_body = second_body_raw.format(name=to_name, prev_month = prevMonth)
		
		if reminder_number == 1:
			postmark.emails.send(From=sender, To=send_to, Cc = cc, Bcc = bcc, Subject=subject, HtmlBody= first_body)
			print("Would have sent first reminder to " + send_to + " at " + distributor.name)
			Reminders.update_reminders_sent(distributor, 1)
		elif reminder_number == 2:
			postmark.emails.send(From=sender, To=send_to, Cc = cc, Bcc = bcc, Subject=subject, HtmlBody= second_body)
			print("Would have sent second reminder to " +  send_to + " at " + distributor.name)
			Reminders.update_reminders_sent(distributor, 2)
		else:
			print("don't have format for sending reminder #", reminder_number)


	def reset_reminders():
		cn = aurora.aurora_connect()
		cur = cn.cursor()   

		cur.execute("update distributors set reminders_sent = 0")

		cur.close()
		cn.close()

	def daily_routine(date, all_distributors):

		first_reminders, second_reminders = Reminders.get_distributors_to_remind(date)
		
		
		for d in first_reminders:
			d_id = d[0]
			if d_id not in all_distributors:
				continue

			distributor = all_distributors[d_id]
			

			CC = ['pos@precisioncorp.net']
			BCC = []
			data_contact = None
			all_contacts = distributor.contacts
			for contact in all_contacts:
				if contact['is_data_contact']:
					data_contact = contact
				if contact['is_cc']:
					CC.append(contact['email'])
				if contact['is_bcc']:
					BCC.append(contact['email'])
				
			# send the first reminder  
			if data_contact:
				Reminders.send_reminder(distributor, data_contact['email'], data_contact['first_name'], CC, BCC, 1, date)
			else:
				print("No data contact for " + distributor.name)
		for d in second_reminders:
			d_id = d[0]
			if d_id not in all_distributors:
				continue

			distributor = all_distributors[d_id]
			CC = ['pos@precisioncorp.net']
			BCC = []
			data_contact = None
			all_contacts = distributor.contacts
			for contact in all_contacts:
				if contact['is_data_contact']:
					data_contact = contact
				if contact['is_cc']:
					CC.append(contact['email'])
				if contact['is_bcc']:
					BCC.append(contact['email'])
				if contact['is_supplier_contact']:
					CC.append(contact['email'])
			if data_contact:	
				Reminders.send_reminder(distributor, data_contact['email'], data_contact['first_name'], CC, BCC, 2, date)
			else:
				print("No data contact for " + distributor.name)
		
		return first_reminders, second_reminders

	
	def update_reminders_sent(distributor, set_to):

		cn = aurora.aurora_connect()
		cur = cn.cursor()

		cur.execute("update distributors set reminders_sent = " + str(set_to) + " where id = %s", (distributor.relationship_id,))
	
		cur.close()
		cn.close()

	def update_received_data(distributor, set_to):

		cn = aurora.aurora_connect()
		cur = cn.cursor()

		cur.execute("update distributors set received_data = " + str(set_to) + " where id = %s", (distributor.relationship_id, ))
		
		cur.close()
		cn.close()



	def notify_downloaded_file(distributor, filename, fpath):
		postmark = PostmarkClient(server_token = Reminders.POSTMARK_TOKEN)
		send_to = 'datavalidation@precisioncorp.net'
		cc = None
		bcc = None
		
		date = datetime.datetime.now()
		months = ["December", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
		prev_month = months[(date.month - 1) % 12]

		print("DOWNLOADED file " + filename + " from " + distributor.name + " to " + fpath)
		# THERE IS A EMAIL FORMAT FROM CHRISTINE, this is a draft for testsing
		postmark.emails.send(From='pos@precisioncorp.net', To=send_to, Cc = cc, Bcc = bcc, Subject='DOWNLOADED ' + filename + ' from ' + distributor.name , HtmlBody='<html><body><p>The ' + prev_month + ' data from ' + distributor.name + ' for ' + distributor.supplier['supplier'] + ' has been saved down: <b>' + fpath + '</b>')

	def notify_uploaded_to_server(distributor, fpath, row_count):
		date = datetime.datetime.now()
		months = ["December", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
		prev_month = months[(date.month - 1) % 12]

		postmark = PostmarkClient(server_token = Reminders.POSTMARK_TOKEN)
		send_to = 'datavalidation@precisioncorp.net'
		cc = None
		bcc = None
		
		print("UPLOADED file " + fpath + " from " + distributor.name + " to database")
		postmark.emails.send(From='pos@precisioncorp.net', To=send_to, Cc = cc, Bcc = bcc, Subject='UPLOADED ' + fpath + ' from ' + distributor.name + ' to database' , HtmlBody='<html><body><p>The ' + prev_month + ' data from '+ distributor.name + ' for ' + distributor.supplier['supplier'] + ' has been imported to the <b>ftp_auto</b> database. <b>' + str(row_count) + '</b> rows were affected.')
		
	def notify_error_uploading(distributor, fpath):
		postmark = PostmarkClient(server_token = Reminders.POSTMARK_TOKEN)
		send_to = 'datavalidation@precisioncorp.net'
		cc = None
		bcc = None

		postmark.emails.send(From='pos@precisioncorp.net', To=send_to, Cc = cc, Bcc = bcc, Subject='ERROR: could not upload ' + fpath + ' from ' + distributor.name + ' to database' , HtmlBody='<html><body><p>Notification that the automation system failed to upload a file to the database.<br><br>Distributor: <b>' + distributor.name + '</b><br>File Path: <b>' + fpath + '</b>')

	def notify_exit(error):
		postmark = PostmarkClient(server_token = Reminders.POSTMARK_TOKEN)
		send_to = 'datavalidation@precisioncorp.net'
		cc = None
		bcc = None
		postmark.emails.send(From='posauto@precisioncorp.net', To=send_to, Cc = cc, Bcc = bcc, Subject='ERROR: the automation system terminated', HtmlBody='<html><body><p>Notification that the automation system stopped running.<br><br>The error reported was: <br><br> ' + repr(error))

	
	def reset_received_data():
		cn = aurora.aurora_connect()
		cur = cn.cursor()

		cur.execute("update distributors set received_data = 0")

		cur.close()
		cn.close()


	def send_daily_reminders(date, all_distributors):
		first_reminders, second_reminders = Reminders.daily_routine(date, all_distributors)
		show_first_reminders = [all_distributors[d_id[0]].name for d_id in first_reminders]
		show_second_reminders = [all_distributors[d_id[0]].name for d_id in second_reminders]
		print("First Reminders sent to: ", show_first_reminders)
		print("Second Reminders sent to: ", show_second_reminders)
