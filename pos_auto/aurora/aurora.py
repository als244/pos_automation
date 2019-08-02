import mysql.connector
import aurora.config

def aurora_connect(user = aurora.config.mysql['user'], password = aurora.config.mysql['password'], host = aurora.config.mysql['host'], database = aurora.config.mysql['database']):
	return mysql.connector.connect(user=user, password=password, host=host, database=database, allow_local_infile=True, autocommit=True, compress=True)

	