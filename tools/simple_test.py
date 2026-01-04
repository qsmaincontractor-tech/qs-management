import sqlite3

try:
    conn = sqlite3.connect('database/QS_Project.db', timeout=5)
    c = conn.cursor()
    c.execute('DELETE FROM "Document Manager"')
    conn.commit()
    c.execute('SELECT COUNT(*) FROM "Document Manager"')
    count = c.fetchone()[0]
    print(f'Records after delete: {count}')
    conn.close()
    print('Test record deleted successfully')
except Exception as e:
    print(f'Error: {e}')