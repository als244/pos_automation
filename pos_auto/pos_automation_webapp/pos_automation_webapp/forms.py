from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, DateField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email



class SupplierForm(FlaskForm):

	supplier = StringField('Supplier', validators=[DataRequired()])
	sender_email = StringField("Sender Email", validators=[DataRequired(), Email()])
	subject_line = StringField('Subject Line, NEEDS to contain "<b>{prev_month}</b>" in it.', validators=[DataRequired()])
	submit = SubmitField("Update Supplier")
	delete = SubmitField("Delete Supplier")


class DistributorForm(FlaskForm):
	"""docstring for AddDistributor"""

	supplier = SelectField('Supplier', choices = [])
	distributor = StringField('Distributor', validators=[DataRequired()])
	delivery_method = SelectField('Delivery Method', choices = [(1, 'Email'), (2, 'FTP')])
	received_data = BooleanField("Received Data This Month Already")
	will_send_reminders = BooleanField("Send late data reminders", default=True)
	internally_notify = BooleanField("Internal notifications", default=True)
	data_import = BooleanField("Data import", default=True)
	business_day_expected = IntegerField("Business Days Expected", validators=[DataRequired()])
	override_second_reminder_date = DateField("Override when the <b>second</b> reminder this month", format="%m/%d/%Y")
	reminders_sent = IntegerField("Reminders already sent this month", default=0)
	notes = TextAreaField("Notes:")
	save_to_path = StringField("Directory Path for <b>saving</b> files")
	sql_template_path = StringField("Absolute Path (ends with filename.sql) for SQL Template to use for import")
	ftp_path = StringField("<b>IF FTP delivery</b>; <u>path</u> for distributor-specific directory for FTP (might be different than on the portal, check on the actual server).")
	submit = SubmitField("Update Distributor")
	delete = SubmitField("Delete Distributor")


class ContactForm(FlaskForm):
	supplier = SelectField('Supplier', choices=[])
	distributor = SelectField("Distributor", choices=[])
	contact = SelectField("Contact", choices=[])
	first_name = StringField("First Name", validators=[DataRequired()])
	last_name = StringField("Last Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired(), Email()])
	is_data_contact = BooleanField("Data Contact", default=True)
	is_supplier_contact = BooleanField("Supplier Contact")
	is_cc = BooleanField("CC")
	is_bcc = BooleanField("BCC")
	submit = SubmitField("Update Contact")
	unlink = SubmitField("Unlink Contact")
	delete = SubmitField("Delete Contact")

class SelectDistributorForm(FlaskForm):

	supplier = SelectField('Supplier', choices= [])
	distributor = SelectField('Distributor', choices = [])
	submit = SubmitField("Select Distributor")

class SelectSupplierForm(FlaskForm):
	supplier = SelectField('Supplier', choices = [])
	submit = SubmitField("Select Supplier")


class SelectContactForm(FlaskForm):
	supplier = SelectField('Supplier', choices= [])
	distributor = SelectField('Distributor', choices = [])
	contact = SelectField("Contact", choices=[])
	submit = SubmitField("Select Contact")
		