from pos_automation_webapp import app, mysql
from flask import render_template, jsonify, request, url_for, redirect
from .forms import SupplierForm, DistributorForm, ContactForm, SelectDistributorForm, SelectSupplierForm, SelectContactForm


@app.route("/")
@app.route("/home")
def home():
	return render_template('index.html')


@app.route("/add/supplier", methods = ['GET', 'POST'])
def addSupplier():

	form = SupplierForm()

	supplier_name = form.supplier.data
	sender_email = form.sender_email.data
	subject_line = form.subject_line.data

	sender_signature, first_email_body, sender_email_body, subject_line = None, None, None, None
	if request.method == 'POST':
		first_email_body = request.form['first_email_body']
		second_email_body = request.form['second_email_body']

		first_email_body = first_email_body.replace('\r', '').replace('\n', '')
		second_email_body = second_email_body.replace('\r', '').replace('\n', '')

		cur = mysql.connection.cursor()

		sql_query = """INSERT INTO suppliers (supplier, sender_email, first_email_body
		, second_email_body, subject_line) VALUES (%s, %s, %s, %s, %s)"""
		cur.execute(sql_query, [supplier_name, sender_email, first_email_body, 
			second_email_body, subject_line])
		mysql.connection.commit()
		cur.close()

	return render_template('supplierForm.html', form = form)


@app.route("/edit/select/supplier", methods = ['GET', 'POST'])
def selectSupplier():

	form = SelectSupplierForm()
	cur = mysql.connection.cursor()
	cur.execute("SELECT id, supplier from suppliers ORDER BY supplier")
	res = cur.fetchall()

	form.supplier.choices = [(supplier['id'], supplier['supplier']) for supplier in res]
	if request.method == 'POST':
		return redirect(url_for('editSupplier', supplier_id = form.supplier.data))


	return render_template('selectSupplier.html', form=form)

@app.route("/edit/supplier/<supplier_id>", methods = ['GET', 'POST'])
def editSupplier(supplier_id):
	cur = mysql.connection.cursor()
	cur.execute("SELECT * from suppliers where id = %s", (supplier_id, ))
	res = cur.fetchall()[0]

	formData = {'supplier': res['supplier'], 'sender_email':res['sender_email'], 'subject_line':res['subject_line']}

	form = SupplierForm(data=formData)


	if request.method == 'POST':
		cur = mysql.connection.cursor()
		if 'delete' in request.form:
			# first delete all the associated distributors
			cur.execute("DELETE from distributors where supplier_id = %s", (supplier_id, ))
			mysql.connection.commit()
			cur.execute("DELETE from suppliers where id = %s", (supplier_id, ))
			mysql.connection.commit()
		else:
			first_email_body = request.form['first_email_body']
			second_email_body = request.form['second_email_body']

			first_email_body = first_email_body.replace('\r', '').replace('\n', '')
			second_email_body = second_email_body.replace('\r', '').replace('\n', '')

			

			sql_query = """UPDATE suppliers SET supplier = %s, sender_email = %s, 
			first_email_body = %s, second_email_body = %s, subject_line = %s where id = %s"""
			cur.execute(sql_query, [form.supplier.data, form.sender_email.data, first_email_body, 
				second_email_body, form.subject_line.data, supplier_id])
			mysql.connection.commit()
			cur.close()
		return redirect(url_for('home'))

	return render_template("supplierForm.html", form=form, first_email=res['first_email_body'], second_email=res['second_email_body'], editing=True)


@app.route("/add/distributor", methods = ['GET', 'POST'])
def addDistributor():
	form = DistributorForm()


	cur = mysql.connection.cursor()

	cur.execute("SELECT id, supplier from suppliers ORDER BY supplier")
	res = cur.fetchall()

	form.supplier.choices =  [(s['id'], s['supplier']) for s in res]

	if request.method == 'POST':
		# new data contact

		delivery_method = 'E' if form.delivery_method.data == '1' else 'F'
		received_data = 1 if form.received_data.data else 0
		will_send_reminders = "Y" if form.will_send_reminders.data else "N"
		internally_notify = "Y" if form.internally_notify.data else "N"
		data_import = 1 if form.data_import.data else 0
		reminders_sent = form.reminders_sent.data if form.reminders_sent.data else 0
		notes = form.notes.data if form.notes.data else None

		sql_query = """INSERT INTO distributors (distributor, supplier_id
		, delivery_method, received_data, escalate, notify, business_day_expected, reminders_sent, notes, data_import) 
		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

		
		cur.execute(sql_query, [form.distributor.data, form.supplier.data, delivery_method, received_data
			, will_send_reminders, internally_notify, form.business_day_expected.data, reminders_sent, notes, data_import])
		mysql.connection.commit()

		cur.execute("SELECT id from distributors where distributor = %s && supplier_id = %s", [form.distributor.data, form.supplier.data])
		res = cur.fetchall()[0]
		distributor_id = res['id']
		if delivery_method == 'F' and len(request.form['ftp_path']) > 0:
			sql_query = """INSERT INTO ftp_info (distributor_id, path) VALUES (%s, %s)"""
			cur.execute(sql_query, [distributor_id, request.form['ftp_path']])
			mysql.connection.commit()

		sql_query = """INSERT INTO rules (distributor_id, save_to_path, sql_template_path)
						VALUES (%s, %s, %s)"""
		cur.execute(sql_query, [distributor_id, request.form['save_to_path'], request.form['sql_template_path']])
		mysql.connection.commit()
	
		cur.close()
		return redirect(url_for('home'))


	return render_template('distributorForm.html', form=form)

@app.route("/edit/select/distributor", methods = ['GET', 'POST'])
def selectDistributor():

	form = SelectDistributorForm()
	cur = mysql.connection.cursor()
	cur.execute("SELECT id, supplier from suppliers ORDER BY supplier")
	res = cur.fetchall()

	form.supplier.choices = [(supplier['id'], supplier['supplier']) for supplier in res]
	first_id = form.supplier.choices[0][0]
	print("supplier choices: ", form.supplier.choices)

	# START WITH SCJ Choices
	cur.execute("SELECT * from distributors where supplier_id = %s ORDER BY distributor", (first_id,))
	res = cur.fetchall()
	form.distributor.choices = [(d['id'], d['distributor']) for d in res]
	print("distributor choices: ", form.distributor.choices)

	if request.method == 'POST':
		return redirect(url_for('editDistributor', distributor_id = form.distributor.data))

	return render_template('selectDistributor.html', form = form)



@app.route("/edit/distributor/<distributor_id>", methods = ['GET', 'POST'])
def editDistributor(distributor_id):
	cur = mysql.connection.cursor()
	cur.execute("SELECT * from distributors where id = %s", (distributor_id, ))
	res = cur.fetchall()[0]
	supplier_id = res['supplier_id']
	

	# CREATING THIS DICT IS REDUDANT BUT WAS USING IT FOR TESTING
	formData = {'distributor':res['distributor'], 'supplier_id':res['supplier_id'], 'delivery_method':res['delivery_method'], 'received_data':res['received_data'], 'will_send_reminders':res['escalate'], 'internally_notify':res['notify'],
	'business_day_expected':res['business_day_expected'], 'override_second_reminder_date':res['override_second_reminder_date'],
	'reminders_sent':res['reminders_sent'], 'notes':res['notes'], 'data_import':res['data_import']}
	form = DistributorForm()

	cur.execute("SELECT id, supplier from suppliers where id = %s", (supplier_id, ))
	res = cur.fetchall()
	form.supplier.choices = [(supplier['id'], supplier['supplier']) for supplier in res]
	form.supplier.data = formData['supplier_id']

	form.distributor.data = formData['distributor']
	if formData['delivery_method']=='F':
		form.delivery_method.data = "2"
	else:
		form.delivery_method.data = "1"

	form.business_day_expected.data = formData['business_day_expected']
	form.override_second_reminder_date.data = formData['override_second_reminder_date']
	form.reminders_sent.data = formData['reminders_sent']
	form.data_import.data =True if formData['data_import'] == 1 else False
	form.received_data.data = True if formData['received_data'] == 1 else False
	form.will_send_reminders.data = True if formData['will_send_reminders'] == "Y" else False
	form.internally_notify.data = True if formData['internally_notify'] == "Y" else False
	form.notes.data = formData['notes']


	cur.execute("SELECT save_to_path, sql_template_path from rules where distributor_id = %s", (distributor_id, ))
	res = cur.fetchall()
	if not res:
		return redirect(url_for('home'))

	form.save_to_path.data = res['save_to_path']
	form.sql_template_path.data = res['sql_template_path']

	cur.execute("SELECT path from ftp_info where distributor_id = %s", (distributor_id, ))
	res = cur.fetchall()
	if res:
		form.ftp_path.data = res[0]['path']

	if request.method == 'POST':
		
		if 'delete' in request.form:
			cur.execute("delete from distributors where id = %s", (distributor_id, ))
			mysql.connection.commit()
		else:
			business_day_expected = int(request.form['business_day_expected'])
			delivery_method = 'E' if request.form['delivery_method'] == '1' else 'F'
			received_data = 1 if 'received_data' in request.form else 0
			will_send_reminders = "Y" if 'will_send_reminders' in request.form else "N"
			internally_notify = "Y" if 'internally_notify' in request.form else "N"
			data_import = 1 if 'data_import' in request.form  else 0
			reminders_sent = int(request.form['reminders_sent']) if request.form['reminders_sent'] else 0
			notes = form.notes.data if form.notes.data else None

			sql_query = """UPDATE distributors set distributor = %s, supplier_id = %s, delivery_method = %s, received_data = %s
			, escalate = %s, notify = %s, business_day_expected = %s, override_second_reminder_date = %s
			, reminders_sent = %s, notes = %s, data_import=%s where id = %s""" 

			cur.execute(sql_query, [form.distributor.data, supplier_id, delivery_method, received_data
				, will_send_reminders, internally_notify, business_day_expected
				, form.override_second_reminder_date.data, reminders_sent, notes, data_import, distributor_id])
			mysql.connection.commit()


	
			if delivery_method == 'F' and len(request.form['ftp_path']) > 0:
				sql_query = """INSERT INTO ftp_info (distributor_id, path) VALUES (%s, %s) ON DUPLICATE KEY UPDATE path = %s"""
				cur.execute(sql_query, [distributor_id, request.form['ftp_path'], request.form['ftp_path']])
				mysql.connection.commit()

			sql_query = """UPDATE rules set save_to_path=%s, sql_template_path=%s where distributor_id = %s"""
			cur.execute(sql_query, [request.form['save_to_path'], request.form['sql_template_path'], distributor_id])
			mysql.connection.commit()

		return redirect(url_for('home'))

	return render_template("distributorForm.html", form=form, editing=True)



# USED TO DETERMINE THE DISTRIBUTORS ASSOCIATED WITH A CERTAIN SUPPLIER ON THE EDIT DISTRIBUTOR PAGE
@app.route("/select/distributor/<supplier_id>")
def fill_in_distributors(supplier_id):
	cur = mysql.connection.cursor()
	cur.execute("SELECT id, distributor from distributors where supplier_id = %s ORDER BY distributor", (supplier_id,))
	res = cur.fetchall()
	cur.close()
	return jsonify({'distributors' : res})


@app.route("/select/contact/info/<contact_id>")
def fill_in_contact_info(contact_id):
	cur = mysql.connection.cursor()
	cur.execute("SELECT * from contacts where id = %s ORDER BY first_name", (contact_id,))
	res = cur.fetchall()
	cur.close()
	return jsonify({'info' : res})

@app.route("/add/contact", methods=["GET", "POST"])
def addContact():
	cur = mysql.connection.cursor()
	form = ContactForm()

	cur.execute("SELECT id, supplier from suppliers ORDER BY supplier")
	res = cur.fetchall()

	form.supplier.choices = [(supplier['id'], supplier['supplier']) for supplier in res]
	print("supplier choices: ", form.supplier.choices)
	if form.supplier.choices:
		first_supplier_id = form.supplier.choices[0][0]
		print(first_supplier_id)
	
		# START WITH SCJ Choices
		cur.execute("SELECT * from distributors where supplier_id = %s ORDER BY distributor", (first_supplier_id,))
		res = cur.fetchall()
		form.distributor.choices = [(d['id'], d['distributor']) for d in res]
	
	cur.execute("SELECT id, first_name, last_name from contacts ORDER BY first_name")
	res = cur.fetchall()
	contact_choices = [(c['id'], c['first_name'] + " " + c['last_name']) for c in res]
	form.contact.choices = [(0, 'I will add a new contact below')] + contact_choices

	if request.method == "POST":
		if int(request.form['contact']) == 0:

			# NEED TO CHECK FOR DUPLICATE EMAIL FIRST!!!


			sql_query = """INSERT INTO contacts (last_name, first_name, email)
						VALUES (%s, %s, %s)"""

			cur.execute(sql_query, [request.form['last_name'], request.form['first_name'], request.form['email']])
			mysql.connection.commit()
			cur.execute("SELECT id from contacts where email=%s", (request.form['email'], ))
			contact_id = cur.fetchall()[0]['id']

		else:
			contact_id = int(request.form['contact'])

		is_data_contact = 1 if 'is_data_contact' in request.form else 0
		is_supplier_contact = 1 if 'is_supplier_contact' in request.form else 0
		is_cc = 1 if 'is_cc' in request.form else 0
		is_bcc = 1 if 'is_bcc' in request.form else 0

		sql_query = """INSERT INTO distributor_contacts (distributor_id, contact_id, is_data_contact, is_supplier_contact 
						, is_cc, is_bcc)
						VALUES(%s, %s, %s, %s, %s, %s)"""

		cur.execute(sql_query, [form.distributor.data, contact_id, is_data_contact, is_supplier_contact, is_cc, is_bcc])
		mysql.connection.commit()
		return redirect(url_for('home'))

	return render_template('contactForm.html', form=form)



@app.route("/edit/select/contact", methods=["GET", "POST"])
def selectContact():

	form = SelectContactForm()

	cur = mysql.connection.cursor()
	cur.execute("SELECT id, supplier from suppliers ORDER BY supplier")
	res = cur.fetchall()

	form.supplier.choices = [(supplier['id'], supplier['supplier']) for supplier in res]
	if form.supplier.choices:
		first_supplier_id = form.supplier.choices[0][0]
		print("supplier choices: ", form.supplier.choices)

		# START WITH SCJ Choices
		cur.execute("SELECT * from distributors where supplier_id = %s order by distributor", (first_supplier_id,))
		res = cur.fetchall()
		form.distributor.choices = [(d['id'], d['distributor']) for d in res]
		if form.distributor.choices:
			first_distrib_id = form.distributor.choices[0][0]
			cur.execute("SELECT contacts.id, contacts.last_name, contacts.first_name from contacts join distributor_contacts on distributor_contacts.contact_id = contacts.id where distributor_id = %s ORDER BY contacts.first_name", (first_distrib_id,))
			res = cur.fetchall()
			form.contact.choices = [(c['id'], c['first_name'] + " " + c['last_name']) for c in res]


	if request.method == "POST":
		return redirect(url_for('editContact', supplier_id = form.supplier.data, distributor_id=form.distributor.data, contact_id = form.contact.data))


	return render_template('selectContact.html', form=form)

@app.route("/select/contact/<distributor>")
def fill_in_contacts(distributor):
	cur = mysql.connection.cursor()
	cur.execute("SELECT contacts.id, contacts.last_name, contacts.first_name from contacts join distributor_contacts on distributor_contacts.contact_id = contacts.id where distributor_id = %s order by contacts.first_name", (distributor,))
	res = cur.fetchall()
	cur.close()
	return jsonify({'contacts' : res})

@app.route("/edit/contact/<supplier_id>/<distributor_id>/<contact_id>", methods=["GET", "POST"])
def editContact(supplier_id, distributor_id, contact_id):

	form = ContactForm()
	cur = mysql.connection.cursor()

	cur.execute("SELECT id, supplier from suppliers ORDER BY supplier")
	res = cur.fetchall()


	form.supplier.choices = [(supplier['id'], supplier['supplier']) for supplier in res]

	# START WITH SCJ Choices
	cur.execute("SELECT * from distributors where supplier_id = %s ORDER BY distributor", (supplier_id,))
	res = cur.fetchall()
	form.distributor.choices = [(d['id'], d['distributor']) for d in res]

	form.supplier.data = supplier_id
	form.distributor.data = distributor_id

	cur.execute("SELECT * from contacts where id = %s", (contact_id,))
	res = cur.fetchall()[0]
	form.first_name.data = res['first_name']
	form.last_name.data = res['last_name']
	form.email.data = res['email']

	cur.execute("SELECT * from distributor_contacts where distributor_id = %s && contact_id = %s", [distributor_id, contact_id])
	res = cur.fetchall()[0]

	form.is_data_contact.data = (res['is_data_contact'] == 1)
	form.is_supplier_contact.data = (res['is_supplier_contact'] == 1)
	form.is_cc.data = res['is_cc'] == 1
	form.is_bcc.data = res['is_bcc'] == 1


	if request.method == "POST":

		if 'delete' in request.form:
			cur.execute("DELETE from distributor_contacts where contact_id = %s", (contact_id, ))
			mysql.connection.commit()
			cur.execute("DELETE from contacts where id = %s", (contact_id, ))
			mysql.connection.commit()
		elif 'unlink' in request.form:
			cur.execute("DELETE from distributor_contacts where contact_id = %s", (contact_id, ))
			mysql.connection.commit()
		else:
			sql_query = """UPDATE contacts set last_name = %s, first_name = %s, email = %s where id = %s"""

			cur.execute(sql_query, [request.form['last_name'], request.form['first_name'], request.form['email'], contact_id])
			mysql.connection.commit()
			is_data_contact = 1 if 'is_data_contact' in request.form else 0
			is_supplier_contact = 1 if 'is_supplier_contact' in request.form else 0
			is_cc = 1 if 'is_cc' in request.form else 0
			is_bcc = 1 if 'is_bcc' in request.form else 0

			sql_query = """UPDATE distributor_contacts set is_data_contact = %s, is_supplier_contact = %s, is_cc = %s
			, is_bcc = %s where distributor_id = %s && contact_id = %s"""

			cur.execute(sql_query, [is_data_contact, is_supplier_contact, is_cc, is_bcc, distributor_id, contact_id])
			mysql.connection.commit()

		return redirect(url_for('home'))


	return render_template('contactForm.html', form=form, editing=True)


@app.route("/viewDatabase")
def viewDatabase():
	return render_template('viewDatabase.html')

@app.route("/other")
def other():
	return render_template('other.html')
