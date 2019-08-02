# distributor class
# sync method pulls relevant data from SQL into class instance
# TODO:
#	add error checking/handling
#
class Distributor:
	
	def __init__(self, relationship_id, db_connection):
		self.db_connection = db_connection
		self.relationship_id = relationship_id
		self.name = ""
		self.supplier_id = 0
		self.supplier = {}
		
		self.delivery_method = ''
		
		self.received_data = False
		
		self.escalate = False
		self.notify = False

		self.business_day_expected = 0
		self.ovveride_first_reminder = None
		self.ovveride_second_reminder = None

		self.reminders_sent = 0

		self.data_import = False
		
		self.ftp_info = {}
		self.rules = []
		

		self.contacts = []
		self.sync()
				
	def sync(self):

		cur = self.db_connection.cursor(buffered = True, dictionary=True)
		

		cur.execute('select * from distributors where id = %s', (self.relationship_id,))
		if cur.rowcount != 0:
			result = cur.fetchall()[0]
			self.name = result['distributor']
			self.supplier_id = result['supplier_id']
			self.delivery_method = result['delivery_method']
			self.received_data = (result['received_data'] == 1)
			self.business_day_expected = result['business_day_expected']
			self.escalate = (result['escalate'] == 'Y')
			self.notify = (result['notify'] == 'Y')
			self.reminders_sent = result['reminders_sent']
			self.data_import = (result['data_import'] == 1)

		
		# get ftp information if needed
		if self.delivery_method == 'F':			
			cur.execute('select * from ftp_info where distributor_id = %s', (self.relationship_id,))
			if cur.rowcount != 0:
				result = cur.fetchall()[0]
				self.ftp_info = result				
		

		# get data contact information
		cur.execute("""
				select contacts.last_name,  contacts.first_name, contacts.email, distributor_contacts.is_data_contact, 
					distributor_contacts.is_supplier_contact,  distributor_contacts.is_cc,  
					distributor_contacts.is_bcc,  distributor_contacts.is_internal
				from distributor_contacts
					inner join contacts
					on distributor_contacts.contact_id = contacts.id 
					where distributor_contacts.distributor_id = %s
			""", (self.relationship_id,))
		result = cur.fetchall()
		for r in result:
			self.contacts.append(r)
		
		



		# THE ORDER MATTERS!!!!

		# get rules		
		cur.execute('select * from rules where distributor_id = %s', (self.relationship_id,))
		result = cur.fetchall()
		
		for r in result:
			self.rules.append(r)	

		cur.execute('select * from suppliers where id = %s', (self.supplier_id,))

		result = cur.fetchall()
		self.supplier = result[0]
		
		cur.close()





