import sqlite3
import json
import os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'QS_Project.db')
DB = os.path.abspath(DB)

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [r[0] for r in c.fetchall()]
res = {}
for t in tables:
    try:
        c.execute(f'SELECT COUNT(*) FROM "{t}"')
        res[t] = c.fetchone()[0]
    except Exception as e:
        res[t] = f'ERROR: {e}'

print(json.dumps({'db': DB, 'tables': tables, 'counts': res}, indent=2))
conn.close()
