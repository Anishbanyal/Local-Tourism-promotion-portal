import sqlite3

conn = sqlite3.connect("tourism_user_data.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")

users = cursor.fetchall()

for user in users:
    print(user)
