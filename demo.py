import sqlite3
c = 'kunalpatel1403@gmail.com'
conn = sqlite3.connect('WeaponDetection.db')
cursor = conn.cursor()
s = "SELECT *  FROM history"
cursor.execute(s)
r = cursor.fetchall()
conn.commit()
conn.close()
print(r)