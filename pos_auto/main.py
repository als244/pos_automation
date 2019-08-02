import aurora
import datetime
import time
import mysql
from distributor import Distributor
from fetchEmail import FetchEmail
from emailManager import EmailManager
from postmarker.core import PostmarkClient
from reminders import Reminders
import ftpmanager
import postmark.config
import email_server.config

import numpy as np
# TESTING STUFF
 

PRECISION_EMAIL_HOST = email_server.config.server_info["host"]
PREICSION_EMAIL_USER = email_server.config.server_info["user"]
PRECISION_EMAIl_PASSWORD = email_server.config.server_info["password"]

POSTMARK_TOKEN = postmark.config.postmark_info["token"]
REMINDER_SEND_FROM = postmark.config.postmark_info["from"]
REMINDER_BCC = postmark.config.postmark_info["bcc"]

prev_month = None
prev_day = None

holidays = np.array(['2019-07-04', '2019-09-02', '2019-10-14', '2019-11-11', '2019-11-28', '2019-12-25'], dtype='datetime64')

now = datetime.datetime.now()

reset = False

while True:
	cur_day = now.strftime("%Y-%m-%d")
	print("TODAY IS " + now.strftime("%Y-%m-%d") + " at " + now.strftime("%H:%M"))

	cur_bus_day = np.busday_count(now.strftime("%Y-%m-01"), cur_day, holidays=holidays)
	print("Current business day since beginning of month: ", str(cur_bus_day + 1))
	# connect to email server
	try:
		email_server = FetchEmail(PRECISION_EMAIL_HOST, PREICSION_EMAIL_USER, PRECISION_EMAIl_PASSWORD)
	except Exception as e:
		# send email, sayng need to restart program
		print("Error connecting to Precision email server: ", e)
		Reminders.notify_exit(e)
		break
	
	# monthy resest of reminders
	if now.month != prev_month:
		if reset:
			Reminders.reset_reminders()
			Reminders.reset_received_data()
		else:
			reset = True
		prev_month = now.month	
		
		cn = aurora.aurora_connect()
		cur = cn.cursor(dictionary = True)
		# get all distributors
		cur.execute('select id from distributors')
		
		result = cur.fetchall()

		#close cursor connection after fetching all distributors
		cur.close()

		try: 
			distributors = {}
			for r in result:
				d = (Distributor(r['id'], cn))
				distributors[d.relationship_id] = d

		except Exception as e:
			# send email reporting error about grabbing distributor info
			print("Error fetching distributor info from database: ", e)
			Reminders.notify_exit(e)
			break
		
	try:
		email_handler = EmailManager(distributors, email_server)
	except Exception as e:
		print("Error setting up email handler: ", e)
		Reminders.notify_exit(e)
		break
	

	# send the daily reminder after 9 am
	#if now.day != prev_day and now.hour > 9:
	email_count = email_handler.parse_emails()
	print("read " + str(email_count) + " emails")	

	
	# close email server
	email_server.close_connection()


	# do FTP check to scan if any distributor added a file
	ftpmanager.check_ftp(distributors)

	# send reminders on a new business day past 10 am
	if now.day != prev_day and now.hour >= 12 and np.is_busday(np.array([now.strftime("%Y-%m-%d")], dtype='datetime64'), holidays=holidays)[0]:
		Reminders.send_daily_reminders(now, distributors)
		prev_day = now.day

	
	#wait 15 minutes to fetch email again
	print("sleeping for 15 min")
	time.sleep(900)
	now += datetime.datetime.now()
#Reminders.reset_reminders()

