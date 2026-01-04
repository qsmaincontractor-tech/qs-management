import sqlite3

conn = sqlite3.connect('database/QS_Project.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM "Sub Contract IP Application"')
count = c.fetchone()[0]
print(f'Sub Contract IP Application table exists, count: {count}')
conn.close()