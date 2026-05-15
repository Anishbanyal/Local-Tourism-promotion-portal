import sqlite3
conn = sqlite3.connect('tourism_users.db')
cursor = conn.cursor()
cursor.execute('''select name from sqlite_master where type='table';''')
print(cursor.fetchall())    