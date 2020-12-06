import mysql.connector
from mysql.connector import errorcode

# MySQL
config = {
  'host':'epms-aws.ctcinzn7r07y.us-east-2.rds.amazonaws.com',
  'user':'admin',
  'password':'wilshire',
  'database':'epms',
}

def readData(sql):
	try:
	    conn = mysql.connector.connect(**config)
	    print("Connection established")
	    cursor = conn.cursor()
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with the user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")
		else:
			print(err)

	# Select Statement
	cursor.execute(sql)
	rows = cursor.fetchall()
	print("Read", cursor.rowcount, "row(s) of data.")

	# Cleanup
	cursor.close()
	conn.close()

	# Return data
	return rows

def updateData(sql):
	try:
	    conn = mysql.connector.connect(**config)
	    print("Connection established")
	    cursor = conn.cursor()
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with the user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")
		else:
			print(err)

	# Update/Delete Statement
	cursor.execute(sql)
	print("Updated", cursor.rowcount, "row(s) of data.")

	# Cleanup
	conn.commit()
	cursor.close()
	conn.close()
	print("Done.")

def insertData(sql):
	try:
	    conn = mysql.connector.connect(**config)
	    print("Connection established")
	    cursor = conn.cursor()
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print("Something is wrong with the user name or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print("Database does not exist")
		else:
			print(err)

	# Update/Delete Statement
	cursor.execute(sql)
	print("Inserted", cursor.rowcount, "row(s) of data.")

	# Cleanup
	conn.commit()
	cursor.close()
	conn.close()
	print("Done.")
