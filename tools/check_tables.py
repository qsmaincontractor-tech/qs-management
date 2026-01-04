import sqlite3

conn = sqlite3.connect('database/QS_Project.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [r[0] for r in c.fetchall()]
print('Tables:', tables)
conn.close()