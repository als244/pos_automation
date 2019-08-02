from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'pre-aurora1.c8ueqdj3eykb.us-west-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'pos.automation'
app.config['MYSQL_PASSWORD'] = 'faN#$VtyW347'
app.config['MYSQL_DB'] = 'ftp_auto'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

app.secret_key = b'fsd90fjel$&#Ndsff2/xvds'

mysql = MySQL(app)


import pos_automation_webapp.views